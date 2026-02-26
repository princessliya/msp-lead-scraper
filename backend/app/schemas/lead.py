from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeadResponse(BaseModel):
    id: int
    job_id: int
    business_name: str
    category: str
    address: str
    phone: str
    website: str
    domain: str
    rating: Optional[float] = None
    reviews: Optional[int] = None
    google_maps_url: str
    emails_found: str
    tech_stack: str
    has_it_mention: bool
    has_existing_msp: bool
    compliance_mention: str
    ssl_valid: bool
    scrape_status: str
    hunter_email: str
    hunter_name: str
    hunter_confidence: Optional[int] = None
    apollo_email: str
    apollo_name: str
    apollo_title: str
    company_size: str
    industry: str
    score: int
    notes: str
    is_archived: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadNotesUpdate(BaseModel):
    notes: str


class BulkDeleteRequest(BaseModel):
    lead_ids: list
