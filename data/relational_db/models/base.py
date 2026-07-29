import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UUIDMixin:
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
