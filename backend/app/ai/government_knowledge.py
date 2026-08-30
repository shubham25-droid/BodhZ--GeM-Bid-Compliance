import re
from typing import Optional, Dict, Any

class GovernmentProcurementEncyclopedia:
    """
    Comprehensive, authoritative repository of Indian Public Procurement Rules,
    GeM Guidelines, GFR 2017 Rules, MSME Policies, Make in India Order,
    Statutory Gateway Verification Standards, and Bid Evaluation Procedures.
    """

    KNOWLEDGE_BASE = {
        # 1. COMPLETE TECHNICAL EVALUATION PROCEDURE ON GEM
        "technical_evaluation_process": {
            "title": "Comprehensive Technical Bid Evaluation Process for Server & IT Tenders on GeM",
            "keywords": [
                "technical evaluation", "evaluation process", "process of technical evaluation",
                "how to evaluate", "server tender evaluation", "evaluation procedure", "bid evaluation steps"
            ],
            "content": (
                "Technical Bid Evaluation on Government e-Marketplace (GeM) follows a rigorous 6-step statutory procedure under GFR 2017:\n\n"
                "1. Pre-Qualification & EMD/Exemption Audit (GFR Rule 170):\n"
                "   • Verification of Earnest Money Deposit (EMD) or statutory exemption certificates (Udyam MSME or DPIIT Startup certificate).\n"
                "   • Verification of signed Bid Security Declaration for exempt entities.\n\n"
                "2. Automated 13-Node Statutory Gateway Verification:\n"
                "   • Node 1 (GSTN): Active registration and regular GSTR-3B monthly filing.\n"
                "   • Node 2 (Income Tax): Valid PAN linked with GSTIN, 206AB compliance.\n"
                "   • Node 3 (Udyam MSME): Valid URN and relevant NIC manufacturing/service codes.\n"
                "   • Node 4 (OEM MAF): Direct Manufacturer Authorization Form with valid validity dates and direct OEM warranty backing.\n"
                "   • Node 5 (GeM Incident Management): Debarred/Suspended/Blacklist checks.\n"
                "   • Node 6 (MCA21): Active company status and Director DINs.\n\n"
                "3. Document Intelligence & OCR Extraction:\n"
                "   • Automated extraction of legal business names, turnover figures, past experience certificates, and ISO/BIS certificates from uploaded PDF bundles.\n"
                "   • Cross-document consistency verification (detecting name variations between PAN, GST, and Bid Forms).\n\n"
                "4. Technical Specification Compliance Matrix:\n"
                "   • Clause-by-clause audit of technical specifications (CPU cores, RAM capacity, NVMe storage, RAID controllers, redundant power supplies).\n"
                "   • Identification of any material deviation or non-conformity.\n\n"
                "5. Technical Evaluation Committee (TEC) Review & Clarification Window:\n"
                "   • For non-material minor discrepancies, a time-bound clarification is issued via GeM clarification portal.\n"
                "   • Finalization of technical qualification scores (0-100) and risk tier assignments.\n\n"
                "6. Financial Bid Opening & Commercial Stage:\n"
                "   • Only technically qualified bidders (Score >= 70, LOW/MEDIUM risk) proceed to commercial price bid opening or Reverse Auction (RA)."
            )
        },

        # 2. LAND BORDER EXEMPTIONS (NEPAL, BHUTAN, BANGLADESH)
        "land_border_exemptions": {
            "title": "GFR 2017 Rule 144(xi) - Land Border Restrictions & Neighboring Country Exemptions",
            "keywords": [
                "nepal", "bhutan", "bangladesh", "land border exemption", "lines of credit", "line of credit",
                "development assistance", "nepal bid", "bhutan bid"
            ],
            "content": (
                "Applicability of GFR Rule 144(xi) to Neighboring Countries (Nepal, Bhutan, Bangladesh):\n\n"
                "1. General Rule: Bidders from countries sharing a land border with India require mandatory DPIIT registration and security clearance.\n\n"
                "2. Statutory Exemption (Order F.No.6/18/2019-PPD):\n"
                "   • Countries to which the Government of India has extended Lines of Credit (LoC) or in which the Government of India is actively engaged in development projects are FULLY EXEMPTED from prior DPIIT registration.\n"
                "   • Eligible Exempt Countries: Nepal, Bhutan, Bangladesh, Maldives, Mauritius, and Sri Lanka.\n\n"
                "3. Conclusion for Procurement Officers:\n"
                "   • A bonafide company from Nepal, Bhutan, or Bangladesh CAN participate in Indian public procurement tenders WITHOUT requiring prior DPIIT registration under Rule 144(xi), provided they fulfill all standard technical and commercial criteria."
            )
        },

        # 3. GFR 2017 RULE 144(XI) LAND BORDER RESTRICTIONS (GENERAL)
        "gfr_144_xi": {
            "title": "GFR 2017 Rule 144(xi) - Land Border Sharing Restrictions (Public Procurement Order)",
            "keywords": ["rule 144(xi)", "144(xi)", "144 xi", "144xi", "land border sharing", "border country", "china restriction", "border rule"],
            "content": (
                "GFR 2017 Rule 144(xi) restricts public procurement from bidders of countries sharing a land border with India:\n\n"
                "1. Mandatory Registration: Any bidder, consortium member, sub-contractor, or beneficial owner from a country sharing a land border with India is eligible only if registered with the Competent Authority (DPIIT Registration Committee).\n"
                "2. Security Clearance: Political and security clearance from the Ministry of External Affairs and Ministry of Home Affairs is mandatory.\n"
                "3. Beneficial Ownership: Covers entities where an individual or company from a land border country holds >= 25% ownership, voting rights, or operational control.\n"
                "4. Exemption: Countries to which the Government of India extends lines of credit or development assistance are exempted."
            )
        },

        # 4. GFR 2017 RULE 144 GENERAL
        "gfr_144": {
            "title": "GFR 2017 Rule 144 - Fundamental Principles of Public Procurement",
            "keywords": ["rule 144", "gfr 144", "principles of procurement", "fundamental principles", "canons of financial propriety"],
            "content": (
                "GFR 2017 Rule 144 lays down the Fundamental Principles of Public Procurement for all Ministries, Departments, and CPSEs:\n\n"
                "1. Efficiency, Economy, and Transparency: Procurements must be made in a transparent, competitive, and cost-effective manner.\n"
                "2. Fair & Equal Treatment: All eligible suppliers must receive equal opportunity without restrictive or customized tender specifications.\n"
                "3. Clear Technical Specifications: Descriptions of goods/services must be generic, functional, and performance-based without mentioning brand names or trademarks.\n"
                "4. Adequate Lead Time: Minimum reasonable bidding time must be allowed to ensure genuine market competition.\n"
                "5. Public Availability: Tender notices must be published on Central Public Procurement Portal (CPPP) and Government e-Marketplace (GeM)."
            )
        },

        # 5. GFR 2017 RULE 149 (GEM MANDATORY)
        "gfr_149": {
            "title": "GFR 2017 Rule 149 - Mandatory Procurement through GeM",
            "keywords": ["rule 149", "gfr 149", "mandatory gem", "procurement through gem", "gem mandatory"],
            "content": (
                "GFR 2017 Rule 149 makes procurement of goods and services through Government e-Marketplace (GeM) mandatory for all Central Ministries, Departments, CPSEs, and Autonomous Bodies:\n\n"
                "1. Direct Purchase (Up to Rs 25,000): Available for any certified supplier meeting quality and specification criteria.\n"
                "2. L1 Purchase (Rs 25,000 to Rs 5,00,000): Mandatory online comparison of at least 3 distinct OEMs/manufacturers meeting specifications to select lowest (L1).\n"
                "3. Bidding / Reverse Auction (Above Rs 5,00,000): Mandatory creation of competitive online bids or Reverse Auction on GeM.\n"
                "4. Rate Contract & Custom Bids: For specialized goods or services not listed in standard GeM catalogs, custom bids or BOQ bids must be issued."
            )
        },

        # 6. MAKE IN INDIA (MII) ORDER & COMPARISON
        "make_in_india_comparison": {
            "title": "Comparison of Class-I vs Class-II Local Suppliers under Make in India (MII) Order",
            "keywords": [
                "compare class 1", "class 1 vs class 2", "class-i vs class-ii", "class 1 and class 2",
                "class i local supplier", "class ii local supplier", "make in india", "local content", "purchase preference"
            ],
            "content": (
                "Comparison of Class-I vs Class-II Local Suppliers under Public Procurement (Preference to Make in India) Order 2017 (Revised 2020):\n\n"
                "1. Local Content Requirement:\n"
                "   • Class-I Local Supplier: Minimum 50% local content (added value in India).\n"
                "   • Class-II Local Supplier: Minimum 20% but less than 50% local content.\n"
                "   • Non-Local Supplier: Less than 20% local content.\n\n"
                "2. Purchase Preference Eligibility:\n"
                "   • Class-I Suppliers: FULLY ELIGIBLE for 20% margin of purchase preference.\n"
                "   • Class-II Suppliers: ELIGIBLE TO BID, but NOT eligible for purchase preference.\n"
                "   • Non-Local Suppliers: BARRED from participating in tenders below Rs 200 Crore (Global Tender threshold).\n\n"
                "3. Purchase Preference Mechanism (L1 Matching):\n"
                "   • If L1 bidder is not a Class-I supplier, the lowest Class-I supplier quoting within L1 + 20% margin is invited to match L1 price for 50% of the total order quantity.\n\n"
                "4. Certification Requirements:\n"
                "   • Tenders up to Rs 10 Crore: Self-declaration of local content percentage.\n"
                "   • Tenders above Rs 10 Crore: Certificate from the Statutory Auditor or Cost Accountant."
            )
        },

        # 7. GFR 2017 RULE 170 (EMD)
        "gfr_170_emd": {
            "title": "GFR 2017 Rule 170 - Earnest Money Deposit (EMD) & Bid Security",
            "keywords": ["emd", "earnest money", "bid security", "rule 170", "gfr 170", "emd exemption", "bid security declaration"],
            "content": (
                "GFR 2017 Rule 170 governs Bid Security / Earnest Money Deposit (EMD):\n\n"
                "1. Amount: Typically 2% to 5% of the estimated contract value, valid for 45 days beyond the final bid validity period.\n"
                "2. Accepted Forms: Insurance Surety Bonds, Account Payee Demand Draft, Fixed Deposit Receipt, Banker's Cheque, or Bank Guarantee via SFMS.\n"
                "3. Mandatory Exemptions:\n"
                "   • Micro and Small Enterprises (MSEs) registered with Udyam or NSIC.\n"
                "   • Startups recognized by DPIIT.\n"
                "   • Government departments and other CPSEs.\n"
                "4. Bid Security Declaration: In lieu of EMD, exempt bidders must submit a signed Bid Security Declaration undertaking suspension from bidding for 1-2 years if they withdraw or modify bids."
            )
        },

        # 8. GFR 2017 RULE 171 (E-PBG)
        "gfr_171_epbg": {
            "title": "GFR 2017 Rule 171 - Performance Security (e-PBG)",
            "keywords": ["epbg", "pbg", "performance security", "rule 171", "gfr 171", "performance bank guarantee"],
            "content": (
                "GFR 2017 Rule 171 mandates Performance Security (e-PBG) to ensure faithful contract execution:\n\n"
                "1. Amount: Usually 3% to 5% (up to 10% for complex contracts) of total contract value.\n"
                "2. Submission Timeline: Must be furnished within 15 to 30 days of award of contract / Letter of Acceptance (LoA).\n"
                "3. Validity: Must remain valid for a period of 60 days beyond the date of completion of all contractual obligations, including warranty obligations.\n"
                "4. Electronic Verification: On GeM, e-PBG is verified automatically via SFMS (Structured Financial Messaging System) structured banking API."
            )
        },

        # 9. MSME PUBLIC PROCUREMENT POLICY
        "msme_policy": {
            "title": "Public Procurement Policy for Micro and Small Enterprises (MSEs) Order 2012",
            "keywords": ["msme", "mse", "udyam", "msme exemption", "msme preference", "25 percent", "sc st msme", "women msme"],
            "content": (
                "Public Procurement Policy for MSEs Order 2012 (Ministry of MSME):\n\n"
                "1. Mandatory Annual Quota: 25% of annual procurement by Central Ministries, Departments, and CPSEs must be from MSEs.\n"
                "2. Sub-Targets: 4% reserved for SC/ST owned MSEs, 3% reserved for Women owned MSEs.\n"
                "3. Price Preference (L1 + 15%): MSEs quoting price within L1+15% price band are allowed to supply at least 25% of the tender requirement by matching L1 price.\n"
                "4. Free Tender Documents & EMD Waiver: 100% exemption from Tender Document Fees and Earnest Money Deposit (EMD).\n"
                "5. Turnover & Experience Relaxation: Officers may relax prior experience and turnover criteria for MSEs under GFR Rule 173(i)."
            )
        },

        # 10. ALL 13 STATUTORY VERIFICATION GATEWAY NODES
        "verification_gateways": {
            "title": "BodhZ 13-Node Statutory Verification Gateway Architecture",
            "keywords": ["13 nodes", "13 gateways", "verification gateway", "statutory nodes", "nodes", "gateways"],
            "content": (
                "BodhZ automated compliance verification spans 13 statutory government gateway nodes:\n\n"
                "1. Node 1 - GSTN Portal: Verifies Active GSTIN, return filing frequency (GSTR-3B), and legal entity structure.\n"
                "2. Node 2 - Income Tax / PAN Gateway: Verifies PAN status, name matching, and Section 206AB TDS compliance.\n"
                "3. Node 3 - Udyam MSME Register: Validates URN registration, enterprise category (Micro/Small/Medium), and NIC codes.\n"
                "4. Node 4 - OEM Authorization Gateway: Cross-checks Manufacturer Authorization Form (MAF) validity and direct warranty backing.\n"
                "5. Node 5 - GeM Incident Management: Checks Debarred, Blacklisted, and Suspended vendor lists across central portals.\n"
                "6. Node 6 - MCA21 Portal: Verifies Corporate Identity Number (CIN), active company status, Director DINs, and charge filings.\n"
                "7. Node 7 - Startup India / DPIIT: Verifies DIPP/DPIIT Certificate of Recognition and turnover exemption eligibility.\n"
                "8. Node 8 - NSIC Gateway: Checks Single Point Registration Scheme (SPRS) validity and monetary limits.\n"
                "9. Node 9 - EPFO Gateway: Verifies Establishment Registration and regular monthly ECR contribution payments.\n"
                "10. Node 10 - ESIC Portal: Checks employer insurance code validity and employee compliance.\n"
                "11. Node 11 - DigiLocker Gateway: Cryptographically verifies authentic certificates issued by Indian government authorities.\n"
                "12. Node 12 - BIS / Quality Gateway: Checks ISI, CRS marks, and laboratory test reports against mandatory standards.\n"
                "13. Node 13 - Land Border Rule 144(xi) Gateway: Checks DPIIT registration for foreign bidders and consortium partners."
            )
        },

        # 11. REVERSE AUCTION (RA) RULES
        "reverse_auction": {
            "title": "Reverse Auction (RA) Rules on GeM",
            "keywords": ["reverse auction", "ra", "ra rules", "auto extension", "decrement"],
            "content": (
                "Reverse Auction (RA) Guidelines on GeM:\n\n"
                "1. Elimination of Non-Responsive Bidders: Only technically qualified bidders participate in RA.\n"
                "2. Elimination Rule on GeM: For tenders with more than 6 qualified bidders, bottom 50% or lowest rankers may be eliminated from RA based on tender terms.\n"
                "3. Auto-Extension: If a bid is submitted in the last 10 minutes of the auction, the auction is automatically extended by 15 minutes.\n"
                "4. Minimum Decrement: Bids must be decreased by a predefined minimum decrement percentage or amount.\n"
                "5. Final L1 Award: The lowest price at the close of RA becomes the final commercial L1."
            )
        },

        # 12. BIDDER DISQUALIFICATION GROUNDS
        "disqualification_grounds": {
            "title": "Statutory Grounds for Bidder Disqualification in Public Procurement",
            "keywords": ["disqualification", "grounds for disqualification", "why bidder disqualified", "rejection of bid", "blacklisting"],
            "content": (
                "Statutory Grounds for Disqualifying a Bidder under GFR 2017 & GeM Terms:\n\n"
                "1. Non-Submission / Invalid EMD: Failure to furnish EMD or valid MSE/Startup exemption certificate.\n"
                "2. Expired OEM Authorization: Expired or unverified Manufacturer Authorization Form (MAF) for OEM-backed goods.\n"
                "3. Inactive / Cancelled GSTIN: Inactive GST registration on GSTN portal.\n"
                "4. Blacklisting / Debarment: Active debarment under GFR Rule 151 or GeM Incident Management.\n"
                "5. Land Border Non-Compliance: Bidders from land border sharing countries lacking DPIIT registration under Rule 144(xi).\n"
                "6. Material Technical Deviation: Failure to meet mandatory specifications in the technical compliance sheet.\n"
                "7. Fraudulent / Manipulated Documents: Submission of forged or altered certificates (triggers criminal prosecution and debarment up to 3 years)."
            )
        }
    }

    @classmethod
    def lookup(cls, query: str) -> Optional[str]:
        q_clean = query.strip().lower()

        # Collect all keywords paired with their topic, sorted by length descending
        all_rules = []
        for topic_key, topic_data in cls.KNOWLEDGE_BASE.items():
            for kw in topic_data["keywords"]:
                all_rules.append((kw, topic_data))

        all_rules.sort(key=lambda x: len(x[0]), reverse=True)

        for kw, topic_data in all_rules:
            if kw in q_clean or re.search(r"\b" + re.escape(kw) + r"\b", q_clean):
                return f"{topic_data['title']}\n\n{topic_data['content']}"

        return None
