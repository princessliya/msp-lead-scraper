from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.cache_service import CacheService

router = APIRouter()


@router.get("/stats")
def cache_stats(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return CacheService(db).stats()


@router.delete("/clear")
def clear_cache(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    cache_type: Optional[str] = Query(None),
):
    count = CacheService(db).clear(cache_type)
    return {"cleared_count": count}
