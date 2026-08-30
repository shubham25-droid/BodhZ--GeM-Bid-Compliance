# 🇮🇳 BodhZ — AI-Powered Integrated Bid Compliance Verification Platform
> **Problem Statement ID: SIH26100** • Smart India Hackathon 2026  
> Sovereign Decision Support for Public Procurement Officers & State Directorate Authorities

---

## 🌟 Executive Overview

**BodhZ** is an enterprise-grade, evidence-backed decision support platform designed to revolutionize public procurement compliance screening under **GFR 2017 Rule 144**. It automates multi-stage statutory verification across **13 government registries**, generates transparent explainable recommendations, and preserves **100% human legal decision authority** with immutable cryptographic auditability.

---

## 🚀 Key Architectural Pillars

1. **Procurement Officer Flagship Workspace**: Central GeM evaluation suite with 13 Layer-4 statutory gateways, comparative matrix, live OCR payload inspections, GFR 144 decision recording, and cryptographic SHA-256 audit logging.
2. **DTE Maharashtra Department Workspace**: Role-scoped state department oversight with departmental monitoring, audit trails, and 13-gateway verification.
3. **Bid Uploader / Vendor Workspace**: Dedicated portal for bidders to view tenders, review statutory checklists, upload bid documents, and respond to committee clarification requests.
4. **Adaptive AI Memory Engine**: Multi-tier memory storing user facts, previous question recall, Hinglish/English understanding, and executive conversation summarization.
5. **13 Statutory Verification Gateways**: Configured connectors for GSTN, Udyam MSME, PAN/CBDT, MCA21, Startup India (DPIIT), NSIC SPRS, EPFO, ESIC, DigiLocker, OEM MAF, Make in India, ISO/BIS, and CPPP Debarment Registry.

---

## 🔑 Pre-Configured Demo Credentials

| Role | Username | Password | Organization / Jurisdiction |
|---|---|---|---|
| **Procurement Officer** | `shubham` | `BodhZ@2026` | Central Public Procurement / GeM Authority |
| **DTE Officer** | `dte_officer` | `DTE@Mah2026` | Directorate of Technical Education, Maharashtra |
| **Bid Uploader / Bidder** | `bidder_tata` | `Bidder@2026` | Tata Advanced Training & Systems Ltd |

---

## 🛠️ Quick Local Deployment

```bash
# 1. Clone repository
git clone <repo-url>
cd "BodhZ_Bid Compliance Project (SIH26100)"

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Start Uvicorn Server
cd backend
uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload
```

Open browser at: `http://localhost:8000`  
API Swagger Docs: `http://localhost:8000/docs`

---

## 🐳 Docker Deployment

```bash
docker-compose up --build -d
```

---

## 🧪 Automated Test Verification

```bash
python scratch/test_officer_full_suite.py
python scratch/test_ai_memory.py
python scratch/test_bidder_dte_integration.py
```
