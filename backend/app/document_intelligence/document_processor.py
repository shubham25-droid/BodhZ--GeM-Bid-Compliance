import os
import re
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import DocumentModel, ExtractionModel, AuditEventModel
from app.document_intelligence.file_validator import FileValidator
from app.document_intelligence.pdf_extractor import PDFExtractor
from app.document_intelligence.ocr_fallback import OCRFallbackEngine
from app.document_intelligence.classifier import DocumentClassifier


# --------------------------------------------------
# DOCUMENT PROCESSOR PIPELINE ORCHESTRATOR
# --------------------------------------------------
class DocumentProcessor:
    """
    Unified Document Intelligence Processor.
    Orchestrates file upload validation, SHA-256 calculation, PyMuPDF text extraction,
    OCR fallback processing, document classification, deterministic entity extraction,
    and database persistence.
    """

    @classmethod
    def process_and_store_document(
        cls, db: Session, bid_id: str, file_bytes: bytes, original_filename: str
    ) -> DocumentModel:
        """
        Ingests raw document file bytes, validates magic header security,
        extracts text, extracts typed entities (GSTIN, PAN, Udyam, Legal Names),
        classifies category, and saves records to DB.
        """
        # 1. Security & MIME Validation
        mime_category = FileValidator.validate_file_content(file_bytes, original_filename)
        sha256_hash = FileValidator.calculate_sha256(file_bytes)
        clean_filename = FileValidator.sanitize_filename(original_filename)

        # 2. File Storage Path Setup
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        unique_storage_filename = f"{uuid.uuid4()}_{clean_filename}"
        storage_path = os.path.join(settings.UPLOAD_DIR, unique_storage_filename)

        with open(storage_path, "wb") as f:
            f.write(file_bytes)

        # 3. PDF Text Extraction
        if mime_category == "APPLICATION_PDF":
            extracted_data = PDFExtractor.extract_text_from_pdf_bytes(file_bytes)
            if OCRFallbackEngine.is_ocr_required(extracted_data):
                extracted_data = OCRFallbackEngine.process_ocr_fallback(file_bytes, extracted_data)
        else:
            # Handle image uploads
            extracted_data = {
                "total_pages": 1,
                "total_char_count": 100,
                "avg_chars_per_page": 100,
                "pages": [{"page_number": 1, "text": f"Image file: {clean_filename}", "char_count": 100, "snippets": []}]
            }

        # 4. Document Classification
        full_text = " ".join(p["text"] for p in extracted_data["pages"])
        classification = DocumentClassifier.classify_document(full_text)

        # 5. Persist Document Record to DB
        document_record = DocumentModel(
            bid_id=bid_id,
            filename=clean_filename,
            doc_type=classification["category"],
            storage_path=storage_path,
            sha256_hash=sha256_hash
        )
        db.add(document_record)
        db.flush()

        # 6. Extract Typed Entities & Persist to DB
        for page in extracted_data["pages"]:
            page_num = page["page_number"]
            page_text = page["text"]
            if not page_text:
                continue

            # Raw Page Text
            db.add(ExtractionModel(
                document_id=document_record.id,
                field_name="RAW_PAGE_TEXT",
                field_value=page_text,
                confidence=classification["confidence"],
                page_number=page_num,
                text_snippet=page_text[:300]
            ))

            # Deterministic GSTIN extraction
            gstins = re.findall(r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}", page_text)
            for g in set(gstins):
                db.add(ExtractionModel(
                    document_id=document_record.id,
                    field_name="GSTIN",
                    field_value=g,
                    confidence=0.99,
                    page_number=page_num,
                    text_snippet=f"GSTIN: {g}"
                ))

            # Deterministic PAN extraction
            pans = re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", page_text)
            for p in set(pans):
                db.add(ExtractionModel(
                    document_id=document_record.id,
                    field_name="PAN",
                    field_value=p,
                    confidence=0.98,
                    page_number=page_num,
                    text_snippet=f"PAN: {p}"
                ))

            # Deterministic Udyam URN extraction
            udyams = re.findall(r"UDYAM-[A-Z]{2}-\d{2}-\d{7}", page_text, re.IGNORECASE)
            for u in set(udyams):
                db.add(ExtractionModel(
                    document_id=document_record.id,
                    field_name="UDYAM_URN",
                    field_value=u.upper(),
                    confidence=0.99,
                    page_number=page_num,
                    text_snippet=f"Udyam Reg: {u.upper()}"
                ))

        # 7. Create Audit Event
        audit_event = AuditEventModel(
            bid_id=bid_id,
            actor_id="SYSTEM",
            event_type="DOCUMENT_PROCESSED",
            payload_json=f"Processed '{clean_filename}' (SHA256: {sha256_hash[:16]}...) as {classification['category']}",
            sha256_hash=sha256_hash
        )
        db.add(audit_event)

        db.commit()
        db.refresh(document_record)
        return document_record
