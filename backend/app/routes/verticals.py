from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.scraper.constants import SECTORS, VERTICALS

router = APIRouter()


@router.get("/list")
def list_verticals(user: Annotated[User, Depends(get_current_user)]):
    """Return all 68 verticals grouped by sector."""
    result = {}
    for name, meta in VERTICALS.items():
        sector = meta["sector"]
        if sector not in result:
            result[sector] = []
        result[sector].append({
            "name": name,
            "icon": meta["icon"],
            "msp_fit": meta["msp_fit"],
            "reason": meta["reason"],
        })
    for sector in result:
        result[sector].sort(key=lambda x: x["msp_fit"], reverse=True)

    return {"sectors": SECTORS, "verticals": result, "total": len(VERTICALS)}
