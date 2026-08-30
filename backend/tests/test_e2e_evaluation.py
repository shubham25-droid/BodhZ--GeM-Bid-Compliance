import os
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.models import TenderModel, RequirementModel, BidderModel, BidModel, AssessmentModel, OfficerDecisionModel
from app.document_intelligence.document_processor import DocumentProcessor

client = TestClient(app)
SAMPLE_DOCS_DIR = "D:/Antigravity Workspace/BodhZ_Bid Compliance Project (SIH26100)/data/sample/documents"


# --------------------------------------------------
# SETUP FIXTURE FOR GE M TENDER & REQUIREMENTS
# --------------------------------------------------
@pytest.fixture
def sample_tender_setup():
    db = SessionLocal()
    unique_num = f"GEM/2026/B/{uuid.uuid4().hex[:6].upper()}"
    tender = TenderModel(
        tender_number=unique_num,
        title="Procurement of Server Infrastructure & Enterprise Storage Systems",
        category="IT Hardware",
        status="ACTIVE"
    )
    db.add(tender)
    db.flush()

    reqs = [
        RequirementModel(tender_id=tender.id, module="GST", title="Valid GSTIN", mandatory=True, weight=25, rule_type="REGISTRATION_AND_CONSISTENCY"),
        RequirementModel(tender_id=tender.id, module="Udyam", title="Udyam MSME Certificate", mandatory=True, weight=20, rule_type="REGISTRATION_VALIDATION"),
        RequirementModel(tender_id=tender.id, module="PAN", title="PAN Card & Legal Name Match", mandatory=True, weight=20, rule_type="IDENTITY_CONSISTENCY"),
        RequirementModel(tender_id=tender.id, module="OEM", title="OEM Authorization Letter", mandatory=True, weight=35, rule_type="AUTHORIZATION_VALIDATION")
    ]
    for r in reqs:
        db.add(r)

    db.commit()
    tender_id = tender.id
    db.close()
    return tender_id


# --------------------------------------------------
# SCENARIO A: FULLY COMPLIANT BIDDER E2E TEST
# --------------------------------------------------
def test_e2e_scenario_a_compliant_bidder(sample_tender_setup):
    db = SessionLocal()
    bidder = BidderModel(
        legal_name=f"Acme Solutions {uuid.uuid4().hex[:4]} Pvt Ltd",
        gstin="27ABCDE1234F1Z5",
        pan_number="ABCDE1234F",
        udyam_number="UDYAM-MH-12-0098234",
        email="bids@acme.in"
    )
    db.add(bidder)
    db.flush()

    bid = BidModel(tender_id=sample_tender_setup, bidder_id=bidder.id)
    db.add(bid)
    db.commit()

    # Upload sample PDFs
    for doc_name in ["GST_Certificate_Sample.pdf", "Udyam_Registration_Sample.pdf", "PAN_Card_Sample.pdf", "OEM_Authorization_Sample.pdf"]:
        doc_path = os.path.join(SAMPLE_DOCS_DIR, doc_name)
        with open(doc_path, "rb") as f:
            file_bytes = f.read()
        DocumentProcessor.process_and_store_document(db, bid.id, file_bytes, doc_name)

    # Trigger Evaluation Endpoint
    response = client.post(f"/api/v1/bids/{bid.id}/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert data["compliance_score"] == 100
    assert data["risk_level"] == "LOW"

    # Fetch Assessment Details
    res_ass = client.get(f"/api/v1/bids/{bid.id}/assessment")
    assert res_ass.status_code == 200
    ass_data = res_ass.json()
    assert len(ass_data["verification_modules"]) == 4

    db.close()


# --------------------------------------------------
# SCENARIO B: OFFICER DECISION & AUDIT TRAIL TEST
# --------------------------------------------------
def test_e2e_officer_decision_and_audit_trail(sample_tender_setup):
    db = SessionLocal()
    bidder = BidderModel(legal_name=f"Beta Systems {uuid.uuid4().hex[:4]} Pvt Ltd")
    db.add(bidder)
    db.flush()

    bid = BidModel(tender_id=sample_tender_setup, bidder_id=bidder.id)
    db.add(bid)
    db.commit()

    # Upload single doc & evaluate
    doc_path = os.path.join(SAMPLE_DOCS_DIR, "GST_Certificate_Sample.pdf")
    with open(doc_path, "rb") as f:
        DocumentProcessor.process_and_store_document(db, bid.id, f.read(), "GST_Certificate_Sample.pdf")

    client.post(f"/api/v1/bids/{bid.id}/evaluate")
    ass = db.query(AssessmentModel).filter(AssessmentModel.bid_id == bid.id).first()

    # Record Officer Decision
    decision_resp = client.post(
        "/api/v1/bids/officer-decision",
        json={
            "assessment_id": ass.id,
            "bid_id": bid.id,
            "decision": "QUALIFIED",
            "notes": "Verified against GST portal; bidder qualified by Procurement Officer."
        }
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["decision"] == "QUALIFIED"

    # Fetch Audit Trail
    audit_resp = client.get(f"/api/v1/audit/{bid.id}")
    assert audit_resp.status_code == 200
    audit_events = audit_resp.json()
    assert len(audit_events) >= 2
    assert any("OFFICER_FINAL_DECISION_RECORDED" in e["event_type"] for e in audit_events)

    db.close()
