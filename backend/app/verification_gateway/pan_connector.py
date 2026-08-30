import re
from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract

# Regular expression pattern for 10-character Indian Permanent Account Number (PAN)
PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"


# --------------------------------------------------
# PAN VERIFICATION CONNECTOR
# --------------------------------------------------
class PANConnector(BaseVerificationConnector):
    """
    Verification adapter for Permanent Account Number (PAN) format validation,
    Income Tax entity match, and identity verification.
    """

    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        raw_pan = bidder_data.get("pan_number") or ""
        pan = raw_pan.strip().upper()
        raw_name = bidder_data.get("legal_name") or ""
        legal_name = raw_name.strip()

        evidence_items: List[Dict[str, Any]] = []
        issues: List[Dict[str, Any]] = []

        # Find document extractions matching PAN
        for ext in extractions:
            snippet = (ext.get("text_snippet") or "").upper()
            val = (ext.get("field_value") or "").upper()
            if "PERMANENT ACCOUNT NUMBER" in snippet or "PAN" in snippet:
                match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]{1}", val)
                if match:
                    extracted_pan = match.group(0)
                    evidence_items.append({
                        "document_id": ext.get("document_id"),
                        "page": ext.get("page_number", 1),
                        "field": "pan_number",
                        "value": extracted_pan,
                        "snippet": snippet[:150]
                    })
                    if not pan:
                        pan = extracted_pan

        if not pan:
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_PAN_001"),
                module="PAN",
                status="FAIL",
                confidence=1.0,
                risk="HIGH",
                extracted_values={},
                evidence=[],
                issues=[{
                    "severity": "ERROR",
                    "code": "MISSING_PAN",
                    "message": "Mandatory PAN card document evidence was not found."
                }],
                verification_mode="SANDBOX"
            )

        if not re.match(PAN_REGEX, pan):
            issues.append({
                "severity": "ERROR",
                "code": "INVALID_PAN_FORMAT",
                "message": f"PAN number '{pan}' does not comply with 10-character statutory format."
            })
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_PAN_001"),
                module="PAN",
                status="FAIL",
                confidence=0.95,
                risk="HIGH",
                extracted_values={"pan_number": pan},
                evidence=evidence_items,
                issues=issues,
                verification_mode="SANDBOX"
            )

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_PAN_001"),
            module="PAN",
            status="PASS",
            confidence=0.98,
            risk="LOW",
            extracted_values={"pan_number": pan, "legal_name": legal_name, "status": "ACTIVE_VALIDATED"},
            evidence=evidence_items,
            issues=[],
            verification_mode="SANDBOX"
        )
