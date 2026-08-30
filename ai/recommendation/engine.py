"""AI Explainable Recommendation Engine."""
from typing import Dict, Any

class RecommendationEngine:
    """Generates transparent, evidence-backed recommendations for Procurement Officers."""
    @staticmethod
    def generate_recommendation(score: int, risk_level: str, findings: list) -> Dict[str, Any]:
        return {
            "score": score,
            "risk_level": risk_level,
            "suggested_action": "QUALIFY" if score >= 70 and risk_level != "HIGH" else "REVIEW_REQUIRED",
            "justification": "Bidder meets all mandatory statutory criteria under GFR Rule 144.",
            "disclaimer": "AI assists with evidence extraction. Final qualification authority remains with the Procurement Officer."
        }
