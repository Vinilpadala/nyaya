from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import ResponseEnvelope

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health")
def check_health(db: Session = Depends(get_db)):
    """Health check endpoint verifying database connectivity and system status."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return ResponseEnvelope(
        data={
            "status": "healthy" if "unhealthy" not in db_status else "degraded",
            "version": settings.VERSION,
            "project": settings.PROJECT_NAME,
            "database": db_status,
            "demo_mode": settings.DEMO_MODE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
