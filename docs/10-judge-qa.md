# BodhZ — SIH Judge Defense & Q&A Master Reference

## 1. Top 10 Judge Questions & Answers

### Q1: Why is AI needed here? Why not simple regex or OCR?
**Answer**: OCR only extracts raw text strings. Deterministic regex validates pattern structures (e.g. GSTIN format). However, GeM tenders contain complex, unstructured natural-language requirements (e.g., *"Bidder must have 3 years OEM authorization in Central CPSEs with minimum ₹10 Cr turnover"*). AI is required to understand unstructured document semantics, contextually link requirements to page snippets, and generate plain-language decision support explanations.

### Q2: How do you prevent LLM hallucinations from disqualifying a valid bidder?
**Answer**: Our architecture enforces strict separation: **Deterministic Python Rules** evaluate numeric thresholds, expirations, and matching conditions. The LLM is used ONLY for natural-language extraction and summary generation. If evidence is ambiguous, the system assigns status `REVIEW_REQUIRED` rather than an automatic failure.

### Q3: Who makes the final qualification or disqualification decision?
**Answer**: The **Procurement Officer**. AI acts strictly as a decision-support tool. The final button to Qualify or Disqualify a bidder is physically and legally restricted to the human Procurement Officer.

### Q4: How do you verify government data if live government APIs are unavailable during testing?
**Answer**: We built a modular `VerificationAdapter` interface. In production with authorized credentials, it connects to official APIs (`LIVE`). When access is restricted during hackathons/sandbox testing, it connects to clearly labelled `SANDBOX` mock connectors returning standardized schemas. The UI explicitly flags whether data originates from an `AUTHORIZED_API`, `SANDBOX`, or `DOCUMENT_CONSISTENCY` check.

### Q5: How do you detect cross-document fraud or inconsistencies?
**Answer**: Our Cross-Document Verification Engine normalizes key identifiers (GSTIN, PAN, Udyam ID, Legal Name) across all uploaded bidder documents (Bid Form, GST Certificate, Financial Audit) and external portal checks. If Document A lists GSTIN `27ABCDE1234F1Z5` while Document B lists `27ABCDE9999X1Z5`, the system immediately flags a severity `HIGH` inconsistency finding linked to both document page references.

### Q6: How is the Compliance Score calculated?
**Answer**: The score (0–100) is configuration-driven based on tender requirement weights (e.g., Financial Eligibility = 30 pts, Statutory GST = 30 pts, OEM Authorization = 40 pts). Points are awarded dynamically based on verified compliance (`PASS`), penalized for `NON_COMPLIANT` items, and flagged for `REVIEW_REQUIRED` items.

### Q7: How do you protect sensitive bidder data and prevent unauthorized scraping?
**Answer**: All backend endpoints are locked behind JWT authentication and role-based access control. Rate limiting middleware (`SlowAPI`), CORS origin restrictions, security headers (`X-Frame-Options`, `CSP`), binary magic-byte MIME validation, and encrypted storage protect the system against unauthorized scraping, bot abuse, and injection attacks.

### Q8: What happens if a mandatory document is missing?
**Answer**: The system detects the missing document during requirement matching, flags it as `MISSING` with status `FAIL`/`REVIEW_REQUIRED`, penalizes the compliance score, increases the risk level to `HIGH` or `CRITICAL`, and highlights the exact missing evidence in the officer's recommendation panel.

### Q9: How is complete auditability guaranteed?
**Answer**: Every action—from tender upload and OCR extraction to verification gateway responses and officer decisions—is written to an immutable Audit Event log storing actor details, event payloads, timestamps, and SHA-256 hashes.

### Q10: How does your solution reduce manual evaluation effort by 60–80%?
**Answer**: Instead of a Procurement Officer manually cross-checking dozens of PDF pages against 10+ government portals, BodhZ automatically extracts all data, runs cross-document checks, verifies portal data, and presents a single consolidated evidence panel with direct page citations, reducing evaluation time from hours to minutes.
