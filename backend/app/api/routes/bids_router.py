from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.models.models import (
    BidModel, BidderModel, TenderModel, AuditEventModel, AssessmentModel,
    VerificationResultModel, FindingModel, OfficerDecisionModel, UserModel,
    DocumentModel, ExtractionModel
)
from app.schemas.schemas import BidCreateSchema, BidResponseSchema

router = APIRouter(prefix="/bids", tags=["Bid Management & Comparative Review Layer"])


# --------------------------------------------------
# 1. CREATE BID SUBMISSION UNDER TENDER
# --------------------------------------------------
@router.post("", response_model=BidResponseSchema, status_code=status.HTTP_201_CREATED, summary="Create Bid Submission")
def create_bid(
    bid_in: BidCreateSchema,
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Registers a bidder profile (if not existing) and creates a bid submission
    linked to a specific GeM tender.
    """
    tender = db.query(TenderModel).filter(
        (TenderModel.id == bid_in.tender_id) | (TenderModel.tender_number == bid_in.tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    # Find or create Bidder
    bidder = db.query(BidderModel).filter(BidderModel.legal_name == bid_in.bidder.legal_name.strip()).first()
    if not bidder:
        bidder = BidderModel(
            legal_name=bid_in.bidder.legal_name.strip(),
            pan_number=bid_in.bidder.pan_number,
            gstin=bid_in.bidder.gstin,
            udyam_number=bid_in.bidder.udyam_number,
            email=bid_in.bidder.email
        )
        db.add(bidder)
        db.flush()

    # Create Bid
    new_bid = BidModel(
        tender_id=tender.id,
        bidder_id=bidder.id,
        status="SUBMITTED",
        lifecycle_status="UPLOADED",
        screening_status="PENDING"
    )
    db.add(new_bid)
    db.flush()

    actor = f"OFFICER ({current_user.username})" if current_user else "SYSTEM"

    # Create Audit Event
    audit = AuditEventModel(
        bid_id=new_bid.id,
        actor_id=actor,
        event_type="BID_SUBMITTED",
        payload_json=f"Bid submitted for tender '{tender.tender_number}' by bidder '{bidder.legal_name}'."
    )
    db.add(audit)

    # Transition tender lifecycle to BIDDING_IN_PROGRESS if ready
    if tender.lifecycle_status in ("READY_FOR_BIDDING", "DRAFT"):
        tender.lifecycle_status = "BIDDING_IN_PROGRESS"

    db.commit()
    db.refresh(new_bid)
    return new_bid


# --------------------------------------------------
# --------------------------------------------------
# 2. LIST BIDS / MY SUBMISSIONS (ROLE-AWARE)
# --------------------------------------------------
@router.get("/my-submissions", summary="Get Submissions for Authenticated Bidder")
def get_my_submissions(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns only the submissions and document verification status belonging to the authenticated bidder."""
    # Find matching bidder by organization name or username
    bidder = db.query(BidderModel).filter(
        (func.lower(BidderModel.legal_name) == func.lower(current_user.organization)) |
        (func.lower(BidderModel.legal_name).contains(current_user.username.lower()))
    ).first()

    if not bidder:
        # Fallback to the first bidder associated with user organization
        bidder = db.query(BidderModel).first()

    if not bidder:
        return {"submissions": []}

    bids = db.query(BidModel).filter(BidModel.bidder_id == bidder.id).all()
    results = []
    for b in bids:
        assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == b.id).order_by(AssessmentModel.created_at.desc()).first()
        ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == b.id).all()
        docs = db.query(DocumentModel).filter(DocumentModel.bid_id == b.id).all()

        results.append({
            "bid_id": b.id,
            "tender_id": b.tender_id,
            "tender_number": b.tender.tender_number if b.tender else "N/A",
            "tender_title": b.tender.title if b.tender else "N/A",
            "submission_date": b.submission_date.strftime("%d %b %Y %H:%M UTC") if b.submission_date else "N/A",
            "status": b.status,
            "lifecycle_status": b.lifecycle_status,
            "screening_status": b.screening_status,
            "compliance_score": assessment.compliance_score if assessment else None,
            "documents_count": len(docs),
            "verified_modules": [{"module": v.module, "status": v.status} for v in ver_results]
        })

    return {
        "bidder_name": bidder.legal_name,
        "gstin": bidder.gstin,
        "submissions_count": len(results),
        "submissions": results
    }


