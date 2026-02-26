from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.dependencies import get_current_user, get_db, get_event_bus, get_job_runner
from app.events.bus import EventBus
from app.jobs.interface import JobRunner
from app.models.scrape_job import JobStatus, ScrapeJob
from app.models.user import User
from app.schemas.scrape import ScrapeJobResponse, ScrapeRequest
from app.scraper.pipeline import ScrapeOrchestrator

router = APIRouter()


def _get_user_api_keys(user: User) -> dict:
    """Get API keys from user settings, falling back to server config."""
    from app.config import settings

    user_keys = json.loads(user.api_keys_json or "{}")
    return {
        "serper_key": user_keys.get("serper_key") or settings.serper_key,
        "serpapi_key": user_keys.get("serpapi_key") or settings.serpapi_key,
        "hunter_key": user_keys.get("hunter_key") or settings.hunter_key,
        "apollo_key": user_keys.get("apollo_key") or settings.apollo_key,
    }


def _get_scoring_weights(user: User) -> dict:
    """Get scoring weights from user settings."""
    weights = json.loads(user.scoring_weights_json or "{}")
    return weights if weights else None


@router.post("/start", response_model=ScrapeJobResponse, status_code=status.HTTP_201_CREATED)
def start_scrape(
    request: ScrapeRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    job_runner: Annotated[JobRunner, Depends(get_job_runner)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
):
    job = ScrapeJob(
        user_id=user.id,
        category=request.category,
        location=request.location,
        num_results_requested=request.num_results,
        delay=request.delay,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Build orchestrator with a fresh DB session for the background thread
    orchestrator = ScrapeOrchestrator(
        db=SessionLocal(),
        event_bus=event_bus,
        api_keys=_get_user_api_keys(user),
        scoring_weights=_get_scoring_weights(user),
    )

    job_runner.submit(
        orchestrator.run,
        job_id=job.id,
        category=request.category,
        location=request.location,
        num_results=request.num_results,
        delay=request.delay,
    )

    return job


@router.get("/{job_id}/status", response_model=ScrapeJobResponse)
def get_job_status(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id, ScrapeJob.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel")
def cancel_job(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id, ScrapeJob.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.PENDING, JobStatus.RUNNING):
        raise HTTPException(status_code=400, detail="Job is not cancellable")
    job.status = JobStatus.CANCELLED
    db.commit()
    return {"job_id": job.id, "status": job.status}


@router.get("/history")
def get_history(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    query = db.query(ScrapeJob).filter(ScrapeJob.user_id == user.id).order_by(ScrapeJob.created_at.desc())
    total = query.count()
    jobs = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "jobs": [ScrapeJobResponse.model_validate(j).model_dump() for j in jobs],
        "total": total,
        "page": page,
        "per_page": per_page,
    }
