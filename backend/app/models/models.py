from datetime import datetime, timezone
import uuid
import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


# --------------------------------------------------
# ENUMS: TENDER & BID LIFECYCLE STATES
# --------------------------------------------------
class TenderLifecycleState(str, enum.Enum):
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    REVIEW_REQUIREMENTS = "REVIEW_REQUIREMENTS"
    READY_FOR_BIDDING = "READY_FOR_BIDDING"
    BIDDING_IN_PROGRESS = "BIDDING_IN_PROGRESS"
    ALL_BIDS_PROCESSED = "ALL_BIDS_PROCESSED"
    SHORTLIST_READY = "SHORTLIST_READY"
    FINAL_REVIEW = "FINAL_REVIEW"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class BidLifecycleState(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    VERIFIED = "VERIFIED"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    QUALIFIED_FOR_FINAL_REVIEW = "QUALIFIED_FOR_FINAL_REVIEW"
    NOT_QUALIFIED = "NOT_QUALIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    OFFICER_DECISION_PENDING = "OFFICER_DECISION_PENDING"
    FINALIZED = "FINALIZED"


class FirstLevelScreeningStatus(str, enum.Enum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    PROCUREMENT_OFFICER = "PROCUREMENT_OFFICER"
    BID_UPLOADER = "BID_UPLOADER"
    DTE_OFFICER = "DTE_OFFICER"
    REVIEWER = "REVIEWER"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


# --------------------------------------------------
# 1. USER & AUTHENTICATION MODEL
# --------------------------------------------------
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False, default="PROCUREMENT_OFFICER")
    organization = Column(String(150), nullable=False, default="Government e-Marketplace (GeM)")
    department = Column(String(150), nullable=False, default="Public Procurement Division")
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenders = relationship("TenderModel", back_populates="creator", cascade="all, delete-orphan")
    officer_decisions = relationship("OfficerDecisionModel", back_populates="officer")


# --------------------------------------------------
# 2. GEM TENDER MODEL (ONE TENDER -> MANY BIDS)
# --------------------------------------------------
class TenderModel(Base):
    __tablename__ = "tenders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(String(50), nullable=True, default="ORG_GEM_CENTRAL", index=True)
    tender_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    source_text = Column(Text, nullable=True)
    status = Column(String(30), default="ACTIVE")
    lifecycle_status = Column(String(30), default="READY_FOR_BIDDING", index=True)
    requirements_confirmed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    creator = relationship("UserModel", back_populates="tenders")
    requirements = relationship("RequirementModel", back_populates="tender", cascade="all, delete-orphan")
    bids = relationship("BidModel", back_populates="tender", cascade="all, delete-orphan")


# --------------------------------------------------
# 3. TENDER REQUIREMENT MODEL
# --------------------------------------------------
class RequirementModel(Base):
    __tablename__ = "requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False)
    module = Column(String(50), nullable=False)  # GST, Udyam, PAN, OEM, Financial, etc.
    title = Column(String(255), nullable=False)
    mandatory = Column(Boolean, default=True)
    weight = Column(Integer, default=25)
    rule_type = Column(String(50), nullable=False)
    rule_config_json = Column(Text, nullable=True)

    tender = relationship("TenderModel", back_populates="requirements")
    verification_results = relationship("VerificationResultModel", back_populates="requirement")


# --------------------------------------------------
# 4. BIDDER PROFILE MODEL
# --------------------------------------------------
class BidderModel(Base):
    __tablename__ = "bidders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_name = Column(String(255), nullable=False, index=True)
    pan_number = Column(String(10), nullable=True, index=True)
    gstin = Column(String(15), nullable=True, index=True)
    udyam_number = Column(String(25), nullable=True, index=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bids = relationship("BidModel", back_populates="bidder")
    historical_records = relationship("HistoricalBidderMatchModel", back_populates="bidder", cascade="all, delete-orphan")


# --------------------------------------------------
# 5. BID SUBMISSION MODEL
# --------------------------------------------------
class BidModel(Base):
    __tablename__ = "bids"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False, index=True)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    submission_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(30), default="SUBMITTED")  # SUBMITTED, PROCESSING, EVALUATED, QUALIFIED, DISQUALIFIED
    lifecycle_status = Column(String(30), default="UPLOADED", index=True)
    screening_status = Column(String(30), default="PENDING", index=True)  # PASS, FAIL, REVIEW, PENDING

    tender = relationship("TenderModel", back_populates="bids")
    bidder = relationship("BidderModel", back_populates="bids")
    documents = relationship("DocumentModel", back_populates="bid", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResultModel", back_populates="bid", cascade="all, delete-orphan")
    assessments = relationship("AssessmentModel", back_populates="bid", cascade="all, delete-orphan")
    audit_events = relationship("AuditEventModel", back_populates="bid", cascade="all, delete-orphan")


# --------------------------------------------------
# 6. UPLOADED DOCUMENT MODEL
# --------------------------------------------------
class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bid_id = Column(String(36), ForeignKey("bids.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False)  # GST_CERT, BID_FORM, UDYAM_CERT, OEM_AUTH, FINANCIAL
    storage_path = Column(String(500), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bid = relationship("BidModel", back_populates="documents")
    extractions = relationship("ExtractionModel", back_populates="document", cascade="all, delete-orphan")


# --------------------------------------------------
# 7. EXTRACTED ENTITY MODEL
# --------------------------------------------------
class ExtractionModel(Base):
    __tablename__ = "extractions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False, index=True)
    field_value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    page_number = Column(Integer, default=1)
    text_snippet = Column(Text, nullable=True)

    document = relationship("DocumentModel", back_populates="extractions")


# --------------------------------------------------
# 8. VERIFICATION RESULT MODEL
# --------------------------------------------------
class VerificationResultModel(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bid_id = Column(String(36), ForeignKey("bids.id"), nullable=False, index=True)
    requirement_id = Column(String(36), ForeignKey("requirements.id"), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)
    status = Column(String(30), nullable=False)  # PASS, FAIL, REVIEW
    confidence = Column(Float, default=1.0)
    risk = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    verification_mode = Column(String(30), default="SANDBOX")  # AUTHORIZED_API, SANDBOX, DOCUMENT_CONSISTENCY, MANUAL

    bid = relationship("BidModel", back_populates="verification_results")
    requirement = relationship("RequirementModel", back_populates="verification_results")
    findings = relationship("FindingModel", back_populates="verification_result", cascade="all, delete-orphan")


# --------------------------------------------------
# 9. FINDING MODEL
# --------------------------------------------------
class FindingModel(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_result_id = Column(String(36), ForeignKey("verification_results.id"), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    code = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)

    verification_result = relationship("VerificationResultModel", back_populates="findings")
    evidence_links = relationship("EvidenceLinkModel", back_populates="finding", cascade="all, delete-orphan")


# --------------------------------------------------
# 10. EVIDENCE PROVENANCE LINK MODEL
# --------------------------------------------------
class EvidenceLinkModel(Base):
    __tablename__ = "evidence_links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    finding_id = Column(String(36), ForeignKey("findings.id"), nullable=False, index=True)
    document_id = Column(String(36), nullable=False)
    extraction_id = Column(String(36), nullable=True)
    page_number = Column(Integer, default=1)

    finding = relationship("FindingModel", back_populates="evidence_links")


# --------------------------------------------------
# 11. DECISION SUPPORT ASSESSMENT MODEL
# --------------------------------------------------
class AssessmentModel(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bid_id = Column(String(36), ForeignKey("bids.id"), nullable=False, index=True)
    compliance_score = Column(Integer, nullable=False)  # 0 to 100
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    ai_recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bid = relationship("BidModel", back_populates="assessments")
    officer_decisions = relationship("OfficerDecisionModel", back_populates="assessment", cascade="all, delete-orphan")


# --------------------------------------------------
# 12. PROCUREMENT OFFICER DECISION MODEL
# --------------------------------------------------
class OfficerDecisionModel(Base):
    __tablename__ = "officer_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False, index=True)
    bid_id = Column(String(36), nullable=False, index=True)
    officer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    decision = Column(String(30), nullable=False)  # QUALIFIED, DISQUALIFIED, REJECTED, NEEDS_CLARIFICATION
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    assessment = relationship("AssessmentModel", back_populates="officer_decisions")
    officer = relationship("UserModel", back_populates="officer_decisions")


# --------------------------------------------------
# 13. AUDIT & TRACEABILITY MODEL
# --------------------------------------------------
class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bid_id = Column(String(36), ForeignKey("bids.id"), nullable=True, index=True)
    actor_id = Column(String(100), nullable=False, default="SYSTEM")
    event_type = Column(String(100), nullable=False, index=True)
    payload_json = Column(Text, nullable=True)
    sha256_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bid = relationship("BidModel", back_populates="audit_events")


# --------------------------------------------------
# 14. 5-YEAR HISTORICAL BIDDER RECORD RESOLUTION MODEL
# --------------------------------------------------
class HistoricalBidderMatchModel(Base):
    """
    Maintains historical memory of previously verified bids across past tenders (5+ years).
    Used for historical entity matching on GSTIN, PAN, Udyam, and legal organization name.
    """
    __tablename__ = "historical_bidder_matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    historical_tender_number = Column(String(50), nullable=False, index=True)
    historical_tender_title = Column(String(255), nullable=False)
    historical_outcome = Column(String(30), nullable=False)  # QUALIFIED, DISQUALIFIED, REJECTED, FINALIZED
    historical_score = Column(Integer, nullable=False, default=85)
    historical_risk = Column(String(20), nullable=False, default="LOW")
    key_findings_summary = Column(Text, nullable=True)
    matched_by = Column(String(50), nullable=False)  # VERIFIED_GSTIN, VERIFIED_PAN, VERIFIED_UDYAM, LEGAL_NAME
    evaluation_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bidder = relationship("BidderModel", back_populates="historical_records")
