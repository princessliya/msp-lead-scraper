from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scrape_jobs.id"), nullable=False, index=True)

    # Core business info (from Google Maps)
    business_name = Column(String(500), nullable=False)
    category = Column(String(255), default="")
    address = Column(String(500), default="")
    phone = Column(String(50), default="")
    website = Column(String(500), default="")
    domain = Column(String(255), default="", index=True)
    rating = Column(Float, nullable=True)
    reviews = Column(Integer, nullable=True)
    google_maps_url = Column(String(500), default="")

    # Scraped data (from website)
    emails_found = Column(Text, default="")
    tech_stack = Column(String(1000), default="")
    has_it_mention = Column(Boolean, default=False)
    has_existing_msp = Column(Boolean, default=False)
    compliance_mention = Column(String(255), default="")
    ssl_valid = Column(Boolean, default=False)
    scrape_status = Column(String(100), default="")

    # Hunter.io enrichment
    hunter_email = Column(String(255), default="")
    hunter_name = Column(String(255), default="")
    hunter_confidence = Column(Integer, nullable=True)

    # Apollo.io enrichment
    apollo_email = Column(String(255), default="")
    apollo_name = Column(String(255), default="")
    apollo_title = Column(String(255), default="")
    company_size = Column(String(50), default="")
    industry = Column(String(255), default="")

    # Scoring
    score = Column(Integer, default=0, index=True)

    # User annotations
    notes = Column(Text, default="")
    is_archived = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scrape_job = relationship("ScrapeJob", back_populates="leads")