@router.get("", response_model=List[BidResponseSchema], summary="List All Bids")
def list_bids(tender_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieves all submitted bids, optionally filtered by tender ID."""
    query = db.query(BidModel)
    if tender_id:
        # Match by tender ID or tender number
        t = db.query(TenderModel).filter((TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)).first()
        t_id = t.id if t else tender_id
        query = query.filter(BidModel.tender_id == t_id)
    return query.order_by(BidModel.submission_date.desc()).all()


# --------------------------------------------------
# 3. FINAL COMPARATIVE MATRIX (OFFICER & AUDITOR ONLY)
# --------------------------------------------------
@router.get("/tenders/{tender_id:path}/comparative-matrix", summary="Get Final Comparative Review Table for All Bids")
def get_comparative_matrix(
    tender_id: str,
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates the official Comparative Evaluation Table for a Tender.
    Restricted: Bid Uploaders are forbidden from viewing competitors' comparative matrices.
    """
    if current_user and current_user.role == "BID_UPLOADER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Bid Uploaders cannot view competitors' comparative evaluation matrix."
        )

    tender = db.query(TenderModel).filter(
        (TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")


    bids = db.query(BidModel).filter(BidModel.tender_id == tender.id).all()
    matrix_rows = []

    for b in bids:
        assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == b.id).order_by(AssessmentModel.created_at.desc()).first()
        ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == b.id).all()
        decision = db.query(OfficerDecisionModel).filter(OfficerDecisionModel.bid_id == b.id).order_by(OfficerDecisionModel.timestamp.desc()).first()

        # Modules breakdown
        modules_summary = []
        missing_docs = []
        issues = []

        for v in ver_results:
            modules_summary.append({
                "module": v.module,
                "status": v.status,
                "risk": v.risk,
                "mode": v.verification_mode
            })
            if v.status == "FAIL":
                missing_docs.append(v.module)

            findings = db.query(FindingModel).filter(FindingModel.verification_result_id == v.id).all()
            for f in findings:
                if f.severity in ("WARNING", "CRITICAL", "ERROR"):
                    issues.append(f"[{v.module}] {f.message}")

        score_val = assessment.compliance_score if assessment else 0
        risk_val = assessment.risk_level if assessment else "UNKNOWN"
        screening = b.screening_status
        if screening == "PENDING" and assessment:
            if risk_val in ("LOW",) and score_val >= 80:
                screening = "PASS"
            elif risk_val in ("CRITICAL",) or score_val < 50:
                screening = "FAIL"
            else:
                screening = "REVIEW"

        matrix_rows.append({
            "bid_id": b.id,
            "bidder_id": b.bidder_id,
            "bidder_name": b.bidder.legal_name if b.bidder else "Unknown",
            "gstin": b.bidder.gstin if b.bidder else "N/A",
            "pan": b.bidder.pan_number if b.bidder else "N/A",
            "udyam": b.bidder.udyam_number if b.bidder else "N/A",
            "compliance_score": score_val,
            "risk_level": risk_val,
            "screening_status": screening,
            "lifecycle_status": b.lifecycle_status,
            "modules_status": modules_summary,
            "missing_mandatory_items": missing_docs,
            "review_issues": issues,
            "ai_recommendation": assessment.ai_recommendation if assessment else "Evaluation pending.",
            "officer_decision": {
                "decision": decision.decision,
                "notes": decision.notes,
                "timestamp": decision.timestamp,
                "officer_name": decision.officer.full_name if decision and decision.officer else "Procurement Officer"
            } if decision else None
        })

    return {
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "tender_title": tender.title,
        "total_bids": len(bids),
        "comparative_matrix": matrix_rows
    }


# --------------------------------------------------
# 4. GET SHORTLISTED / QUALIFIED BIDS
# --------------------------------------------------
@router.get("/tenders/{tender_id:path}/shortlisted", summary="Get Shortlisted Bids for Final Comparative Review")
def get_shortlisted_bids(tender_id: str, db: Session = Depends(get_db)):
    """Returns only technically qualified or reviewable shortlisted bids for final officer review."""
    tender = db.query(TenderModel).filter(
        (TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    full_matrix = get_comparative_matrix(tender.id, db)
    shortlisted = [
        row for row in full_matrix["comparative_matrix"]
        if row["screening_status"] in ("PASS", "REVIEW") or (row["compliance_score"] >= 60 and row["risk_level"] != "CRITICAL")
    ]

    return {
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "total_submitted_bids": full_matrix["total_bids"],
        "shortlisted_count": len(shortlisted),
        "shortlisted_bids": shortlisted
    }


# --------------------------------------------------
# 5. GET 5-YEAR HISTORICAL RECORD & COMPARISON
# --------------------------------------------------
@router.get("/{bid_id}/historical-record", summary="Get 5-Year Historical Resolution & Comparison")
def get_bid_historical_record(bid_id: str, db: Session = Depends(get_db)):
    """
    Retrieves repeat bidder memory across historical tenders (5+ years).
    Returns prior scores, previous evaluation outcomes, and key findings
    side-by-side with current tender evaluation without overriding current decision.
    """
    from app.decision_support.historical_service import HistoricalEntityResolver
    history_report = HistoricalEntityResolver.resolve_bidder_history(db, bid_id)
    return history_report


# --------------------------------------------------
# 6. GET BID DETAILS BY ID
# --------------------------------------------------
@router.get("/{bid_id}", response_model=BidResponseSchema, summary="Get Bid Details by ID")
def get_bid(bid_id: str, db: Session = Depends(get_db)):
    """Fetches submission status and profile for a specific bid ID."""
    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found")
    return bid
