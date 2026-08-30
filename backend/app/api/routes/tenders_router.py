import json
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.models.models import UserModel, TenderModel, RequirementModel, BidModel, AuditEventModel
from app.schemas.schemas import (
    TenderCreateSchema, TenderResponseSchema, RequirementResponseSchema, RequirementCreateSchema
)
from app.document_intelligence.file_validator import FileValidator
from app.document_intelligence.pdf_extractor import PDFExtractor
from app.tender_intelligence.requirement_extractor import TenderRequirementExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenders", tags=["Tender Intelligence & Management Layer"])


# --------------------------------------------------
# 1. CREATE TENDER MANUALLY (STRUCTURED JSON)
# --------------------------------------------------
@router.post("", response_model=TenderResponseSchema, status_code=status.HTTP_201_CREATED, summary="Create GeM Procurement Tender")
def create_tender(
    tender_in: TenderCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registers a new GeM procurement tender along with its structured requirements.
    Associates the tender with the authenticated officer and organization.
    """
    existing = db.query(TenderModel).filter(
        func.lower(TenderModel.tender_number) == tender_in.tender_number.strip().lower()
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tender number '{tender_in.tender_number}' already exists in the system."
        )

    new_tender = TenderModel(
        user_id=current_user.id,
        organization_id=current_user.organization or "ORG_GEM_CENTRAL",
        tender_number=tender_in.tender_number.strip(),
        title=tender_in.title.strip(),
        description=tender_in.description,
        category=tender_in.category or "General",
        source_text=tender_in.source_text,
        status="ACTIVE",
        lifecycle_status="READY_FOR_BIDDING",
        requirements_confirmed=True
    )
    db.add(new_tender)
    db.flush()

    # Add associated requirements if provided
    if tender_in.requirements:
        for req_in in tender_in.requirements:
            req_model = RequirementModel(
                tender_id=new_tender.id,
                module=req_in.module,
                title=req_in.title,
                mandatory=req_in.mandatory,
                weight=req_in.weight,
                rule_type=req_in.rule_type,
                rule_config_json=json.dumps(req_in.rule_config) if req_in.rule_config else None
            )
            db.add(req_model)

    # Audit Trail
    audit = AuditEventModel(
        actor_id=f"OFFICER ({current_user.username})",
        event_type="TENDER_CREATED",
        payload_json=f"Created tender {new_tender.tender_number} with {len(tender_in.requirements or [])} requirements."
    )
    db.add(audit)

    db.commit()
    db.refresh(new_tender)
    return new_tender


# --------------------------------------------------
# 2. UPLOAD TENDER PDF & RUN TENDER INTELLIGENCE
# --------------------------------------------------
@router.post("/upload-pdf", summary="Upload Tender Notice PDF & Extract Requirements")
async def upload_tender_pdf(
    file: UploadFile = File(...),
    tender_number: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form("IT & Infrastructure"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingests an official Tender Notice / NIT document PDF:
    1. Validates magic byte header & calculates SHA-256 hash.
    2. Executes PyMuPDF digital text extraction.
    3. Runs Automated Tender Intelligence Extractor to derive statutory requirements.
    4. Creates Tender in state 'REVIEW_REQUIREMENTS' with requirements_confirmed=False.
    5. Returns Tender + Requirements for Procurement Officer confirmation.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty tender file uploaded.")

    mime_cat = FileValidator.validate_file_content(file_bytes, file.filename or "tender.pdf")
    sha256_hash = FileValidator.calculate_sha256(file_bytes)

    # Extract text
    if mime_cat == "APPLICATION_PDF":
        extracted = PDFExtractor.extract_text_from_pdf_bytes(file_bytes)
        full_text = " ".join(p["text"] for p in extracted.get("pages", []))
    else:
        full_text = file_bytes.decode("utf-8", errors="ignore")

    # Generate tender number if omitted
    t_num = tender_number.strip() if tender_number else f"GEM/2026/B/{abs(hash(sha256_hash)) % 1000000:06d}"
    t_title = title.strip() if title else f"Tender {t_num} - {category}"

    # Prevent duplicate
    existing = db.query(TenderModel).filter(func.lower(TenderModel.tender_number) == t_num.lower()).first()
    if existing:
        t_num = f"{t_num}_{int(func.random() * 1000) if hasattr(func, 'random') else '1'}"

    # Extract requirements
    extracted_reqs = TenderRequirementExtractor.extract_requirements(full_text, category, t_title)

    new_tender = TenderModel(
        user_id=current_user.id,
        organization_id=current_user.organization or "ORG_GEM_CENTRAL",
        tender_number=t_num,
        title=t_title,
        description=f"Auto-ingested from '{file.filename}' (SHA256: {sha256_hash[:16]}...)",
        category=category,
        source_text=full_text[:4000],
        status="ACTIVE",
        lifecycle_status="REVIEW_REQUIREMENTS",
        requirements_confirmed=False
    )
    db.add(new_tender)
    db.flush()

    persisted_reqs = []
    for r in extracted_reqs:
        req_obj = RequirementModel(
            tender_id=new_tender.id,
            module=r["module"],
            title=r["title"],
            mandatory=r["mandatory"],
            weight=r["weight"],
            rule_type=r["rule_type"],
            rule_config_json=json.dumps(r.get("rule_config", {}))
        )
        db.add(req_obj)
        persisted_reqs.append(req_obj)

    # Audit Trail
    audit = AuditEventModel(
        actor_id=f"OFFICER ({current_user.username})",
        event_type="TENDER_UPLOADED_AND_EXTRACTED",
        payload_json=f"Uploaded tender PDF '{file.filename}' ({len(persisted_reqs)} requirements extracted).",
        sha256_hash=sha256_hash
    )
    db.add(audit)

    db.commit()
    db.refresh(new_tender)

    return {
        "tender_id": new_tender.id,
        "tender_number": new_tender.tender_number,
        "title": new_tender.title,
        "category": new_tender.category,
        "lifecycle_status": new_tender.lifecycle_status,
        "requirements_confirmed": new_tender.requirements_confirmed,
        "requirements_count": len(persisted_reqs),
        "requirements": [
            {
                "id": req.id,
                "module": req.module,
                "title": req.title,
                "mandatory": req.mandatory,
                "weight": req.weight,
                "rule_type": req.rule_type
            }
            for req in persisted_reqs
        ],
        "next_step": "Review and confirm statutory requirements to transition tender to READY_FOR_BIDDING."
    }


# --------------------------------------------------
# 3. CONFIRM TENDER REQUIREMENTS (LIFECYCLE TRANSITION)
# --------------------------------------------------
@router.post("/{tender_id}/confirm-requirements", summary="Procurement Officer Confirms Requirements")
def confirm_tender_requirements(
    tender_id: str,
    requirements: Optional[List[RequirementCreateSchema]] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enforces the human-in-the-loop requirement confirmation step:
    1. Updates requirement weights and mandatory flags if adjusted.
    2. Sets requirements_confirmed=True.
    3. Transitions Tender lifecycle from REVIEW_REQUIREMENTS -> READY_FOR_BIDDING.
    4. Emits an immutable audit log.
    """
    tender = db.query(TenderModel).filter(TenderModel.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if requirements:
        # Clear previous and replace with confirmed requirements
        db.query(RequirementModel).filter(RequirementModel.tender_id == tender.id).delete()
        for r_in in requirements:
            req_model = RequirementModel(
                tender_id=tender.id,
                module=r_in.module,
                title=r_in.title,
                mandatory=r_in.mandatory,
                weight=r_in.weight,
                rule_type=r_in.rule_type,
                rule_config_json=json.dumps(r_in.rule_config) if r_in.rule_config else None
            )
            db.add(req_model)

    tender.lifecycle_status = "READY_FOR_BIDDING"
    tender.requirements_confirmed = True

    audit = AuditEventModel(
        actor_id=f"OFFICER ({current_user.username})",
        event_type="TENDER_REQUIREMENTS_CONFIRMED",
        payload_json=f"Officer confirmed requirements for tender {tender.tender_number}. Status is now READY_FOR_BIDDING."
    )
    db.add(audit)

    db.commit()
    db.refresh(tender)

    return {
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "lifecycle_status": tender.lifecycle_status,
        "requirements_confirmed": tender.requirements_confirmed,
        "status": "SUCCESS",
        "message": "Tender requirements confirmed. Tender is now READY_FOR_BIDDING. Bidders can now be added."
    }


# --------------------------------------------------
# 4. LIST TENDERS (WITH USER / TENANT ISOLATION)
# --------------------------------------------------
@router.get("", response_model=List[TenderResponseSchema], summary="List All Active Tenders")
def list_tenders(
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all active published procurement tenders.
    Guarantees that tenders uploaded by Procurement Officers immediately appear for Bidder users
    to browse and submit proposal bundles.
    """
    query = db.query(TenderModel)
    return query.order_by(TenderModel.created_at.desc()).all()



# --------------------------------------------------
# 5. GET TENDER DETAILS BY ID
# --------------------------------------------------
@router.get("/{tender_id}", response_model=TenderResponseSchema, summary="Get Tender Details by ID")
def get_tender(tender_id: str, db: Session = Depends(get_db)):
    """Fetches full tender details and structured requirements for a given tender ID."""
    tender = db.query(TenderModel).filter(
        (TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


# --------------------------------------------------
# 6. GET TENDER LIFECYCLE & BATCH STATUS
# --------------------------------------------------
@router.get("/{tender_id}/lifecycle", summary="Get Tender Lifecycle & Bid Progress")
def get_tender_lifecycle_status(tender_id: str, db: Session = Depends(get_db)):
    """
    Returns real-time batch processing metrics:
    - Total submitted bids
    - Processed vs pending bids count
    - First-level screening breakdown (PASS, FAIL, REVIEW)
    - Transition readiness (ALL_BIDS_PROCESSED trigger)
    """
    tender = db.query(TenderModel).filter(
        (TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    bids = db.query(BidModel).filter(BidModel.tender_id == tender.id).all()
    total_bids = len(bids)
    processed_bids = sum(1 for b in bids if b.status in ("QUALIFIED", "DISQUALIFIED", "NEEDS_CLARIFICATION", "EVALUATED"))
    pending_bids = total_bids - processed_bids

    qualified_count = sum(1 for b in bids if b.status == "QUALIFIED" or b.screening_status == "PASS")
    disqualified_count = sum(1 for b in bids if b.status == "DISQUALIFIED" or b.screening_status == "FAIL")
    review_count = sum(1 for b in bids if b.status == "NEEDS_CLARIFICATION" or b.screening_status == "REVIEW")

    all_processed = (total_bids > 0 and pending_bids == 0)

    # Auto update tender state if all processed
    if all_processed and tender.lifecycle_status in ("BIDDING_IN_PROGRESS", "READY_FOR_BIDDING"):
        tender.lifecycle_status = "ALL_BIDS_PROCESSED"
        db.commit()

    return {
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "title": tender.title,
        "lifecycle_status": tender.lifecycle_status,
        "requirements_confirmed": tender.requirements_confirmed,
        "total_bids": total_bids,
        "processed_bids": processed_bids,
        "pending_bids": pending_bids,
        "screening_breakdown": {
            "qualified": qualified_count,
            "disqualified": disqualified_count,
            "needs_review": review_count
        },
        "all_bids_processed": all_processed,
        "can_proceed_to_comparative_review": (qualified_count > 0 or all_processed)
    }
