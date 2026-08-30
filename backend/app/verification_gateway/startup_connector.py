from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class StartupIndiaConnector(BaseVerificationConnector):
    """
    Verification connector for Startup India DPIIT Recognition Certificate.
    """

    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        dpiit_no = bidder_data.get("dpiit_number") or ""
        evidence_items: List[Dict[str, Any]] = []

        for ext in extractions:
            snippet = ext.get("text_snippet") or ""
            if "DPIIT" in snippet.upper() or "STARTUP" in snippet.upper():
                evidence_items.append({
                    "document_id": ext.get("document_id"),
                    "page": ext.get("page_number", 1),
                    "field": "dpiit_number",
                    "snippet": snippet[:150]
                })

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_STARTUP_001"),
            module="STARTUP_INDIA",
            status="REVIEW",
            confidence=0.80,
            risk="LOW",
            extracted_values={"dpiit_number": dpiit_no or "N/A"},
            evidence=evidence_items,
            issues=[{
                "severity": "INFO",
                "code": "STARTUP_API_UNAVAILABLE",
                "message": "Startup India Portal API unavailable. Manual Officer verification recommended."
            }],
            verification_mode="UNAVAILABLE"
        )
