from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.models import (
    BidModel, VerificationResultModel, FindingModel, EvidenceLinkModel,
    AssessmentModel, AuditEventModel, RequirementModel, ExtractionModel
)
from app.verification_gateway.base_connector import VerificationResultContract
from app.decision_support.scoring_engine import ScoringEngine
from app.decision_support.risk_engine import RiskEngine
from app.decision_support.recommendation_generator import RecommendationGenerator


# --------------------------------------------------
# DECISION SUPPORT SERVICE
# --------------------------------------------------
class DecisionSupportService:
    """
    Service layer executing scoring, risk assessment, recommendation generation,
    and persisting verification results, findings, and evidence links to database.
    """

    @classmethod
    def evaluate_and_persist_bid(
        cls, db: Session, bid: BidModel, verification_results: List[VerificationResultContract]
    ) -> AssessmentModel:
        """
        Calculates compliance score and risk level, generates recommendation,
        and saves complete verification assessment and evidence links to database.
        """
        # Fetch requirements for scoring weight calculation
        requirements_models = db.query(RequirementModel).filter(RequirementModel.tender_id == bid.tender_id).all()
        req_dicts = [
            {"id": r.id, "module": r.module, "weight": r.weight, "mandatory": r.mandatory}
            for r in requirements_models
        ]

        # 1. Calculate Score & Risk Level
        score = ScoringEngine.calculate_compliance_score(verification_results, req_dicts)
        risk_level = RiskEngine.evaluate_risk_level(score, verification_results)

        # 2. Generate Grounded AI Recommendation
        bidder_name = bid.bidder.legal_name if bid.bidder else "Submitted Bidder"
        ai_rec = RecommendationGenerator.generate_recommendation(
            bidder_name=bidder_name,
            compliance_score=score,
            risk_level=risk_level,
            verification_results=verification_results
        )

        # 3. Persist Assessment Record
        assessment = AssessmentModel(
            bid_id=bid.id,
            compliance_score=score,
            risk_level=risk_level,
            ai_recommendation=ai_rec
        )
        db.add(assessment)
        db.flush()

        # 4. Clear & Persist Verification Results and Findings
        db.query(VerificationResultModel).filter(VerificationResultModel.bid_id == bid.id).delete()

        for res in verification_results:
            v_model = VerificationResultModel(
                bid_id=bid.id,
                requirement_id=res.requirement_id,
                module=res.module,
                status=res.status,
                confidence=res.confidence,
                risk=res.risk,
                verification_mode=res.verification_mode
            )
            db.add(v_model)
            db.flush()

            for issue in res.issues:
                finding = FindingModel(
                    verification_result_id=v_model.id,
                    severity=issue.get("severity", "WARNING"),
                    code=issue.get("code", "VERIFICATION_ISSUE"),
                    message=issue.get("message", "")
                )
                db.add(finding)
                db.flush()

                # Add evidence provenance links
                for ev in res.evidence:
                    link = EvidenceLinkModel(
                        finding_id=finding.id,
                        document_id=ev.get("document_id", "DOC_UNKNOWN"),
                        extraction_id=None,
                        page_number=ev.get("page", 1)
                    )
                    db.add(link)

        # 5. Update Bid Status
        bid.status = "EVALUATED"

        # 6. Audit Trail Event
        audit = AuditEventModel(
            bid_id=bid.id,
            actor_id="SYSTEM",
            event_type="COMPLIANCE_EVALUATION_COMPLETED",
            payload_json=f"Evaluation completed: Score={score}/100, Risk={risk_level}, Modules evaluated={len(verification_results)}"
        )
        db.add(audit)

        db.commit()
        db.refresh(assessment)
        return assessment
