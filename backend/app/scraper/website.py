from __future__ import annotations

import json
import logging
import re
import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.scraper.constants import (
    COMPLIANCE_KEYWORDS,
    EXTRA_PATHS,
    HEADERS,
    IT_KEYWORDS,
    MSP_TOOL_SIGNALS,
    TECH_SIGNALS,
)

log = logging.getLogger(__name__)


def _request_with_retry(url: str, max_retries: int = 3, timeout: int = 10) -> requests.Response:
    """GET with exponential backoff on 429/5xx."""
    resp = None
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
                time.sleep(2 ** (attempt + 1))
            else:
                raise
    return resp


def _extract_emails_from_soup(soup: BeautifulSoup, raw_html: str = "") -> set:
    """Extract emails from visible text, mailto links, JSON-LD, meta tags, and de-obfuscation."""
    # Remove script/style so their content isn't matched
    for tag in soup.find_all(["script", "style", "noscript"]):
        if tag.get("type") != "application/ld+json":
            tag.decompose()

    emails = set()

    # 1. Visible text
    visible_text = soup.get_text(separator=" ", strip=True)
    emails.update(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", visible_text))

    # 2. Mailto links
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").split("?")[0].strip()
            if "@" in email:
                emails.add(email)

    # 3. JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            ld_data = json.loads(script.string or "")
            _extract_from_jsonld(ld_data, emails)
        except (json.JSONDecodeError, TypeError):
            pass

    # 4. Meta tags
    for meta in soup.find_all("meta"):
        content = meta.get("content", "")
        if content:
            emails.update(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", content))

    # 5. De-obfuscation
    if raw_html:
        deobfuscated = raw_html.replace(" [at] ", "@").replace("(at)", "@").replace(" AT ", "@")
        emails.update(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", deobfuscated))

    # Filter junk
    junk_patterns = [
        "example", "domain", "youremail", "sentry", "wixpress", "schema",
        "placeholder", "test@", "noreply", "no-reply",
    ]
    emails = {e for e in emails if not any(x in e.lower() for x in junk_patterns)}
    return emails


def _extract_from_jsonld(data, emails: set):
    """Recursively extract email fields from JSON-LD."""
    if isinstance(data, dict):
        for key in ("email", "contactPoint"):
            if key in data:
                val = data[key]
                if isinstance(val, str) and "@" in val:
                    emails.add(val.replace("mailto:", ""))
                elif isinstance(val, (dict, list)):
                    _extract_from_jsonld(val, emails)
        for v in data.values():
            if isinstance(v, (dict, list)):
                _extract_from_jsonld(v, emails)
    elif isinstance(data, list):
        for item in data:
            _extract_from_jsonld(item, emails)


def detect_tech_stack(html: str) -> tuple:
    """Returns (detected_techs: list, has_existing_msp: bool)."""
    html_lower = html.lower()
    detected = []
    for tech, patterns in TECH_SIGNALS.items():
        if any(p in html_lower for p in patterns):
            detected.append(tech)
    has_existing_msp = bool(set(detected) & MSP_TOOL_SIGNALS)
    return detected, has_existing_msp


def scrape_website(url: str) -> dict:
    """Scrape homepage + contact/about pages for emails, tech, IT mentions, compliance."""
    result = {
        "emails_found": "",
        "tech_stack": "",
        "has_it_mention": False,
        "has_existing_msp": False,
        "compliance_mention": "",
        "ssl_valid": False,
        "scrape_status": "ok",
    }

    if not url:
        result["scrape_status"] = "no_website"
        return result

    all_emails = set()
    all_html = ""
    all_page_text = ""

    urls_to_try = [url] + [urljoin(url.rstrip("/") + "/", p.lstrip("/")) for p in EXTRA_PATHS]

    for page_url in urls_to_try:
        try:
            resp = _request_with_retry(page_url, max_retries=2, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            all_emails.update(_extract_emails_from_soup(soup, resp.text))
            all_html += resp.text.lower() + " "
            all_page_text += soup.get_text(separator=" ", strip=True).lower() + " "
        except Exception:
            if page_url == url:
                result["scrape_status"] = "homepage_error"

    try:
        result["emails_found"] = "; ".join(sorted(all_emails)[:5])

        # Tech stack
        detected, has_existing_msp = detect_tech_stack(all_html)
        result["tech_stack"] = ", ".join(detected)
        result["has_existing_msp"] = has_existing_msp

        # IT staff mentions
        result["has_it_mention"] = any(kw in all_page_text for kw in IT_KEYWORDS)

        # Compliance mentions
        found_compliance = [kw for kw in COMPLIANCE_KEYWORDS if kw in all_page_text]
        result["compliance_mention"] = ", ".join(found_compliance[:3]) if found_compliance else ""

        # SSL check
        result["ssl_valid"] = url.startswith("https://")

    except Exception as e:
        result["scrape_status"] = f"error: {str(e)[:60]}"

    return result
