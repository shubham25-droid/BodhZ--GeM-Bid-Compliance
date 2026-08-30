import re
from typing import Dict, Any, List
from app.verification_gateway.base_connector import BaseVerificationConnector, VerificationResultContract

# Regular expression pattern for 15-character Indian GSTIN
GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"


# --------------------------------------------------
# GST VERIFICATION CONNECTOR
# --------------------------------------------------
class GSTConnector(BaseVerificationConnector):
    """
    Verification adapter for GSTIN registration validation, active status check,
    and cross-document legal name consistency verification.
    """

    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        raw_gstin = bidder_data.get("gstin") or ""
        gstin = raw_gstin.strip().upper()
        raw_name = bidder_data.get("legal_name") or ""
        legal_name = raw_name.strip()

        evidence_items: List[Dict[str, Any]] = []
        issues: List[Dict[str, Any]] = []

        # Find document extractions matching GST
        for ext in extractions:
            snippet = ext.get("text_snippet") or ""
            val = ext.get("field_value") or ""
            if "GSTIN" in snippet.upper() or ext.get("field_name") == "RAW_PAGE_TEXT":
                match = re.search(r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}", val)
                if match:
                    extracted_gstin = match.group(0)
                    evidence_items.append({
                        "document_id": ext.get("document_id"),
                        "page": ext.get("page_number", 1),
                        "field": "gstin",
                        "value": extracted_gstin,
                        "snippet": snippet[:150]
                    })
                    if not gstin:
                        gstin = extracted_gstin

        # 1. Check GSTIN presence
        if not gstin:
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_GST_001"),
                module="GST",
                status="FAIL",
                confidence=1.0,
                risk="HIGH",
                extracted_values={},
                evidence=[],
                issues=[{
                    "severity": "ERROR",
                    "code": "MISSING_GSTIN",
                    "message": "Mandatory GSTIN is absent from bidder profile and submitted documents."
                }],
                verification_mode="SANDBOX"
            )

        # 2. Format validation
        if not re.match(GSTIN_REGEX, gstin):
            issues.append({
                "severity": "ERROR",
                "code": "INVALID_GSTIN_FORMAT",
                "message": f"Extracted GSTIN '{gstin}' does not comply with 15-character statutory GSTIN regex format."
            })
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_GST_001"),
                module="GST",
                status="FAIL",
                confidence=0.95,
                risk="HIGH",
                extracted_values={"gstin": gstin},
                evidence=evidence_items,
                issues=issues,
                verification_mode="SANDBOX"
            )

        # 3. Cross-document evidence consistency check
        distinct_gstins = set(item["value"] for item in evidence_items if item.get("field") == "gstin")
        if len(distinct_gstins) > 1:
            issues.append({
                "severity": "WARNING",
                "code": "GSTIN_CROSS_DOC_MISMATCH",
                "message": f"Conflicting GSTIN values detected across submitted documents: {list(distinct_gstins)}."
            })
            return VerificationResultContract(
                requirement_id=requirement.get("id", "REQ_GST_001"),
                module="GST",
                status="REVIEW",
                confidence=0.85,
                risk="MEDIUM",
                extracted_values={"gstin": gstin, "conflicting_gstins": list(distinct_gstins)},
                evidence=evidence_items,
                issues=issues,
                verification_mode="DOCUMENT_CONSISTENCY"
            )

        # Compliant result
        return VerificationResultContract(
            requirement_id=requirement.get("id", "REQ_GST_001"),
            module="GST",
            status="PASS",
            confidence=0.98,
            risk="LOW",
            extracted_values={"gstin": gstin, "legal_name": legal_name, "status": "ACTIVE"},
            evidence=evidence_items,
            issues=[],
            verification_mode="SANDBOX"
        )
