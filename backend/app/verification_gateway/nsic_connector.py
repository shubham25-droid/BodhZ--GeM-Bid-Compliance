from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class NSICConnector(BaseVerificationConnector):
    """
    Verification connector for NSIC Single Point Registration Scheme.
    """

    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        nsic_no = bidder_data.get("nsic_number") or ""
        evidence_items: List[Dict[str, Any]] = []

        for ext in extractions:
            snippet = ext.get("text_snippet") or ""
            if "NSIC" in snippet.upper():
                evidence_items.append({
                    "document_id": ext.get("document_id"),
                    "page": ext.get("page_number", 1),
                    "field": "nsic_number",
                    "snippet": snippet[:150]
                })

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_NSIC_001"),
            module="NSIC",
            status="REVIEW",
            confidence=0.80,
            risk="LOW",
            extracted_values={"nsic_number": nsic_no or "N/A"},
            evidence=evidence_items,
            issues=[{
                "severity": "INFO",
                "code": "NSIC_API_UNAVAILABLE",
                "message": "NSIC Register API unconfigured. Manual document review required."
            }],
            verification_mode="UNAVAILABLE"
        )
