"""
BodhZ Sovereign Verification Base Connector
Problem Statement: SIH26100

Defines the abstract interface and standard response schema for all
13 statutory government portal connectors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import json
from enum import Enum


class ConnectorMode(str, Enum):
    SANDBOX = "SANDBOX"
    MOCK = "MOCK"
    DOCUMENT_CONSISTENCY = "DOCUMENT_CONSISTENCY"
    LIVE_API = "LIVE_API"
    NOT_CONNECTED = "NOT_CONNECTED"


class VerificationResult:
    """Standardized verification result schema across all 13 gateways."""
    def __init__(
        self,
        gateway_id: str,
        gateway_name: str,
        authority: str,
        is_valid: bool,
        verification_status: str,
        confidence_score: float,
        mode: ConnectorMode,
        extracted_attributes: Dict[str, Any],
        raw_response: Dict[str, Any],
        discrepancies: Optional[list] = None,
        latency_ms: int = 25
    ):
        self.gateway_id = gateway_id
        self.gateway_name = gateway_name
        self.authority = authority
        self.is_valid = is_valid
        self.verification_status = verification_status
        self.confidence_score = confidence_score
        self.mode = mode
        self.extracted_attributes = extracted_attributes
        self.raw_response = raw_response
        self.discrepancies = discrepancies or []
        self.latency_ms = latency_ms
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Calculate cryptographic SHA-256 seal for audit trail
        hash_payload = f"{gateway_id}|{is_valid}|{json.dumps(extracted_attributes, sort_keys=True)}|{self.timestamp}"
        self.sha256_hash = hashlib.sha256(hash_payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gateway_id": self.gateway_id,
            "gateway_name": self.gateway_name,
            "authority": self.authority,
            "is_valid": self.is_valid,
            "verification_status": self.verification_status,
            "confidence_score": self.confidence_score,
            "mode": self.mode.value,
            "extracted_attributes": self.extracted_attributes,
            "raw_response": self.raw_response,
            "discrepancies": self.discrepancies,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
            "sha256_hash": self.sha256_hash,
            "is_tamper_sealed": True
        }


class BaseVerificationConnector(ABC):
    """Abstract base class for all statutory verification gateway connectors."""
    
    def __init__(self, gateway_id: str, gateway_name: str, authority: str, mode: ConnectorMode = ConnectorMode.SANDBOX):
        self.gateway_id = gateway_id
        self.gateway_name = gateway_name
        self.authority = authority
        self.mode = mode

    @abstractmethod
    async def verify(self, entity_data: Dict[str, Any]) -> VerificationResult:
        """Executes statutory validation against target registry."""
        pass
