from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text

from .database import Base


class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(100), nullable=False, index=True)
    user_agent = Column(Text, nullable=False)
    first_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    visit_count = Column(Integer, nullable=False, default=1)
