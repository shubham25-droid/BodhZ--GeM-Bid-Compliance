# 🇮🇳 BodhZ — AI-Powered Integrated Bid Compliance Verification Platform
> **Smart India Hackathon 2026** • Problem Statement ID: **`SIH26100`**  
> **Domain**: Smart Governance & Public Procurement (GeM / State Directorates)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.109-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python)](https://python.org)
[![Security](https://img.shields.io/badge/Integrity-SHA--256_Immutable-blue.svg)](https://en.wikipedia.org/wiki/SHA-2)
[![GFR 2017](https://img.shields.io/badge/Mandate-GFR_Rule_144-orange.svg)](https://doe.gov.in)
[![SIH 2026](https://img.shields.io/badge/Hackathon-SIH2026_SIH26100-FF9933.svg)](https://sih.gov.in)

---

## ⚠️ Important Legal & Architectural Mandate

> **BodhZ is a decision-support and verification platform. The AI does not independently qualify or disqualify bidders. Final qualification/disqualification authority remains 100% with the authorized Human Procurement Officer under GFR 2017 Rule 144.**

---

## 📌 Problem Statement (SIH26100)

In public procurement (Government e-Marketplace - GeM and State Directorates), evaluating technical bid compliance is manual, voluminous, and error-prone. Procurement officers must manually review multi-page PDF submissions, cross-verify entity credentials across disparate government portals, and ensure strict compliance with statutory mandates like **GFR 2017 Rule 144**, **Make in India Order 2017**, and **Land Border Restrictions (Rule 144(xi))**.

### The Problem We Solve:
- **Fragmented Portals**: Manual cross-checking across GSTN, MCA21, EPFO, ESIC, Udyam, etc.
- **Voluminous Unindexed Documents**: Hundreds of pages per bidder leading to long screening cycles.
- **Discrepancy Overlook**: Entity name variations, invalid UDINs, and expired certifications.
- **CAG / Vigilance Auditability**: Need for an immutable cryptographic audit trail of all decision steps.

---

## 💡 Proposed Solution

**BodhZ** provides an end-to-end, evidence-backed decision support pipeline that automates document ingestion, statutory registry verification across **13 government gateways**, calculates multi-criteria compliance scores, and presents explainable evidence citations for **Human Officer Legal Decision Sign-Off**.

```text
Tender (NIT / RFP)
       ↓
Tender Intelligence (Mandatory Rule & Threshold Extraction)
       ↓
Structured Procurement Requirements
       ↓
Bidder Documents (Technical Proposals, Balances, Certificates)
       ↓
Document Intelligence / OCR (Cryptographic SHA-256 Tamper Proofing)
       ↓
Structured Bidder Data
       ↓
13 Statutory Government Portal Gateways (GSTN, Udyam, MCA21, EPFO, PAN...)
       ↓
Cross-Verification & Entity Consistency Engine
       ↓
Compliance Engine (Missing / Inconsistent / Non-Compliant Detection)
       ↓
Compliance Score (0–100) + Risk Classification (Low / Medium / High)
       ↓
Evidence-Based AI Recommendation (Page-level Citations & Reasoning)
       ↓
Procurement Officer (100% Sovereign Legal Authority under GFR Rule 144)
       ↓
Final Qualification / Disqualification Decision
       ↓
Immutable Cryptographic Audit Trail + Printable Evaluation Dossier
```

---

## 🌟 Key Features

1. **Multi-Role Workspaces**:
   - **Central Procurement Officer (GeM)**: Flagship evaluation cockpit, 13-gateway inspection, comparative matrix, and GFR 144 sign-off.
   - **DTE Maharashtra Officer**: Departmental monitoring, compliance oversight, and audit trail inspection.
   - **Bid Uploader / Vendor**: Submission portal, document upload with integrity hashes, and clarification responses.
2. **13 Statutory Verification Gateway Adapters**:
   - Modular connectors with explicit mode declarations (`SANDBOX`, `LIVE_API`, `DOCUMENT_CONSISTENCY`).
   - Integrated with GSTN, Udyam, PAN, MCA21, Startup India, NSIC, EPFO, ESIC, DigiLocker, OEM MAF, Make in India, ISO/BIS, and CPPP Debarment Registry.
3. **Adaptive AI Memory Engine**:
   - Stores user facts, quotes previous question context, supports English & Hinglish queries, and generates multi-turn summaries.
4. **Cryptographic SHA-256 Audit Trail**:
   - Every verification, upload, score calculation, and officer remark is immutably logged with SHA-256 provenance.
5. **Ultra-Modern 3D Indian GovTech UI**:
   - 3D perspective animations, rotating 24-spoke Ashoka Chakra motifs, Tricolor accents, and 100% mobile responsiveness.

---

## 🏛️ Government Portal Connectors (13 Gateways)

| Gateway ID | Statutory Authority / Portal | Verification Scope | Status |
|---|---|---|---|
| `GW-01` | **GSTN Tax Portal** | Active GSTIN, GSTR-3B filings, Trade Name | 🟢 Live Sandbox |
| `GW-02` | **Udyam MSME Registry** | Micro/Small/Medium classification, EMD Exemption | 🟢 Live Sandbox |
| `GW-03` | **CBDT / PAN Gateway** | PAN validity, ITR filing track record | 🟢 Live Sandbox |
| `GW-04` | **MCA21 Corporate Registry** | CIN status, DIN active director roster | 🟢 Live Sandbox |
| `GW-05` | **Startup India (DPIIT)** | DPIIT certificate, Turnover/Experience waiver | 🟢 Live Sandbox |
| `GW-06` | **NSIC SPRS Registry** | Single Point Registration Scheme capacity | 🟢 Live Sandbox |
| `GW-07` | **EPFO Provident Fund** | Establishment code, monthly ECR challans | 🟢 Live Sandbox |
| `GW-08` | **ESIC Social Security** | ESI employer contribution compliance | 🟢 Live Sandbox |
| `GW-09` | **MeitY DigiLocker** | Cryptographically verified credentials | 🟢 Live Sandbox |
| `GW-10` | **OEM MAF Authorization** | Manufacturer Authorization validity & warranty | 🟢 Live Sandbox |
| `GW-11` | **Make in India (MII)** | Class-I / Class-II local content declaration | 🟢 Live Sandbox |
| `GW-12` | **ISO / BIS Standards** | ISO 9001, ISO 27001, BIS standards validity | 🟢 Live Sandbox |
| `GW-13` | **CPPP Debarment Registry** | Land Border Rule 144(xi), Debarment & Blacklist | 🟢 Live Sandbox |

---

## 🔑 Pre-Configured Demo Credentials

| Role | Username | Password | Jurisdiction / Scope |
|---|---|---|---|
| **Procurement Officer** (Primary) | `shubham` | `BodhZ@2026` | Central GeM Public Procurement Authority |
| **DTE Officer** | `dte_officer` | `DTE@Mah2026` | Directorate of Technical Education, Maharashtra |
| **Bid Uploader / Vendor** | `bidder_tata` | `Bidder@2026` | Tata Advanced Training & Systems Ltd |

---

## 🛠️ Quick Start & Installation

### Option 1: Local Python Environment
```bash
# 1. Clone the repository
git clone https://github.com/shubham25-droid/BodhZ--GeM-Bid-Compliance.git
cd BodhZ--GeM-Bid-Compliance

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Start the application
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open **`http://localhost:8000`** in your browser.  
Interactive API Docs: **`http://localhost:8000/docs`**

### Option 2: Docker Deployment
```bash
docker-compose up --build -d
```

---

## 🧪 Automated Test Verification

```bash
# Run Procurement Officer Suite
python scratch/test_officer_full_suite.py

# Run AI Memory & Brain Suite
python scratch/test_ai_memory.py

# Run Bidder & DTE Integration Suite
python scratch/test_bidder_dte_integration.py
```

---

## 📁 Repository Structure

```text
BodhZ-GeM-Bid-Compliance/
├── backend/                  # FastAPI Application Core
│   ├── app/
│   │   ├── api/routes/       # Modular API Routers (Auth, Bids, Tenders, DTE, Bidder)
│   │   ├── core/             # Security, JWT, Limiter, Config
│   │   ├── database/         # SQLite Models & Database Session
│   │   ├── services/         # Rule Matcher, Document Intelligence
│   │   ├── static/           # Official BodhZ Logo Assets
│   │   └── main.py           # Unified Web Application & SPA
│   └── requirements.txt      # Python Dependencies
│
├── connectors/               # 13 Modular Statutory Verification Gateways
│   ├── base_connector.py     # Base Abstract Class & VerificationResult Schema
│   ├── gst/                  # GSTN Tax Portal Connector
│   ├── udyam/                # Udyam MSME Registry Connector
│   ├── pan_income_tax/       # CBDT PAN Connector
│   ├── mca/                  # MCA21 Corporate Registry Connector
│   ├── startup_india/        # DPIIT Startup India Connector
│   ├── nsic/                 # NSIC SPRS Connector
│   ├── epfo/                 # EPFO Provident Fund Connector
│   ├── esic/                 # ESIC Social Security Connector
│   ├── digilocker/           # MeitY DigiLocker Connector
│   ├── gem/                  # OEM MAF Authorization Connector
│   ├── make_in_india/        # Make in India Local Content Connector
│   ├── bis/                  # ISO / BIS Standards Connector
│   └── blacklist_debarment/  # CPPP Debarment & Rule 144(xi) Connector
│
├── ai/                       # AI Intelligence Engines
│   ├── document_extraction/  # Multi-page OCR & SHA-256 Sealing
│   ├── requirement_extraction/ # NIT Rule Extraction
│   ├── consistency_analysis/ # Cross-Document Discrepancy Detection
│   ├── recommendation/       # Explainable AI Recommendation
│   └── chatbot/              # Adaptive Memory & Assistant
│
├── compliance_rules/         # Legal & Statutory Rules
│   ├── statutory/            # GFR 2017 Rule 144, Make in India, MSME Order
│   ├── tender_specific/      # Custom NIT Thresholds
│   └── scoring/              # 0-100 Weighted Scoring Algorithm
│
├── docs/sih/                 # Comprehensive SIH 2026 Documentation
│   ├── problem-statement.md  # Official SIH26100 Problem Statement
│   ├── feature-mapping.md    # PS-to-Feature Mapping Matrix
│   ├── architecture.md       # 5-Layer End-to-End Architecture
│   ├── workflow.md           # Procurement Lifecycle Workflow
│   ├── tech-stack.md         # Technology Stack Matrix
│   ├── team-roles.md         # Role & Permissions Model
│   └── future-scope.md       # Scaling & Future Roadmap
│
├── sample-data/              # Real-World RFPs & Bidder Data
│   ├── tender/               # DTE Maharashtra, NFL, ICAR RFPs
│   └── bidders/              # Bidder Submissions
│
├── .env.example              # Environment Configuration Template
├── .gitignore                # Comprehensive Python Exclusions
├── Dockerfile                # Production Container Specification
├── docker-compose.yml        # Multi-Container Orchestration
├── Procfile                  # PaaS Deployment Entrypoint
└── README.md                 # Project Overview & Guide
```

---

## 👥 Project Team & Hackathon Submission
- **Platform**: BodhZ (GeM Bid Compliance Verification)
- **Problem Statement ID**: `SIH26100`
- **Theme**: Smart Governance & Public Procurement
- **Smart India Hackathon 2026**
