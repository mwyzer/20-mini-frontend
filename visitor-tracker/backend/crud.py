from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Visitor

DEDUPE_WINDOW_MINUTES = 10


def _normalize_ip(raw_ip: Optional[str]) -> str:
    if raw_ip and "," in raw_ip:
        return raw_ip.split(",")[0].strip()
    return raw_ip or "unknown"


def _normalize_ua(user_agent: Optional[str]) -> str:
    return user_agent or "unknown"


def log_visit(
    session: Session,
    *,
    ip_address: Optional[str],
    user_agent: Optional[str],
    timestamp: Optional[datetime] = None,
) -> Visitor:
    now = timestamp or datetime.utcnow()
    normalized_ip = _normalize_ip(ip_address)
    normalized_ua = _normalize_ua(user_agent)

    cutoff = now - timedelta(minutes=DEDUPE_WINDOW_MINUTES)
    existing = (
        session.execute(
            select(Visitor)
            .where(
                Visitor.ip_address == normalized_ip,
                Visitor.user_agent == normalized_ua,
                Visitor.last_seen >= cutoff,
            )
            .order_by(Visitor.last_seen.desc())
        )
        .scalars()
        .first()
    )

    if existing:
        existing.last_seen = now
        existing.visit_count += 1
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    visitor = Visitor(
        ip_address=normalized_ip,
        user_agent=normalized_ua,
        first_seen=now,
        last_seen=now,
        visit_count=1,
    )
    session.add(visitor)
    session.commit()
    session.refresh(visitor)
    return visitor


def _apply_time_filter(query, range_label: Optional[str]):
    now = datetime.utcnow()
    if range_label == "day":
        return query.where(Visitor.last_seen >= now - timedelta(days=1))
    if range_label == "week":
        return query.where(Visitor.last_seen >= now - timedelta(days=7))
    return query


def get_visitors(session: Session, range_label: Optional[str] = None) -> Iterable[Visitor]:
    query = select(Visitor).order_by(Visitor.last_seen.desc())
    query = _apply_time_filter(query, range_label)
    return session.execute(query).scalars().all()


def get_stats(session: Session, range_label: Optional[str] = None) -> dict:
    base_query = select(Visitor)
    filtered_query = _apply_time_filter(base_query, range_label)

    visitors = session.execute(filtered_query).scalars().all()
    unique_visitors = len(visitors)
    total_visits = sum(v.visit_count for v in visitors)
    return {"unique_visitors": unique_visitors, "total_visits": total_visits}
