from typing import List, Dict, Any
from app.verification_gateway.base_connector import VerificationResultContract


# --------------------------------------------------
# GROUNDED AI RECOMMENDATION GENERATOR
# --------------------------------------------------
class RecommendationGenerator:
    """
    Synthesizes evidence-grounded decision support recommendations for Procurement Officers.
    Strictly avoids hallucination by citing empirical verification findings and source documents.
    """

    @classmethod
    def generate_recommendation(
        cls, bidder_name: str, compliance_score: int, risk_level: str, verification_results: List[VerificationResultContract]
    ) -> str:
        """Generates plain-language decision support recommendation citing exact findings."""
        passed_modules = [r.module for r in verification_results if r.status == "PASS"]
        review_modules = [r.module for r in verification_results if r.status == "REVIEW"]
        failed_modules = [r.module for r in verification_results if r.status == "FAIL"]

        findings_summary: List[str] = []
        for r in verification_results:
            for issue in r.issues:
                findings_summary.append(f"[{r.module}] {issue.get('message', '')}")

        rec_lines = [
            f"Bidder '{bidder_name}' achieved a Compliance Score of {compliance_score}/100 with an assessed Risk Level of {risk_level}."
        ]

        if passed_modules:
            rec_lines.append(f"Satisfactory evidence verified for: {', '.join(passed_modules)}.")

        if review_modules:
            rec_lines.append(f"Attention/Review required for module(s): {', '.join(review_modules)} due to document inconsistency or interpretation requirements.")

        if failed_modules:
            rec_lines.append(f"CRITICAL NON-COMPLIANCE detected for module(s): {', '.join(failed_modules)}.")

        if findings_summary:
            rec_lines.append(f"Specific Findings: {' '.join(findings_summary)}")

        rec_lines.append(
            "RECOMMENDED ACTION: Procurement Officer review is recommended before recording final qualification decision. "
            "The final qualification or disqualification decision remains 100% with the Procurement Officer."
        )

        return " ".join(rec_lines)
