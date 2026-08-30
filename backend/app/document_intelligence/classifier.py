import re
from typing import Dict, Any


# --------------------------------------------------
# DOCUMENT CLASSIFIER CLASS
# --------------------------------------------------
class DocumentClassifier:
    """
    Classifies document types based on statutory regex patterns and keyword density.
    Categories: GST_CERTIFICATE, UDYAM_CERTIFICATE, PAN_CARD, OEM_AUTHORIZATION, BID_FORM, OTHER.
    """

    # Keyword rules for document classification
    KEYWORDS = {
        "GST_CERTIFICATE": [
            r"GSTIN", r"FORM GST REG-06", r"GOVERNMENT OF INDIA", r"GOODS AND SERVICES TAX",
            r"REGISTRATION CERTIFICATE", r"TAX DEPARTMENT"
        ],
        "UDYAM_CERTIFICATE": [
            r"UDYAM", r"MINISTRY OF MICRO, SMALL", r"ENTERPRISE TYPE", r"UDYAM REGISTRATION NUMBER",
            r"MSME", r"UDYAM-"
        ],
        "PAN_CARD": [
            r"INCOME TAX DEPARTMENT", r"PERMANENT ACCOUNT NUMBER", r"GOVT OF INDIA", r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        ],
        "OEM_AUTHORIZATION": [
            r"MANUFACTURER AUTHORIZATION", r"OEM AUTHORIZATION", r"AUTHORIZATION LETTER",
            r"CERTIFICATE OF AUTHORIZATION", r"DISTRIBUTOR AUTHORIZATION", r"WE HEREBY AUTHORIZE"
        ],
        "BID_FORM": [
            r"BID SUBMISSION FORM", r"TENDER NO", r"DECLARATION BY BIDDER", r"GEM TENDER", r"FINANCIAL BID"
        ]
    }

    @classmethod
    def classify_document(cls, full_text: str) -> Dict[str, Any]:
        """
        Scores input document text against category regex keywords
        and returns the top classification category and confidence score.
        """
        text_upper = full_text.upper()
        scores: Dict[str, int] = {category: 0 for category in cls.KEYWORDS}

        for category, patterns in cls.KEYWORDS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_upper)
                scores[category] += len(matches) * 2

        best_category = max(scores, key=scores.get)  # type: str
        top_score = scores[best_category]

        if top_score == 0:
            return {"category": "OTHER", "confidence": 0.50, "matched_score": 0}

        confidence = round(min(0.60 + (top_score * 0.08), 0.99), 2)
        return {
            "category": best_category,
            "confidence": confidence,
            "matched_score": top_score
        }
