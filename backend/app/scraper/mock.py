from __future__ import annotations


def mock_places(query: str, location: str) -> list:
    """Fake places for testing without API keys."""
    return [
        {
            "title": f"Sample {query.title()} Co.",
            "types": [query],
            "address": f"123 Main St, {location}",
            "phone": "555-1234",
            "website": "https://example.com",
            "rating": 4.5,
            "reviews": 87,
        },
        {
            "title": f"Metro {query.title()} Group",
            "types": [query],
            "address": f"456 Oak Ave, {location}",
            "phone": "555-5678",
            "website": "https://example.org",
            "rating": 4.1,
            "reviews": 32,
        },
        {
            "title": f"{location} {query.title()} LLC",
            "types": [query],
            "address": f"789 Pine Rd, {location}",
            "phone": "555-9012",
            "website": "",
            "rating": 3.8,
            "reviews": 12,
        },
    ]
