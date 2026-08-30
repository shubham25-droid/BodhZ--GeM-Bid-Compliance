from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# --------------------------------------------------
# AUTH & USER SCHEMAS
# --------------------------------------------------
class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    full_name: Optional[str] = None
    organization: Optional[str] = None


class LoginRequestSchema(BaseModel):
    username: str = Field(..., description="Officer or Auditor username")
    password: str = Field(..., description="Account password")


class RegisterRequestSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Official government or organization email")
    password: str = Field(..., min_length=6, description="Strong password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Officer full legal name")
    organization: Optional[str] = Field("Government e-Marketplace (GeM)", description="Procurement Ministry/CPSE/Org")
    department: Optional[str] = Field("Public Procurement Division", description="Department/Section")
    role: Optional[str] = Field("PROCUREMENT_OFFICER", description="Assigned system role")
    phone: Optional[str] = Field(None, description="Official contact number")


class UserResponseSchema(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    organization: Optional[str] = "GeM"
    department: Optional[str] = "Procurement"
    phone: Optional[str] = None
    is_active: bool
    email_verified: bool = True

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# TENDER SCHEMAS
# --------------------------------------------------
class RequirementCreateSchema(BaseModel):
    module: str
    title: str
    mandatory: bool = True
    weight: int = 25
    rule_type: str = "GATEWAY_STATUS"
    rule_config: Optional[Dict[str, Any]] = None


class RequirementResponseSchema(BaseModel):
    id: str
    tender_id: str
    module: str
    title: str
    mandatory: bool
    weight: int
    rule_type: str
    rule_config_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TenderCreateSchema(BaseModel):
    tender_number: str = Field(..., json_schema_extra={"example": "GEM/2026/B/882109"})
    title: str = Field(..., json_schema_extra={"example": "Supply of Server Infrastructure"})
    description: Optional[str] = None
    category: Optional[str] = "IT Hardware"
    source_text: Optional[str] = None
    requirements: Optional[List[RequirementCreateSchema]] = []


class TenderResponseSchema(BaseModel):
    id: str
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    tender_number: str
    title: str
    description: Optional[str]
    category: Optional[str]
    status: str
    lifecycle_status: str = "READY_FOR_BIDDING"
    requirements_confirmed: bool = True
    created_at: datetime
    requirements: List[RequirementResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# BID & BIDDER SCHEMAS
# --------------------------------------------------
class BidderCreateSchema(BaseModel):
    legal_name: str
    pan_number: Optional[str] = None
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None
    email: Optional[EmailStr] = None


class BidderResponseSchema(BaseModel):
    id: str
    legal_name: str
    pan_number: Optional[str]
    gstin: Optional[str]
    udyam_number: Optional[str]
    email: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class BidCreateSchema(BaseModel):
    tender_id: str
    bidder: BidderCreateSchema


class BidResponseSchema(BaseModel):
    id: str
    tender_id: str
    bidder_id: str
    submission_date: datetime
    status: str
    lifecycle_status: str = "UPLOADED"
    screening_status: str = "PENDING"
    bidder: Optional[BidderResponseSchema] = None

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# HISTORICAL BIDDER MATCH SCHEMA (5-YEAR MEMORY)
# --------------------------------------------------
class HistoricalBidderMatchResponseSchema(BaseModel):
    id: str
    bidder_id: str
    historical_tender_number: str
    historical_tender_title: str
    historical_outcome: str
    historical_score: int
    historical_risk: str
    key_findings_summary: Optional[str]
    matched_by: str
    evaluation_date: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# EVIDENCE & VERIFICATION SCHEMAS
# --------------------------------------------------
class EvidenceLinkResponseSchema(BaseModel):
    id: str
    finding_id: str
    document_id: str
    extraction_id: Optional[str]
    page_number: int

    model_config = ConfigDict(from_attributes=True)


class FindingResponseSchema(BaseModel):
    id: str
    severity: str
    code: str
    message: str
    evidence_links: List[EvidenceLinkResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)


class VerificationResultResponseSchema(BaseModel):
    id: str
    bid_id: str
    requirement_id: str
    module: str
    status: str
    confidence: float
    risk: str
    verification_mode: str
    findings: List[FindingResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# ASSESSMENT & OFFICER DECISION SCHEMAS
# --------------------------------------------------
class AssessmentResponseSchema(BaseModel):
    id: str
    bid_id: str
    compliance_score: int
    risk_level: str
    ai_recommendation: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OfficerDecisionCreateSchema(BaseModel):
    assessment_id: str
    bid_id: str
    decision: str = Field(..., description="QUALIFIED or DISQUALIFIED or NEEDS_CLARIFICATION or REJECTED")
    notes: Optional[str] = Field(None, description="Detailed justification notes by the officer")


class OfficerDecisionResponseSchema(BaseModel):
    id: str
    assessment_id: str
    bid_id: str
    officer_id: str
    decision: str
    notes: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# AUDIT EVENT SCHEMA
# --------------------------------------------------
class AuditEventResponseSchema(BaseModel):
    id: str
    bid_id: Optional[str]
    actor_id: str
    event_type: str
    payload_json: Optional[str]
    sha256_hash: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# AI HYBRID CHAT SCHEMAS
# --------------------------------------------------
class ChatRequestSchema(BaseModel):
    message: str = Field(..., description="User question or query text")
    user_name: Optional[str] = Field(None, description="Authenticated officer username")
    user_role: Optional[str] = Field(None, description="Authenticated officer role")
    tender_id: Optional[str] = Field(None, description="Active tender ID for context retrieval")
    bidder_id: Optional[str] = Field(None, description="Active bidder ID for context retrieval")
    active_tender_data: Optional[Dict[str, Any]] = None
    active_bidder_data: Optional[Dict[str, Any]] = None
    all_tenders: Optional[List[Dict[str, Any]]] = Field(default=[], description="List of all workspace tenders")
    all_bidders: Optional[List[Dict[str, Any]]] = Field(default=[], description="List of all workspace bidders")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Recent chat conversation history")


class ChatResponseSchema(BaseModel):
    reply: str
    source: str
    model: str
