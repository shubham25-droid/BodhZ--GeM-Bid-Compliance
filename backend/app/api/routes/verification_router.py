from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.db_seeder import seed_initial_database
from app.models.models import (
    BidModel, RequirementModel, ExtractionModel, DocumentModel,
    VerificationResultModel, FindingModel, AssessmentModel, OfficerDecisionModel, AuditEventModel, UserModel, TenderModel
)
from app.core.security import get_current_user, get_optional_current_user
from app.schemas.schemas import OfficerDecisionCreateSchema, OfficerDecisionResponseSchema, ChatRequestSchema, ChatResponseSchema
from app.compliance_engine.compliance_engine import ComplianceEngine
from app.decision_support.decision_service import DecisionSupportService
from app.ai.chatbot_service import BodhZChatbotService

router = APIRouter(prefix="/bids", tags=["Compliance Verification & Decision Support"])
chatbot_service = BodhZChatbotService()


# --------------------------------------------------
# HYBRID AI CHATBOT API ENDPOINT (OPENAI + BODHZ SYSTEM CONTEXT)
# --------------------------------------------------
@router.post("/ai-chat", response_model=ChatResponseSchema, summary="Hybrid OpenAI & Context-Aware AI Chatbot Endpoint")
async def chat_with_bodhz_ai(
    chat_in: ChatRequestSchema,
    db: Session = Depends(get_db)
):
    """
    Backend-only endpoint for AI Chatbot interactions.
    
    Security & Architecture Rules:
    - Frontend NEVER communicates directly with OpenAI API.
    - OpenAI API key is kept 100% secure on the backend (.env).
    - Executes real backend database tools against live SQLite schema.
    - Synthesizes grounded prompt with Master System Prompt rules.
    - Returns structured reply from OpenAI model or BodhZ grounded engine.
    """
    # Ensure database is seeded with initial GeM records
    seed_initial_database(db)

    tender_data = chat_in.active_tender_data
    bidder_data = chat_in.active_bidder_data

    # Attempt to load tender from DB if tender_id provided
    if not tender_data and chat_in.tender_id:
        t_model = db.query(TenderModel).filter(
            (TenderModel.id == chat_in.tender_id) | (TenderModel.tender_number == chat_in.tender_id)
        ).first()
        if t_model:
            tender_data = {
                "id": t_model.id,
                "tender_number": t_model.tender_number,
                "title": t_model.title,
                "category": t_model.category
            }

    # Attempt to load bidder from DB if bidder_id provided
    if not bidder_data and chat_in.bidder_id:
        bid_model = db.query(BidModel).filter(BidModel.id == chat_in.bidder_id).first()
        if bid_model:
            assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == bid_model.id).order_by(AssessmentModel.created_at.desc()).first()
            ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == bid_model.id).all()
            
            modules = []
            for v in ver_results:
                modules.append({
                    "name": v.module,
                    "status": v.status,
                    "mode": v.verification_mode,
                    "source": "Verification Gateway",
                    "reason": f"Risk assessment: {v.risk}"
                })

            bidder_data = {
                "id": bid_model.id,
                "name": bid_model.bidder.legal_name if bid_model.bidder else "Unknown",
                "gstin": bid_model.bidder.gstin if bid_model.bidder else "N/A",
                "score": assessment.compliance_score if assessment else 0,
                "risk": assessment.risk_level if assessment else "UNKNOWN",
                "status": bid_model.status,
                "recommendation": assessment.ai_recommendation if assessment else "",
                "modules": modules
            }

    # Process message using Hybrid BodhZ Chatbot Service with DB Session
    res = await chatbot_service.process_chat_message(
        user_message=chat_in.message,
        db=db,
        active_tender=tender_data,
        active_bidder=bidder_data,
        conversation_history=chat_in.history,
        user_name=chat_in.user_name,
        user_role=chat_in.user_role,
        all_tenders=chat_in.all_tenders,
        all_bidders=chat_in.all_bidders
    )

    return ChatResponseSchema(
        reply=res["reply"],
        source=res["source"],
        model=res["model"]
    )


# --------------------------------------------------
# TRIGGER END-TO-END BID COMPLIANCE EVALUATION
# --------------------------------------------------
@router.post("/{bid_id}/evaluate", summary="Run Complete Verification & Compliance Evaluation Engine")
@router.post("/evaluate", summary="Run Complete Verification & Compliance Evaluation Engine (Query Param)")
async def evaluate_bid(bid_id: str, db: Session = Depends(get_db)):
    """
    Triggers complete integrated evaluation workflow:
    1. Loads tender requirements and extracted document evidence.
    2. Runs Verification Gateway adapters (GST, Udyam, PAN, OEM).
    3. Runs Cross-Document Inconsistency Detector.
    4. Calculates Compliance Score (0-100) & Risk Level (LOW, MEDIUM, HIGH, CRITICAL).
    5. Synthesizes Grounded AI Recommendation & persists results to database.
    """
    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    requirements_models = db.query(RequirementModel).filter(RequirementModel.tender_id == bid.tender_id).all()
    requirements = [
        {
            "id": r.id,
            "module": r.module,
            "title": r.title,
            "mandatory": r.mandatory,
            "weight": r.weight,
            "rule_type": r.rule_type
        }
        for r in requirements_models
    ]

    documents = db.query(DocumentModel).filter(DocumentModel.bid_id == bid.id).all()
    doc_ids = [d.id for d in documents]

    extractions_models = db.query(ExtractionModel).filter(ExtractionModel.document_id.in_(doc_ids)).all() if doc_ids else []
    extractions = [
        {
            "id": ext.id,
            "document_id": ext.document_id,
            "page_number": ext.page_number,
            "field_name": ext.field_name,
            "field_value": ext.field_value,
            "text_snippet": ext.text_snippet
        }
        for ext in extractions_models
    ]

    bidder_profile = {
        "legal_name": bid.bidder.legal_name if bid.bidder else "",
        "gstin": bid.bidder.gstin if bid.bidder else "",
        "pan_number": bid.bidder.pan_number if bid.bidder else "",
        "udyam_number": bid.bidder.udyam_number if bid.bidder else ""
    }

    engine = ComplianceEngine()
    ver_results = await engine.evaluate_bid_compliance(bidder_profile, requirements, extractions)

    assessment = DecisionSupportService.evaluate_and_persist_bid(db, bid, ver_results)

    return {
        "bid_id": bid.id,
        "compliance_score": assessment.compliance_score,
        "risk_level": assessment.risk_level,
        "ai_recommendation": assessment.ai_recommendation,
        "created_at": assessment.created_at,
        "verification_results_count": len(ver_results)
    }


