# 🏛️ BodhZ Statutory Government Verification Connectors (SIH26100)

This module contains modular, decoupled verification adapters for all **13 statutory government registries and authority portals**.

## 🛡️ Modular Architecture & Verification Modes

To ensure full transparency during SIH evaluation and future enterprise integration, every connector explicitly declares its **Verification Mode**:

| Mode | Description |
|---|---|
| `SANDBOX` | Connected to simulated government registry sandbox emitting realistic payloads with latency & SHA-256 hash. |
| `LIVE_API` | Connected to production government API gateway (e.g. NIC, GSTN, Open Banking, DigiLocker). |
| `DOCUMENT_CONSISTENCY` | Cross-validates cryptographic hashes and optical entity extractions against uploaded documents. |
| `MOCK` | Standalone deterministic unit test response. |
| `NOT_CONNECTED` | Connector disabled or pending departmental API credentials. |

---

## 📋 13 Statutory Gateway Registry Directory

1. **`connectors/gst/`**: GSTN Tax Portal (GSTR-3B, Active Taxpayer Status, Legal Name Match)
2. **`connectors/udyam/`**: Udyam MSME Registry (Classification: Micro/Small/Medium, EMD Exemption)
3. **`connectors/pan_income_tax/`**: CBDT PAN & ITR Gateway (PAN Validity, ITR filing history)
4. **`connectors/mca/`**: Ministry of Corporate Affairs MCA21 (CIN status, DIN director roster)
5. **`connectors/startup_india/`**: DPIIT Startup India (DPIIT recognition, turnover/experience exemption)
6. **`connectors/nsic/`**: NSIC Single Point Registration Scheme (Monetary capacity limit)
7. **`connectors/epfo/`**: Employees' Provident Fund Organisation (Establishment code, ECR filing)
8. **`connectors/esic/`**: Employees' State Insurance Corporation (ESIC contribution compliance)
9. **`connectors/digilocker/`**: MeitY DigiLocker Gateway (Cryptographically signed government credentials)
10. **`connectors/gem/`**: GeM / OEM Authorization Form MAF (OEM partnership & warranty validity)
11. **`connectors/make_in_india/`**: Make in India (Class-I / Class-II Local Content Declaration)
12. **`connectors/bis/`**: Bureau of Indian Standards & ISO Certification (ISO 9001, ISO 27001)
13. **`connectors/blacklist_debarment/`**: CPPP & Vigilance Debarment Registry (Land Border Rule 144(xi), Debarment Check)
