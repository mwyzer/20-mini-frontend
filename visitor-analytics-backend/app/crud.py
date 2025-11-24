from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from .models import Visitor

DEDUP_MINUTES_DEFAULT = 10


def log_visitor(
    db: Session,
    ip_address: str,
    user_agent: str,
    now: Optional[datetime] = None,
    dedup_minutes: int = DEDUP_MINUTES_DEFAULT,
) -> Tuple[Visitor, bool]:
    """Create or update a visitor record.

    Returns a tuple of (visitor, created)
    """

    now = now or datetime.utcnow()
    window_start = now - timedelta(minutes=dedup_minutes)

    existing = (
        db.query(Visitor)
        .filter(
            Visitor.ip_address == ip_address,
            Visitor.user_agent == user_agent,
            Visitor.last_seen >= window_start,
        )
        .order_by(Visitor.last_seen.desc())
        .first()
    )

    if existing:
        existing.last_seen = now
        existing.visit_count += 1
        db.commit()
        db.refresh(existing)
        return existing, False

    visitor = Visitor(
        ip_address=ip_address,
        user_agent=user_agent,
        first_seen=now,
        last_seen=now,
    )
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    return visitor, True


def _window_to_timedelta(window: str) -> timedelta:
    normalized = window.lower()
    if normalized == "day":
        return timedelta(days=1)
    if normalized == "week":
        return timedelta(weeks=1)
    raise ValueError("Unsupported window. Use 'day' or 'week'.")


def get_visitors(db: Session, window: str) -> List[Visitor]:
    delta = _window_to_timedelta(window)
    since = datetime.utcnow() - delta
    return (
        db.query(Visitor)
        .filter(Visitor.last_seen >= since)
        .order_by(Visitor.last_seen.desc())
        .all()
    )


def summarize_visitors(db: Session, window: str):
    visitors = get_visitors(db, window)
    total_hits = sum(v.visit_count for v in visitors)
    latest = visitors[0] if visitors else None
    return {
        "window": window,
        "unique_visitors": len(visitors),
        "total_hits": total_hits,
        "latest_visitor": latest,
    }
