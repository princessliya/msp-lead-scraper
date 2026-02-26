"""
MSP Lead Scraper
================
Finds SMB leads (potential clients) for MSP owners.

Flow:
  1. Search Google Maps for businesses by category + city
     (supports Serper.dev OR SerpAPI — auto-detects which key you have)
  2. Scrape each business website for emails & tech signals
  3. Enrich emails via Hunter.io API (optional)
  4. Export clean CSV ready for outreach

Requirements:
  pip install requests beautifulsoup4 pandas tqdm python-dotenv

API Keys needed (free tiers available):
  - Serper:    https://serper.dev           (2,500 free searches/month)  ← recommended
  - SerpAPI:   https://serpapi.com          (100 free searches/month)
  - Hunter.io: https://hunter.io            (25 free searches/month)
  Put whichever key(s) you have in your .env file (see .env.example)
"""

import os
import re
import time
import csv
import json
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

SERPAPI_KEY  = os.getenv("SERPAPI_KEY", "")
SERPER_KEY   = os.getenv("SERPER_KEY", "")
HUNTER_KEY   = os.getenv("HUNTER_KEY", "")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Tech stack keywords to detect on websites
TECH_SIGNALS = {
    "Microsoft 365": ["microsoft365", "office365", "outlook.com", "microsoftonline"],
    "Google Workspace": ["workspace.google", "gsuite", "google workspace"],
    "WordPress": ["wp-content", "wp-includes", "wordpress"],
    "Shopify": ["shopify", "myshopify.com"],
    "HubSpot": ["hubspot.com", "hs-scripts"],
    "Salesforce": ["salesforce.com", "force.com"],
    "Cloudflare": ["cloudflare"],
    "AWS": ["amazonaws.com", "cloudfront.net"],
    "Zoom": ["zoom.us"],
    "Slack": ["slack.com"],
}

# ── Geocoding Helper (for Serper) ─────────────────────────────────────────────

