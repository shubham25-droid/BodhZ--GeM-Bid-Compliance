import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import hash_password
from app.models.models import (
    UserModel, TenderModel, RequirementModel, BidderModel, BidModel,
    DocumentModel, ExtractionModel, VerificationResultModel, FindingModel,
    AssessmentModel, AuditEventModel, HistoricalBidderMatchModel
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# COMPREHENSIVE INITIAL DATABASE SEEDER (REAL GOVT RFPs)
# --------------------------------------------------
def seed_initial_database(db: Session):
    """
    Populates authentic Indian Government, State, and CPSE procurement tenders into SQLite:
    1. DTE Maharashtra — Center of Excellence (COE) & Technical Training RFP
    2. National Fertilizers Limited (NFL / CPSE) — Web App Security Audit & VAPT
    3. ICAR-IIMR — Agricultural Machinery (Seed Drill & Multi-Millet Thresher)
    """
    # 1. SEED USERS WITH OFFICIAL PROFESSIONAL PROFILES
    demo_users = [
        {
            "username": "shubham",
            "email": "shubham@gem.gov.in",
            "password": "BodhZ@2026",
            "full_name": "Officer Shubham (Senior Procurement Officer)",
            "role": "PROCUREMENT_OFFICER",
            "organization": "Government e-Marketplace (GeM)",
            "department": "Public Procurement & Compliance Division",
            "phone": "+91 98765 43210"
        },
        {
            "username": "bidder_tata",
            "email": "rajiv.mehta@tatasystems.com",
            "password": "Bidder@2026",
            "full_name": "Rajiv Mehta (Authorized Bid Representative)",
            "role": "BID_UPLOADER",
            "organization": "Tata Advanced Training & Systems Ltd",
            "department": "Govt & PSU Bidding Division",
            "phone": "+91 98222 33445"
        },
        {
            "username": "officer_dte",
            "email": "officer.dte@dte.maharashtra.gov.in",
            "password": "Dte@2026",
            "full_name": "Dr. Rajesh Kumar (State Technical Education Officer)",
            "role": "DTE_OFFICER",
            "organization": "Directorate of Technical Education (DTE Maharashtra)",
            "department": "Higher & Technical Education Department",
            "phone": "+91 98111 22233"
        },
        {
            "username": "auditor1",
            "email": "auditor1@cag.gov.in",
            "password": "Auditor@2026",
            "full_name": "Priya Sharma (Principal Procurement Auditor)",
            "role": "AUDITOR",
            "organization": "Comptroller & Auditor General (CAG)",
            "department": "Public Procurement Audit Directorate",
            "phone": "+91 98444 55566"
        }
    ]

    primary_user = None
    for u in demo_users:
        existing_user = db.query(UserModel).filter(func.lower(UserModel.username) == u["username"].lower()).first()
        if not existing_user:
            new_u = UserModel(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                organization=u.get("organization", "GeM"),
                department=u.get("department", "Procurement"),
                phone=u.get("phone", ""),
                is_active=True,
                email_verified=True
            )
            db.add(new_u)
            db.flush()
            if u["username"] == "shubham":
                primary_user = new_u
        else:
            # Sync metadata & role
            existing_user.role = u["role"]
            existing_user.full_name = u["full_name"]
            existing_user.organization = u["organization"]
            existing_user.department = u["department"]
            existing_user.hashed_password = hash_password(u["password"])
            if u["username"] == "shubham":
                primary_user = existing_user
    db.commit()

    if not primary_user:
        primary_user = db.query(UserModel).first()

    # 2. SEED REAL-WORLD GOVERNMENT TENDERS
    tenders_data = [
        {
            "number": "DTE/2026/RFP/COE/4901",
            "title": "Establishment, Operationalization & Maintenance of Center of Excellence (COE) and Technical Training Centers",
            "desc": "RFP for selection of agency for setting up Center of Excellence & technical training facilities across State Government engineering institutes under DTE Maharashtra.",
            "category": "Technical Education & Skill Infrastructure",
            "lifecycle_status": "ALL_BIDS_PROCESSED",
            "rules": [
                {"module": "GST", "title": "Active GSTIN Registration Certificate & GSTR-3B Monthly Return Compliance", "mandatory": True, "weight": 15, "rule_type": "GATEWAY_STATUS"},
                {"module": "PAN", "title": "Income Tax PAN / TAN Card Validity & Legal Name Match", "mandatory": True, "weight": 10, "rule_type": "IDENTITY_MATCH"},
                {"module": "Incorporation", "title": "Certificate of Incorporation (Companies Act 1956/2013 / LLP Act 2008) with Registered/Regional Office in Maharashtra", "mandatory": True, "weight": 10, "rule_type": "DOCUMENT_CONSISTENCY"},
                {"module": "Turnover", "title": "CA Certified Minimum Average Annual Turnover of INR 10 Crores during last 3 Audited Financial Years (FY 20-21, 21-22, 22-23)", "mandatory": True, "weight": 15, "rule_type": "FINANCIAL_THRESHOLD"},
                {"module": "PastExperience", "title": "Similar COE / Technical Training Center Project Execution in last 5 Years (1x ₹5.0 Cr or 2x ₹2.5 Cr or 3x ₹2.0 Cr)", "mandatory": True, "weight": 15, "rule_type": "DOCUMENT_CONSISTENCY"},
                {"module": "NetWorth", "title": "CA Certificate for Positive Net Worth during last 3 Audited Financial Years", "mandatory": True, "weight": 10, "rule_type": "FINANCIAL_THRESHOLD"},
                {"module": "OEM", "title": "Manufacturer Authorization Form (MAF) from all Hardware & Software Technology Partners (Annexure-8)", "mandatory": True, "weight": 10, "rule_type": "DOCUMENT_CONSISTENCY"},
                {"module": "ISO", "title": "Valid ISO 9001:2015 (Quality Management System) Certificate", "mandatory": True, "weight": 5, "rule_type": "DOCUMENT_CONSISTENCY"},
                {"module": "EPFO_ESIC", "title": "Minimum 6 Full-Time Payroll Staff with PF/PT Numbers including Minimum 3 OEM Certified Trainers", "mandatory": True, "weight": 5, "rule_type": "GATEWAY_STATUS"},
                {"module": "NonBlacklisting", "title": "Self-Certification on Company Letterhead for Not Being Blacklisted / Debarred", "mandatory": True, "weight": 5, "rule_type": "STATUTORY_DECLARATION"}
            ]
        },
        {
            "number": "NFL/CO/IT/VAPT/2026/08",
            "title": "Comprehensive Cyber Security Audit & VAPT of Web Applications and Data Center Infrastructure",
            "desc": "NIT by National Fertilizers Limited (NFL / Central PSU) for Vulnerability Assessment, Penetration Testing (VAPT) and Security Audit of Web Applications, APIs and Data Center.",
            "category": "Cyber Security & IT Security Audit",
            "lifecycle_status": "READY_FOR_BIDDING",
            "rules": [
                {"module": "CERT_IN", "title": "Valid CERT-In Empanelled Organization Certificate as on Bid Submission Date", "mandatory": True, "weight": 20, "rule_type": "STATUTORY_AUTHORIZATION"},
                {"module": "GST", "title": "Active GST Registration Certificate & Timely Tax Filing", "mandatory": True, "weight": 15, "rule_type": "GATEWAY_STATUS"},
                {"module": "PAN", "title": "Permanent Account Number (PAN) Issued by Income Tax Dept", "mandatory": True, "weight": 10, "rule_type": "IDENTITY_MATCH"},
                {"module": "EPFO_ESIC", "title": "P.F. Registration No. & ESI Registration No. Issued by Respective Authorities", "mandatory": True, "weight": 10, "rule_type": "GATEWAY_STATUS"},
                {"module": "Turnover", "title": "Average Annual Financial Turnover during last 3 Years >= INR 4.0 Lakhs (Audited Balance Sheets)", "mandatory": True, "weight": 10, "rule_type": "FINANCIAL_THRESHOLD"},
                {"module": "PastExperience", "title": "Successfully Completed Similar Web App Security Audits (3x ₹5.35L or 2x ₹6.69L or 1x ₹10.71L)", "mandatory": True, "weight": 15, "rule_type": "DOCUMENT_CONSISTENCY"},
                {"module": "LandBorder", "title": "Provisions for Procurement from Bidders Sharing Land Border with India Undertaking (Form-I / Form-II)", "mandatory": True, "weight": 5, "rule_type": "STATUTORY_DECLARATION"},
                {"module": "MakeInIndia", "title": "Make in India (MII) Local Content Self-Certification (Class-I / Class-II)", "mandatory": True, "weight": 5, "rule_type": "STATUTORY_DECLARATION"},
                {"module": "NonBlacklisting", "title": "Affidavit on Non-Judicial Stamp Paper Attested by Notary for Not Being Blacklisted (Annexure-VI)", "mandatory": True, "weight": 10, "rule_type": "STATUTORY_DECLARATION"}
            ]
        },
        {
            "number": "GEM/2026/B/IIMR/6641",
            "title": "Supply, Installation, Commissioning & On-Site Warranty of Agricultural Machinery (Seed Drill & Multi-Millet Thresher)",
            "desc": "Tender notice by ICAR - Indian Institute of Millets Research (IIMR), Hyderabad for procurement of precision millet seed drills and motorized multi-millet threshers.",
            "category": "Agricultural Machinery & Processing Equipment",
            "lifecycle_status": "READY_FOR_BIDDING",
            "rules": [
                {"module": "GST", "title": "GST Registration Certificate & Active Status on GSTN", "mandatory": True, "weight": 20, "rule_type": "GATEWAY_STATUS"},
                {"module": "PAN", "title": "Income Tax PAN Card Copy", "mandatory": True, "weight": 15, "rule_type": "IDENTITY_MATCH"},
                {"module": "OEM", "title": "Manufacturer Authorization Certificate (MAF) in case of Authorized Dealer", "mandatory": True, "weight": 20, "rule_type": "DOCUMENT_CONSISTENCY"},
                {"module": "TechnicalCompliance", "title": "Signed Compliance Sheet of Technical Specifications (Annexure-I) & Equipment Manual/Brochure", "mandatory": True, "weight": 15, "rule_type": "DOCUMENT_CONSISTENCY"},
                {"module": "MakeInIndia", "title": "Make in India (MII) Local Content Certificate (Class-I >= 50% / Class-II >= 20%)", "mandatory": True, "weight": 15, "rule_type": "STATUTORY_DECLARATION"},
                {"module": "NonBlacklisting", "title": "Declaration for Not Being Blacklisted on Letterhead (Annexure-II)", "mandatory": True, "weight": 10, "rule_type": "STATUTORY_DECLARATION"},
                {"module": "Udyam", "title": "Udyam MSME Certificate for EMD Waiver & Relaxation", "mandatory": False, "weight": 5, "rule_type": "EXEMPTION_VERIFY"}
            ]
        }
    ]

    for t_info in tenders_data:
        org_id = "ORG_DTE_MAHARASHTRA" if "DTE" in t_info["number"] else ("ORG_NFL_CENTRAL" if "NFL" in t_info["number"] else "ORG_ICAR_CENTRAL")
        existing_t = db.query(TenderModel).filter(TenderModel.tender_number == t_info["number"]).first()
        if not existing_t:
            tender_obj = TenderModel(
                user_id=primary_user.id if primary_user else None,
                organization_id=org_id,
                tender_number=t_info["number"],
                title=t_info["title"],
                description=t_info["desc"],
                category=t_info["category"],
                status="ACTIVE",
                lifecycle_status=t_info.get("lifecycle_status", "READY_FOR_BIDDING"),
                requirements_confirmed=True
            )
            db.add(tender_obj)
            db.flush()

            for r_info in t_info["rules"]:
                req_obj = RequirementModel(
                    tender_id=tender_obj.id,
                    module=r_info["module"],
                    title=r_info["title"],
                    mandatory=r_info["mandatory"],
                    weight=r_info["weight"],
                    rule_type=r_info["rule_type"]
                )
                db.add(req_obj)
            db.commit()
        else:
            if not existing_t.user_id and primary_user:
                existing_t.user_id = primary_user.id
                existing_t.lifecycle_status = t_info.get("lifecycle_status", "READY_FOR_BIDDING")
                db.commit()

    # 3. SEED REALISTIC BIDDERS FOR DTE MAHARASHTRA TENDER (DTE/2026/RFP/COE/4901)
    target_tender = db.query(TenderModel).filter(TenderModel.tender_number == "DTE/2026/RFP/COE/4901").first()
    if target_tender:
        bidders_data = [
            {
                "legal_name": "Tata Advanced Training & Systems Ltd",
                "pan": "AAACT1098F",
                "gstin": "27AAACT1098F1Z5",
                "udyam": "UDYAM-MH-01-0089241",
                "email": "tenders@tatatraining.com",
                "status": "QUALIFIED",
                "lifecycle_status": "QUALIFIED_FOR_FINAL_REVIEW",
                "screening_status": "PASS",
                "score": 95,
                "risk": "LOW",
                "recommendation": "Bidder fully complies with all Pre-Qualification criteria under DTE RFP Section 4.2: ₹15.8 Cr Turnover, 3 Completed COE Centers, 8 Full-Time Payroll Staff with PF numbers, Valid OEM MAF and ISO 9001:2015. Recommended for Technical Evaluation.",
                "doc_name": "Tata_DTE_COE_Bid_Bundle.pdf",
                "findings": [
                    {"severity": "INFO", "code": "GST_VERIFIED", "msg": "GSTIN 27AAACT1098F1Z5 verified active with 36 months regular 3B filings."},
                    {"severity": "INFO", "code": "TURNOVER_VERIFIED", "msg": "Audited turnover certified at ₹15.80 Cr average (exceeds ₹10 Cr minimum)."},
                    {"severity": "INFO", "code": "OEM_VERIFIED", "msg": "Valid OEM MAF letters verified for all hardware and simulation software."}
                ]
            },
            {
                "legal_name": "EduTech Infoway Solutions Pvt Ltd",
                "pan": "AACCE3099P",
                "gstin": "27AACCE3099P1Z2",
                "udyam": "UDYAM-MH-03-0091823",
                "email": "bids@edutechinfoway.in",
                "status": "NEEDS_CLARIFICATION",
                "lifecycle_status": "NEEDS_REVIEW",
                "screening_status": "REVIEW",
                "score": 75,
                "risk": "MEDIUM",
                "recommendation": "REVIEW REQUIRED: Bidder satisfies turnover (₹11.2 Cr) and project experience. However, 1 of 6 employee PF numbers requires verification against EPFO gateway. Officer clarification recommended before final qualification.",
                "doc_name": "EduTech_COE_Proposal.pdf",
                "findings": [
                    {"severity": "WARNING", "code": "EPFO_PF_MISMATCH", "msg": "Minor verification flag on Employee #4 PF account number on EPFO Gateway."},
                    {"severity": "INFO", "code": "GST_VERIFIED", "msg": "GSTIN active on GSTN Gateway."}
                ]
            },
            {
                "legal_name": "Apex Cyber Skills & Infra Ltd",
                "pan": "AABCA2045K",
                "gstin": "27AABCA2045K1Z8",
                "udyam": "UDYAM-MH-02-0044129",
                "email": "gov@apexcyberskills.com",
                "status": "DISQUALIFIED",
                "lifecycle_status": "NOT_QUALIFIED",
                "screening_status": "FAIL",
                "score": 40,
                "risk": "CRITICAL",
                "recommendation": "CRITICAL NON-COMPLIANCE: Bidder average annual turnover of ₹3.20 Cr falls below mandatory threshold of ₹10.00 Cr. Additionally, ISO 9001:2015 certificate validity expired on 15/01/2024. Disqualification mandatory under DTE Section 4.2.",
                "doc_name": "Apex_COE_Submission.pdf",
                "findings": [
                    {"severity": "CRITICAL", "code": "TURNOVER_BELOW_MINIMUM", "msg": "Average turnover ₹3.2 Cr is below mandatory ₹10 Cr requirement."},
                    {"severity": "CRITICAL", "code": "ISO_EXPIRED", "msg": "ISO 9001:2015 certificate expired on 15/01/2024."}
                ]
            }
        ]

        reqs = db.query(RequirementModel).filter(RequirementModel.tender_id == target_tender.id).all()

        for b_data in bidders_data:
            existing_bidder = db.query(BidderModel).filter(BidderModel.legal_name == b_data["legal_name"]).first()
            if not existing_bidder:
                bidder_obj = BidderModel(
                    legal_name=b_data["legal_name"],
                    pan_number=b_data["pan"],
                    gstin=b_data["gstin"],
                    udyam_number=b_data["udyam"],
                    email=b_data["email"]
                )
                db.add(bidder_obj)
                db.flush()
            else:
                bidder_obj = existing_bidder

            existing_bid = db.query(BidModel).filter(
                BidModel.tender_id == target_tender.id,
                BidModel.bidder_id == bidder_obj.id
            ).first()

            if not existing_bid:
                bid_obj = BidModel(
                    tender_id=target_tender.id,
                    bidder_id=bidder_obj.id,
                    status=b_data["status"],
                    lifecycle_status=b_data["lifecycle_status"],
                    screening_status=b_data["screening_status"]
                )
                db.add(bid_obj)
                db.flush()

                # Add Document
                doc_obj = DocumentModel(
                    bid_id=bid_obj.id,
                    filename=b_data["doc_name"],
                    doc_type="BID_SUBMISSION_BUNDLE",
                    storage_path=f"/storage/bids/{b_data['doc_name']}",
                    sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                )
                db.add(doc_obj)
                db.flush()

                # Add Extractions
                ext1 = ExtractionModel(document_id=doc_obj.id, field_name="Legal Name", field_value=b_data["legal_name"], page_number=1)
                ext2 = ExtractionModel(document_id=doc_obj.id, field_name="GSTIN", field_value=b_data["gstin"], page_number=1)
                ext3 = ExtractionModel(document_id=doc_obj.id, field_name="PAN", field_value=b_data["pan"], page_number=1)
                db.add_all([ext1, ext2, ext3])

                # Add Verification Results
                for req in reqs:
                    v_status = "PASS"
                    v_risk = "LOW"
                    if b_data["risk"] == "CRITICAL" and ("Turnover" in req.module or "ISO" in req.module):
                        v_status = "FAIL"
                        v_risk = "CRITICAL"
                    elif b_data["risk"] == "MEDIUM" and "EPFO" in req.module:
                        v_status = "REVIEW"
                        v_risk = "MEDIUM"

                    ver_res = VerificationResultModel(
                        bid_id=bid_obj.id,
                        requirement_id=req.id,
                        module=req.module,
                        status=v_status,
                        risk=v_risk,
                        verification_mode="SANDBOX"
                    )
                    db.add(ver_res)
                    db.flush()

                    for f in b_data["findings"]:
                        if req.module.upper() in f["code"]:
                            finding_obj = FindingModel(
                                verification_result_id=ver_res.id,
                                severity=f["severity"],
                                code=f["code"],
                                message=f["msg"]
                            )
                            db.add(finding_obj)

                # Add Assessment
                assess_obj = AssessmentModel(
                    bid_id=bid_obj.id,
                    compliance_score=b_data["score"],
                    risk_level=b_data["risk"],
                    ai_recommendation=b_data["recommendation"]
                )
                db.add(assess_obj)

                # Add Audit Event
                audit_obj = AuditEventModel(
                    bid_id=bid_obj.id,
                    actor_id="OFFICER_SHUBHAM",
                    event_type="BID_EVALUATION_COMPLETED",
                    payload_json=json.dumps({"bidder": b_data["legal_name"], "score": b_data["score"], "risk": b_data["risk"]}),
                    sha256_hash="f5a9c8b74123..."
                )
                db.add(audit_obj)

            # Historical memory for Tata Advanced Training (Evaluated in 2023 for Central IT Tender)
            if bidder_obj.legal_name == "Tata Advanced Training & Systems Ltd":
                hist_existing = db.query(HistoricalBidderMatchModel).filter(
                    HistoricalBidderMatchModel.bidder_id == bidder_obj.id
                ).first()
                if not hist_existing:
                    hist_record = HistoricalBidderMatchModel(
                        bidder_id=bidder_obj.id,
                        historical_tender_number="GEM/2023/B/104921",
                        historical_tender_title="Procurement of Technical Simulation & Lab Infrastructure",
                        historical_outcome="QUALIFIED",
                        historical_score=96,
                        historical_risk="LOW",
                        key_findings_summary="Bidder verified with active GSTIN, 100% turnover criteria met, and valid OEM authorizations. Flawless compliance.",
                        matched_by="VERIFIED_GSTIN",
                        evaluation_date=datetime(2023, 8, 28, 11, 30, tzinfo=timezone.utc)
                    )
                    db.add(hist_record)

        db.commit()
        logger.info("Successfully seeded database with authentic DTE Maharashtra, NFL CPSE, and ICAR-IIMR real tenders.")
