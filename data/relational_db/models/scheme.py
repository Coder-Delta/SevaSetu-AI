from sqlalchemy import Column, String, Text, Boolean
from .base import Base, UUIDMixin, TimestampMixin

class Scheme(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "schemes"

    scheme_name = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    details = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    eligibility = Column(Text, nullable=True)
    application_process = Column(Text, nullable=True)
    documents_required = Column(Text, nullable=True)
    level = Column(String, nullable=True)  # 'Central', 'State'
    scheme_category = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
