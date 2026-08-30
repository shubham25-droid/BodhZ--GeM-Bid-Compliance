# BodhZ System Architecture Specifications

## 1. Complete Architecture Diagram
```
GeM Tender Requirements           Bidder Submitted PDFs         Authorized External Sources
         │                                 │                                │
         ▼                                 ▼                                ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│ LAYER 1: INPUT   │             │ LAYER 1: INPUT   │             │ LAYER 1: INPUT   │
│ File Upload &    │             │ Document Storage │             │ Auth Source      │
│ Validation       │             │ SHA-256 Check    │             │ Configuration    │
└────────┬─────────┘             └────────┬─────────┘             └────────┬─────────┘
         │                                 │                                │
         ▼                                 ▼                                │
┌──────────────────┐             ┌──────────────────┐                       │
│ LAYER 2: TENDER  │             │ LAYER 3: DOC AI  │                       │
│ Requirement      │             │ Text + OCR       │                       │
│ Extraction       │             │ Snippet Evidence │                       │
└────────┬─────────┘             └────────┬─────────┘                       │
         │                                 │                                │
         └────────────────┐                │                                │
                          ▼                ▼                                ▼
                 ┌──────────────────────────────────────────────────────────────────┐
                 │ LAYER 4: INTEGRATED VERIFICATION GATEWAY                         │
                 │ GSTAdapter | UdyamAdapter | PANAdapter | OEMAdapter              │
                 │ (LIVE Authorized API or SANDBOX Mock Connector)                  │
                 └────────────────────────┬─────────────────────────────────┘
                                          │
                                          ▼
                 ┌──────────────────────────────────────────────────────────────────┐
                 │ LAYER 5: AI COMPLIANCE & VERIFICATION ENGINE                     │
                 │ - Missing Requirement Detection                                 │
                 │ - Cross-Document Inconsistency Detection                         │
                 │ - Non-Compliance Verification                                    │
                 │ - Deterministic Rules + LLM Reasoning                            │
                 └────────────────────────┬─────────────────────────────────┘
                                          │
                                          ▼
                 ┌──────────────────────────────────────────────────────────────────┐
                 │ LAYER 6: DECISION SUPPORT ENGINE                                 │
                 │ - Compliance Score (0 - 100)                                     │
                 │ - Risk Level Assessment (LOW / MEDIUM / HIGH / CRITICAL)         │
                 │ - Grounded AI Recommendation                                     │
                 └────────────────────────┬─────────────────────────────────┘
                                          │
                                          ▼
                 ┌──────────────────────────────────────────────────────────────────┐
                 │ LAYER 7: PROCUREMENT OFFICER DASHBOARD                           │
                 │ - Verification Overview & Status Cards                           │
                 │ - Evidence Viewer with Page & Snippet References                 │
                 │ - Officer Review Form (QUALIFY / DISQUALIFY / REJECT)            │
                 └────────────────────────┬─────────────────────────────────┘
                                          │
                                          ▼
                 ┌──────────────────────────────────────────────────────────────────┐
                 │ LAYER 8: AUDIT & TRACEABILITY LAYER                              │
                 │ Immutable SHA-256 Audit Trail of All Checks, Evidence & Decisions│
                 └──────────────────────────────────────────────────────────────────┘
```

## 2. Core Modules & Data Schemas

### Verification Adapter Interface
Every verification connector implements the standard interface:
```python
class BaseVerificationConnector(ABC):
    @abstractmethod
    async def verify(self, bidder_data: dict, requirement: dict) -> VerificationResult:
        pass
```

### Result Schema Contract
```json
{
  "requirement_id": "REQ_GST_001",
  "module": "GST",
  "status": "PASS",
  "confidence": 0.98,
  "risk": "LOW",
  "extracted_values": {
    "gstin": "27ABCDE1234F1Z5",
    "legal_name": "Acme Solutions Pvt Ltd"
  },
  "evidence": [
    {
      "document_id": "DOC_9921",
      "page": 1,
      "field": "gstin",
      "value": "27ABCDE1234F1Z5",
      "snippet": "GSTIN: 27ABCDE1234F1Z5"
    }
  ],
  "issues": [],
  "verification_mode": "SANDBOX"
}
```
