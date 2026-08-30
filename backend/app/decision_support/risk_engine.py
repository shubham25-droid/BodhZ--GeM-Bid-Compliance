from typing import List
from app.verification_gateway.base_connector import VerificationResultContract


# --------------------------------------------------
# RISK ASSESSMENT ENGINE
# --------------------------------------------------
class RiskEngine:
    """
    Evaluates the overall Bidder Risk Level tier (LOW, MEDIUM, HIGH, CRITICAL)
    based on mandatory failures, unresolved inconsistencies, or missing documents.
    """

    @classmethod
    def evaluate_risk_level(
        cls, compliance_score: int, verification_results: List[VerificationResultContract]
    ) -> str:
        """
        Determines risk level:
        - CRITICAL: Any mandatory statutory check status is FAIL with severe risk.
        - HIGH: Compliance score < 50 or multiple mandatory checks FAIL/REVIEW.
        - MEDIUM: Compliance score between 50 and 84 or unresolved identity inconsistencies.
        - LOW: Compliance score >= 85 with all mandatory checks PASS.
        """
        has_critical_failure = any(r.status == "FAIL" and r.risk == "HIGH" for r in verification_results)
        has_review = any(r.status == "REVIEW" for r in verification_results)
        fail_count = sum(1 for r in verification_results if r.status == "FAIL")

        if has_critical_failure or fail_count >= 2:
            return "CRITICAL"
        elif compliance_score < 60 or fail_count == 1:
            return "HIGH"
        elif has_review or compliance_score < 85:
            return "MEDIUM"
        else:
            return "LOW"
