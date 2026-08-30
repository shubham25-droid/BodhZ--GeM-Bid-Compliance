from typing import Dict, Any, Optional, List

class BodhZContextTools:
    """
    Backend Authorization & Context Data Tools.
    Performs secure data retrieval for chatbot queries without sending raw DB handles to the LLM.
    """

    @staticmethod
    def get_current_tender(tender: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not tender:
            return {"status": "NO_TENDER_SELECTED", "message": "No active tender selected in workspace."}
        return {
            "tender_id": tender.get("id"),
            "tender_title": tender.get("title"),
            "rules_count": tender.get("rulesCount", 4),
            "status": tender.get("status", "ACTIVE")
        }

    @staticmethod
    def get_current_bidder(bidder: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not bidder:
            return {"status": "NO_BIDDER_SELECTED", "message": "No active bidder selected in workspace."}
        return {
            "bidder_id": bidder.get("id"),
            "bidder_name": bidder.get("name"),
            "gstin": bidder.get("gstin"),
            "compliance_score": bidder.get("score"),
            "risk_tier": bidder.get("risk"),
            "verification_status": bidder.get("status"),
            "recommendation": bidder.get("recommendation"),
            "findings_count": len(bidder.get("findings", []))
        }

    @staticmethod
    def get_compliance_findings(bidder: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not bidder or "findings" not in bidder:
            return []
        return bidder.get("findings", [])

    @staticmethod
    def get_verification_results(bidder: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not bidder or "modules" not in bidder:
            return []
        return bidder.get("modules", [])