# --------------------------------------------------
# GET DASHBOARD ASSESSMENT DETAILS
# --------------------------------------------------
@router.get("/{bid_id}/assessment", summary="Get Compliance Assessment & Dashboard Data")
def get_assessment_details(bid_id: str, db: Session = Depends(get_db)):
    """Fetches full compliance assessment, module verification cards, findings, and evidence references."""
    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == bid.id).order_by(AssessmentModel.created_at.desc()).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found for this bid. Run evaluation first.")

    ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == bid.id).all()

    modules_data = []
    all_findings = []

    for v in ver_results:
        findings = db.query(FindingModel).filter(FindingModel.verification_result_id == v.id).all()
        findings_list = []
        for f in findings:
            f_item = {
                "id": f.id,
                "module": v.module,
                "severity": f.severity,
                "code": f.code,
                "message": f.message
            }
            findings_list.append(f_item)
            all_findings.append(f_item)

        modules_data.append({
            "id": v.id,
            "requirement_id": v.requirement_id,
            "module": v.module,
            "status": v.status,
            "confidence": f"{int(v.confidence * 100)}%",
            "risk": v.risk,
            "verification_mode": v.verification_mode,
            "findings": findings_list
        })

    decision = db.query(OfficerDecisionModel).filter(OfficerDecisionModel.bid_id == bid.id).order_by(OfficerDecisionModel.timestamp.desc()).first()

    return {
        "bid_id": bid.id,
        "tender_number": bid.tender.tender_number if bid.tender else "",
        "bidder_name": bid.bidder.legal_name if bid.bidder else "",
        "gstin": bid.bidder.gstin if bid.bidder else "",
        "pan": bid.bidder.pan_number if bid.bidder else "",
        "udyam": bid.bidder.udyam_number if bid.bidder else "",
        "compliance_score": assessment.compliance_score,
        "risk_level": assessment.risk_level,
        "ai_recommendation": assessment.ai_recommendation,
        "verification_modules": modules_data,
        "findings": all_findings,
        "officer_decision": {
            "id": decision.id,
            "decision": decision.decision,
            "notes": decision.notes,
            "timestamp": decision.timestamp
        } if decision else None
    }


# --------------------------------------------------
# RECORD PROCUREMENT OFFICER DECISION
# --------------------------------------------------
@router.post("/officer-decision", response_model=OfficerDecisionResponseSchema, summary="Record Procurement Officer Final Decision")
def record_officer_decision(
    decision_in: OfficerDecisionCreateSchema,
    current_user: Optional[UserModel] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Records the human Procurement Officer's final qualification decision (QUALIFIED, DISQUALIFIED, NEEDS_CLARIFICATION, REJECTED)
    with audit justification notes. Updates bid status, lifecycle status to FINALIZED, and generates an immutable audit record.
    """
    if current_user and current_user.role == "BID_UPLOADER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Bid Uploaders are not authorized to make or record official procurement qualification decisions."
        )

    bid = db.query(BidModel).filter(BidModel.id == decision_in.bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    if current_user:
        officer_id = current_user.id
        officer_name = current_user.username
    else:
        officer = db.query(UserModel).filter(UserModel.role == "PROCUREMENT_OFFICER").first()
        officer_id = officer.id if officer else "OFFICER_DEFAULT"
        officer_name = officer.username if officer else "Procurement Officer"

    new_decision = OfficerDecisionModel(
        assessment_id=decision_in.assessment_id,
        bid_id=decision_in.bid_id,
        officer_id=officer_id,
        decision=decision_in.decision,
        notes=decision_in.notes
    )
    db.add(new_decision)
    bid.status = decision_in.decision
    bid.lifecycle_status = "FINALIZED"

    audit = AuditEventModel(
        bid_id=bid.id,
        actor_id=f"OFFICER ({officer_name})",
        event_type="OFFICER_FINAL_DECISION_RECORDED",
        payload_json=f"Officer recorded final decision '{decision_in.decision}'. Justification notes: {decision_in.notes or 'None'}"
    )
    db.add(audit)

    # Check if all bids under this tender are finalized
    if bid.tender:
        sibling_bids = db.query(BidModel).filter(BidModel.tender_id == bid.tender_id).all()
        if all(b.status in ("QUALIFIED", "DISQUALIFIED", "REJECTED") or b.id == bid.id for b in sibling_bids):
            bid.tender.lifecycle_status = "COMPLETED"

    db.commit()
    db.refresh(new_decision)
    return new_decision
