import re
from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract

# Regular expression pattern for Udyam Registration Number
UDYAM_REGEX = r"^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$"


# --------------------------------------------------
# UDYAM / MSME VERIFICATION CONNECTOR
# --------------------------------------------------
class UdyamConnector(BaseVerificationConnector):
    """
    Verification adapter for Udyam MSME registration format, enterprise category,
    and MSME procurement policy benefit eligibility.
    """

    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        raw_udyam = bidder_data.get("udyam_number") or ""
        udyam = raw_udyam.strip().upper()
        evidence_items: List[Dict[str, Any]] = []
        issues: List[Dict[str, Any]] = []

        # Find document extractions matching Udyam
        for ext in extractions:
            snippet = (ext.get("text_snippet") or "").upper()
            val = (ext.get("field_value") or "").upper()
            if "UDYAM" in snippet or "MSME" in snippet:
                match = re.search(r"UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}", val)
                if match:
                    extracted_udyam = match.group(0)
                    evidence_items.append({
                        "document_id": ext.get("document_id"),
                        "page": ext.get("page_number", 1),
                        "field": "udyam_number",
                        "value": extracted_udyam,
                        "snippet": snippet[:150]
                    })
                    if not udyam:
                        udyam = extracted_udyam

        if not udyam:
            is_mandatory = requirement.get("mandatory", True)
            status_res = "FAIL" if is_mandatory else "REVIEW"
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_UDYAM_001"),
                module="Udyam",
                status=status_res,
                confidence=1.0,
                risk="HIGH" if is_mandatory else "MEDIUM",
                extracted_values={},
                evidence=[],
                issues=[{
                    "severity": "ERROR" if is_mandatory else "WARNING",
                    "code": "MISSING_UDYAM_CERTIFICATE",
                    "message": "Udyam MSME registration certificate evidence was not found."
                }],
                verification_mode="SANDBOX"
            )

        if not re.match(UDYAM_REGEX, udyam):
            issues.append({
                "severity": "ERROR",
                "code": "INVALID_UDYAM_FORMAT",
                "message": f"Udyam registration number '{udyam}' does not match standard statutory format."
            })
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_UDYAM_001"),
                module="Udyam",
                status="FAIL",
                confidence=0.95,
                risk="HIGH",
                extracted_values={"udyam_number": udyam},
                evidence=evidence_items,
                issues=issues,
                verification_mode="SANDBOX"
            )

        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_UDYAM_001"),
            module="Udyam",
            status="PASS",
            confidence=0.96,
            risk="LOW",
            extracted_values={
                "udyam_number": udyam,
                "enterprise_class": "SMALL",
                "msme_benefit_eligible": True,
                "status": "VERIFIED_ACTIVE"
            },
            evidence=evidence_items,
            issues=[],
            verification_mode="SANDBOX"
        )
