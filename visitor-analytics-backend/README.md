# Visitor Analytics Backend

FastAPI service for recording and summarizing visitor activity with deduplication and request logging middleware.

## Running locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API uses SQLite by default (`visitor_analytics.db`). Set `DATABASE_URL` to use PostgreSQL or another database.

## Endpoints
- `POST /visitors` – manually register a visitor (IP/user-agent default to the request values).
- `GET /visitors?window=day|week` – list visitors filtered by time window.
- `GET /visitors/summary?window=day|week` – summary counts for the given window.
- `GET /health` – service health check.

A middleware automatically logs every incoming request (except docs) and performs deduplication for repeated visitors within 10 minutes.
