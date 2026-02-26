from pathlib import Path

from pydantic_settings import BaseSettings

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Database
    database_url: str = f"sqlite:///{_BACKEND_DIR / 'msp_leads.db'}"

    # JWT
    jwt_secret: str = "change-me-in-production-use-a-real-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_expiration_minutes: int = 60 * 24  # 24 hours
    jwt_refresh_expiration_days: int = 30

    # API Keys
    serper_key: str = ""
    serpapi_key: str = ""
    hunter_key: str = ""
    apollo_key: str = ""

    # Scraper defaults
    default_delay: float = 1.5
    default_num_results: int = 20

    # CORS — accepts a comma-separated string or "*"
    # Kept as str so pydantic-settings doesn't try to JSON-parse it
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
