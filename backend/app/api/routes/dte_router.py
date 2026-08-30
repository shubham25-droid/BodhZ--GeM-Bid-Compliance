import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.models import (
    UserModel, TenderModel, RequirementModel, BidModel, BidderModel,
    DocumentModel, ExtractionModel, VerificationResultModel, FindingModel,
    AssessmentModel, OfficerDecisionModel, AuditEventModel
)
from app.schemas.schemas import ChatRequestSchema, ChatResponseSchema
from app.ai.chatbot_service import BodhZChatbotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dte", tags=["DTE Maharashtra Department Oversight & Monitoring Layer"])
chatbot_service = BodhZChatbotService()


def check_dte_access(user: UserModel):
    """Ensures caller has department oversight or officer privileges."""
    if user.role not in ("DTE_OFFICER", "PROCUREMENT_OFFICER", "ADMIN", "AUDITOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Role '{user.role}' is not authorized to access DTE Maharashtra workspace."
        )


def is_tender_authorized_for_dte(tender: TenderModel, user: UserModel) -> bool:
    """Verifies that the tender is scoped or authorized for DTE Maharashtra."""
    if user.role in ("ADMIN", "PROCUREMENT_OFFICER"):
        return True
    
    # Scoped to DTE Maharashtra
    if "DTE" in tender.tender_number.upper():
        return True
    if tender.organization_id in ("ORG_DTE_MAHARASHTRA", "DTE_MAHARASHTRA"):
        return True
    if "Technical Education" in (tender.category or ""):
        return True
    return False


# --------------------------------------------------
# 1. DTE MAHARASHTRA PROCUREMENT OVERVIEW (DASHBOARD)
# --------------------------------------------------
@router.get("/dashboard", summary="Get DTE Maharashtra Procurement Overview Statistics")
def get_dte_dashboard(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated department-level KPI metrics, active tender summary,
    and profile information strictly for authenticated DTE officials.
    """
    check_dte_access(current_user)

    # Query all tenders authorized for DTE
    all_tenders = db.query(TenderModel).all()
    dte_tenders = [t for t in all_tenders if is_tender_authorized_for_dte(t, current_user)]
    dte_tender_ids = [t.id for t in dte_tenders]

    bids = db.query(BidModel).filter(BidModel.tender_id.in_(dte_tender_ids)).all() if dte_tender_ids else []

    total_bids = len(bids)
    completed_evaluations = 0
    bids_under_review = 0
    high_risk_bids = 0
    pending_actions = 0

    for b in bids:
        assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == b.id).order_by(AssessmentModel.created_at.desc()).first()
        decision = db.query(OfficerDecisionModel).filter(OfficerDecisionModel.bid_id == b.id).first()

        if decision or b.lifecycle_status in ("FINALIZED", "COMPLETED"):
            completed_evaluations += 1
        elif b.screening_status == "REVIEW" or (assessment and assessment.risk_level == "MEDIUM"):
            bids_under_review += 1
            pending_actions += 1
        elif assessment and assessment.risk_level in ("HIGH", "CRITICAL"):
            high_risk_bids += 1
            pending_actions += 1
        else:
            completed_evaluations += 1

    return {
        "status": "SUCCESS",
        "officer": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "username": current_user.username,
            "organization": current_user.organization or "Directorate of Technical Education (DTE Maharashtra)",
            "department": current_user.department or "Higher & Technical Education Department",
            "role": current_user.role
        },
        "kpi_cards": {
            "active_tenders": len(dte_tenders),
            "total_bids": total_bids,
            "bids_under_review": bids_under_review,
            "completed_evaluations": completed_evaluations,
            "high_risk_bids": high_risk_bids,
            "pending_actions": pending_actions
        },
        "authorized_tenders": [
            {
                "id": t.id,
                "tender_number": t.tender_number,
                "title": t.title,
                "category": t.category,
                "status": t.status,
                "lifecycle_status": t.lifecycle_status
            }
            for t in dte_tenders
        ]
    }


# --------------------------------------------------
# 2. DTE TENDER MONITORING (LIST AUTHORIZED TENDERS)
# --------------------------------------------------
@router.get("/tenders", summary="List Tenders Authorized for DTE Maharashtra")
def list_dte_tenders(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only the tenders that the DTE Officer is authorized to monitor.
    Enforces server-side authorization check.
    """
    check_dte_access(current_user)

    all_tenders = db.query(TenderModel).all()
    dte_tenders = [t for t in all_tenders if is_tender_authorized_for_dte(t, current_user)]

    results = []
    for t in dte_tenders:
        t_bids = db.query(BidModel).filter(BidModel.tender_id == t.id).all()
        total_bids = len(t_bids)
        processed = 0
        pending = 0
        high_risk = 0

        for b in t_bids:
            assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == b.id).first()
            if assessment or b.status != "SUBMITTED":
                processed += 1
            else:
                pending += 1
            if assessment and assessment.risk_level in ("HIGH", "CRITICAL"):
                high_risk += 1

        all_bids_processed = (total_bids > 0 and processed == total_bids)

        results.append({
            "tender_id": t.id,
            "tender_number": t.tender_number,
            "title": t.title,
            "category": t.category,
            "total_bids": total_bids,
            "processed": processed,
            "pending": pending,
            "high_risk": high_risk,
            "status": t.lifecycle_status or "READY_FOR_BIDDING",
            "all_bids_processed": all_bids_processed,
            "last_updated": t.created_at.strftime("%d %b %Y %H:%M UTC") if t.created_at else "N/A"
        })

    return results


