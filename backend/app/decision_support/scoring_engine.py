from typing import List, Dict, Any
from app.verification_gateway.base_connector import VerificationResultContract


# --------------------------------------------------
# COMPLIANCE SCORING ENGINE
# --------------------------------------------------
class ScoringEngine:
    """
    Calculates a transparent, configuration-driven Compliance Score (0–100)
    based on requirement weights and verification outcomes.
    """

    @classmethod
    def calculate_compliance_score(
        cls, verification_results: List[VerificationResultContract], requirements: List[Dict[str, Any]]
    ) -> int:
        """
        Computes weighted score: PASS = 100% of weight, REVIEW = 50% of weight, FAIL = 0% of weight.
        Returns integer score between 0 and 100.
        """
        if not requirements:
            return 100

        total_weight = sum(r.get("weight", 20) for r in requirements)
        earned_score = 0.0

        req_weight_map = {r.get("id", f"REQ_{i}"): r.get("weight", 20) for i, r in enumerate(requirements)}
        module_weight_map = {r.get("module", "").upper(): r.get("weight", 20) for r in requirements}

        for res in verification_results:
            weight = req_weight_map.get(res.requirement_id, module_weight_map.get(res.module.upper(), 20))
            if res.status == "PASS":
                earned_score += weight
            elif res.status == "REVIEW":
                earned_score += (weight * 0.60)
            elif res.status == "FAIL":
                earned_score += 0.0

        final_score = int(round((earned_score / max(total_weight, 1)) * 100))
        return max(0, min(100, final_score))
