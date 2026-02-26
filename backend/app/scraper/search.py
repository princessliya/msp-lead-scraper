from __future__ import annotations

import logging
import time

import requests

from app.scraper.constants import HEADERS

log = logging.getLogger(__name__)


def _geocode_location(location: str) -> str:
    """Convert city/state to '@lat,lon,14z' for Serper. Returns empty string on failure."""
    try:
        params = {"q": location, "format": "json", "limit": 1}
        headers = {"User-Agent": "MSPLeadScraper/2.0"}
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params, headers=headers, timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return f"@{data[0]['lat']},{data[0]['lon']},14z"
    except Exception as e:
        log.warning(f"Geocoding failed for '{location}': {e}")
    return ""


def _search_serper(query: str, location: str, num_results: int, serper_key: str) -> list:
    """Search Google Maps via Serper.dev (2,500 free/month)."""
    coords = _geocode_location(location)
    results = []
    page = 1

    while len(results) < num_results:
        payload = {"q": f"{query} in {location}"}
        if coords:
            payload["ll"] = coords
        if page > 1:
            payload["page"] = page

        try:
            resp = requests.post(
                "https://google.serper.dev/maps",
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                json=payload, timeout=15,
            )
            resp.raise_for_status()
            places = resp.json().get("places", [])
            if not places:
                break
            results.extend(places)
            page += 1
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Serper error: {e}")
            break

    return results[:num_results]


def _search_serpapi(query: str, location: str, num_results: int, serpapi_key: str) -> list:
    """Search Google Maps via SerpAPI (100 free/month)."""
    results = []
    start = 0

    while len(results) < num_results:
        params = {
            "engine": "google_maps",
            "q": f"{query} in {location}",
            "type": "search",
            "api_key": serpapi_key,
            "start": start,
        }
        try:
            resp = requests.get("https://serpapi.com/search", params=params, timeout=15)
            resp.raise_for_status()
            places = resp.json().get("local_results", [])
            if not places:
                break
            results.extend(places)
            start += len(places)
            time.sleep(1)
        except Exception as e:
            log.error(f"SerpAPI error: {e}")
            break

    return results[:num_results]


def search_google_places(
    query: str,
    location: str,
    num_results: int = 20,
    serper_key: str = "",
    serpapi_key: str = "",
) -> list:
    """Auto-detect which API to use: Serper > SerpAPI > mock."""
    from app.scraper.mock import mock_places

    if serper_key:
        log.info("Using Serper.dev for Google Maps search")
        return _search_serper(query, location, num_results, serper_key)
    elif serpapi_key:
        log.info("Using SerpAPI for Google Maps search")
        return _search_serpapi(query, location, num_results, serpapi_key)
    else:
        log.warning("No API key set. Using mock data.")
        return mock_places(query, location)


def parse_place(place: dict) -> dict:
    """Normalize API response fields from Serper or SerpAPI."""
    category = place.get("category", "")
    if not category and "types" in place:
        category = ", ".join(place.get("types", []))

    return {
        "business_name": place.get("title", ""),
        "category": category,
        "address": place.get("address", ""),
        "phone": place.get("phoneNumber", "") or place.get("phone", ""),
        "website": place.get("website", ""),
        "rating": place.get("rating", None),
        "reviews": place.get("reviews", place.get("ratingCount", None)),
        "google_maps_url": place.get("cid", "") or place.get("place_id_search", ""),
    }
