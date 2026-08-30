import os
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.models import TenderModel, BidderModel, BidModel
from app.document_intelligence.file_validator import FileValidator
from app.document_intelligence.pdf_extractor import PDFExtractor
from app.document_intelligence.classifier import DocumentClassifier

client = TestClient(app)
SAMPLE_DOCS_DIR = "D:/Antigravity Workspace/BodhZ_Bid Compliance Project (SIH26100)/data/sample/documents"


# --------------------------------------------------
# FILE VALIDATOR SECURITY TEST
# --------------------------------------------------
def test_file_validator_magic_bytes():
    """Verifies that non-PDF fake files are rejected by magic byte security checks."""
    fake_bytes = b"This is plain text pretending to be a pdf file."
    with pytest.raises(Exception) as excinfo:
        FileValidator.validate_file_content(fake_bytes, "test.pdf")
    assert "Security validation failed" in str(excinfo.value)


# --------------------------------------------------
# DIGITAL PDF TEXT EXTRACTION TEST
# --------------------------------------------------
def test_pdf_extraction_on_gst_sample():
    """Verifies PyMuPDF text extraction on generated GST Certificate sample."""
    gst_pdf_path = os.path.join(SAMPLE_DOCS_DIR, "GST_Certificate_Sample.pdf")
    assert os.path.exists(gst_pdf_path)

    with open(gst_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    extracted = PDFExtractor.extract_text_from_pdf_bytes(pdf_bytes)
    assert extracted["total_pages"] == 1
    assert "27ABCDE1234F1Z5" in extracted["pages"][0]["text"]
    assert "Acme Solutions Pvt Ltd" in extracted["pages"][0]["text"]


# --------------------------------------------------
# DOCUMENT CLASSIFICATION TEST
# --------------------------------------------------
def test_document_classification_categories():
    """Verifies document classification matching on synthetic document text."""
    gst_text = "FORM GST REG-06 GOODS AND SERVICES TAX REGISTRATION CERTIFICATE GSTIN 27ABCDE1234F1Z5"
    res_gst = DocumentClassifier.classify_document(gst_text)
    assert res_gst["category"] == "GST_CERTIFICATE"
    assert res_gst["confidence"] > 0.80

    udyam_text = "MINISTRY OF MICRO, SMALL ENTERPRISES UDYAM REGISTRATION NUMBER UDYAM-MH-12-0098234"
    res_udyam = DocumentClassifier.classify_document(udyam_text)
    assert res_udyam["category"] == "UDYAM_CERTIFICATE"
    assert res_udyam["confidence"] > 0.80


# --------------------------------------------------
# END-TO-END DOCUMENT UPLOAD & PROCESSING API TEST
# --------------------------------------------------
def test_document_upload_api():
    """Verifies POST /api/v1/documents/bids/{bid_id} upload endpoint."""
    db = SessionLocal()
    unique_num = f"GEM/DOC/{uuid.uuid4().hex[:6].upper()}"
    tender = TenderModel(tender_number=unique_num, title="Test Tender")
    db.add(tender)
    db.flush()

    bidder = BidderModel(legal_name=f"Test Bidder {unique_num}")
    db.add(bidder)
    db.flush()

    bid = BidModel(tender_id=tender.id, bidder_id=bidder.id)
    db.add(bid)
    db.commit()

    gst_pdf_path = os.path.join(SAMPLE_DOCS_DIR, "GST_Certificate_Sample.pdf")
    with open(gst_pdf_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        f"/api/v1/documents/bids/{bid.id}",
        files={"file": ("GST_Certificate_Sample.pdf", file_bytes, "application/pdf")}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "GST_Certificate_Sample.pdf"
    assert data["doc_type"] == "GST_CERTIFICATE"
    assert len(data["sha256_hash"]) == 64
    assert data["extracted_snippets_count"] >= 1

    db.close()
