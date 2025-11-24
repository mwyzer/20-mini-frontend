from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Visitor Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.middleware("http")
async def log_visit_middleware(request: Request, call_next):
    response = await call_next(request)

    # Skip logging for documentation endpoints to avoid noise
    if request.url.path.startswith(("/docs", "/openapi", "/redoc")):
        return response

    ip_address = request.headers.get("x-forwarded-for")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with SessionLocal() as db:
        crud.log_visitor(db, ip_address=ip_address, user_agent=user_agent, now=datetime.utcnow())

    return response


@app.post("/visitors", response_model=schemas.Visitor)
def add_visitor(
    payload: schemas.VisitorCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = payload.ip_address or request.client.host
    user_agent = payload.user_agent or request.headers.get("user-agent", "unknown")

    if not ip_address:
        raise HTTPException(status_code=400, detail="IP address is required")

    visitor, _ = crud.log_visitor(db, ip_address=ip_address, user_agent=user_agent, now=datetime.utcnow())
    return visitor


@app.get("/visitors", response_model=List[schemas.Visitor])
def list_visitors(window: str = "day", db: Session = Depends(get_db)):
    try:
        return crud.get_visitors(db, window)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/visitors/summary", response_model=schemas.Summary)
def visitor_summary(window: str = "day", db: Session = Depends(get_db)):
    try:
        summary = crud.summarize_visitors(db, window)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    latest = summary.get("latest_visitor")
    return schemas.Summary(**summary, latest_visitor=latest)


@app.get("/health")
def health():
    return {"status": "ok"}
