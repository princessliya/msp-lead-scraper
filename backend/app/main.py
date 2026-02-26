import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.database import create_tables
from app.routes import auth, cache, events, export, leads, scrape, settings as settings_routes, verticals

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


logger = logging.getLogger(__name__)


def _parse_cors_origins(raw: str) -> list[str]:
    raw = raw.strip()
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warn if using the default JWT secret
    if settings.jwt_secret == "change-me-in-production-use-a-real-secret":
        logger.warning(
            "⚠️  Using default JWT secret! Set JWT_SECRET env var in production."
        )

    # Ensure the database directory exists
    db_url = settings.database_url
    if db_url.startswith("sqlite"):
        db_path = db_url.split("///")[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="MSP Lead Scraper",
        version="2.0.0",
        description="Find and score SMB leads for Managed Service Providers",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_cors_origins(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(scrape.router, prefix="/api/scrape", tags=["scrape"])
    app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
    app.include_router(verticals.router, prefix="/api/verticals", tags=["verticals"])
    app.include_router(export.router, prefix="/api/export", tags=["export"])
    app.include_router(settings_routes.router, prefix="/api/settings", tags=["settings"])
    app.include_router(cache.router, prefix="/api/cache", tags=["cache"])
    app.include_router(events.router, prefix="/api/events", tags=["events"])

    # Serve frontend static files in production.
    # Using a catch-all GET route instead of app.mount("/", StaticFiles(...))
    # to avoid routing conflicts where the mount intercepts API POST requests.
    if FRONTEND_DIST.exists():
        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str) -> FileResponse:
            file = FRONTEND_DIST / full_path
            if file.is_file():
                return FileResponse(str(file))
            return FileResponse(str(FRONTEND_DIST / "index.html"))

    return app


app = create_app()
