from typing import Dict, Any, List
from app.verification_gateway.base_connector import VerificationResultContract
from app.verification_gateway.gst_connector import GSTConnector
from app.verification_gateway.udyam_connector import UdyamConnector
from app.verification_gateway.pan_connector import PANConnector
from app.verification_gateway.oem_connector import OEMConnector
from app.verification_gateway.mca_connector import MCAConnector
from app.verification_gateway.startup_connector import StartupIndiaConnector
from app.verification_gateway.nsic_connector import NSICConnector
from app.verification_gateway.epfo_connector import EPFOConnector
from app.verification_gateway.esic_connector import ESICConnector
from app.verification_gateway.digilocker_connector import DigiLockerConnector
from app.verification_gateway.debarment_connector import DebarmentConnector
from app.verification_gateway.incometax_connector import IncomeTaxConnector
from app.verification_gateway.localcontent_connector import LocalContentConnector


# --------------------------------------------------
# UNIFIED 13-NODE VERIFICATION GATEWAY MANAGER
# --------------------------------------------------
class VerificationGateway:
    """
    Unified Verification Gateway orchestrating all 13 SIH26100 statutory adapters:
    1. GST Registration & Returns
    2. Udyam / MSME Registration
    3. PAN Verification
    4. MCA21 Corporate Status
    5. Startup India Recognition
    6. NSIC Registration
    7. EPFO (Provident Fund)
    8. ESIC (State Insurance)
    9. OEM Authorization
    10. DigiLocker Document Verification
    11. Blacklisting / Debarment List Check
    12. Income Tax Compliance
    13. Make in India / Local Content Certificate
    """

    def __init__(self):
        self.connectors = {
            "GST": GSTConnector(),
            "UDYAM": UdyamConnector(),
            "PAN": PANConnector(),
            "OEM": OEMConnector(),
            "MCA21": MCAConnector(),
            "STARTUP_INDIA": StartupIndiaConnector(),
            "NSIC": NSICConnector(),
            "EPFO": EPFOConnector(),
            "ESIC": ESICConnector(),
            "DIGILOCKER": DigiLockerConnector(),
            "DEBARMENT": DebarmentConnector(),
            "INCOME_TAX": IncomeTaxConnector(),
            "MAKE_IN_INDIA": LocalContentConnector()
        }

    async def run_verification_for_requirement(
        self, bidder_data: Dict[str, Any], requirement: Dict[str, Any], extractions: List[Dict[str, Any]]
    ) -> VerificationResultContract:
        """
        Selects the matching verification connector for a given tender requirement module
        and executes verification.
        """
        module_name = requirement.get("module", "").upper()

        if "GST" in module_name:
            connector_key = "GST"
        elif "UDYAM" in module_name or "MSME" in module_name:
            connector_key = "UDYAM"
        elif "PAN" in module_name:
            connector_key = "PAN"
        elif "OEM" in module_name:
            connector_key = "OEM"
        elif "MCA" in module_name or "CORP" in module_name:
            connector_key = "MCA21"
        elif "STARTUP" in module_name:
            connector_key = "STARTUP_INDIA"
        elif "NSIC" in module_name:
            connector_key = "NSIC"
        elif "EPFO" in module_name or "PF" in module_name:
            connector_key = "EPFO"
        elif "ESIC" in module_name or "ESI" in module_name:
            connector_key = "ESIC"
        elif "DIGILOCKER" in module_name or "HASH" in module_name:
            connector_key = "DIGILOCKER"
        elif "DEBAR" in module_name or "BLACK" in module_name:
            connector_key = "DEBARMENT"
        elif "TAX" in module_name or "INCOME" in module_name:
            connector_key = "INCOME_TAX"
        elif "LOCAL" in module_name or "MAKE" in module_name or "INDIA" in module_name:
            connector_key = "MAKE_IN_INDIA"
        else:
            connector_key = "GST"

        connector = self.connectors.get(connector_key, self.connectors["GST"])
        return await connector.verify(bidder_data, requirement, extractions)
