from __future__ import annotations

import csv
import io
import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.lead import Lead
from app.models.scrape_job import ScrapeJob
from app.models.user import User
from app.schemas.lead import LeadResponse

router = APIRouter()

EXPORT_FIELDS = [
    "score", "business_name", "category", "address", "phone",
    "website", "domain", "rating", "reviews",
    "emails_found", "hunter_email", "apollo_email",
    "hunter_name", "apollo_name", "apollo_title", "hunter_confidence",
    "company_size", "industry",
    "tech_stack", "has_it_mention", "has_existing_msp",
    "compliance_mention", "ssl_valid", "scrape_status",
]


def _get_filtered_leads(db: Session, user: User, job_id=None, min_score=0):
    user_job_ids = db.query(ScrapeJob.id).filter(ScrapeJob.user_id == user.id).subquery()
    query = db.query(Lead).filter(Lead.job_id.in_(user_job_ids), Lead.score >= min_score)
    if job_id:
        query = query.filter(Lead.job_id == job_id)
    return query.order_by(Lead.score.desc()).all()


@router.get("/csv")
def export_csv(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    job_id: Optional[int] = Query(None),
    min_score: int = Query(0, ge=0),
):
    leads = _get_filtered_leads(db, user, job_id, min_score)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    for lead in leads:
        writer.writerow({f: getattr(lead, f, "") for f in EXPORT_FIELDS})

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@router.get("/json")
def export_json(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    job_id: Optional[int] = Query(None),
    min_score: int = Query(0, ge=0),
):
    leads = _get_filtered_leads(db, user, job_id, min_score)
    data = [LeadResponse.model_validate(l).model_dump() for l in leads]
    return StreamingResponse(
        iter([json.dumps(data, indent=2, default=str)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=leads.json"},
    )
