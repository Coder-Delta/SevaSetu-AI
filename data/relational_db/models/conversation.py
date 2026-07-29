import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, Uuid
from sqlalchemy.orm import relationship
from .base import Base, UUIDMixin, TimestampMixin

class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Structure: [{"role": "user"/"assistant", "content": "...", "timestamp": "...", "language": "en"/"hi"/"bn"}]
    messages = Column(JSON, default=list, nullable=False)
    session_language = Column(String, default="en", nullable=False)

    user = relationship("User")
