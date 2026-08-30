import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# --------------------------------------------------
# BODHZ CONTEXT BUILDER (ENHANCED WITH OFFICER & WORKSPACE BINDING)
# --------------------------------------------------
class BodhZContextBuilder:
    """
    Extracts authorized system context from BodhZ backend database or active workspace.
    
    Ensures:
    - Officer identity and decision mandate are clearly bounded.
    - Active tender specifications and extracted rules are accurately represented.
    - Active bidder evaluation profile, OCR extractions, and verification statuses are grounded.
    """

    @staticmethod
    def build_system_context(
        active_tender: Optional[Dict[str, Any]] = None,
        active_bidder: Optional[Dict[str, Any]] = None,
        user_name: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> str:
        context_parts = []
        context_parts.append("=== BODHZ SYSTEM CONTEXT & ACTIVE WORKSPACE STATE ===")
        context_parts.append("Project: BodhZ — GeM Bid Compliance Verification Platform (SIH26100)")
        context_parts.append("Platform Role: Decision-Support AI Assistant for Government Procurement Officers.")
        
        # Officer Session Context
        officer_name = user_name.strip() if user_name else "Senior Procurement Officer"
        role_title = "Senior Procurement Officer" if (not user_role or "PROCUREMENT" in user_role.upper()) else "Compliance Auditor"
        context_parts.append(f"\n--- AUTHENTICATED PROCUREMENT OFFICER SESSION ---")
        context_parts.append(f"Current Officer Name: {officer_name}")
        context_parts.append(f"Designation: {role_title}")
        context_parts.append("Authority: 100% Final Qualification & Disqualification Decision Authority.")

        # Active Tender Context
        if active_tender:
            context_parts.append("\n--- ACTIVE TENDER SPECIFICATION ---")
            context_parts.append(f"Tender ID: {active_tender.get('id', 'N/A')}")
            context_parts.append(f"Tender Title: {active_tender.get('title', 'N/A')}")
            context_parts.append("Configured Mandatory Rules: GST Registration, Udyam MSME, PAN Identity Match, OEM Authorization.")
            context_parts.append(f"Tender Status: {active_tender.get('status', 'ACTIVE')}")
        else:
            context_parts.append("\n--- ACTIVE TENDER SPECIFICATION ---")
            context_parts.append("No specific tender selected in current workspace context.")

        # Active Bidder Context
        if active_bidder:
            context_parts.append("\n--- ACTIVE BIDDER EVALUATION PROFILE ---")
            context_parts.append(f"Bid ID: {active_bidder.get('id', 'N/A')}")
            context_parts.append(f"Bidder Legal Name: {active_bidder.get('name', 'N/A')}")
            context_parts.append(f"Extracted GSTIN: {active_bidder.get('gstin', 'N/A')}")
            context_parts.append(f"Compliance Score: {active_bidder.get('score', 0)}/100")
            context_parts.append(f"Assessed Risk Tier: {active_bidder.get('risk', 'N/A')} RISK")
            context_parts.append(f"Current Review Status: {active_bidder.get('status', 'N/A')}")
            
            rec = active_bidder.get('recommendation', '')
            if rec:
                context_parts.append(f"Grounded AI Analysis & Recommendation: {rec}")

            modules = active_bidder.get('modules', [])
            if modules:
                context_parts.append("\nVerification Module Results (13 Gateway Nodes):")
                for m in modules:
                    context_parts.append(
                        f"  - [{m.get('name')}]: Status={m.get('status')}, Mode={m.get('mode')}, Source={m.get('source')}, Finding={m.get('reason')}"
                    )

            findings = active_bidder.get('findings', [])
            if findings:
                context_parts.append("\nCompliance Findings & Document Citations:")
                for f in findings:
                    context_parts.append(
                        f"  - Title: {f.get('title')}\n    Description: {f.get('desc')}\n    Document Evidence Citation: {f.get('source')}"
                    )

        else:
            context_parts.append("\n--- ACTIVE BIDDER EVALUATION PROFILE ---")
            context_parts.append("No specific bidder selected in current workspace context.")

        context_parts.append("\n--- OFFICIAL INDIAN GOVERNMENT PORTALS DIRECTORY ---")
        context_parts.append("- GeM Portal: https://gem.gov.in/")
        context_parts.append("- GSTN Portal: https://www.gst.gov.in/")
        context_parts.append("- Udyam MSME Register: https://udyamregistration.gov.in/")
        context_parts.append("- Income Tax / PAN e-Filing: https://eportal.incometax.gov.in/")
        context_parts.append("- MCA21 Corporate Portal: https://www.mca.gov.in/")
        context_parts.append("- Startup India (DPIIT): https://www.startupindia.gov.in/")
        context_parts.append("- NSIC Register: https://www.nsic.co.in/")
        context_parts.append("- EPFO Provident Fund: https://www.epfindia.gov.in/")
        context_parts.append("- ESIC Portal: https://www.esic.gov.in/")
        context_parts.append("- DigiLocker: https://www.digilocker.gov.in/")
        context_parts.append("- CPPP E-Procurement: https://eprocure.gov.in/")

        return "\n".join(context_parts)
