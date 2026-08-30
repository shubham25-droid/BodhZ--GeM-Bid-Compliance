from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import BidModel, DocumentModel, ExtractionModel
from app.document_intelligence.document_processor import DocumentProcessor

router = APIRouter(prefix="/documents", tags=["Document Intelligence Layer"])


# --------------------------------------------------
# UPLOAD BIDDER DOCUMENT
# --------------------------------------------------
@router.post("/bids/{bid_id}", status_code=status.HTTP_201_CREATED, summary="Upload Bidder Document PDF")
@router.post("/upload", status_code=status.HTTP_201_CREATED, summary="Upload Bidder Document PDF (Query Param)")
async def upload_bidder_document(
    bid_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Ingests bidder document file, performs magic byte security check, calculates SHA-256 hash,
    saves file to storage, executes PyMuPDF text extraction & document classification,
    and returns processed document metadata and page snippets.
    """
    bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid submission not found.")

    file_bytes = await file.read()
    doc_record = DocumentProcessor.process_and_store_document(
        db=db,
        bid_id=bid.id,
        file_bytes=file_bytes,
        original_filename=file.filename or "uploaded_doc.pdf"
    )

    extractions = db.query(ExtractionModel).filter(ExtractionModel.document_id == doc_record.id).all()

    return {
        "id": doc_record.id,
        "bid_id": doc_record.bid_id,
        "filename": doc_record.filename,
        "doc_type": doc_record.doc_type,
        "sha256_hash": doc_record.sha256_hash,
        "uploaded_at": doc_record.uploaded_at,
        "extracted_snippets_count": len(extractions),
        "extractions": [
            {
                "id": ext.id,
                "page_number": ext.page_number,
                "field_name": ext.field_name,
                "confidence": ext.confidence,
                "text_snippet": ext.text_snippet
            }
            for ext in extractions
        ]
    }


# --------------------------------------------------
# GET DOCUMENT DETAILS & EXTRACTED TEXT
# --------------------------------------------------
@router.get("/{document_id}", summary="Get Extracted Text and Page Snippets")
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    """Fetches document metadata, classification category, and extracted page text snippets."""
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    extractions = db.query(ExtractionModel).filter(ExtractionModel.document_id == doc.id).all()
    return {
        "id": doc.id,
        "bid_id": doc.bid_id,
        "filename": doc.filename,
        "doc_type": doc.doc_type,
        "sha256_hash": doc.sha256_hash,
        "uploaded_at": doc.uploaded_at,
        "extractions": [
            {
                "id": ext.id,
                "page_number": ext.page_number,
                "field_name": ext.field_name,
                "confidence": ext.confidence,
                "field_value": ext.field_value,
                "text_snippet": ext.text_snippet
            }
            for ext in extractions
        ]
    }
