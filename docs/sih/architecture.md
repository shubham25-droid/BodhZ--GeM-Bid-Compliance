# 🏗️ BodhZ End-to-End System Architecture

```text
               +-------------------------------------------+
               |        Tender Document (NIT / RFP)        |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |         Tender Intelligence Engine        |
               |  (Clause extraction, Threshold parsing)   |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |     Structured Procurement Requirements    |
               +-------------------------------------------+
                                     |
       +-----------------------------+-----------------------------+
       |                                                           |
       v                                                           v
+-----------------------------+             +-------------------------------+
|   Bidder Technical Bundle   |             | 13 Statutory Portal Gateways  |
|  (PDFs, UDIN, MAF, Audits)  |             | (GSTN, Udyam, MCA21, EPFO...) |
+-----------------------------+             +-------------------------------+
       |                                                           |
       v                                                           v
+-----------------------------+             +-------------------------------+
|  Document AI Engine (OCR)   |             |   Live Sandbox Connectors     |
|   (SHA-256 Tamper Proof)    |             |  (Payload, Latency & Hash)    |
+-----------------------------+             +-------------------------------+
       |                                                           |
       +-----------------------------+-----------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |         Compliance & Scoring Engine       |
               |  (Missing proofs, Anomaly & Risk tier)    |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |   Evidence-Backed AI Recommendation       |
               |    (Page-level citations & Explanations)  |
               +-------------------------------------------+
                                     |
                                     v
               +===========================================+
               |       PROCUREMENT OFFICER WORKSPACE       |
               |   (100% Human Legal Authority - GFR 144)  |
               +===========================================+
                                     |
                                     v
               +-------------------------------------------+
               |  Immutable Cryptographic Audit Trail      |
               |    (SHA-256 Event Log & PDF Dossier)      |
               +-------------------------------------------+
```
