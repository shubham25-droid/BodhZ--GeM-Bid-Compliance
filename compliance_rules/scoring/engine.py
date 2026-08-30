"""Multidimensional Compliance Scoring Algorithm (0–100 Scale)."""
from typing import Dict, Any

class ComplianceScoringEngine:
    """Calculates weighted multi-criteria scores."""
    @staticmethod
    def calculate_score(evaluation_factors: Dict[str, bool]) -> Dict[str, Any]:
        weights = {
            "gst_valid": 15,
            "udyam_valid": 10,
            "turnover_met": 25,
            "experience_met": 25,
            "oem_maf_valid": 15,
            "land_border_cleared": 10
        }
        total_score = sum(weights.get(k, 0) for k, v in evaluation_factors.items() if v)
        risk = "LOW" if total_score >= 80 else ("MEDIUM" if total_score >= 60 else "HIGH")
        return {
            "score": total_score,
            "max_score": 100,
            "risk_level": risk,
            "breakdown": weights
        }
