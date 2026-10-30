"""Pydantic request/response models for the API."""

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


# --- Query ---


class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class OfficeInfo(BaseModel):
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    working_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None


class ServiceRecommendation(BaseModel):
    institution: str
    department: str
    office: Optional[OfficeInfo] = None
    service_name: str
    required_documents: list[str] = []
    confidence: float
    explanation: str


class QueryStatus(str, Enum):
    matched = "matched"
    needs_clarification = "needs_clarification"
    no_match = "no_match"


class QueryResponse(BaseModel):
    status: QueryStatus
    recommendation: Optional[ServiceRecommendation] = None
    recommendations: list[ServiceRecommendation] = []  # multi-intent matches
    alternatives: list[ServiceRecommendation] = []
    question: Optional[str] = None
    conversation_id: Optional[str] = None
    top_candidates: list[ServiceRecommendation] = []
    query_id: str


# --- Feedback ---


class FeedbackRequest(BaseModel):
    query_id: str
    feedback: str = Field(..., pattern="^(correct|incorrect)$")


# --- Intent (internal, used by agent pipeline) ---


class Intent(BaseModel):
    category: str
    sub_intent: str
    entities: dict = {}
    query_text: str = ""  # sub-query text for multi-intent


class IntentExtractionResult(BaseModel):
    intents: list[Intent]
    is_multi_intent: bool = False


class Candidate(BaseModel):
    service_id: str
    service_name: str
    description: str
    department_name: str
    institution_name: str
    similarity_score: float
    office_address: Optional[str] = None
    office_lat: Optional[float] = None
    office_lng: Optional[float] = None
    working_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    required_documents: list[str] = []
    typical_duration: Optional[str] = None
    fees: Optional[str] = None


class RerankResult(BaseModel):
    best_match_id: str
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    is_ambiguous: bool = False
    used_fallback: bool = False


# --- Auth ---


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12)
    role: Literal["officer"] = "officer"
    institution_id: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    institution_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    institution_id: Optional[str] = None


class OfficerResponse(UserResponse):
    institution_name: str


# --- Institutions CRUD ---


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., pattern="^(federal|regional|municipal)$")
    description: Optional[str] = None


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = Field(default=None, pattern="^(federal|regional|municipal)$")
    description: Optional[str] = None


class InstitutionResponse(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    is_approved: bool
    created_at: str


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: str
    institution_id: str
    name: str
    description: Optional[str] = None


class ServiceCreate(BaseModel):
    department_id: str
    office_id: Optional[str] = None
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    example_phrasings: list[str] = []
    required_documents: list[str] = []
    typical_duration: Optional[str] = None
    fees: Optional[str] = None


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    example_phrasings: Optional[list[str]] = None
    required_documents: Optional[list[str]] = None
    typical_duration: Optional[str] = None
    fees: Optional[str] = None
    office_id: Optional[str] = None


class ServiceResponse(BaseModel):
    id: str
    department_id: str
    office_id: Optional[str] = None
    name: str
    description: str
    example_phrasings: list[str] = []
    required_documents: list[str] = []
    typical_duration: Optional[str] = None
    fees: Optional[str] = None
    has_embedding: bool = False
