from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.reports.report_generator import ComplianceReportGenerator

router = APIRouter(prefix="/reports", tags=["Official Compliance Reports & Export"])


# --------------------------------------------------
# 1. GET PRINTABLE HTML REPORT FOR A BID EVALUATION
# --------------------------------------------------
@router.get("/bids/{bid_id}/html", response_class=HTMLResponse, summary="Get Printable HTML Compliance Report")
def get_bid_evaluation_report(bid_id: str, db: Session = Depends(get_db)):
    """
    Renders an executive, print-ready official compliance evaluation dossier
    with scoring, gateway nodes breakdown, evidence citations, AI recommendation,
    5-year history, and officer final decision.
    """
    html_content = ComplianceReportGenerator.generate_bid_evaluation_report_html(db, bid_id)
    return HTMLResponse(content=html_content, status_code=200)