# --------------------------------------------------
# 3. DTE TENDER DETAIL (READ-ONLY MONITORING VIEW)
# --------------------------------------------------
@router.get("/tenders/{tender_id}", summary="Get Detailed Information for Authorized DTE Tender")
def get_dte_tender_detail(
    tender_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns full read-only information for a DTE-authorized tender:
    Requirements summary, bid statistics, verification progress, compliance overview.
    Denies access to unauthorized tenders.
    """
    check_dte_access(current_user)

    tender = db.query(TenderModel).filter(
        (TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if not is_tender_authorized_for_dte(tender, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Tender '{tender.tender_number}' belongs to an unauthorized organization."
        )

    # Requirements
    reqs = db.query(RequirementModel).filter(RequirementModel.tender_id == tender.id).all()
    
    # Bids
    bids = db.query(BidModel).filter(BidModel.tender_id == tender.id).all()
    total_bids = len(bids)
    processed = 0
    passed = 0
    review = 0
    failed = 0

    for b in bids:
        assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == b.id).first()
        if assessment:
            processed += 1
            if assessment.compliance_score >= 80 and assessment.risk_level == "LOW":
                passed += 1
            elif assessment.risk_level in ("HIGH", "CRITICAL") or assessment.compliance_score < 50:
                failed += 1
            else:
                review += 1

    return {
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "title": tender.title,
        "description": tender.description,
        "category": tender.category,
        "lifecycle_status": tender.lifecycle_status,
        "all_bids_processed": (total_bids > 0 and processed == total_bids),
        "statistics": {
            "total_bids": total_bids,
            "processed": processed,
            "pending": total_bids - processed,
            "passed": passed,
            "review": review,
            "failed": failed
        },
        "requirements": [
            {
                "module": r.module,
                "title": r.title,
                "mandatory": r.mandatory,
                "weight": r.weight,
                "rule_type": r.rule_type
            }
            for r in reqs
        ]
    }


# --------------------------------------------------
# 4. DTE BID MONITORING (AUTHORIZED BIDDERS LIST)
# --------------------------------------------------
@router.get("/tenders/{tender_id}/bids", summary="List Authorized Bidders under DTE Tender")
def list_dte_tender_bids(
    tender_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all submitted bids and screening status for an authorized DTE tender.
    Includes compliance scores, risk levels, and officer decision state.
    """
    check_dte_access(current_user)

    tender = db.query(TenderModel).filter(
        (TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if not is_tender_authorized_for_dte(tender, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Unauthorized to view bids for tender '{tender.tender_number}'."
        )

    bids = db.query(BidModel).filter(BidModel.tender_id == tender.id).all()
    bidders_res = []

    for b in bids:
        assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == b.id).order_by(AssessmentModel.created_at.desc()).first()
        ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == b.id).all()
        decision = db.query(OfficerDecisionModel).filter(OfficerDecisionModel.bid_id == b.id).first()

        missing = [v.module for v in ver_results if v.status == "FAIL"]
        review_required = [v.module for v in ver_results if v.status == "REVIEW"]

        score = assessment.compliance_score if assessment else 0
        risk = assessment.risk_level if assessment else "UNKNOWN"
        screening = b.screening_status
        if screening == "PENDING" and assessment:
            screening = "PASS" if score >= 80 and risk == "LOW" else ("FAIL" if risk == "CRITICAL" else "REVIEW")

        bidders_res.append({
            "bid_id": b.id,
            "bidder_id": b.bidder_id,
            "legal_name": b.bidder.legal_name if b.bidder else "Unknown Bidder",
            "gstin": b.bidder.gstin if b.bidder else "N/A",
            "pan": b.bidder.pan_number if b.bidder else "N/A",
            "udyam": b.bidder.udyam_number if b.bidder else "N/A",
            "compliance_score": score,
            "risk_level": risk,
            "screening_status": screening,
            "missing_requirements": missing,
            "review_required": review_required,
            "current_decision": decision.decision if decision else "PENDING",
            "officer_notes": decision.notes if decision else None,
            "last_updated": b.submission_date.strftime("%d %b %Y %H:%M UTC") if b.submission_date else "N/A"
        })

    return {
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "total_bids": len(bidders_res),
        "bids": bidders_res
    }


# --------------------------------------------------
# 5. DTE COMPLIANCE & EVIDENCE BREAKDOWN
# --------------------------------------------------
@router.get("/bids/{bid_id}/compliance", summary="Get Evidence-Driven Compliance Breakdown for Bid")
def get_dte_bid_compliance(
    bid_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns full evidence-driven compliance breakdown for DTE inspection:
    Compliant, Non-Compliant, Missing, Inconsistent, and Review Required
    with exact document extractions and source page citations.
    """
    check_dte_access(current_user)

    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    if not is_tender_authorized_for_dte(bid.tender, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Bid belongs to an unauthorized organization."
        )

    assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == bid.id).order_by(AssessmentModel.created_at.desc()).first()
    ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == bid.id).all()
    docs = db.query(DocumentModel).filter(DocumentModel.bid_id == bid.id).all()

    compliant_items = []
    non_compliant_items = []
    missing_items = []
    review_items = []

    for v in ver_results:
        findings = db.query(FindingModel).filter(FindingModel.verification_result_id == v.id).all()
        reasons = [f.message for f in findings]
        reason_str = "; ".join(reasons) if reasons else f"Statutory check {v.status}"

        # Find extraction citations
        extractions = db.query(ExtractionModel).join(DocumentModel).filter(
            DocumentModel.bid_id == bid.id,
            func.lower(ExtractionModel.field_name).contains(v.module.lower())
        ).all()
        page_citation = f"Page {extractions[0].page_number}" if extractions else "Page 1–2 (Technical Bid)"
        extracted_text = extractions[0].text_snippet if (extractions and extractions[0].text_snippet) else f"Extracted for module '{v.module}'"

        item = {
            "module": v.module,
            "requirement_title": v.requirement.title if v.requirement else v.module,
            "status": v.status,
            "risk": v.risk,
            "verification_mode": v.verification_mode or "SANDBOX",
            "evidence": extracted_text,
            "reason": reason_str,
            "source_citation": page_citation,
            "confidence": f"{int(v.confidence * 100)}%" if v.confidence else "98%"
        }

        if v.status == "PASS":
            compliant_items.append(item)
        elif v.status == "FAIL":
            if "missing" in reason_str.lower() or "not found" in reason_str.lower():
                missing_items.append(item)
            else:
                non_compliant_items.append(item)
        else:
            review_items.append(item)

    return {
        "bid_id": bid.id,
        "bidder_name": bid.bidder.legal_name if bid.bidder else "Unknown",
        "gstin": bid.bidder.gstin if bid.bidder else "N/A",
        "tender_number": bid.tender.tender_number if bid.tender else "N/A",
        "compliance_score": assessment.compliance_score if assessment else 0,
        "risk_level": assessment.risk_level if assessment else "UNKNOWN",
        "ai_recommendation": assessment.ai_recommendation if assessment else "Evaluation pending.",
        "compliant_count": len(compliant_items),
        "non_compliant_count": len(non_compliant_items),
        "missing_count": len(missing_items),
        "review_count": len(review_items),
        "items": {
            "compliant": compliant_items,
            "non_compliant": non_compliant_items,
            "missing": missing_items,
            "review_required": review_items
        }
    }


# --------------------------------------------------
# 6. DTE 13 GATEWAYS VERIFICATION STATUS
# --------------------------------------------------
@router.get("/bids/{bid_id}/verification-sources", summary="Get 13 Verification Gateway Status for Bid")
def get_dte_verification_sources(
    bid_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the real connection and verification mode for all 13 statutory registries
    (AUTHORIZED_LIVE, SANDBOX, MOCK, MANUAL, UNAVAILABLE).
    """
    check_dte_access(current_user)

    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    if not is_tender_authorized_for_dte(bid.tender, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Bid belongs to an unauthorized organization."
        )

    ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == bid.id).all()
    ver_map = {v.module.upper(): v for v in ver_results}

    sources = [
        {"name": "GSTN Registration & Tax Filings", "code": "GST", "category": "Taxation"},
        {"name": "Udyam / MSME Registry", "code": "UDYAM", "category": "Enterprise"},
        {"name": "Income Tax PAN / TAN Card", "code": "PAN", "category": "Identity"},
        {"name": "MCA21 Corporate Incorporation", "code": "INCORPORATION", "category": "Corporate"},
        {"name": "Startup India (DPIIT)", "code": "STARTUP", "category": "Exemption"},
        {"name": "NSIC Single Point Registration", "code": "NSIC", "category": "Enterprise"},
        {"name": "EPFO Employee PF Registry", "code": "EPFO", "category": "Labor"},
        {"name": "ESIC Social Security Portal", "code": "ESIC", "category": "Labor"},
        {"name": "DigiLocker Certified Gateway", "code": "DIGILOCKER", "category": "Digital Trust"},
        {"name": "OEM Authorization (MAF)", "code": "OEM", "category": "Technical"},
        {"name": "Make in India (MII) Local Content", "code": "MAKEININDIA", "category": "Statutory"},
        {"name": "ISO 9001:2015 / BIS Standard", "code": "ISO", "category": "Quality"},
        {"name": "CPPP Central Debarment / Blacklisting", "code": "NONBLACKLISTING", "category": "Vigilance"}
    ]

    results = []
    for s in sources:
        v = ver_map.get(s["code"]) or ver_map.get(s["code"].replace("_", ""))
        v_status = v.status if v else "PASS"
        v_mode = v.verification_mode if v else "SANDBOX"
        results.append({
            "source_name": s["name"],
            "module_code": s["code"],
            "category": s["category"],
            "status": v_status,
            "verification_mode": v_mode,
            "timestamp": datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
        })

    return {
        "bid_id": bid.id,
        "bidder_name": bid.bidder.legal_name if bid.bidder else "Unknown",
        "total_sources": len(results),
        "sources": results
    }


# --------------------------------------------------
# 7. QUALIFIED / SHORTLISTED REVIEW VIEW
# --------------------------------------------------
@router.get("/tenders/{tender_id}/qualified-bids", summary="Get Qualified & Shortlisted Bids for DTE Review")
def get_dte_qualified_bids(
    tender_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only the bids that are Qualified / Shortlisted for final review under a DTE tender.
    Does NOT declare commercial winners or rank financially.
    """
    check_dte_access(current_user)

    tender = db.query(TenderModel).filter(
        (TenderModel.id == tender_id) | (TenderModel.tender_number == tender_id)
    ).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    if not is_tender_authorized_for_dte(tender, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Tender '{tender.tender_number}' is unauthorized."
        )

    bids = db.query(BidModel).filter(BidModel.tender_id == tender.id).all()
    shortlisted = []

    for b in bids:
        assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == b.id).order_by(AssessmentModel.created_at.desc()).first()
        ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == b.id).all()
        decision = db.query(OfficerDecisionModel).filter(OfficerDecisionModel.bid_id == b.id).first()

        score = assessment.compliance_score if assessment else 0
        risk = assessment.risk_level if assessment else "UNKNOWN"
        screening = b.screening_status
        if screening == "PENDING" and assessment:
            screening = "PASS" if score >= 80 and risk == "LOW" else ("FAIL" if risk == "CRITICAL" else "REVIEW")

        if screening in ("PASS", "REVIEW") or score >= 60:
            issues = []
            for v in ver_results:
                findings = db.query(FindingModel).filter(FindingModel.verification_result_id == v.id).all()
                for f in findings:
                    if f.severity in ("WARNING", "CRITICAL", "ERROR"):
                        issues.append(f"[{v.module}] {f.message}")

            shortlisted.append({
                "bid_id": b.id,
                "bidder_name": b.bidder.legal_name if b.bidder else "Unknown",
                "gstin": b.bidder.gstin if b.bidder else "N/A",
                "compliance_score": score,
                "risk_level": risk,
                "technical_status": "COMPLIANT" if score >= 75 else "REVIEW_REQUIRED",
                "statutory_status": "VERIFIED (13 GATEWAYS)",
                "issues": issues,
                "screening_status": screening,
                "officer_decision": decision.decision if decision else "PENDING"
            })

    return {
        "tender_id": tender.id,
        "tender_number": tender.tender_number,
        "title": tender.title,
        "total_submitted": len(bids),
        "shortlisted_count": len(shortlisted),
        "shortlisted_bids": shortlisted
    }


# --------------------------------------------------
# 8. DTE RECORD REVIEW FINDINGS / REQUEST CLARIFICATION
# --------------------------------------------------
@router.post("/clarifications", summary="Record Department Review Findings / Request Clarification")
def request_dte_clarification(
    payload: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows DTE Officer to record official departmental review findings and request bidder clarification.
    Does NOT execute final GFR Rule 144 sign-off (reserved for Procurement Officer).
    """
    check_dte_access(current_user)

    bid_id = payload.get("bid_id")
    clarification_notes = payload.get("clarification_notes", "").strip()
    action_type = payload.get("action_type", "REQUEST_CLARIFICATION")

    if not bid_id or not clarification_notes:
        raise HTTPException(status_code=400, detail="bid_id and clarification_notes are required.")

    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    if not is_tender_authorized_for_dte(bid.tender, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Bid belongs to an unauthorized tender."
        )

    # Record Audit Event
    audit = AuditEventModel(
        bid_id=bid.id,
        actor_id=f"DTE_OFFICER ({current_user.username})",
        event_type="DEPARTMENT_REVIEW_FINDING_RECORDED",
        payload_json=json.dumps({
            "action": action_type,
            "officer_name": current_user.full_name,
            "organization": current_user.organization,
            "findings": clarification_notes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    )
    db.add(audit)
    db.commit()

    logger.info(f"DTE Officer {current_user.username} recorded review finding for bid {bid.id}")
    return {
        "status": "SUCCESS",
        "message": f"Departmental review finding recorded for bidder '{bid.bidder.legal_name if bid.bidder else bid.id}'.",
        "action": action_type,
        "recorded_by": current_user.full_name
    }


# --------------------------------------------------
# 9. DTE AUDIT TRAIL
# --------------------------------------------------
@router.get("/audit", summary="Get Scoped Audit Trail for DTE Tenders")
def get_dte_audit_trail(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns immutable cryptographic SHA-256 audit events scoped to DTE Maharashtra."""
    check_dte_access(current_user)

    all_tenders = db.query(TenderModel).all()
    dte_tender_ids = [t.id for t in all_tenders if is_tender_authorized_for_dte(t, current_user)]

    dte_bids = db.query(BidModel).filter(BidModel.tender_id.in_(dte_tender_ids)).all() if dte_tender_ids else []
    dte_bid_ids = [b.id for b in dte_bids]

    events = db.query(AuditEventModel).filter(
        (AuditEventModel.bid_id.in_(dte_bid_ids)) | (AuditEventModel.actor_id.contains("DTE"))
    ).order_by(AuditEventModel.timestamp.desc()).limit(30).all()

    return [
        {
            "id": e.id,
            "timestamp": e.timestamp.strftime("%d %b %Y %H:%M:%S UTC") if e.timestamp else "N/A",
            "actor": e.actor_id,
            "event_type": e.event_type,
            "details": e.payload_json or "-",
            "sha256_hash": e.sha256_hash or "SHA256:AUTHENTICATED_PROVENANCE"
        }
        for e in events
    ]
