import uuid
from sqlalchemy import Column, String, Float, Text, ForeignKey, JSON, Uuid
from sqlalchemy.orm import relationship
from .base import Base, UUIDMixin, TimestampMixin

class Application(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "applications"

    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Uuid(as_uuid=True), ForeignKey("schemes.id"), nullable=False)
    
    # Status can be: 'draft', 'documents_pending', 'submitted', 'under_review', 'approved', 'rejected'
    status = Column(String, default="draft", nullable=False)
    
    # Stores references/URLs of uploaded documents, format: {"Aadhaar Card": "object_name", ...}
    documents_metadata = Column(JSON, nullable=True)
    
    eligibility_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User")
    scheme = relationship("Scheme")
