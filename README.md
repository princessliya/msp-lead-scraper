# MSP Lead Scraper

Find and score SMB leads for Managed Service Providers. Full-stack web app with real-time scraping, lead scoring, and 68 industry verticals.

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React 19 + TypeScript + Tailwind CSS
- **Auth:** JWT with bcrypt password hashing
- **Real-time:** Server-Sent Events for live scrape progress

## Quick Start (Local)

### Prerequisites

- Python 3.9+
- Node.js 18+

### 1. Backend

```bash
cd backend
cp .env.example .env        # edit with your API keys (optional)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — register an account and start scraping.

### 3. Docker (alternative)

```bash
docker compose up --build
```

Open **http://localhost:8000**.

## API Keys

| API | Free Tier | Purpose |
|-----|-----------|---------|
| [Serper.dev](https://serper.dev) | 2,500 searches/month | Google search results |
| [SerpAPI](https://serpapi.com) | 100 searches/month | Google Maps business data |
| [Hunter.io](https://hunter.io) | 25 searches/month | Email enrichment |
| [Apollo.io](https://apollo.io) | Free tier available | Contact enrichment |

> **No API keys?** The app runs in mock data mode so you can explore all features without any keys.

## Features

- **Dashboard** — Run scrapes with real-time SSE progress, see results instantly
- **68 Verticals** — Pre-configured across 13 sectors (Healthcare, Legal, Finance, etc.) with MSP fit scores
- **Lead Scoring** — Automatic 0-100 scoring based on website, contacts, tech stack, and IT indicators
- **Lead Management** — Filter, sort, search, and paginate all your leads
- **Lead Details** — Contact info, tech stack badges, notes, and business intel
- **Bulk Export** — CSV and JSON export with filters
- **Job History** — Track all past scrapes with status and results
- **Settings** — Manage API keys and customize scoring weights
- **Auth** — Secure JWT login with token refresh

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET` | Yes (production) | Secret key for JWT tokens |
| `CORS_ORIGINS` | No | Comma-separated origins or `*` |
| `SERPER_KEY` | No | Serper.dev API key |
| `SERPAPI_KEY` | No | SerpAPI key |
| `HUNTER_KEY` | No | Hunter.io API key |
| `APOLLO_KEY` | No | Apollo.io API key |
| `DATABASE_URL` | No | Default: SQLite in backend dir |

## Deploy to Railway

1. Push this repo to GitHub
2. Sign up at [railway.app](https://railway.app) with GitHub
3. New Project → Deploy from GitHub → select this repo
4. Add environment variables: `JWT_SECRET`, `CORS_ORIGINS=*`
5. Generate a public domain under Settings → Networking
6. Visit your URL — done!

## License

MIT
