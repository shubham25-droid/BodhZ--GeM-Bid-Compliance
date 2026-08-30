from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class MCAConnector(BaseVerificationConnector):
    """
    Verification connector for MCA21 Corporate Identification Number (CIN) and Active Company Status.
    Exposes explicit verification status (SANDBOX or UNAVAILABLE - MANUAL REVIEW REQUIRED).
    """

    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        legal_name = (bidder_data.get("legal_name") or "").strip()
        cin = bidder_data.get("cin") or ""

        evidence_items: List[Dict[str, Any]] = []
        for ext in extractions:
            snippet = ext.get("text_snippet") or ""
            if "CIN" in snippet.upper() or "COMPANY" in snippet.upper():
                evidence_items.append({
                    "document_id": ext.get("document_id"),
                    "page": ext.get("page_number", 1),
                    "field": "cin",
                    "snippet": snippet[:150]
                })

        # If live MCA gateway is unconfigured, return structured UNAVAILABLE response allowing Manual Review
        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_MCA_001"),
            module="MCA21",
            status="REVIEW",
            confidence=0.80,
            risk="LOW",
            extracted_values={"legal_name": legal_name, "cin": cin or "UNVERIFIED"},
            evidence=evidence_items,
            issues=[{
                "severity": "INFO",
                "code": "MCA_CONNECTOR_UNAVAILABLE",
                "message": "MCA21 Live API Connector unconfigured in sandbox mode. Manual verification required by Procurement Officer."
            }],
            verification_mode="UNAVAILABLE"
        )
