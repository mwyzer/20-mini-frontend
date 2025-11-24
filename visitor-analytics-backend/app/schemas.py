from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VisitorBase(BaseModel):
    ip_address: str = Field(..., alias="ip")
    user_agent: str

    class Config:
        allow_population_by_field_name = True


class VisitorCreate(BaseModel):
    ip_address: Optional[str] = Field(None, alias="ip")
    user_agent: Optional[str]

    class Config:
        allow_population_by_field_name = True


class Visitor(VisitorBase):
    id: int
    first_seen: datetime
    last_seen: datetime
    visit_count: int

    class Config:
        orm_mode = True


class VisitorList(BaseModel):
    visitors: List[Visitor]


class Summary(BaseModel):
    window: str
    unique_visitors: int
    total_hits: int
    latest_visitor: Optional[Visitor]

    class Config:
        orm_mode = True
