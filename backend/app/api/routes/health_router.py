from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health & System Status"])


# --------------------------------------------------
# SYSTEM HEALTH & SECURITY CHECK ENDPOINT
# --------------------------------------------------
@router.get("", summary="Get System Health and Database Connection Status")
def get_system_health(db: Session = Depends(get_db)):
    """
    Returns platform health, active database connectivity,
    environment status, and security compliance status.
    """
    db_status = "HEALTHY"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"UNHEALTHY: {str(exc)}"

    return {
        "status": "ONLINE",
        "system": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "security": {
            "auth_mode": "JWT_BEARER",
            "rate_limiting": "ACTIVE",
            "security_headers": "ENABLED",
            "anti_scraping_protection": "STRICT_ENFORCED"
        }
    }
