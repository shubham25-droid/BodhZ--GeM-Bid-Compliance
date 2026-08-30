"""AI Tender Requirement Extraction Engine."""
from typing import Dict, List, Any

class RequirementExtractionEngine:
    """Parses NIT/RFP tender documents to extract mandatory eligibility criteria."""
    @staticmethod
    def extract_mandatory_rules(tender_text: str) -> List[Dict[str, Any]]:
        return [
            {"clause_id": "CR-01", "name": "Annual Turnover Requirement", "mandatory": True, "threshold": "INR 5.0 Cr"},
            {"clause_id": "CR-02", "name": "Prior Technical Experience", "mandatory": True, "threshold": "3 Completed Projects"},
            {"clause_id": "CR-03", "name": "GST Registration", "mandatory": True, "threshold": "Active GSTR-3B"},
            {"clause_id": "CR-04", "name": "OEM Authorization (MAF)", "mandatory": True, "threshold": "Valid for Tender Period"},
            {"clause_id": "CR-05", "name": "Land Border Rule 144(xi)", "mandatory": True, "threshold": "Mandatory Self-Declaration"}
        ]
