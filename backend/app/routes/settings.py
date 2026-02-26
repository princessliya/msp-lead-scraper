from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.scraper.scoring import DEFAULT_WEIGHTS

router = APIRouter()


class APIKeysUpdate(BaseModel):
    serper_key: str = ""
    serpapi_key: str = ""
    hunter_key: str = ""
    apollo_key: str = ""


class ScoringWeightsUpdate(BaseModel):
    weights: dict


@router.get("/api-keys")
def get_api_keys(user: Annotated[User, Depends(get_current_user)]):
    keys = json.loads(user.api_keys_json or "{}")
    from app.config import settings
    return {
        "serper_key_set": bool(keys.get("serper_key") or settings.serper_key),
        "serpapi_key_set": bool(keys.get("serpapi_key") or settings.serpapi_key),
        "hunter_key_set": bool(keys.get("hunter_key") or settings.hunter_key),
        "apollo_key_set": bool(keys.get("apollo_key") or settings.apollo_key),
    }


@router.put("/api-keys")
def update_api_keys(
    body: APIKeysUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    keys = {}
    if body.serper_key:
        keys["serper_key"] = body.serper_key
    if body.serpapi_key:
        keys["serpapi_key"] = body.serpapi_key
    if body.hunter_key:
        keys["hunter_key"] = body.hunter_key
    if body.apollo_key:
        keys["apollo_key"] = body.apollo_key
    user.api_keys_json = json.dumps(keys)
    db.commit()
    return {"updated": True}


@router.get("/scoring-weights")
def get_scoring_weights(user: Annotated[User, Depends(get_current_user)]):
    weights = json.loads(user.scoring_weights_json or "{}")
    return weights if weights else DEFAULT_WEIGHTS


@router.put("/scoring-weights")
def update_scoring_weights(
    body: ScoringWeightsUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    user.scoring_weights_json = json.dumps(body.weights)
    db.commit()
    return {"updated": True}
