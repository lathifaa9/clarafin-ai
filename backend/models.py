import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Authentication Models ---
class UserBase(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Enter a valid email address")
        return normalized

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(UserBase):
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# --- Document Models ---
class DocumentResponse(BaseModel):
    id: int
    filename: str
    doc_type: str
    upload_date: datetime
    file_size: int

    class Config:
        from_attributes = True

# --- Analysis Models ---
class RunAnalysisRequest(BaseModel):
    doc_ids: List[int] = Field(min_length=1)
    groq_api_key: Optional[str] = None

class AnalysisDetail(BaseModel):
    current_state: str = Field(description="Structured interpretation, liquidity ratios, margins, revenues, anomalies")
    gap_detection: str = Field(description="Gaps found in documents, and decisions blocked because of it")
    forward_flags: str = Field(description="Reasoned pattern-based flags (runway, seasonal pressure, receivables risk)")
    traceability_map: Dict[str, List[Dict[str, Any]]] = Field(description="Claim to source mappings")

class AnalysisResponse(BaseModel):
    id: str
    status: str  # pending, parsing, computing, finished, failed
    progress_message: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    doc_ids: List[int]
