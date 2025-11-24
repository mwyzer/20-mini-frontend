# Visitor Tracker

A simple FastAPI + React visitor analytics dashboard that stores visitor data, deduplicates repeated hits, and surfaces real-time stats.

## Backend (FastAPI)

- Stores visitors in SQLite by default (`visitors.db`).
- Deduplicates visitors that repeat within 10 minutes (updates the last_seen timestamp and increments `visit_count`).
- Middleware captures incoming requests except health/docs/stats/list lookups.
- Supports range filtering (`day`, `week`, or all-time) for both stats and visitor lists.
- CORS is enabled for all origins so the React dashboard can fetch data.

### Running the API

```bash
cd visitor-tracker/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`.

### Key endpoints

- `POST /visitors` — log a visitor (IP/User-Agent inferred when not provided)
- `GET /visitors?range=day|week` — list visitors with optional time filter
- `GET /stats?range=day|week` — aggregated visitor counts

## Frontend (React)

A lightweight React dashboard served from a static HTML page (no build step required) that polls the API every 5 seconds.

### Usage

Simply open `visitor-tracker/frontend/index.html` in a dev server (e.g. VSCode Live Server or `python -m http.server 3000` from inside the `frontend` folder) and ensure the backend is running on `http://localhost:8000`.

Features:

- Realtime visitor count cards and visit history table
- Filter by last day, week, or all time
- Minimal responsive layout with a quick bar chart visualization of visits
