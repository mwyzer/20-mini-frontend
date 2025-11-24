from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VisitorBase(BaseModel):
    ip_address: Optional[str] = Field(None, description="IPv4 or IPv6 address")
    user_agent: Optional[str] = Field(None, description="User agent string")


class VisitorCreate(VisitorBase):
    timestamp: Optional[datetime] = Field(None, description="Custom timestamp override")


class VisitorRead(BaseModel):
    id: int
    ip_address: str
    user_agent: str
    first_seen: datetime
    last_seen: datetime
    visit_count: int

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    unique_visitors: int
    total_visits: int
