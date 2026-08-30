from typing import Dict, Any, List
from app.verification_gateway.gateway import VerificationGateway
from app.verification_gateway.base_connector import VerificationResultContract
from app.compliance_engine.inconsistency_detector import InconsistencyDetector


# --------------------------------------------------
# AI COMPLIANCE ENGINE CLASS
# --------------------------------------------------
class ComplianceEngine:
    """
    Core AI Compliance & Verification Engine.
    Orchestrates Tender Requirement matching vs Bidder Evidence vs Verification Gateway checks,
    detecting Missing, Inconsistent, and Non-Compliant findings.
    """

    def __init__(self):
        self.gateway = VerificationGateway()

    async def evaluate_bid_compliance(
        self, bidder_profile: Dict[str, Any], requirements: List[Dict[str, Any]], extractions: List[Dict[str, Any]]
    ) -> List[VerificationResultContract]:
        """
        Evaluates a bidder submission across all active tender requirements,
        running module verification connectors and cross-document inconsistency checks.
        """
        results: List[VerificationResultContract] = []

        # 1. Run verification connectors per requirement
        for req in requirements:
            ver_result = await self.gateway.run_verification_for_requirement(
                bidder_data=bidder_profile,
                requirement=req,
                extractions=extractions
            )
            results.append(ver_result)

        # 2. Run Cross-Document Inconsistency Checks
        cross_inconsistencies = InconsistencyDetector.detect_cross_document_inconsistencies(
            bidder_profile=bidder_profile,
            extractions=extractions
        )

        # 3. Inject cross-document inconsistency findings into relevant module results
        if cross_inconsistencies:
            for result in results:
                if result.module in ("GST", "PAN"):
                    for inc in cross_inconsistencies:
                        result.issues.append({
                            "severity": inc.get("severity", "WARNING"),
                            "code": inc.get("code", "INCONSISTENCY_DETECTED"),
                            "message": inc.get("message", "")
                        })
                        if result.status == "PASS":
                            result.status = "REVIEW"
                            result.risk = "MEDIUM"

        return results
