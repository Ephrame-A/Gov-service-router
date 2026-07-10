"""Pydantic request/response models for the API."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --- Query ---


class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class OfficeInfo(BaseModel):
    address: str
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
    alternatives: list[ServiceRecommendation] = []
    question: Optional[str] = None  # for needs_clarification
    conversation_id: Optional[str] = None
    top_candidates: list[ServiceRecommendation] = []  # for no_match
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


class Candidate(BaseModel):
    service_id: str
    service_name: str
    description: str
    department_name: str
    institution_name: str
    similarity_score: float
    office_address: Optional[str] = None
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
