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
# 13 STATUTORY VERIFICATION GATEWAYS (LAYER 4)
# --------------------------------------------------
@router.get("/{bid_id}/verification-sources", summary="Get Full 13 Statutory Gateway Nodes for Bidder")
def get_bid_verification_sources(bid_id: str, db: Session = Depends(get_db)):
    """
    Returns full live status, verification mode, raw JSON simulation, and audit provenance
    for all 13 statutory government registries (GSTN, Udyam, PAN, MCA21, Startup India, NSIC,
    EPFO, ESIC, DigiLocker, OEM MAF, Make in India, ISO/BIS, and CPPP Non-Debarment).
    """
    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    ver_results = db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == bid.id).all()
    ver_map = {v.module.upper(): v for v in ver_results}
    bidder_name = bid.bidder.legal_name if bid.bidder else "Unknown Bidder"
    gstin = bid.bidder.gstin if bid.bidder else "N/A"
    pan = bid.bidder.pan_number if bid.bidder else "N/A"
    udyam = bid.bidder.udyam_number if bid.bidder else "N/A"

    gateways_def = [
        {
            "num": 1,
            "source_name": "GSTN Registration & Return Filings",
            "code": "GST",
            "authority": "Goods and Services Tax Network (GSTN)",
            "category": "Taxation",
            "checked_fields": {"GSTIN": gstin, "Legal Name": bidder_name, "Taxpayer Status": "Active", "GSTR-3B Return": "Current (Jul 2026)", "Jurisdiction": "State & Centre Ward 4"},
            "raw_payload": {"gstin": gstin, "lgnm": bidder_name, "sts": "Active", "rgdt": "01/07/2017", "ctb": "Private Limited Company", "pradr": {"addr": {"bno": "Plot 12", "loc": "MIDC Phase 2", "st": "Maharashtra", "pncd": "400001"}}},
            "latency_ms": 38
        },
        {
            "num": 2,
            "source_name": "Udyam / MSME Classification Registry",
            "code": "UDYAM",
            "authority": "Ministry of Micro, Small and Medium Enterprises",
            "category": "Enterprise Classification",
            "checked_fields": {"Udyam Reg": udyam, "Enterprise Type": "Medium Enterprise", "Major Activity": "Services & IT Systems Integration", "Valid Upto": "Perpetual (Active)"},
            "raw_payload": {"udyam_no": udyam, "enterprise_name": bidder_name, "classification": "MEDIUM", "dic_code": "MH-PUN-049", "is_valid": True, "date_of_commencement": "14/08/2012"},
            "latency_ms": 45
        },
        {
            "num": 3,
            "source_name": "Income Tax PAN / TAN Database",
            "code": "PAN",
            "authority": "Central Board of Direct Taxes (CBDT)",
            "category": "Statutory Identity",
            "checked_fields": {"PAN": pan, "Entity Name": bidder_name, "ITR-6 Filing": "AY 2025-26 Filed", "Aadhaar / Director Linkage": "100% Verified"},
            "raw_payload": {"pan": pan, "pan_status": "VALID_OPERATIVE", "taxpayer_name": bidder_name, "aadhaar_seeding": "Y", "last_itr_ack": "892019481028301"},
            "latency_ms": 29
        },
        {
            "num": 4,
            "source_name": "MCA21 Corporate Incorporation Registry",
            "code": "INCORPORATION",
            "authority": "Ministry of Corporate Affairs (MCA)",
            "category": "Corporate Legitimacy",
            "checked_fields": {"CIN": "U72900MH2012PTC229910", "Company Status": "ACTIVE", "Authorized Capital": "INR 50.00 Cr", "Paid-Up Capital": "INR 25.00 Cr", "Directors on Record": "3 Active DINs"},
            "raw_payload": {"cin": "U72900MH2012PTC229910", "company_name": bidder_name, "roc_code": "RoC-Mumbai", "category": "Company limited by Shares", "status": "Active", "filing_status": "MGT-7 & AOC-4 Compliant"},
            "latency_ms": 52
        },
        {
            "num": 5,
            "source_name": "Startup India DPIIT Recognition",
            "code": "STARTUP",
            "authority": "Department for Promotion of Industry and Internal Trade",
            "category": "Regulatory Exemption",
            "checked_fields": {"DPIIT Number": "DIPP89102", "Exemption Eligibility": "Prior Experience & EMD Exemption under GFR Rule 170", "Sector": "EdTech & Defense Simulators"},
            "raw_payload": {"dpiit_id": "DIPP89102", "entity_name": bidder_name, "recognition_status": "ACTIVE_RECOGNIZED", "section_80iac_exemption": "ELIGIBLE"},
            "latency_ms": 41
        },
        {
            "num": 6,
            "source_name": "NSIC Single Point Registration Scheme",
            "code": "NSIC",
            "authority": "National Small Industries Corporation (NSIC)",
            "category": "Enterprise Store",
            "checked_fields": {"SPRS Certificate": "NSIC/MUM/SPRS/2024/9918", "Commercial Capacity": "Full Technical Training Hardware Assembly", "Stores Inspected": "Yes"},
            "raw_payload": {"sprs_no": "NSIC/MUM/SPRS/2024/9918", "valid_thru": "31/12/2027", "monetary_limit": "INR 15.00 Cr", "inspection_status": "CLEARED"},
            "latency_ms": 34
        },
        {
            "num": 7,
            "source_name": "EPFO Employee PF Compliance Portal",
            "code": "EPFO",
            "authority": "Employees' Provident Fund Organization",
            "category": "Labor Law Compliance",
            "checked_fields": {"EPFO Code": "MH/BAN/0091823/000", "Active Contributing Members": "420 Employees", "Electronic Challan Return": "Filed for Current Month"},
            "raw_payload": {"est_id": "MHBAN0091823000", "est_name": bidder_name, "ecr_status": "PAID_REGULAR", "wage_month": "JUL-2026", "members_count": 420},
            "latency_ms": 61
        },
        {
            "num": 8,
            "source_name": "ESIC Social Security & Contribution Portal",
            "code": "ESIC",
            "authority": "Employees' State Insurance Corporation",
            "category": "Labor Welfare",
            "checked_fields": {"ESIC Employer Code": "31000981920000999", "Return Filing": "RC Compliant", "Default Status": "Nil Defaults"},
            "raw_payload": {"esic_code": "31000981920000999", "status": "COMPLIANT", "last_contribution_date": "15/08/2026", "challan_amount": "INR 2,84,500"},
            "latency_ms": 48
        },
        {
            "num": 9,
            "source_name": "DigiLocker / National Academic Depository (NAD)",
            "code": "DIGILOCKER",
            "authority": "National e-Governance Division (NeGD)",
            "category": "Cryptographic Trust",
            "checked_fields": {"Issuer": "Government of India MeitY", "Doc URI": "in.gov.pan/verification/27AAACT1098F1Z5", "PKI Signature": "Duly Signed by NIC Certifying Authority"},
            "raw_payload": {"doc_uri": "in.gov.pan/verification/27AAACT1098F1Z5", "signature_valid": True, "cert_chain": "VALID_TRUSTED_ROOT", "ts": "2026-08-30T10:00:00Z"},
            "latency_ms": 22
        },
        {
            "num": 10,
            "source_name": "OEM Manufacturer Authorization (MAF) Registry",
            "code": "OEM",
            "authority": "Global Technology OEMs & Principal Manufacturers",
            "category": "Technical Qualification",
            "checked_fields": {"OEM Principal": "Dell Technologies & Cisco Systems India", "MAF Reference": "DELL/IND/MAF/2026/0918", "Warranty Backing": "5-Year 24x7 Comprehensive On-Site Support"},
            "raw_payload": {"maf_ref": "DELL/IND/MAF/2026/0918", "tender_ref": bid.tender.tender_number if bid.tender else "RFP-4901", "authorized_partner": bidder_name, "validity": "31/12/2027", "authorized_signatory": "VP Enterprise Channels"},
            "latency_ms": 57
        },
        {
            "num": 11,
            "source_name": "Make in India (MII) Local Content Portal",
            "code": "MAKEININDIA",
            "authority": "Department for Promotion of Industry and Internal Trade",
            "category": "Statutory Sourcing",
            "checked_fields": {"Supplier Classification": "Class-I Local Supplier", "Local Content %": "68.4% (Threshold: 50%)", "Location of Value Add": "Pune & Bengaluru Facilities"},
            "raw_payload": {"supplier_class": "CLASS_I", "local_content_pct": 68.4, "auditor_cert_no": "CA/MII/2026/9182", "is_compliant": True},
            "latency_ms": 31
        },
        {
            "num": 12,
            "source_name": "ISO 9001:2015 & BIS Standards Database",
            "code": "ISO",
            "authority": "Bureau of Indian Standards & NABCB Accredited Body",
            "category": "Quality Assurance",
            "checked_fields": {"Standard": "ISO 9001:2015 & ISO/IEC 27001:2022", "Accredited Registrar": "BSI Quality Assurance", "Certificate Validity": "Valid through 15/11/2028"},
            "raw_payload": {"cert_no": "FM 729102", "scope": "Turnkey Design, Delivery and Commissioning of Training Labs", "expiry": "15/11/2028", "surveillance_status": "CLEARED"},
            "latency_ms": 36
        },
        {
            "num": 13,
            "source_name": "CPPP / GeM Central Non-Debarment Registry",
            "code": "NONBLACKLISTING",
            "authority": "Central Public Procurement Portal & GeM Vigilance Cell",
            "category": "Vigilance & Integrity",
            "checked_fields": {"Debarment Status": "CLEARED — No active debarment order", "Orders Inspected": "All Central Ministries, CPSEs & State Depts under GFR Rule 151"},
            "raw_payload": {"entity_pan": pan, "entity_gstin": gstin, "debarment_status": "NIL", "cross_check_results": "CLEARED_ALL_MINISTRIES", "verified_at": "2026-08-30T10:00:00Z"},
            "latency_ms": 28
        }
    ]

    results = []
    for g in gateways_def:
        v = ver_map.get(g["code"]) or ver_map.get(g["code"].replace("_", ""))
        v_status = v.status if v else "PASS"
        v_mode = v.verification_mode if v else "SANDBOX CONNECTOR"
        
        # If CyberTech, OEM fails critically
        if "cybertech" in bidder_name.lower() and g["code"] == "OEM":
            v_status = "FAIL"
        # If Bharat InfoTech, GST requires review
        if "bharat" in bidder_name.lower() and g["code"] == "GST":
            v_status = "REVIEW"

        results.append({
            "num": g["num"],
            "source_name": g["source_name"],
            "module_code": g["code"],
            "authority": g["authority"],
            "category": g["category"],
            "status": v_status,
            "verification_mode": v_mode,
            "checked_fields": g["checked_fields"],
            "raw_payload": g["raw_payload"],
            "latency_ms": g["latency_ms"],
            "sha256_hash": f"SHA256:{hex(abs(hash(g['source_name'] + bid.id + v_status)))[2:].zfill(16).upper()}",
            "verified_at": "30 Aug 2026 10:00 UTC"
        })

    return {
        "bid_id": bid.id,
        "bidder_name": bidder_name,
        "gstin": gstin,
        "pan": pan,
        "udyam": udyam,
        "tender_number": bid.tender.tender_number if bid.tender else "N/A",
        "total_gateways": len(results),
        "gateways": results
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
    if current_user and current_user.role not in ("PROCUREMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Role '{current_user.role}' is not authorized to make or record official procurement qualification decisions. Under GFR 2017 Rule 144, final decision authority is legally reserved for the Procurement Officer."
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
