from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.scrape_job import JobStatus


class ScrapeRequest(BaseModel):
    category: str
    location: str
    num_results: int = 20
    delay: float = 1.5


class ScrapeJobResponse(BaseModel):
    id: int
    category: str
    location: str
    num_results_requested: int
    status: JobStatus
    lead_count: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScrapeJobListResponse(BaseModel):
    jobs: list
    total: int
    page: int
    per_page: int
