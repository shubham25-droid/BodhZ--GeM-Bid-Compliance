# BodhZ — AI-Powered Integrated Bid Compliance Verification Platform for GeM Procurement
**Problem Statement**: SIH26100  
**Target User**: Procurement Officers (Central & State Public Procurement Departments, CPSEs)

---

## 1. Executive Summary
Government procurement via the Government e-Marketplace (GeM) requires procurement officers to verify bid submissions across dozens of statutory, financial, regulatory, and tender-specific requirements. Manual verification across fragmented portals (GSTN, Udyam, MCA21, Income Tax, OEM portals) is time-consuming, prone to human error, and lacks auditable evidence preservation.

**BodhZ** automates and standardizes this verification process by combining:
1. Automated Tender Intelligence to extract structured eligibility rules.
2. AI-assisted Document Intelligence to parse bidder submissions and link extracted data directly to page snippets.
3. A Verification Gateway connecting to authorized portals (or sandbox mock connectors).
4. A Deterministic Compliance & Cross-Document Engine to identify missing, inconsistent, or non-compliant information.
5. An Evidence-Grounded Decision Support System delivering a 0–100 Compliance Score, Risk Level, and AI Recommendation.
6. A Procurement Officer Dashboard where human officers retain 100% final qualification/disqualification authority.
7. An Immutable Audit & Traceability Log.

---

## 2. Core Operating Principle
```
Evidence → Rule → Verification → Result → Explanation
```
- **Evidence**: Source document, page number, confidence, exact text snippet.
- **Rule**: Configured numeric threshold, date expiration, mandatory flag, or regex pattern.
- **Verification**: Verified status from authoritative external portal or cross-document comparison.
- **Result**: PASS, FAIL, or REVIEW REQUIRED.
- **Explanation**: Plain-language justification grounding the result in empirical evidence.

---

## 3. SIH Problem Statement Alignment Matrix

| SIH26100 Requirement | BodhZ System Capability | Layer Implementation |
| :--- | :--- | :--- |
| **Understand Tender Requirements** | Extracts structured rule objects with operators, thresholds, mandatory flags | Layer 2 (`tender_intelligence`) |
| **Process Bidder Documents** | Native PDF parsing + OCR fallback with bounding box/page evidence | Layer 3 (`document_intelligence`) |
| **Verify External Sources** | Modular `VerificationAdapter` (GST, Udyam, PAN, OEM, Blacklist) | Layer 4 (`verification_gateway`) |
| **Detect Missing/Inconsistent Data** | Cross-document mismatch detection & mandatory field validation | Layer 5 (`compliance_engine`) |
| **Compliance Score & Risk Level** | Weighted score (0-100) & 4-tier risk assessment (Low/Med/High/Critical) | Layer 6 (`decision_support`) |
| **Evidence-Based AI Recommendation** | Grounded summary citing exact findings without hallucinated outcomes | Layer 6 (`decision_support`) |
| **Officer Final Decision Authority** | UI workflow enforcing officer decision recording & override log | Layer 7 (`procurement_dashboard`) |
| **Complete Auditability** | SHA-256 event logging of checks, sources, timestamps & decisions | Layer 8 (`audit_traceability`) |
