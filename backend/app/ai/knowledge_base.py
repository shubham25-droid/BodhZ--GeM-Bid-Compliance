# --------------------------------------------------
# AUTHORITATIVE GOVERNMENT PROCUREMENT KNOWLEDGE BASE (PLAIN TEXT)
# --------------------------------------------------
class BodhZKnowledgeBase:
    """
    Authoritative Procurement Knowledge Base for BodhZ SIH26100.
    Provides plain text definitions without markdown symbols.
    """

    BODHZ_PURPOSE = (
        "BodhZ Procurement Compliance Platform (SIH26100)\n\n"
        "BodhZ is an AI-powered integrated decision-support platform engineered for Government e-Marketplace (GeM) Procurement evaluation.\n\n"
        "Core Capabilities:\n"
        "1. Automated Requirement Extraction: Extracts statutory clauses, experience criteria, and financial thresholds from Tender PDFs.\n"
        "2. Document Intelligence and OCR: Scans and parses bidder submission forms, certificates, and invoices.\n"
        "3. Multi-Gateway Verification: Cross-verifies data across 13 statutory nodes such as GSTN, Udyam MSME, PAN, OEM Auth, and Debarment List.\n"
        "4. Compliance and Risk Scoring: Computes a transparent 0 to 100 Compliance Score and Risk Tier classification.\n"
        "5. Human Authority Mandate: Preserves 100% human Procurement Officer final qualification decision authority."
    )

    PORTALS_COUNT_ANSWER = (
        "There is no single fixed number of verification portals applicable to every bid. "
        "Verification sources are dynamically determined based on specific tender eligibility requirements and bidder claims. "
        "The SIH26100 platform evaluates sources including Udyam MSME, GSTN, PAN, Income Tax, MCA21, Startup India, DPIIT, "
        "NSIC, EPFO, ESIC, DigiLocker, Make in India local content, BIS, OEM Authorization Letters, and Debarment Registers."
    )

    OFFICER_DECISION_ANSWER = (
        "No. BodhZ AI operates strictly as a decision-support system. "
        "The final binding qualification or disqualification decision remains 100% with the Procurement Officer."
    )

    @staticmethod
    def get_general_definition(term: str) -> str:
        t = term.lower()
        if "bids" in t or "bid" in t:
            return (
                "Public Procurement Bid Definition\n\n"
                "In public procurement under GeM and Central Public Procurement Portal guidelines, a Bid represents a formal, "
                "legally binding technical and commercial offer submitted by an eligible supplier or OEM in response to an official tender.\n\n"
                "Core Components of a Bid Submission:\n"
                "Technical Bid: Specification compliance sheets, experience certificates, and OEM Manufacturer Authorization Forms.\n"
                "Financial Bid: Price schedule and BOQ rate breakdowns.\n"
                "Statutory Eligibility Instruments: GST Registration, PAN, Udyam MSME Certificate, and EMD or exemption undertakings under GFR 2017 Rule 170."
            )
        elif "tender" in t:
            return (
                "Public Tender Definition\n\n"
                "A Tender is an official public invitation issued by a Ministry, Government Department, or CPSE under GFR 2017 Rule 144, "
                "inviting competitive proposals from qualified vendors for the supply of goods, services, or execution of infrastructure works."
            )
        elif "gst" in t:
            return (
                "Goods and Services Tax Compliance\n\n"
                "GST is a mandatory indirect tax registration in India. In GeM tender evaluations, active GSTIN registration and verified tax return filing status "
                "serve as primary statutory eligibility criteria."
            )
        elif "msme" in t or "udyam" in t:
            return (
                "Udyam MSME Registration and Benefits\n\n"
                "Micro, Small and Medium Enterprises registered on the official Udyam Portal receive statutory procurement preferences under the "
                "Public Procurement Policy for MSEs Order 2012, including Earnest Money Deposit waivers and purchase preferences."
            )
        elif "ocr" in t:
            return (
                "Optical Character Recognition Engine\n\n"
                "OCR is an automated document intelligence technology used by BodhZ to extract structured text, key-value fields, GSTINs, validity dates, "
                "and legal names from scanned PDF bidder submissions for automated rule verification."
            )
        elif "pan" in t or "income tax" in t:
            return (
                "PAN and Income Tax Verification\n\n"
                "Permanent Account Number is a 10-digit legal tax identifier issued by the Income Tax Department. "
                "It is used during bid evaluation to verify legal entity identity and Section 206AB tax compliance status."
            )
        elif "gfr" in t or "rule 170" in t:
            return (
                "GFR 2017 Rule 170 EMD Exemption\n\n"
                "Under General Financial Rules 2017 Rule 170, Earnest Money Deposit is waived for Micro and Small Enterprises "
                "registered on Udyam and DPIIT Recognized Startups upon submission of valid registration proof."
            )
        elif "finding" in t:
            return (
                "Procurement Finding Definition\n\n"
                "In procurement and compliance review, a finding is a documented observation or evidence result identified during tender evaluation or audit.\n\n"
                "A finding typically highlights:\n"
                "1. Statutory compliance gaps or missing certificates\n"
                "2. Adverse legal name or date discrepancies across documents\n"
                "3. Verified status confirmations from statutory gateways (GSTN, Udyam, PAN)\n"
                "4. Unclear items requiring manual Procurement Officer review"
            )
        elif "compliance score" in t or "score" in t:
            return (
                "Compliance Score Definition\n\n"
                "A Compliance Score is an automated metric ranging from 0 to 100 that indicates how thoroughly a bidder satisfies tender eligibility criteria, statutory rules, and document verifications.\n\n"
                "Key Evaluation Factors:\n"
                "Active statutory registrations (GSTN, Udyam MSME, PAN)\n"
                "Valid OEM Authorization Letters\n"
                "Document consistency and OCR extraction accuracy\n"
                "Absence of debarment or blacklisting records\n\n"
                "Note: The Compliance Score is advisory. The final qualification decision remains 100% with the Procurement Officer."
            )
        elif "gem" in t or "portal" in t:
            return (
                "Government e-Marketplace\n\n"
                "GeM is India's official online portal for public procurement of goods and services by Central and State Ministries, Departments, and CPSEs."
            )
        elif "procurement" in t:
            return (
                "Public Procurement Overview\n\n"
                "Public procurement is the government process of purchasing goods, services, and works from commercial suppliers in a transparent, competitive, and fair manner under GFR 2017 rules."
            )
        
        return ""
