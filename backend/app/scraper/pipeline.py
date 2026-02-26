from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.events.bus import EventBus
from app.events.models import ScrapeEvent
from app.models.lead import Lead
from app.models.scrape_job import JobStatus, ScrapeJob
from app.scraper.enrichment import enrich_apollo, enrich_email_hunter
from app.scraper.scoring import score_lead
from app.scraper.search import parse_place, search_google_places
from app.scraper.website import scrape_website

log = logging.getLogger(__name__)


class ScrapeOrchestrator:
    """Full scrape pipeline: search -> scrape -> enrich -> score -> persist."""

    def __init__(
        self,
        db: Session,
        event_bus: EventBus,
        api_keys: dict,
        scoring_weights: dict = None,
    ):
        self.db = db
        self.event_bus = event_bus
        self.api_keys = api_keys
        self.scoring_weights = scoring_weights

    def run(self, job_id: int, category: str, location: str, num_results: int = 20, delay: float = 1.5):
        job = self.db.query(ScrapeJob).get(job_id)
        job.status = JobStatus.RUNNING
        self.db.commit()
        self._emit(job_id, "started", {"category": category, "location": location})

        try:
            # Search
            self._emit(job_id, "searching", {"category": category, "location": location})
            places = search_google_places(
                category, location, num_results,
                serper_key=self.api_keys.get("serper_key", ""),
                serpapi_key=self.api_keys.get("serpapi_key", ""),
            )
            self._emit(job_id, "search_complete", {"count": len(places)})

            if not places:
                job.status = JobStatus.COMPLETED
                job.lead_count = 0
                job.completed_at = datetime.now(timezone.utc)
                self.db.commit()
                self._emit(job_id, "completed", {"lead_count": 0})
                return

            # Process each place
            leads_data = []
            for i, place in enumerate(places):
                if self._is_cancelled(job_id):
                    job.status = JobStatus.CANCELLED
                    self.db.commit()
                    self._emit(job_id, "cancelled", {})
                    return

                lead_data = parse_place(place)

                # Scrape website
                website_data = scrape_website(lead_data["website"])
                lead_data.update(website_data)

                # Enrichment
                domain = ""
                if lead_data["website"]:
                    try:
                        domain = urlparse(lead_data["website"]).netloc.replace("www.", "")
                    except Exception:
                        pass
                lead_data["domain"] = domain

                hunter_data = enrich_email_hunter(domain, self.api_keys.get("hunter_key", ""))
                lead_data.update(hunter_data)

                apollo_data = enrich_apollo(domain, self.api_keys.get("apollo_key", ""))
                lead_data.update(apollo_data)

                # Score
                lead_data["score"] = score_lead(lead_data, self.scoring_weights)
                leads_data.append(lead_data)

                self._emit(job_id, "lead_processed", {
                    "index": i + 1,
                    "total": len(places),
                    "business_name": lead_data["business_name"],
                    "score": lead_data["score"],
                    "scrape_status": lead_data.get("scrape_status", ""),
                })
                time.sleep(delay)

            # Deduplicate
            leads_data = self._deduplicate(leads_data)

            # Persist to DB
            for ld in leads_data:
                lead = Lead(job_id=job_id, **self._to_model_fields(ld))
                self.db.add(lead)

            job.status = JobStatus.COMPLETED
            job.lead_count = len(leads_data)
            job.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self._emit(job_id, "completed", {"lead_count": len(leads_data)})

        except Exception as e:
            log.error(f"Pipeline error for job {job_id}: {e}", exc_info=True)
            job.status = JobStatus.FAILED
            job.error_message = str(e)[:500]
            self.db.commit()
            self._emit(job_id, "failed", {"error": str(e)[:200]})

    def _emit(self, job_id: int, event_type: str, data: dict):
        self.event_bus.publish(f"job:{job_id}", ScrapeEvent(type=event_type, data=data))

    def _is_cancelled(self, job_id: int) -> bool:
        self.db.expire_all()
        job = self.db.query(ScrapeJob).get(job_id)
        return job.status == JobStatus.CANCELLED

    def _deduplicate(self, leads: list) -> list:
        seen_domains = set()
        seen_names = set()
        unique = []
        for lead in leads:
            d = lead.get("domain", "")
            n = lead.get("business_name", "")
            if d and d in seen_domains:
                continue
            if not d and n in seen_names:
                continue
            if d:
                seen_domains.add(d)
            seen_names.add(n)
            unique.append(lead)
        return unique

    def _to_model_fields(self, data: dict) -> dict:
        return {
            "business_name": data.get("business_name", ""),
            "category": data.get("category", ""),
            "address": data.get("address", ""),
            "phone": data.get("phone", ""),
            "website": data.get("website", ""),
            "domain": data.get("domain", ""),
            "rating": data.get("rating"),
            "reviews": data.get("reviews"),
            "google_maps_url": data.get("google_maps_url", ""),
            "emails_found": data.get("emails_found", ""),
            "tech_stack": data.get("tech_stack", ""),
            "has_it_mention": data.get("has_it_mention", False),
            "has_existing_msp": data.get("has_existing_msp", False),
            "compliance_mention": data.get("compliance_mention", ""),
            "ssl_valid": data.get("ssl_valid", False),
            "scrape_status": data.get("scrape_status", ""),
            "hunter_email": data.get("hunter_email", ""),
            "hunter_name": data.get("hunter_name", ""),
            "hunter_confidence": data.get("hunter_confidence"),
            "apollo_email": data.get("apollo_email", ""),
            "apollo_name": data.get("apollo_name", ""),
            "apollo_title": data.get("apollo_title", ""),
            "company_size": data.get("company_size", ""),
            "industry": data.get("industry", ""),
            "score": data.get("score", 0),
        }
