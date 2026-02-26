from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.lead import Lead
from app.models.scrape_job import ScrapeJob
from app.models.user import User
from app.schemas.lead import BulkDeleteRequest, LeadNotesUpdate, LeadResponse

router = APIRouter()


@router.get("")
def list_leads(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    job_id: Optional[int] = Query(None),
    min_score: int = Query(0, ge=0, le=100),
    max_score: int = Query(100, ge=0, le=100),
    has_email: Optional[bool] = Query(None),
    has_it_mention: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("score"),
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    user_job_ids = db.query(ScrapeJob.id).filter(ScrapeJob.user_id == user.id).subquery()
    query = db.query(Lead).filter(Lead.job_id.in_(user_job_ids))

    if job_id is not None:
        query = query.filter(Lead.job_id == job_id)
    query = query.filter(Lead.score >= min_score, Lead.score <= max_score)

    if has_email is True:
        query = query.filter(
            (Lead.emails_found != "") | (Lead.hunter_email != "") | (Lead.apollo_email != "")
        )
    if has_it_mention is not None:
        query = query.filter(Lead.has_it_mention == has_it_mention)
    if category:
        query = query.filter(Lead.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            Lead.business_name.ilike(f"%{search}%") | Lead.address.ilike(f"%{search}%")
        )

    query = query.filter(Lead.is_archived == False)

    sort_col = getattr(Lead, sort_by, Lead.score)
    query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

    total = query.count()
    leads = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "leads": [LeadResponse.model_validate(l).model_dump() for l in leads],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    job = db.query(ScrapeJob).filter(ScrapeJob.id == lead.job_id, ScrapeJob.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}/notes", response_model=LeadResponse)
def update_notes(
    lead_id: int,
    body: LeadNotesUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    job = db.query(ScrapeJob).filter(ScrapeJob.id == lead.job_id, ScrapeJob.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.notes = body.notes
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    job = db.query(ScrapeJob).filter(ScrapeJob.id == lead.job_id, ScrapeJob.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"deleted": True}


@router.post("/bulk-delete")
def bulk_delete(
    body: BulkDeleteRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    user_job_ids = [j.id for j in db.query(ScrapeJob.id).filter(ScrapeJob.user_id == user.id).all()]
    deleted = (
        db.query(Lead)
        .filter(Lead.id.in_(body.lead_ids), Lead.job_id.in_(user_job_ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"deleted_count": deleted}
