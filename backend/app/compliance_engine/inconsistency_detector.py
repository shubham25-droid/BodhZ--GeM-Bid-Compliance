import re
from typing import Dict, Any, List


# --------------------------------------------------
# GENERALIZED STRING NORMALIZATION & SIMILARITY HELPERS
# --------------------------------------------------
def normalize_business_name(name: str) -> str:
    """Strips punctuation and corporate entity suffixes for pure root entity comparison."""
    if not name:
        return ""
    n = re.sub(r"[^\w\s]", " ", name.lower())
    # Remove standard business suffix variations
    n = re.sub(
        r"\b(pvt|private|ltd|limited|llp|inc|incorporated|corp|corporation|co|company|enterprises|enterprise|solutions|systems|technologies|tech)\b",
        "",
        n
    )
    return " ".join(n.split())


def calculate_entity_similarity(name1: str, name2: str) -> float:
    """Calculates Jaccard token overlap between normalized entity names."""
    norm1 = normalize_business_name(name1)
    norm2 = normalize_business_name(name2)
    t1 = set(norm1.split())
    t2 = set(norm2.split())
    if not t1 or not t2:
        return 0.0
    return len(t1.intersection(t2)) / len(t1.union(t2))


# --------------------------------------------------
# CROSS-DOCUMENT INCONSISTENCY DETECTOR
# --------------------------------------------------
class InconsistencyDetector:
    """
    Generalized cross-document audit engine.
    Compares identifiers (GSTIN, PAN, Udyam) and legal names across all submitted bidder PDFs
    and external portal records to flag conflicting values, identity mismatches, or altered text.
    """

    @classmethod
    def detect_cross_document_inconsistencies(
        cls, bidder_profile: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Scans all extracted document snippets and profile data to identify
        conflicting GSTINs, legal name variations, or mismatched PAN numbers.
        """
        inconsistencies: List[Dict[str, Any]] = []

        # 1. Collect all extracted GSTINs across document pages
        gstin_map: Dict[str, List[Dict[str, Any]]] = {}
        for ext in extractions:
            snippet = ext.get("text_snippet", "") or ext.get("field_value", "")
            matches = re.findall(r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}", snippet)
            for gstin in matches:
                if gstin not in gstin_map:
                    gstin_map[gstin] = []
                gstin_map[gstin].append({
                    "document_id": ext.get("document_id"),
                    "page_number": ext.get("page_number", 1),
                    "snippet": snippet[:150]
                })

        if len(gstin_map) > 1:
            inconsistencies.append({
                "severity": "CRITICAL",
                "code": "GSTIN_CROSS_DOCUMENT_MISMATCH",
                "message": f"Conflicting GSTIN values detected across submitted document pages: {list(gstin_map.keys())}",
                "details": gstin_map
            })

        # 2. Check for PAN mismatches across documents
        pan_map: Dict[str, List[Dict[str, Any]]] = {}
        for ext in extractions:
            snippet = ext.get("text_snippet", "") or ext.get("field_value", "")
            matches = re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", snippet)
            for pan in matches:
                if pan not in pan_map:
                    pan_map[pan] = []
                pan_map[pan].append({
                    "document_id": ext.get("document_id"),
                    "page_number": ext.get("page_number", 1),
                    "snippet": snippet[:150]
                })

        if len(pan_map) > 1:
            inconsistencies.append({
                "severity": "WARNING",
                "code": "PAN_CROSS_DOCUMENT_MISMATCH",
                "message": f"Multiple PAN numbers detected across submitted document bundle: {list(pan_map.keys())}",
                "details": pan_map
            })

        # 3. Dynamic Generalized Legal Name Spelling / Suffix Variation Detector
        profile_name = bidder_profile.get("legal_name", "").strip()
        if profile_name:
            for ext in extractions:
                snippet = ext.get("text_snippet", "") or ext.get("field_value", "")
                # Search for candidate business names inside document snippet
                lines = snippet.split("\n")
                for line in lines:
                    line_clean = line.strip()
                    if len(line_clean) < 4:
                        continue

                    # If line contains common business keywords
                    if any(w in line_clean.lower() for w in ["pvt", "ltd", "limited", "solutions", "systems", "technologies", "tech", "enterprises", "corporation"]):
                        # Check if line differs from profile_name but shares core tokens
                        if line_clean.upper() != profile_name.upper():
                            sim = calculate_entity_similarity(profile_name, line_clean)
                            if sim >= 0.35:
                                inconsistencies.append({
                                    "severity": "WARNING",
                                    "code": "LEGAL_NAME_SPELLING_VARIATION",
                                    "message": (
                                        f"Minor identity legal name variation detected: Bid Profile lists '{profile_name}' "
                                        f"whereas document evidence lists '{line_clean}'."
                                    ),
                                    "evidence": {
                                        "document_id": ext.get("document_id"),
                                        "page_number": ext.get("page_number", 1),
                                        "snippet": snippet[:150]
                                    }
                                })
                                break

        return inconsistencies
