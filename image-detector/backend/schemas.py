from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class BoundingBox(BaseModel):
    x: float = Field(..., ge=0, le=100)
    y: float = Field(..., ge=0, le=100)
    width: float = Field(..., ge=0, le=100)
    height: float = Field(..., ge=0, le=100)


class DetectedObject(BaseModel):
    label: str
    bbox: BoundingBox
    confidence: Optional[float] = Field(None, ge=0, le=1)


class DetectionResponse(BaseModel):
    id: int
    filename: str
    objects: List[DetectedObject]
    created_at: datetime

    @validator("created_at", pre=True)
    def parse_datetime(cls, value):
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)


class DetectionUpdate(BaseModel):
    filename: Optional[str] = None
    objects: Optional[List[DetectedObject]] = None


class DetectionCreate(BaseModel):
    filename: str
    objects: List[DetectedObject]
