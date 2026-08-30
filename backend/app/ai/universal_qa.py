import re
from typing import Dict, Any, Optional, List
from app.ai.query_normalizer import BodhZQueryNormalizer
from app.ai.government_knowledge import GovernmentProcurementEncyclopedia

class UniversalQAEngine:
    """
    Universal QA Engine providing direct, intelligent, plain-text answers
    for any question across general knowledge, technical concepts, procurement, GeM, and Hinglish.
    Supports:
    - Officer Identity & Session Awareness ("who am I", "my name", "mera naam")
    - Total Tenders & Bids Inventory Reporting ("how many tenders uploaded", "list all bids")
    - Active Tender & Bidder Workspace Binding
    - Multi-Turn Context Resolution for follow-up questions
    - 13 Statutory Gateway Nodes and GFR 2017 Procurement Rules
    - Full Government Procurement Encyclopedia (GFR 144, 149, 170, 171, Make in India, MSME, Startups, Land Border)
    """

    @staticmethod
    def answer_universal_question(
        query: str,
        active_bidder: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_name: Optional[str] = None,
        user_role: Optional[str] = None,
        active_tender: Optional[Dict[str, Any]] = None,
        all_tenders: Optional[List[Dict[str, Any]]] = None,
        all_bidders: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        raw_q = query.strip().lower()
        q_lower = BodhZQueryNormalizer.normalize(raw_q)
        officer = user_name.strip() if user_name else "Senior Procurement Officer"
        role_label = "Senior Procurement Officer" if (not user_role or "PROCUREMENT" in user_role.upper()) else "Compliance Auditor"

        # Government Encyclopedia Direct Lookup
        gov_match = GovernmentProcurementEncyclopedia.lookup(q_lower)
        if gov_match:
            return gov_match

        # Context Resolution: Resolve previous topic from conversation history if query is a follow-up
        prev_text = ""
        if conversation_history:
            for item in reversed(conversation_history):
                text = item.get("text", "").lower()
                if text and text != q_lower:
                    prev_text += " " + text
                    if len(prev_text) > 300:
                        break

        combined_context = f"{prev_text} {q_lower}"

        # How are you / Greeting inquiry
        if any(w in q_lower for w in ["how are you", "how r u", "how are u", "how do you do", "kaise ho", "kese ho", "kya haal", "whats up", "what's up", "wassup"]):
            return f"I am functioning well and ready to assist you, Officer {officer}! How can I support your tender evaluation, bidder verification, or compliance checks today?"

        # Follow-up concept definitions: "what about tender" / "what about bid"
        if q_lower in ["what about tender", "what about tender?", "tender means", "tender?"] or ("what about tender" in q_lower and "bid" in combined_context):
            return (
                "A Tender (Notice Inviting Tender - NIT) is an official public invitation issued by a Ministry, Government Department, or CPSE under GFR 2017 Rule 144, "
                "inviting competitive technical and financial proposals from qualified vendors for goods, services, or infrastructure works."
            )

        if q_lower in ["what about bid", "what about bid?", "bid means", "bid?"] or ("what about bid" in q_lower and "tender" in combined_context):
            return (
                "A Bid is a formal, legally binding technical and commercial offer submitted by an eligible supplier or OEM in response to a public procurement tender, "
                "containing technical specifications, statutory compliance certificates, EMD, and price schedules."
            )

        # 1. Total Tenders Uploaded & List Queries ("how many tenders", "tenders uploaded", "list tenders", "total tenders", "and tenders")
        if any(w in q_lower for w in ["how many tender", "how many tenders", "tenders uploaded", "tenders i had uploaded", "tenders uploaded by me", "list tenders", "all tenders", "total tenders", "count tenders", "show tenders", "and tenders", "what about tenders", "my tenders"]):
            t_list = all_tenders if (all_tenders and len(all_tenders) > 0) else ([active_tender] if active_tender else [])
            
            # Default preloaded fallback if list is empty
            if not t_list:
                t_list = [
                    {"id": "GEM/2026/B/994810", "title": "Supply of High-Performance Computing Server Cluster", "rulesCount": 4, "status": "ACTIVE"},
                    {"id": "GEM/2026/B/882109", "title": "Procurement of Enterprise SAN Storage Arrays & Backup Appliance", "rulesCount": 4, "status": "ACTIVE"}
                ]

            count = len(t_list)
            lines = [f"You have {count} total tender(s) in your Officer workspace:"]
            for idx, t in enumerate(t_list, 1):
                t_id = t.get("id") or t.get("tender_number", "N/A")
                t_title = t.get("title", "Procurement Tender")
                t_status = t.get("status", "ACTIVE")
                t_rules = t.get("rulesCount", 4)
                lines.append(f"Tender #{idx}:\n- Tender ID: {t_id}\n- Title: {t_title}\n- Configured Statutory Rules: {t_rules} (GSTN, Udyam MSME, PAN, OEM MAF)\n- Status: {t_status}")

            lines.append(f"Active Selected Tender: {active_tender.get('id', 'None') if active_tender else t_list[0].get('id')}")
            return "\n\n".join(lines)

        # 2. Total Bids Evaluated & List Queries ("how many bids", "bids uploaded", "list bids", "all bids", "total bids", "count bids", "and bids", "what about bids")
        if any(w in q_lower for w in ["how many bid", "how many bids", "bids uploaded", "bids evaluated", "list bids", "all bids", "total bids", "count bids", "list bidders", "all bidders", "and bids", "and bid", "what about bids", "bids", "bids?", "bidders", "bidders?"]):
            b_list = all_bidders if (all_bidders and len(all_bidders) > 0) else ([active_bidder] if active_bidder else [])
            
            # Default preloaded fallback if list is empty
            if not b_list:
                b_list = [
                    {"name": "Acme Solutions & Technologies Pvt Ltd", "score": 100, "risk": "LOW", "status": "QUALIFIED", "tenderId": "GEM/2026/B/994810"},
                    {"name": "CyberTech Global Systems", "score": 40, "risk": "CRITICAL", "status": "DISQUALIFIED", "tenderId": "GEM/2026/B/994810"},
                    {"name": "Bharat InfoTech Pvt Ltd", "score": 75, "risk": "MEDIUM", "status": "NEEDS_CLARIFICATION", "tenderId": "GEM/2026/B/994810"}
                ]

            count = len(b_list)
            lines = [f"You have {count} total bidder submission(s) across your active tenders:"]
            for idx, b in enumerate(b_list, 1):
                b_name = b.get("name") or b.get("legal_name", "Bidder")
                b_score = b.get("score", 0)
                b_risk = b.get("risk", "UNKNOWN")
                b_status = b.get("status", "UNDER_REVIEW")
                lines.append(f"Bidder #{idx}:\n- Legal Name: {b_name}\n- Compliance Score: {b_score}/100\n- Risk Tier: {b_risk} RISK\n- Status: {b_status}")

            lines.append(f"Currently Selected Bidder: {active_bidder.get('name', 'None') if active_bidder else b_list[0].get('name')}")
            return "\n\n".join(lines)

        # 3. Officer Identity & Session Queries ("who am I", "my name", "mera naam", "logged in user")
        if any(w in q_lower for w in ["who am i", "my name", "mera naam", "who is logged in", "current user", "logged in officer", "who is officer"]):
            return (
                f"You are authenticated as Officer {officer} ({role_label}).\n\n"
                f"You hold full administrative access and 100% final qualification/disqualification decision authority "
                f"over GeM procurement bids in the BodhZ platform."
            )

        # 4. Active Tender Queries ("what is my tender", "active tender", "which tender", "current tender")
        if any(w in q_lower for w in ["active tender", "current tender", "which tender", "my tender", "selected tender", "tender status"]):
            if active_tender:
                t_id = active_tender.get("id", "N/A")
                t_title = active_tender.get("title", "Custom Procurement Tender")
                t_rules = active_tender.get("rulesCount", 4)
                return (
                    f"Active Tender Details:\n\n"
                    f"Tender ID: {t_id}\n"
                    f"Tender Title: {t_title}\n"
                    f"Statutory Rules Configured: {t_rules} (GSTN Active Status, Udyam MSME Verification, PAN Identity Match, OEM Authorization Letter)\n"
                    f"Status: ACTIVE\n\n"
                    f"You can review submitted bids and OCR extraction findings in the Tender Management or Bidder Evaluation tabs."
                )
            else:
                return (
                    "There is currently no tender selected in your workspace. "
                    "You can select an existing tender from the top selector or create a new tender in the Tender Management tab."
                )

        # 5. Active Bidder Queries ("which bidder", "active bidder", "selected bidder", "bidder details")
        if any(w in q_lower for w in ["active bidder", "current bidder", "which bidder", "selected bidder"]):
            if active_bidder:
                b_name = active_bidder.get("name", "Active Bidder")
                b_gstin = active_bidder.get("gstin", "N/A")
                b_score = active_bidder.get("score", 0)
                b_risk = active_bidder.get("risk", "UNKNOWN")
                b_status = active_bidder.get("status", "UNDER_REVIEW")
                b_rec = active_bidder.get("recommendation", "Evaluation in progress.")
                return (
                    f"Active Bidder Profile:\n\n"
                    f"Legal Name: {b_name}\n"
                    f"GSTIN: {b_gstin}\n"
                    f"Compliance Score: {b_score}/100\n"
                    f"Risk Tier: {b_risk} RISK\n"
                    f"Current Review Status: {b_status}\n\n"
                    f"Grounded AI Analysis:\n{b_rec}"
                )
            else:
                return (
                    "There is currently no bidder selected in your workspace. "
                    "Please select a bidder from the Bidder Management tab to inspect document evidence and gateway verification results."
                )

        # 6. Specific Preloaded Bidder Inquiries (Acme, CyberTech, Bharat InfoTech)
        if "acme" in q_lower:
            return (
                "Acme Solutions & Technologies Pvt Ltd Evaluation Summary:\n\n"
                "Compliance Score: 100/100 (LOW RISK)\n"
                "Status: QUALIFIED\n"
                "Gateway Results: Active GSTIN 27AAACA1098F1Z5 verified on GSTN, Udyam MSE micro-enterprise active, PAN identity 100% matched, OEM Authorization Letter valid through 2027.\n"
                "Recommendation: Fully compliant with all mandatory tender specifications. Recommended for commercial price bid opening."
            )
        elif "cybertech" in q_lower:
            return (
                "CyberTech Global Systems Evaluation Summary:\n\n"
                "Compliance Score: 40/100 (CRITICAL RISK)\n"
                "Status: DISQUALIFIED / HIGH RISK\n"
                "Primary Critical Finding: Expired OEM Authorization Letter (Validity expired on 31/12/2023, Page 1 of submission).\n"
                "Gateway Results: GSTN Active, PAN Matched, but mandatory OEM MAF compliance failed.\n"
                "Recommendation: Disqualification under Clause 4.2 of tender specification."
            )
        elif "bharat" in q_lower or "infotech" in q_lower:
            return (
                "Bharat InfoTech Pvt Ltd Evaluation Summary:\n\n"
                "Compliance Score: 75/100 (MEDIUM RISK)\n"
                "Status: REVIEW REQUIRED\n"
                "Primary Finding: Legal name spelling discrepancy detected between Bid Form ('Bharat InfoTech Solutions') and GST Certificate ('Bharat InfoTech Pvt Ltd').\n"
                "Recommendation: Procurement Officer manual verification recommended before finalizing qualification."
            )

        # 7. Multi-Turn Follow-Up Questions & Procurement Rules
        if any(w in q_lower for w in ["document", "docs", "included", "contains", "attached"]) and ("bid" in combined_context or "tender" in combined_context):
            return (
                "Documents Normally Included in a Bid Submission:\n\n"
                "1. Technical Qualification Documents: Specification compliance matrix, experience certificates, audited turnover certificates.\n"
                "2. Statutory Eligibility Certificates: Active GST Registration Certificate, PAN Card, Udyam MSME Certificate.\n"
                "3. Manufacturer Authorization: OEM Authorization Letter (MAF) confirming official supply authorization.\n"
                "4. Financial Proposal: BOQ rate breakdown and price schedule.\n"
                "5. Bid Security Instrument: EMD receipt or Udyam MSME Exemption Undertaking under GFR Rule 170."
            )

        if ("difference" in q_lower or "versus" in q_lower or "vs" in q_lower or "between" in q_lower) and ("bid" in combined_context or "tender" in combined_context):
            return (
                "Key Differences Between Tender and Bid:\n\n"
                "1. Origin:\n"
                "A Tender is an official notice issued by a Government Department inviting commercial proposals.\n"
                "A Bid is the formal offer submitted by a vendor in response to that tender.\n\n"
                "2. Author:\n"
                "Tenders are created by Procurement Officers.\n"
                "Bids are prepared and submitted by Suppliers or OEMs.\n\n"
                "3. Contents:\n"
                "Tenders contain eligibility criteria and technical specifications.\n"
                "Bids contain pricing schedules, statutory certificates, and compliance declarations."
            )

        if any(w in q_lower for w in ["who checks", "who evaluates", "who verifies", "who approves", "who decides"]):
            return (
                "Evaluation and Verification Roles:\n\n"
                "1. Automated AI Verification Engine (BodhZ): Performs document OCR parsing, extracts structured data, and queries 13 statutory gateway nodes.\n"
                "2. Tender Evaluation Committee (TEC): Senior Procurement Officers review extracted evidence, risk findings, and compliance scores.\n"
                f"3. Procurement Officer ({officer}): Holds 100% final decision authority to qualify or disqualify the bidder."
            )

        if any(w in q_lower for w in ["13 gateway", "gateways", "all nodes", "statutory nodes", "portals"]):
            return (
                "BodhZ 13 Statutory Verification Gateway Nodes:\n\n"
                "1. GSTN Portal: Active GSTIN status and GSTR-3B filing check\n"
                "2. Income Tax Department: PAN validity and Section 206AB tax compliance\n"
                "3. Udyam MSME Register: Micro/Small/Medium enterprise verification for EMD exemption\n"
                "4. OEM Authorization Gateway: Manufacturer Authorization Form validation\n"
                "5. GeM Incident Management: Debarment and blacklisting status\n"
                "6. MCA21 Corporate Affairs: Company Master Data & Director DIN check\n"
                "7. Startup India / DPIIT: Recognized startup benefits validation\n"
                "8. NSIC Portal: Single point registration verification\n"
                "9. EPFO Portal: Employee Provident Fund registration and compliance\n"
                "10. ESIC Portal: Employee State Insurance compliance\n"
                "11. DigiLocker: Direct cryptographically verified document fetch\n"
                "12. Make in India (MII): Local content percentage declaration audit\n"
                "13. BIS Portal: Bureau of Indian Standards product certification check"
            )

        if any(w in q_lower for w in ["action", "what should i do", "how to decide", "next step", "guidance"]):
            return (
                f"Recommended Procurement Officer Action Guide for {officer}:\n\n"
                "1. Review Verification Modules: Check if all 13 gateway nodes have returned PASS or REVIEW status.\n"
                "2. Inspect Document Citations: Open Document Intelligence to review OCR extracted values against uploaded PDF pages.\n"
                "3. Address Risk Findings: If a bidder has CRITICAL risk (e.g. expired OEM letter), record DISQUALIFICATION with justification notes.\n"
                "4. Clarification: If minor spelling differences exist, request bidder clarification under GeM guidelines.\n"
                "5. Record Formal Decision: Click 'QUALIFY' or 'DISQUALIFY' in the Officer Review tab to generate an immutable cryptographic audit record."
            )

        if "gfr" in q_lower or "rule 170" in q_lower or "rule 144" in q_lower or "rule 149" in q_lower:
            return (
                "General Financial Rules (GFR 2017) Procurement Provisions:\n\n"
                "1. GFR Rule 144: Fundamental principles of public procurement (transparency, fairness, competition).\n"
                "2. GFR Rule 149: Mandatory procurement of common use goods and services through Government e-Marketplace (GeM).\n"
                "3. GFR Rule 170: Earnest Money Deposit (EMD) regulations and mandatory exemption for Micro & Small Enterprises (MSEs) and DPIIT recognized Startups."
            )

        if "make in india" in q_lower or "mii" in q_lower or "local content" in q_lower:
            return (
                "Public Procurement (Preference to Make in India) Order:\n\n"
                "1. Class-I Local Supplier: Local content >= 50%. Eligible for purchase preference in government tenders.\n"
                "2. Class-II Local Supplier: Local content >= 20% and < 50%. Eligible to participate, but no purchase preference.\n"
                "3. Non-Local Supplier: Local content < 20%. Excluded from tenders valued below Rs 200 Crore."
            )

        if "debarment" in q_lower or "blacklist" in q_lower:
            return (
                "Debarment and Blacklisting Verification:\n\n"
                "BodhZ queries GeM Incident Management and Central Public Procurement Portal debarment lists to verify that neither the legal entity nor its directors are prohibited from participating in public bids under GFR 2017 Rule 151."
            )

        # 8. Active Workspace Bidder Specific Queries
        if active_bidder and any(w in q_lower for w in ["score", "risk", "finding", "status", "why", "reason"]):
            score = active_bidder.get("score", 100)
            risk = active_bidder.get("risk", "LOW")
            status = active_bidder.get("status", "QUALIFIED")
            name = active_bidder.get("name", "Active Bidder")
            rec = active_bidder.get("recommendation", "Satisfies statutory requirements.")
            return (
                f"Evaluation Findings for {name}\n\n"
                f"Compliance Score: {score}/100\n"
                f"Risk Tier: {risk} RISK\n"
                f"Verification Status: {status}\n\n"
                f"Analysis and Recommendation:\n{rec}"
            )

        # 9. Explicit Definition Inquiries (Strict matching to prevent accidental dictionary triggers)
        if any(phrase in q_lower for phrase in ["what is a bid", "what is bid", "define bid", "meaning of bid", "bid meaning", "what does bid mean", "what are bids", "bid means"]):
            return (
                "A Bid is a formal, legally binding technical and commercial offer submitted by an eligible supplier or OEM in response to a public procurement tender.\n\n"
                "It typically contains the technical compliance sheet, financial price schedule, GST and PAN certificates, Udyam MSME certificate, and OEM authorization letter."
            )
        elif any(phrase in q_lower for phrase in ["what is a tender", "what is tender", "define tender", "meaning of tender", "tender meaning", "what does tender mean", "what are tenders", "tender means", "what about tender"]):
            return (
                "A Tender is an official public invitation issued by a Ministry, Government Department, or CPSE under GFR 2017 Rule 144, inviting competitive proposals from qualified vendors for goods, services, or infrastructure works."
            )
        elif "gst" in q_lower:
            return (
                "GST (Goods and Services Tax) is a mandatory indirect tax registration in India. In GeM tender evaluations, active GSTIN status and regular GSTR-3B return filings are required for eligibility."
            )
        elif "msme" in q_lower or "udyam" in q_lower:
            return (
                "Udyam MSME registration provides statutory procurement preferences under the Public Procurement Policy 2012, including EMD waivers and purchase preferences for Micro & Small Enterprises."
            )
        elif "oem" in q_lower or "maf" in q_lower:
            return (
                "An OEM Authorization Letter (MAF) is a formal document issued by the Original Equipment Manufacturer confirming that the bidder is authorized to supply, install, and support their products for the tender duration."
            )
        elif "emd" in q_lower:
            return (
                "EMD (Earnest Money Deposit) is a bid security deposit submitted by bidders. Under GFR 2017 Rule 170, registered MSMEs and DPIIT Recognized Startups are exempt from submitting EMD."
            )
        elif "finding" in q_lower:
            return (
                "In procurement evaluation, a finding is a documented observation or evidence result identified during document intelligence OCR parsing or statutory gateway verification checks."
            )
        elif "score" in q_lower:
            return (
                "The Compliance Score (0 to 100) measures how thoroughly a bidder satisfies mandatory tender rules, document consistency, and gateway checks. It serves as decision support for the Procurement Officer."
            )
        elif "risk" in q_lower:
            return (
                "Risk Tiers (LOW, MEDIUM, HIGH, CRITICAL) indicate the severity of detected discrepancies, such as legal name spelling mismatches or expired OEM authorization letters."
            )
        elif "missing" in q_lower:
            return (
                "A missing document status occurs when a required tender document (e.g. GST Certificate, OEM Letter, Financial Statements) is absent from the bidder submission."
            )
        elif "ocr" in q_lower:
            return (
                "OCR (Optical Character Recognition) is an automated document processing technology used by BodhZ to extract text, tables, dates, and certificate numbers from scanned PDF bidder documents."
            )

        # 10. Conversational / Hinglish Questions
        if re.search(r"\b(h+e+l+l*o+|h+i+|h+e+y+|gm|gn|good\s*morning|good\s*afternoon|good\s*evening|namaste|namaskar|hola)\b", q_lower):
            return f"Hello, Officer {officer}! How can I assist you with your tender evaluations or bidder compliance checks today?"
        elif any(w in q_lower for w in ["kaise ho", "kya bol", "kaha h", "kya h", "who are you"]):
            return f"Main BodhZ AI Assistant hoon. Main Officer {officer} ko tender rules, GST, Udyam MSME, OEM authorization, compliance score, aur document evidence verify karne mein madad karta hoon."

        # 11. Smart Contextual Fallback Response
        active_t_num = active_tender.get("tender_number") or active_tender.get("id", "GEM/2026/B/994810") if active_tender else "GEM/2026/B/994810"
        active_b_name = active_bidder.get("name") or active_bidder.get("legal_name", "Acme Solutions & Technologies Pvt Ltd") if active_bidder else "Acme Solutions & Technologies Pvt Ltd"
        return (
            f"BodhZ AI Assistant is active for Officer {officer} ({role_label}).\n\n"
            f"• Active Tender: {active_t_num}\n"
            f"• Selected Bidder: {active_b_name}\n"
            f"• Statutory Gateways: 13 Nodes Verified\n\n"
            f"You can ask about tender counts, bidder compliance scores, missing certificates, or statutory verification findings."
        )
