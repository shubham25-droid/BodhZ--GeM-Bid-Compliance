import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ==================================================
# REAL-WORLD GOVERNMENT TENDER REQUIREMENT EXTRACTOR
# ==================================================
# Purpose: Automatically extracts structured eligibility rules from real Indian
#          Government, CPSE, and State RFP / NIT documents (DTE, NFL, ICAR, GeM).
# ==================================================

class TenderRequirementExtractor:
    """
    Automated Tender Intelligence Extractor for Indian Public Procurement.
    Parses real-world RFP / NIT tender text and extracts exact statutory eligibility criteria.
    """

    @classmethod
    def extract_requirements(
        cls, tender_text: str, category: Optional[str] = "General", title: Optional[str] = ""
    ) -> List[Dict[str, Any]]:
        """
        Parses tender notice text against standard Indian procurement statutory clauses:
        - GSTIN & 3B Monthly Return Filing
        - PAN / Income Tax Compliance
        - Legal Entity Registration (Companies Act / LLP / Shop Act / Sole Proprietorship)
        - CA Audited Average Annual Turnover & Positive Net Worth
        - Similar Works / Past Project Experience (1, 2, or 3 work order thresholds)
        - OEM Manufacturer Authorization Form (MAF)
        - CERT-In Empanelment (for VAPT / Cyber Security / IT Audits)
        - Manpower / Full-time Payroll with EPFO & ESIC Registration
        - Make in India (MII) Local Content (Class-I >= 50%, Class-II >= 20%)
        - Non-Blacklisting Notarized Affidavit (Annexure-VI / Annexure-II)
        - Land Border Sharing GFR 2017 Rule 144(xi) Undertaking (Form-I / Form-II)
        - ISO 9001:2015 Quality Management Certificate
        - Udyam MSME Certificate (Public Procurement Policy 2012)
        """
        text_lower = (tender_text or "").lower()
        title_lower = (title or "").lower()
        combined = f"{title_lower} {text_lower}"

        requirements: List[Dict[str, Any]] = []

        # 1. GST Registration (Mandatory in 100% of Indian Tenders)
        requirements.append({
            "module": "GST",
            "title": "Active GSTIN Registration Certificate & GSTR-3B Monthly Return Compliance",
            "mandatory": True,
            "weight": 15,
            "rule_type": "GATEWAY_STATUS",
            "rule_config": {
                "require_active_status": True,
                "require_regular_filing": True,
                "node_id": "NODE_1_GSTN"
            }
        })

        # 2. Income Tax PAN Card & 206AB Compliance (Mandatory)
        requirements.append({
            "module": "PAN",
            "title": "Income Tax PAN / TAN Card Validity & Name Matching",
            "mandatory": True,
            "weight": 15,
            "rule_type": "IDENTITY_MATCH",
            "rule_config": {
                "require_valid_pan": True,
                "cross_check_gstin": True,
                "node_id": "NODE_2_INCOMETAX"
            }
        })

        # 3. Certificate of Incorporation / Legal Status
        if any(w in combined for w in ["incorporation", "companies act", "llp", "partnership", "shop act", "sole proprietorship", "articles of association"]):
            requirements.append({
                "module": "Incorporation",
                "title": "Certificate of Incorporation / Registration (Companies Act / LLP / Shop Act)",
                "mandatory": True,
                "weight": 10,
                "rule_type": "DOCUMENT_CONSISTENCY",
                "rule_config": {
                    "require_roc_or_shop_act": True,
                    "node_id": "NODE_5_MCA21"
                }
            })

        # 4. Financial Turnover (Audited Balance Sheet & CA Certificate)
        if any(w in combined for w in ["turnover", "audited", "balance sheet", "profit & loss", "financial year", "crore", "lacs", "lakh"]):
            turnover_match = re.search(r"(?:turnover\s*(?:of|is|min|minimum)?\s*(?:inr|rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(?:cr|crore|lakh|lacs|lac)?)", combined)
            min_desc = turnover_match.group(0).title() if turnover_match else "Minimum 3-Year Average Annual Turnover"
            requirements.append({
                "module": "Turnover",
                "title": f"CA Certified Average Annual Turnover ({min_desc}) with Audited Balance Sheets",
                "mandatory": True,
                "weight": 15,
                "rule_type": "FINANCIAL_THRESHOLD",
                "rule_config": {
                    "require_ca_certificate": True,
                    "require_3_years_audited": True
                }
            })

        # 5. Positive Net Worth (CA Certificate)
        if any(w in combined for w in ["net worth", "positive net worth"]):
            requirements.append({
                "module": "NetWorth",
                "title": "CA Certified Positive Net Worth Certificate for last 3 Financial Years",
                "mandatory": True,
                "weight": 10,
                "rule_type": "FINANCIAL_THRESHOLD",
                "rule_config": {
                    "require_positive_net_worth": True
                }
            })

        # 6. Past Project Experience / Similar Works Execution
        if any(w in combined for w in ["similar work", "similar works", "past experience", "work order", "completion certificate", "centre of excellence", "training center"]):
            requirements.append({
                "module": "PastExperience",
                "title": "Satisfactory Completion of Similar Works (Work Orders & Performance Certificates)",
                "mandatory": True,
                "weight": 15,
                "rule_type": "DOCUMENT_CONSISTENCY",
                "rule_config": {
                    "require_work_orders": True,
                    "require_completion_cert": True
                }
            })

        # 7. OEM Manufacturer Authorization Form (MAF)
        is_oem = any(w in combined for w in [
            "oem", "maf", "manufacturer authorization", "hardware", "software",
            "server", "equipment", "machinery", "thresher", "seed drill", "storage"
        ])
        if is_oem:
            requirements.append({
                "module": "OEM",
                "title": "Manufacturer Authorization Form (MAF) with Direct Warranty Backing (Annexure-8 / Annexure-3)",
                "mandatory": True,
                "weight": 15,
                "rule_type": "DOCUMENT_CONSISTENCY",
                "rule_config": {
                    "require_direct_oem_signature": True,
                    "require_valid_date_range": True,
                    "node_id": "NODE_4_OEM_GATEWAY"
                }
            })

        # 8. CERT-In Empanelment (for Cyber Security / VAPT / IT Audit tenders)
        if any(w in combined for w in ["cert-in", "cert in", "vapt", "security audit", "vulnerability assessment", "penetration testing"]):
            requirements.append({
                "module": "CERT_IN",
                "title": "Valid CERT-In Empanelment Certificate as on bid submission date",
                "mandatory": True,
                "weight": 20,
                "rule_type": "STATUTORY_AUTHORIZATION",
                "rule_config": {
                    "require_cert_in_empanelment": True
                }
            })

        # 9. Manpower / Payroll with EPF & ESIC Registration
        if any(w in combined for w in ["epfo", "epf", "esic", "esi registration", "payroll", "human resources", "pf number", "trainers"]):
            requirements.append({
                "module": "EPFO_ESIC",
                "title": "EPFO (PF) & ESIC Registration with Self-Certified Payroll Manpower Details",
                "mandatory": True,
                "weight": 10,
                "rule_type": "GATEWAY_STATUS",
                "rule_config": {
                    "require_pf_registration": True,
                    "require_esi_registration": True,
                    "node_id": "NODE_8_EPFO"
                }
            })

        # 10. Make in India (MII) Local Content Declaration (DPIIT Order 2017)
        if any(w in combined for w in ["make in india", "local content", "class i local", "class 1 local", "mii", "dpiit"]):
            requirements.append({
                "module": "MakeInIndia",
                "title": "Make in India (MII) Local Content Self-Certification (Class-I >= 50% / Class-II >= 20%)",
                "mandatory": True,
                "weight": 10,
                "rule_type": "STATUTORY_DECLARATION",
                "rule_config": {
                    "require_local_content_percentage": True
                }
            })

        # 11. Non-Blacklisting Undertaking / Notarized Affidavit
        if any(w in combined for w in ["blacklist", "blacklisting", "non-blacklisting", "debarred", "notarized affidavit", "annexure-vi", "annexure-ii"]):
            requirements.append({
                "module": "NonBlacklisting",
                "title": "Notarized Non-Blacklisting Affidavit on Non-Judicial Stamp Paper (Annexure-VI / II)",
                "mandatory": True,
                "weight": 10,
                "rule_type": "STATUTORY_DECLARATION",
                "rule_config": {
                    "require_notary_seal": True,
                    "require_stamp_paper": True,
                    "node_id": "NODE_10_CPPP_DEBARMENT"
                }
            })

        # 12. GFR 2017 Rule 144(xi) Land Border Sharing Compliance
        if any(w in combined for w in ["land border", "rule 144(xi)", "144(xi)", "form-i", "form-ii", "neighboring country"]):
            requirements.append({
                "module": "LandBorder",
                "title": "GFR 2017 Rule 144(xi) Land Border Country Compliance Undertaking (Form-I / II)",
                "mandatory": True,
                "weight": 10,
                "rule_type": "STATUTORY_DECLARATION",
                "rule_config": {
                    "require_undertaking": True,
                    "node_id": "NODE_11_LAND_BORDER"
                }
            })

        # 13. ISO 9001:2015 Quality Management Certification
        if any(w in combined for w in ["iso 9001", "iso9001", "quality management", "iso certification"]):
            requirements.append({
                "module": "ISO",
                "title": "Valid ISO 9001:2015 Quality Management System (QMS) Certificate",
                "mandatory": True,
                "weight": 10,
                "rule_type": "DOCUMENT_CONSISTENCY",
                "rule_config": {
                    "require_valid_iso": True,
                    "node_id": "NODE_12_BIS_ISO"
                }
            })

        # 14. Udyam MSME Registration (Public Procurement Policy 2012)
        requirements.append({
            "module": "Udyam",
            "title": "Udyam MSME Registration Certificate for EMD Waiver & Public Procurement Benefits",
            "mandatory": False,
            "weight": 10,
            "rule_type": "EXEMPTION_VERIFY",
            "rule_config": {
                "allow_emd_waiver": True,
                "node_id": "NODE_3_UDYAM_MSME"
            }
        })

        # Normalize weights so they proportionally sum to 100
        total_weight = sum(r["weight"] for r in requirements)
        if total_weight > 0:
            for r in requirements:
                r["weight"] = max(5, int(round((r["weight"] / total_weight) * 100)))

        return requirements
