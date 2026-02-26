from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cache import CacheEntry

log = logging.getLogger(__name__)

# Default TTLs in hours
TTL_GEOCODE = 24 * 30       # 30 days
TTL_SEARCH = 24 * 7         # 7 days
TTL_WEBSITE = 24 * 3        # 3 days
TTL_ENRICHMENT = 24 * 30    # 30 days


class CacheService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str, cache_type: str = "") -> Optional[Any]:
        entry = self.db.query(CacheEntry).filter(CacheEntry.key == key).first()
        if entry is None:
            return None
        if entry.expires_at and entry.expires_at < datetime.now(timezone.utc):
            self.db.delete(entry)
            self.db.commit()
            return None
        return json.loads(entry.data)

    def set(self, key: str, cache_type: str, data: Any, ttl_hours: int = 24 * 7):
        existing = self.db.query(CacheEntry).filter(CacheEntry.key == key).first()
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=ttl_hours)

        if existing:
            existing.data = json.dumps(data, default=str)
            existing.created_at = now
            existing.expires_at = expires
        else:
            entry = CacheEntry(
                key=key,
                cache_type=cache_type,
                data=json.dumps(data, default=str),
                created_at=now,
                expires_at=expires,
            )
            self.db.add(entry)
        self.db.commit()

    def clear(self, cache_type: str | None = None) -> int:
        query = self.db.query(CacheEntry)
        if cache_type:
            query = query.filter(CacheEntry.cache_type == cache_type)
        count = query.count()
        query.delete()
        self.db.commit()
        return count

    def stats(self) -> dict:
        total = self.db.query(CacheEntry).count()
        by_type = dict(
            self.db.query(CacheEntry.cache_type, func.count(CacheEntry.id))
            .group_by(CacheEntry.cache_type)
            .all()
        )
        return {"total_entries": total, "by_type": by_type}
