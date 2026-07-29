from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# --- Auth & User Schemas ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    preferred_language: str = "en"
    input_mode: str = "text"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    preferred_language: str
    input_mode: str
    age: Optional[int] = None
    income_bracket: Optional[str] = None
    category: Optional[str] = None
    occupation: Optional[str] = None
    location_state: Optional[str] = None
    location_district: Optional[str] = None
    education_level: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    input_mode: Optional[str] = None
    age: Optional[int] = None
    income_bracket: Optional[str] = None
    category: Optional[str] = None
    occupation: Optional[str] = None
    location_state: Optional[str] = None
    location_district: Optional[str] = None
    education_level: Optional[str] = None

# --- Scheme Schemas ---

class SchemeResponse(BaseModel):
    id: UUID
    scheme_name: str
    slug: str
    details: Optional[str] = None
    benefits: Optional[str] = None
    eligibility: Optional[str] = None
    application_process: Optional[str] = None
    documents_required: Optional[str] = None
    level: Optional[str] = None
    scheme_category: Optional[str] = None
    tags: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SchemeSearchRequest(BaseModel):
    query: str
    language: str = "en"
    top_k: int = 5

class SchemeSearchResult(BaseModel):
    scheme: SchemeResponse
    relevance_score: float
    eligibility_explanation: Optional[str] = None

# --- Chat Schemas ---

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None
    language: Optional[str] = "en"

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    conversation_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    response: str
    language: str
    conversation_id: UUID
    schemes_referenced: Optional[List[SchemeResponse]] = None

# --- Application Schemas ---

class ApplicationCreate(BaseModel):
    scheme_id: UUID

class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    scheme_id: UUID
    status: str
    documents_metadata: Optional[Dict[str, str]] = None
    eligibility_score: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    scheme: Optional[SchemeResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
