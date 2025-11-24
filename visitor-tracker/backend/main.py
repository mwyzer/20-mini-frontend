from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Visitor Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


EXCLUDED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}
EXCLUDED_GET_PATHS = {"/stats", "/visitors"}


@app.middleware("http")
async def log_visitor(request: Request, call_next):
    should_skip = request.url.path in EXCLUDED_PATHS
    if request.method == "GET" and request.url.path in EXCLUDED_GET_PATHS:
        should_skip = True
    if request.method == "POST" and request.url.path == "/visitors":
        should_skip = True

    if not should_skip and request.method != "OPTIONS":
        client_ip = request.headers.get("x-forwarded-for")
        if not client_ip and request.client:
            client_ip = request.client.host
        with SessionLocal() as session:
            crud.log_visit(
                session,
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                timestamp=datetime.utcnow(),
            )

    response = await call_next(request)
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/visitors", response_model=schemas.VisitorRead)
async def create_visitor(
    visitor: schemas.VisitorCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    client_ip = visitor.ip_address or request.headers.get("x-forwarded-for")
    if not client_ip and request.client:
        client_ip = request.client.host
    logged = crud.log_visit(
        db,
        ip_address=client_ip,
        user_agent=visitor.user_agent or request.headers.get("user-agent"),
        timestamp=visitor.timestamp,
    )
    return logged


@app.get("/visitors", response_model=list[schemas.VisitorRead])
async def list_visitors(
    time_range: Optional[str] = Query(None, alias="range"), db: Session = Depends(get_db)
):
    return crud.get_visitors(db, range_label=time_range)


@app.get("/stats", response_model=schemas.StatsResponse)
async def visitor_stats(
    time_range: Optional[str] = Query(None, alias="range"), db: Session = Depends(get_db)
):
    return crud.get_stats(db, range_label=time_range)


@app.get("/")
async def root():
    return {"message": "Visitor tracking API is running"}
