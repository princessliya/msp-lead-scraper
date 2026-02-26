from __future__ import annotations

# Default scoring weights
DEFAULT_WEIGHTS = {
    "website_present": 15,
    "phone_present": 5,
    "reviews_10plus": 5,
    "reviews_50plus": 5,
    "reviews_100plus": 5,
    "rating_4plus": 5,
    "email_scraped": 10,
    "email_verified": 10,
    "email_decision_maker": 5,
    "no_it_staff": 10,
    "existing_msp_penalty": -15,
    "cloud_tools": 5,
    "compliance_mention": 5,
    "ssl_present": 3,
    "business_size_medium": 5,
}


def score_lead(lead: dict, weights: dict | None = None) -> int:
    """Score a lead 0-100 based on MSP-prospect quality signals."""
    w = weights or DEFAULT_WEIGHTS
    score = 0

    # Website present
    if lead.get("website"):
        score += w.get("website_present", 15)

    # Phone
    if lead.get("phone"):
        score += w.get("phone_present", 5)

    # Reviews (maturity buckets)
    try:
        reviews = int(lead.get("reviews") or 0)
        if reviews >= 10:
            score += w.get("reviews_10plus", 5)
        if reviews >= 50:
            score += w.get("reviews_50plus", 5)
        if reviews >= 100:
            score += w.get("reviews_100plus", 5)
        # Business size from reviews
        if 50 <= reviews <= 200:
            score += w.get("business_size_medium", 5)
    except (ValueError, TypeError):
        pass

    # Rating
    try:
        rating = float(lead.get("rating") or 0)
        if rating >= 4.0:
            score += w.get("rating_4plus", 5)
    except (ValueError, TypeError):
        pass

    # Email quality tiers
    has_verified = bool(lead.get("hunter_email") or lead.get("apollo_email"))
    has_scraped = bool(lead.get("emails_found"))
    if has_verified:
        score += w.get("email_verified", 10)
        # Decision-maker bonus
        title = (lead.get("apollo_title") or lead.get("hunter_name") or "").lower()
        if any(t in title for t in ["owner", "ceo", "president", "founder"]):
            score += w.get("email_decision_maker", 5)
    elif has_scraped:
        score += w.get("email_scraped", 10)

    # No IT staff
    if not lead.get("has_it_mention", True):
        score += w.get("no_it_staff", 10)

    # Existing MSP (negative)
    if lead.get("has_existing_msp"):
        score += w.get("existing_msp_penalty", -15)

    # Cloud tools
    tech = lead.get("tech_stack", "")
    if any(t in tech for t in ["Microsoft 365", "Google Workspace"]):
        score += w.get("cloud_tools", 5)

    # Compliance mentions
    if lead.get("compliance_mention"):
        score += w.get("compliance_mention", 5)

    # SSL
    if lead.get("ssl_valid"):
        score += w.get("ssl_present", 3)

    return max(0, min(score, 100))
