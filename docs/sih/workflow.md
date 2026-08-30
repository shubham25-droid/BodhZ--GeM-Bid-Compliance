# 🔄 End-to-End Procurement Workflow

1. **Phase 1: Ingestion & Clause Extraction**: Procurement Officer uploads the NIT document. BodhZ parses eligibility thresholds (Turnover, Completed projects, Certifications).
2. **Phase 2: Bidder Proposal Submission**: Bidder uploads technical document bundle via the Bid Uploader Portal. Each page is sealed with a cryptographic SHA-256 hash.
3. **Phase 3: Automated Statutory Cross-Verification**: Parallel query dispatch across all 13 statutory connectors (GSTN, Udyam, CBDT PAN, MCA21, EPFO, etc.).
4. **Phase 4: Multidimensional Compliance Scoring**: Scores calculated on 0–100 scale; discrepancies and risk levels (Low, Medium, High) classified.
5. **Phase 5: Officer Review & Final Sign-Off**: Officer reviews evidence citations, records binding legal remarks under GFR Rule 144, and cryptographically signs the final evaluation dossier.
