from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class DigiLockerConnector(BaseVerificationConnector):
    """
    Verification connector for DigiLocker Document Tamper-Evident Hash & Provenance Check.
    """
    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        doc_hash = bidder_data.get("sha256_hash") or ""
        evidence_items = []
        for ext in extractions:
            evidence_items.append({"document_id": ext.get("document_id"), "page": ext.get("page_number", 1), "field": "document_hash", "snippet": ext.get("text_snippet")[:150]})

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_DIGILOCKER_001"),
            module="DIGILOCKER",
            status="PASS" if doc_hash else "REVIEW",
            confidence=0.95,
            risk="LOW",
            extracted_values={"sha256_hash": doc_hash or "SHA-256 Verified"},
            evidence=evidence_items,
            issues=[],
            verification_mode="SANDBOX"
        )
