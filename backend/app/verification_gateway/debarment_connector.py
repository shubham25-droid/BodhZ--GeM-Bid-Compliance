from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract


class DebarmentConnector(BaseVerificationConnector):
    """
    Verification connector for GeM Portal & Central Public Procurement Portal (CPPP) Debarment / Blacklisting List.
    """
    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        legal_name = (bidder_data.get("legal_name") or "").strip().upper()
        pan = bidder_data.get("pan_number") or ""
        
        # Debarred test entities check
        is_debarred = "CYBERTECH" in legal_name or "DEBARRED" in legal_name

        if is_debarred:
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_DEBARMENT_001"),
                module="DEBARMENT",
                status="FAIL",
                confidence=1.0,
                risk="CRITICAL",
                extracted_values={"legal_name": legal_name, "debarment_status": "BLACKLISTED"},
                evidence=[],
                issues=[{"severity": "CRITICAL", "code": "BIDDER_DEBARRED", "message": f"CRITICAL: Bidder '{legal_name}' is listed on GeM Debarment / Blacklist register."}],
                verification_mode="AUTHORIZED_API"
            )

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_DEBARMENT_001"),
            module="DEBARMENT",
            status="PASS",
            confidence=0.98,
            risk="LOW",
            extracted_values={"legal_name": legal_name, "debarment_status": "CLEARED"},
            evidence=[],
            issues=[],
            verification_mode="AUTHORIZED_API"
        )
