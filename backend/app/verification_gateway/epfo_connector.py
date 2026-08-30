from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class EPFOConnector(BaseVerificationConnector):
    """
    Verification connector for Employees' Provident Fund Organisation (EPFO) Code.
    """
    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        epfo_code = bidder_data.get("epfo_code") or ""
        evidence_items = []
        for ext in extractions:
            if "EPFO" in (ext.get("text_snippet") or "").upper() or "PF" in (ext.get("text_snippet") or "").upper():
                evidence_items.append({"document_id": ext.get("document_id"), "page": ext.get("page_number", 1), "field": "epfo_code", "snippet": ext.get("text_snippet")[:150]})

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_EPFO_001"),
            module="EPFO",
            status="REVIEW",
            confidence=0.80,
            risk="LOW",
            extracted_values={"epfo_code": epfo_code or "N/A"},
            evidence=evidence_items,
            issues=[{"severity": "INFO", "code": "EPFO_API_UNAVAILABLE", "message": "EPFO Portal API unconfigured. Manual Officer review required."}],
            verification_mode="UNAVAILABLE"
        )
