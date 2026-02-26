from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.config import settings
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.scrape import RecommendationsResponse, VerticalRecommendation
from app.scraper.constants import SECTORS, VERTICALS
from app.scraper.search import search_google_places

router = APIRouter()

# One search query per sector group — covers all 13 sectors in 8 searches
_SECTOR_QUERIES: list[tuple[list[str], str]] = [
    (["Healthcare"],                    "medical clinic dental office doctor urgent care"),
    (["Legal"],                         "law firm attorney legal services"),
    (["Financial", "Professional"],     "accounting firm financial advisor insurance agency consulting"),
    (["Construction"],                  "construction company contractor builder remodeling"),
    (["Manufacturing", "Logistics"],    "manufacturing company warehouse distribution industrial"),
    (["Automotive"],                    "auto repair shop car dealership body shop"),
    (["Real Estate"],                   "real estate agency property management"),
    (["Education", "Nonprofit"],        "private school tutoring center nonprofit organization"),
    (["Hospitality", "Fitness"],        "hotel restaurant gym fitness center"),
]


def _density_label(count: int, max_count: int) -> str:
    if max_count == 0:
        return "N/A"
    ratio = count / max_count
    if ratio >= 0.75:
        return "Very High"
    if ratio >= 0.45:
        return "High"
    if ratio >= 0.20:
        return "Medium"
    return "Low"


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


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    location: Annotated[str, Query(description="City and state, e.g. 'Chicago, IL'")],
    user: Annotated[User, Depends(get_current_user)],
):
    """
    Return the top 10 MSP-target verticals ranked by real local business density
    for the given location. Requires a Serper.dev or SerpAPI key for live data;
    falls back to MSP-fit-only ranking otherwise.
    """
    has_key = bool(settings.serper_key or settings.serpapi_key)

    if not has_key:
        # No API key — rank purely by MSP fit, no local data
        recs = [
            VerticalRecommendation(
                name=name,
                icon=meta["icon"],
                sector=meta["sector"],
                msp_fit=meta["msp_fit"],
                reason=meta["reason"],
                local_count=0,
                local_score=float(meta["msp_fit"]),
                density_label="N/A",
            )
            for name, meta in VERTICALS.items()
        ]
        recs.sort(key=lambda v: v.local_score, reverse=True)
        return RecommendationsResponse(
            location=location,
            recommendations=recs[:10],
            has_api_key=False,
            message=(
                "Add a Serper.dev key in Settings to get real local business "
                "density data for this location."
            ),
        )

    # Run one search per sector group against the user-supplied location
    sector_counts: dict[str, int] = {}
    for sectors, query in _SECTOR_QUERIES:
        results = search_google_places(
            query=query,
            location=location,
            num_results=10,
            serper_key=settings.serper_key,
            serpapi_key=settings.serpapi_key,
        )
        count = len(results)
        for sector in sectors:
            sector_counts[sector] = sector_counts.get(sector, 0) + count

    max_count = max(sector_counts.values(), default=1)

    recs = []
    for name, meta in VERTICALS.items():
        sector = meta["sector"]
        count = sector_counts.get(sector, 0)
        # Density bonus: up to +10 points for markets flooded with that sector
        density_bonus = (min(count / max(max_count, 1), 1.0)) * 10
        local_score = round(meta["msp_fit"] + density_bonus, 1)
        recs.append(
            VerticalRecommendation(
                name=name,
                icon=meta["icon"],
                sector=sector,
                msp_fit=meta["msp_fit"],
                reason=meta["reason"],
                local_count=count,
                local_score=local_score,
                density_label=_density_label(count, max_count),
            )
        )

    recs.sort(key=lambda v: v.local_score, reverse=True)
    return RecommendationsResponse(
        location=location,
        recommendations=recs[:10],
        has_api_key=True,
        message=None,
    )
