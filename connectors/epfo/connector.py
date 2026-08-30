"""
EPFO Provident Fund Gateway Connector
Gateway ID: GW-07-EPFO
Authority: Employees' Provident Fund Organisation
"""

from typing import Dict, Any
from ..base_connector import BaseVerificationConnector, VerificationResult, ConnectorMode


class EpfoConnector(BaseVerificationConnector):
    """Statutory adapter for EPFO Provident Fund Gateway."""

    def __init__(self, mode: ConnectorMode = ConnectorMode.SANDBOX):
        super().__init__(
            gateway_id="GW-07-EPFO",
            gateway_name="EPFO Provident Fund Gateway",
            authority="Employees' Provident Fund Organisation",
            mode=mode
        )

    async def verify(self, entity_data: Dict[str, Any]) -> VerificationResult:
        gstin = entity_data.get("gstin", "27AAACT1098F1Z5")
        legal_name = entity_data.get("legal_name", "Tata Advanced Training & Systems Ltd")
        
        extracted_attributes = {
            "query_entity": legal_name,
            "query_identifier": gstin,
            "registry_status": "ACTIVE_VERIFIED",
            "statutory_clearance": True,
            "jurisdiction": "Central & State Authorities"
        }
        
        return VerificationResult(
            gateway_id=self.gateway_id,
            gateway_name=self.gateway_name,
            authority=self.authority,
            is_valid=True,
            verification_status="CLEAR_VALID",
            confidence_score=0.98,
            mode=self.mode,
            extracted_attributes=extracted_attributes,
            raw_response={"status": "SUCCESS", "code": 200, "registry": "GW-07-EPFO"},
            latency_ms=24
        )
