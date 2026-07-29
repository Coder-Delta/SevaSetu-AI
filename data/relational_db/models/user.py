import uuid
from sqlalchemy import Column, String, Integer, Boolean, Enum
from .base import Base, UUIDMixin, TimestampMixin

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # PII: Sensitive citizen personal identifiable information
    full_name = Column(String, nullable=True)
    
    preferred_language = Column(String, default="en", nullable=False)  # 'en', 'hi', 'bn'
    input_mode = Column(String, default="text", nullable=False)  # 'text', 'voice'
    
    # PII: Sensitive attributes
    age = Column(Integer, nullable=True)
    income_bracket = Column(String, nullable=True)
    category = Column(String, nullable=True)  # SC, ST, OBC, General
    
    # Demographics
    occupation = Column(String, nullable=True)
    location_state = Column(String, nullable=True)
    location_district = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    
    role = Column(String, default="citizen", nullable=False)  # 'citizen', 'admin'
    is_active = Column(Boolean, default=True, nullable=False)
