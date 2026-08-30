from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AuditEventModel
from app.schemas.schemas import AuditEventResponseSchema

router = APIRouter(prefix="/audit", tags=["Audit & Traceability Layer"])


# --------------------------------------------------
# GET AUDIT TRAIL TIMELINE FOR A BID
# --------------------------------------------------
@router.get("", response_model=List[AuditEventResponseSchema], summary="List Audit Logs")
@router.get("/{bid_id}", response_model=List[AuditEventResponseSchema], summary="Get Immutable Audit Log Timeline")
def get_audit_trail(bid_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Retrieves the complete SHA-256 hashed audit log timeline for a bid,
    recording automated checks, external portal responses, and officer decisions.
    """
    query = db.query(AuditEventModel)
    if bid_id:
        query = query.filter(AuditEventModel.bid_id == bid_id)
    events = query.order_by(AuditEventModel.timestamp.desc()).all()
    return events