def _geocode_location(location: str) -> str:
    """
    Convert a city/state string to '@lat,lon,14z' format using free Nominatim API.
    Serper's /maps endpoint needs coordinates, not city names.
    Returns empty string on failure.
    """
    try:
        params = {"q": location, "format": "json", "limit": 1}
        headers_geo = {"User-Agent": "MSPLeadScraper/1.0"}
        resp = requests.get("https://nominatim.openstreetmap.org/search",
                            params=params, headers=headers_geo, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            return f"@{lat},{lon},14z"
    except Exception as e:
        log.warning(f"Geocoding failed for '{location}': {e}")
    return ""


# ── Google Places Search (Serper.dev or SerpAPI) ─────────────────────────────

def _search_serper(query: str, location: str, num_results: int) -> list[dict]:
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
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            places = data.get("places", [])
            if not places:
                break
            results.extend(places)
            page += 1
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Serper error: {e}")
            break

    return results[:num_results]


def _search_serpapi(query: str, location: str, num_results: int) -> list[dict]:
    """Search Google Maps via SerpAPI (100 free/month)."""
    results = []
    start = 0

    while len(results) < num_results:
        params = {
            "engine": "google_maps",
            "q": f"{query} in {location}",
            "type": "search",
            "api_key": SERPAPI_KEY,
            "start": start,
        }
        try:
            resp = requests.get("https://serpapi.com/search", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            places = data.get("local_results", [])
            if not places:
                break
            results.extend(places)
            start += len(places)
            time.sleep(1)
        except Exception as e:
            log.error(f"SerpAPI error: {e}")
            break

    return results[:num_results]


def search_google_places(query: str, location: str, num_results: int = 20) -> list[dict]:
    """
    Search Google Maps for businesses. Auto-detects which API key is available:
      1. Serper.dev  (SERPER_KEY)  — 2,500 free/month  ← preferred
      2. SerpAPI     (SERPAPI_KEY) — 100 free/month
      3. Mock data   (no key)     — for testing
    """
    if SERPER_KEY:
        log.info("Using Serper.dev for Google Maps search")
        return _search_serper(query, location, num_results)
    elif SERPAPI_KEY:
        log.info("Using SerpAPI for Google Maps search")
        return _search_serpapi(query, location, num_results)
    else:
        log.warning("No SERPER_KEY or SERPAPI_KEY set. Using mock data for testing.")
        return _mock_places(query, location)


def parse_place(place: dict) -> dict:
    """Extract relevant fields from a search result (works with both Serper and SerpAPI)."""
    # Serper uses 'title', SerpAPI uses 'title' too — same field name
    # Serper uses 'phoneNumber', SerpAPI uses 'phone'
    # Serper uses 'category', SerpAPI uses 'types' (list)
    category = place.get("category", "")
    if not category and "types" in place:
        category = ", ".join(place.get("types", []))

    return {
        "business_name":  place.get("title", ""),
        "category":       category,
        "address":        place.get("address", ""),
        "phone":          place.get("phoneNumber", "") or place.get("phone", ""),
        "website":        place.get("website", ""),
        "rating":         place.get("rating", ""),
        "reviews":        place.get("reviews", place.get("ratingCount", "")),
        "google_maps_url": place.get("cid", "") or place.get("place_id_search", ""),
    }


# ── HTTP Helper with Retry ────────────────────────────────────────────────────

def _request_with_retry(url: str, max_retries: int = 3, timeout: int = 10) -> requests.Response:
    """GET request with exponential backoff on 429/5xx errors."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                log.warning(f"Got {resp.status_code} for {url}, retrying in {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                log.warning(f"Connection error for {url}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    return resp  # fallback (shouldn't reach here)


# ── Website Scraper ───────────────────────────────────────────────────────────

# Subpages to check for extra emails and signals
_EXTRA_PATHS = ["/contact", "/contact-us", "/about", "/about-us"]


def _extract_emails_from_soup(soup: BeautifulSoup) -> set[str]:
    """Extract emails from visible page text only (skip <script> and <style> tags)."""
    # Remove script and style elements so their contents aren't matched
    for tag in soup.find_all(["script", "style", "noscript"]):
        tag.decompose()

    visible_text = soup.get_text(separator=" ", strip=True)
    emails = set(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", visible_text))

    # Also grab mailto: links (these are intentional contact emails)
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").split("?")[0].strip()
            if "@" in email:
                emails.add(email)

    # Filter out common junk
    emails = {e for e in emails if not any(x in e.lower() for x in [
        "example", "domain", "youremail", "sentry", "wixpress", "schema",
        "placeholder", "test@", "noreply", "no-reply"
    ])}
    return emails


def scrape_website(url: str) -> dict:
    """
    Visit a business website (homepage + /contact + /about) and extract:
    - Emails found on the pages
    - Tech stack signals
    - Whether they mention IT / support staff
    """
    result = {
        "emails_found":    "",
        "tech_stack":      "",
        "has_it_mention":  False,
        "scrape_status":   "ok",
    }

    if not url:
        result["scrape_status"] = "no_website"
        return result

    all_emails = set()
    all_html = ""
    all_page_text = ""

    # Pages to scrape: homepage + common subpages
    urls_to_try = [url] + [urljoin(url.rstrip("/") + "/", p.lstrip("/")) for p in _EXTRA_PATHS]

    for page_url in urls_to_try:
        try:
            resp = _request_with_retry(page_url, max_retries=2, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Collect emails (from clean visible text)
            all_emails.update(_extract_emails_from_soup(soup))

            # Accumulate raw HTML + text for tech/IT detection
            all_html += resp.text.lower() + " "
            all_page_text += soup.get_text(separator=" ", strip=True).lower() + " "

        except Exception:
            # Subpage failures are fine — only flag if homepage failed
            if page_url == url:
                result["scrape_status"] = "homepage_error"

    try:
        result["emails_found"] = "; ".join(sorted(all_emails)[:5])

        # Detect tech stack
        detected = []
        for tech, patterns in TECH_SIGNALS.items():
            if any(p in all_html for p in patterns):
                detected.append(tech)
        result["tech_stack"] = ", ".join(detected)

        # Check for IT staff mentions (no dedicated IT = good MSP prospect)
        it_keywords = ["it department", "it director", "it manager", "sys admin",
                       "sysadmin", "chief technology officer", "cto", "it staff"]
        result["has_it_mention"] = any(kw in all_page_text for kw in it_keywords)

    except Exception as e:
        result["scrape_status"] = f"error: {str(e)[:60]}"

    return result


# ── Hunter.io Email Enrichment ────────────────────────────────────────────────

def enrich_email_hunter(domain: str) -> dict:
    """
    Use Hunter.io domain search to find verified business emails.
    Returns a dict with enriched email info.
    """
    result = {"hunter_email": "", "hunter_name": "", "hunter_confidence": ""}

    if not HUNTER_KEY or not domain:
        return result

    try:
        params = {"domain": domain, "api_key": HUNTER_KEY, "limit": 3}
        resp = requests.get("https://api.hunter.io/v2/domain-search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        emails = data.get("emails", [])

        if emails:
            # Prioritize decision-maker titles
            priority_titles = ["owner", "ceo", "president", "founder", "director", "manager"]
            best = None
            for e in emails:
                pos = (e.get("position") or "").lower()
                if any(t in pos for t in priority_titles):
                    best = e
                    break
            if not best:
                best = emails[0]

            result["hunter_email"]      = best.get("value", "")
            result["hunter_name"]       = f"{best.get('first_name','')} {best.get('last_name','')}".strip()
            result["hunter_confidence"] = best.get("confidence", "")

    except Exception as e:
        log.warning(f"Hunter.io error for {domain}: {e}")

    return result


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_lead(lead: dict) -> int:
    """
    Score a lead 0-100 based on MSP-prospect quality signals.
    Higher = better prospect.
    """
    score = 0

    # Has a website (shows they're real and established)
    if lead.get("website"):
        score += 20

    # Has phone number
    if lead.get("phone"):
        score += 10

    # Has reviews (established business)
    try:
        reviews = int(lead.get("reviews", 0))
        if reviews >= 10:
            score += 10
        if reviews >= 50:
            score += 10
    except (ValueError, TypeError):
        pass

    # Has rating (4+ stars = healthy business)
    try:
        rating = float(lead.get("rating", 0))
        if rating >= 4.0:
            score += 10
    except (ValueError, TypeError):
        pass

    # Email found = contactable
    if lead.get("emails_found") or lead.get("hunter_email"):
        score += 20

    # No dedicated IT staff = prime MSP prospect
    if not lead.get("has_it_mention", True):
        score += 15

    # Uses cloud tools but no MSP = opportunity
    tech = lead.get("tech_stack", "")
    if any(t in tech for t in ["Microsoft 365", "Google Workspace"]):
        score += 5

    return min(score, 100)


# ── Main Orchestrator ─────────────────────────────────────────────────────────

def run_scraper(
    business_category: str,
    location: str,
    num_results: int = 20,
    output_file: str = "leads.csv",
    delay_between_sites: float = 1.5,
) -> pd.DataFrame:
    """
    Full pipeline: search → scrape → enrich → score → export.
    """
    log.info(f"🔍 Searching for '{business_category}' in '{location}' ({num_results} results)...")
    places = search_google_places(business_category, location, num_results)
    log.info(f"✅ Found {len(places)} places")

    leads = []

    for place in tqdm(places, desc="Processing leads"):
        lead = parse_place(place)

        # Scrape website
        website_data = scrape_website(lead["website"])
        lead.update(website_data)

        # Hunter.io enrichment
        domain = ""
        if lead["website"]:
            try:
                domain = urlparse(lead["website"]).netloc.replace("www.", "")
            except Exception:
                pass
        hunter_data = enrich_email_hunter(domain)
        lead.update(hunter_data)
        lead["domain"] = domain

        # Score the lead
        lead["score"] = score_lead(lead)

        leads.append(lead)
        time.sleep(delay_between_sites)

    # Build DataFrame
    df = pd.DataFrame(leads)

    # Deduplicate by domain (or business_name if no domain)
    before_dedup = len(df)
    if "domain" in df.columns:
        # Keep first occurrence (highest quality from earlier in results)
        df = df.drop_duplicates(subset=["domain"], keep="first")
        # Also dedupe rows with empty domain by business_name
        mask_empty = df["domain"] == ""
        if mask_empty.any():
            deduped_empty = df[mask_empty].drop_duplicates(subset=["business_name"], keep="first")
            df = pd.concat([df[~mask_empty], deduped_empty], ignore_index=True)
    else:
        df = df.drop_duplicates(subset=["business_name"], keep="first")
    if before_dedup > len(df):
        log.info(f"🧹 Removed {before_dedup - len(df)} duplicate lead(s)")

    # Reorder columns for readability
    col_order = [
        "score", "business_name", "category", "address", "phone",
        "website", "domain", "rating", "reviews",
        "emails_found", "hunter_email", "hunter_name", "hunter_confidence",
        "tech_stack", "has_it_mention", "scrape_status", "google_maps_url",
    ]
    df = df[[c for c in col_order if c in df.columns]]
    df = df.sort_values("score", ascending=False)

    # Export
    df.to_csv(output_file, index=False)
    log.info(f"💾 Saved {len(df)} leads to {output_file}")

    # Summary
    email_count = df["emails_found"].ne("").sum()
    if "hunter_email" in df.columns:
        email_count += df["hunter_email"].ne("").sum()
    log.info(f"\n{'='*50}")
    log.info(f"  Total leads:         {len(df)}")
    log.info(f"  With email:          {email_count}")
    log.info(f"  Avg score:           {df['score'].mean():.1f}/100")
    if len(df) > 0:
        log.info(f"  Top lead:            {df.iloc[0]['business_name']} (score: {df.iloc[0]['score']})")
    log.info(f"{'='*50}")

    return df


# ── Mock Data (for testing without API keys) ──────────────────────────────────

def _mock_places(query: str, location: str) -> list[dict]:
    """Returns fake places for testing the pipeline without API keys."""
    return [
        {"title": f"Sample {query.title()} Co.", "types": [query], "address": f"123 Main St, {location}",
         "phone": "555-1234", "website": "https://example.com", "rating": 4.5, "reviews": 87},
        {"title": f"Metro {query.title()} Group", "types": [query], "address": f"456 Oak Ave, {location}",
         "phone": "555-5678", "website": "https://example.org", "rating": 4.1, "reviews": 32},
        {"title": f"{location} {query.title()} LLC", "types": [query], "address": f"789 Pine Rd, {location}",
         "phone": "555-9012", "website": "", "rating": 3.8, "reviews": 12},
    ]


# ── CLI Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MSP Lead Scraper — Find SMB prospects for MSPs")
    parser.add_argument("--category", "-c", default="dental office",
                        help="Business category to target (e.g. 'dental office', 'law firm', 'accounting firm')")
    parser.add_argument("--location", "-l", default="Austin, TX",
                        help="City/region to search (e.g. 'Austin, TX', 'Chicago')")
    parser.add_argument("--results", "-n", type=int, default=20,
                        help="Number of leads to pull (default: 20)")
    parser.add_argument("--output", "-o", default="leads.csv",
                        help="Output CSV filename (default: leads.csv)")
    parser.add_argument("--delay", "-d", type=float, default=1.5,
                        help="Seconds between website requests (default: 1.5)")
    args = parser.parse_args()

    df = run_scraper(
        business_category=args.category,
        location=args.location,
        num_results=args.results,
        output_file=args.output,
        delay_between_sites=args.delay,
    )

    print(f"\n🎯 Top 5 Leads:\n")
    print(df[["score", "business_name", "phone", "hunter_email", "tech_stack"]].head(5).to_string(index=False))
