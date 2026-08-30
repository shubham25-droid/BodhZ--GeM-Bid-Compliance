from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class ESICConnector(BaseVerificationConnector):
    """
    Verification connector for Employees' State Insurance Corporation (ESIC) Registration.
    """
    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        esic_no = bidder_data.get("esic_number") or ""
        evidence_items = []
        for ext in extractions:
            if "ESIC" in (ext.get("text_snippet") or "").upper() or "ESI" in (ext.get("text_snippet") or "").upper():
                evidence_items.append({"document_id": ext.get("document_id"), "page": ext.get("page_number", 1), "field": "esic_number", "snippet": ext.get("text_snippet")[:150]})

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_ESIC_001"),
            module="ESIC",
            status="REVIEW",
            confidence=0.80,
            risk="LOW",
            extracted_values={"esic_number": esic_no or "N/A"},
            evidence=evidence_items,
            issues=[{"severity": "INFO", "code": "ESIC_API_UNAVAILABLE", "message": "ESIC Portal API unconfigured. Manual verification required."}],
            verification_mode="UNAVAILABLE"
        )
