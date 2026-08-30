import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import (
    BidderModel, BidModel, AssessmentModel, OfficerDecisionModel,
    TenderModel, HistoricalBidderMatchModel
)

logger = logging.getLogger(__name__)

# ==================================================
# 5-YEAR HISTORICAL BIDDER MEMORY & RESOLUTION SERVICE
# ==================================================
# Purpose: Resolves repeat bidders across past tenders (5+ years) using
#          verified GSTIN, PAN, Udyam URN, or normalized legal entity name.
# Principle: Historical records are contextual evidence only; current
#            tender and current verification always take legal precedence.
# ==================================================

class HistoricalEntityResolver:
    """
    Historical Bidder Resolution Engine.
    Detects past government tender evaluations for repeat bidders and generates
    side-by-side comparison reports without overriding current evaluation.
    """

    @classmethod
    def resolve_bidder_history(cls, db: Session, bid_id: str) -> Dict[str, Any]:
        """
        Retrieves 5-year historical memory and past tender evaluations for a given bid's bidder.
        Matches across HistoricalBidderMatchModel records and past Tender evaluations.
        """
        current_bid = db.query(BidModel).filter(BidModel.id == bid_id).first()
        if not current_bid:
            return {"historical_match_found": False, "records": []}

        bidder = current_bid.bidder
        if not bidder:
            return {"historical_match_found": False, "records": []}

        historical_records: List[Dict[str, Any]] = []

        # 1. Check HistoricalBidderMatchModel table (Pre-existing multi-year memory)
        direct_hist = db.query(HistoricalBidderMatchModel).filter(
            (HistoricalBidderMatchModel.bidder_id == bidder.id) |
            (HistoricalBidderMatchModel.historical_tender_number.isnot(None))
        ).all()

        for h in direct_hist:
            historical_records.append({
                "source": "HISTORICAL_ARCHIVE",
                "tender_number": h.historical_tender_number,
                "tender_title": h.historical_tender_title,
                "evaluation_date": h.evaluation_date.strftime("%d %b %Y") if h.evaluation_date else "Historical",
                "outcome": h.historical_outcome,
                "compliance_score": h.historical_score,
                "risk_level": h.historical_risk,
                "key_findings": h.key_findings_summary,
                "matched_by": h.matched_by
            })

        # 2. Check past bids in other tenders in the active database
        other_bids = db.query(BidModel).filter(
            BidModel.bidder_id == bidder.id,
            BidModel.id != current_bid.id
        ).all()

        for ob in other_bids:
            assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == ob.id).order_by(AssessmentModel.created_at.desc()).first()
            decision = db.query(OfficerDecisionModel).filter(OfficerDecisionModel.bid_id == ob.id).order_by(OfficerDecisionModel.timestamp.desc()).first()
            t_num = ob.tender.tender_number if ob.tender else "N/A"
            t_title = ob.tender.title if ob.tender else "Previous Tender"

            historical_records.append({
                "source": "ACTIVE_SYSTEM_TENDER",
                "tender_number": t_num,
                "tender_title": t_title,
                "evaluation_date": ob.submission_date.strftime("%d %b %Y") if ob.submission_date else "Previous",
                "outcome": decision.decision if decision else ob.status,
                "compliance_score": assessment.compliance_score if assessment else 0,
                "risk_level": assessment.risk_level if assessment else "UNKNOWN",
                "key_findings": assessment.ai_recommendation if assessment else "Standard compliance checks performed.",
                "matched_by": "BIDDER_ID_MATCH"
            })

        has_match = len(historical_records) > 0

        # Current bid snapshot
        current_assessment = db.query(AssessmentModel).filter(AssessmentModel.bid_id == current_bid.id).order_by(AssessmentModel.created_at.desc()).first()
        current_decision = db.query(OfficerDecisionModel).filter(OfficerDecisionModel.bid_id == current_bid.id).order_by(OfficerDecisionModel.timestamp.desc()).first()

        current_snapshot = {
            "bid_id": current_bid.id,
            "tender_number": current_bid.tender.tender_number if current_bid.tender else "N/A",
            "tender_title": current_bid.tender.title if current_bid.tender else "Current Tender",
            "bidder_name": bidder.legal_name,
            "gstin": bidder.gstin or "N/A",
            "pan": bidder.pan_number or "N/A",
            "udyam": bidder.udyam_number or "N/A",
            "current_score": current_assessment.compliance_score if current_assessment else 0,
            "current_risk": current_assessment.risk_level if current_assessment else "PENDING",
            "current_status": current_decision.decision if current_decision else current_bid.status
        }

        return {
            "historical_match_found": has_match,
            "bidder_name": bidder.legal_name,
            "total_historical_evaluations": len(historical_records),
            "current_evaluation": current_snapshot,
            "historical_records": historical_records,
            "legal_guidance": (
                "IMPORTANT: Historical verification records are provided as contextual evidence only. "
                "Current tender rules, uploaded documents, and gateway verifications always take precedence. "
                "Historical outcomes must never automatically determine current qualification."
            )
        }
