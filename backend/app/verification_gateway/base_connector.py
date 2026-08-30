from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


# --------------------------------------------------
# VERIFICATION RESULT CONTRACT SCHEMA
# --------------------------------------------------
class VerificationResultContract(BaseModel):
    requirement_id: str
    module: str
    status: str  # PASS, FAIL, REVIEW
    confidence: float
    risk: str  # LOW, MEDIUM, HIGH, CRITICAL
    extracted_values: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    issues: List[Dict[str, Any]]
    verification_mode: str  # AUTHORIZED_API, SANDBOX, DOCUMENT_CONSISTENCY


# --------------------------------------------------
# BASE VERIFICATION CONNECTOR ABSTRACT CLASS
# --------------------------------------------------
class BaseVerificationConnector(ABC):
    """
    Abstract base class for all government portal and external verification connectors.
    Enforces a standardized verification interface across GST, Udyam, PAN, and OEM modules.
    """

    @abstractmethod
    async def verify(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        """
        Executes verification check comparing bidder data, tender requirement,
        and extracted document evidence.
        """
        pass
