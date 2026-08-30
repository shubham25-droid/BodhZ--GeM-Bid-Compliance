from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class LocalContentConnector(BaseVerificationConnector):
    """
    Verification connector for Make in India / Local Content Certificate.
    """
    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        evidence_items = []
        for ext in extractions:
            if "MAKE IN INDIA" in (ext.get("text_snippet") or "").upper() or "LOCAL CONTENT" in (ext.get("text_snippet") or "").upper():
                evidence_items.append({"document_id": ext.get("document_id"), "page": ext.get("page_number", 1), "field": "local_content_cert", "snippet": ext.get("text_snippet")[:150]})

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_LOCALCONTENT_001"),
            module="MAKE_IN_INDIA",
            status="PASS" if evidence_items else "REVIEW",
            confidence=0.85,
            risk="LOW",
            extracted_values={"local_content_class": "Class-I Local Supplier (>=50%)"},
            evidence=evidence_items,
            issues=[],
            verification_mode="DOCUMENT_CONSISTENCY"
        )
