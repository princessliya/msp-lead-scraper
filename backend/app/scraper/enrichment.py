from __future__ import annotations

import logging

import requests

log = logging.getLogger(__name__)


def enrich_email_hunter(domain: str, hunter_key: str = "") -> dict:
    """Hunter.io domain search. Free tier: 25/month."""
    result = {"hunter_email": "", "hunter_name": "", "hunter_confidence": None}

    if not hunter_key or not domain:
        return result

    try:
        params = {"domain": domain, "api_key": hunter_key, "limit": 3}
        resp = requests.get("https://api.hunter.io/v2/domain-search", params=params, timeout=10)
        resp.raise_for_status()
        emails = resp.json().get("data", {}).get("emails", [])

        if emails:
            priority_titles = ["owner", "ceo", "president", "founder", "director", "manager"]
            best = None
            for e in emails:
                pos = (e.get("position") or "").lower()
                if any(t in pos for t in priority_titles):
                    best = e
                    break
            if not best:
                best = emails[0]

            result["hunter_email"] = best.get("value", "")
            result["hunter_name"] = f"{best.get('first_name', '')} {best.get('last_name', '')}".strip()
            result["hunter_confidence"] = best.get("confidence")

    except Exception as e:
        log.warning(f"Hunter.io error for {domain}: {e}")

    return result


def enrich_apollo(domain: str, apollo_key: str = "") -> dict:
    """Apollo.io enrichment. Free tier: 50 credits/month."""
    result = {
        "apollo_email": "",
        "apollo_name": "",
        "apollo_title": "",
        "company_size": "",
        "industry": "",
    }

    if not apollo_key or not domain:
        return result

    try:
        # Organization enrichment
        resp = requests.post(
            "https://api.apollo.io/v1/organizations/enrich",
            headers={"Content-Type": "application/json"},
            json={"api_key": apollo_key, "domain": domain},
            timeout=10,
        )
        resp.raise_for_status()
        org = resp.json().get("organization", {})
        result["company_size"] = str(org.get("estimated_num_employees", "")) if org.get("estimated_num_employees") else ""
        result["industry"] = org.get("industry", "") or ""

        # People search for decision maker
        people_resp = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": apollo_key,
                "q_organization_domains": domain,
                "person_titles": ["owner", "ceo", "president", "founder", "office manager"],
                "page": 1,
                "per_page": 1,
            },
            timeout=10,
        )
        people_resp.raise_for_status()
        people = people_resp.json().get("people", [])
        if people:
            p = people[0]
            result["apollo_email"] = p.get("email", "") or ""
            result["apollo_name"] = p.get("name", "") or ""
            result["apollo_title"] = p.get("title", "") or ""

    except Exception as e:
        log.warning(f"Apollo.io error for {domain}: {e}")

    return result
