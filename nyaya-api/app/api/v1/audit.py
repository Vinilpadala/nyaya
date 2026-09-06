from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogDTO, AuditLogCreateDTO
from app.schemas.common import ResponseEnvelope
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["Tamper-Evident Chambers Audit Trail"])

SENSITIVE_KEYS = {"password", "token", "access_token", "secret", "secret_key", "hashed_password", "authorization"}


def sanitize_payload(payload: Any) -> Any:
    """Recursively scrub any sensitive authentication tokens or credentials from audit metadata."""
    if not isinstance(payload, dict):
        return payload
    sanitized: Dict[str, Any] = {}
    for k, v in payload.items():
        if any(sens in k.lower() for sens in SENSITIVE_KEYS):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = sanitize_payload(v)
        else:
            sanitized[k] = v
    return sanitized


def format_audit_dto(log: AuditLog, fallback_user: Optional[User] = None) -> AuditLogDTO:
    user = log.user or fallback_user
    chambers_user = (
        f"{user.full_name} ({user.role})"
        if user
        else "Chambers System / Unassigned"
    )
    court_division = (
        user.court_division
        if user
        else "Commercial Appellate Division, High Court"
    )

    # Determine descriptive target from metadata payload or action
    meta = log.metadata_payload or {}
    target = (
        meta.get("target")
        or meta.get("query")
        or meta.get("suit_number")
        or meta.get("matter_title")
        or meta.get("title")
        or log.endpoint
        or "Chambers Session Operation"
    )

    return AuditLogDTO(
        id=log.id,
        timestamp=log.timestamp,
        chambers_user=chambers_user,
        action=log.action,
        target=str(target),
        court_division=court_division,
        endpoint=log.endpoint or "/api/v1/chambers",
        ip_address=log.ip_address or "127.0.0.1",
        metadata_payload=sanitize_payload(meta),
    )


@router.get("", response_model=ResponseEnvelope[List[AuditLogDTO]])
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200, description="Max audit log entries to return"),
    action: Optional[str] = Query(None, description="Optional filter by action type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve tamper-evident audit trail records.
    Judges, Registrars, and Admins can review all division & chambers audit events.
    Research clerks are strictly confined to their own session records.
    """
    query = db.query(AuditLog)

    # Authorization filter:
    if current_user.role in ["JUDGE", "REGISTRAR", "ADMIN"]:
        # Judicial supervisory authority: view division/chambers events + unassigned system events
        query = query.join(User, AuditLog.user_id == User.id, isouter=True).filter(
            or_(
                AuditLog.user_id == current_user.id,
                AuditLog.user_id.is_(None),
                User.court_division == current_user.court_division,
            )
        )
    else:
        # Research clerk: restricted strictly to own session operations
        query = query.filter(AuditLog.user_id == current_user.id)

    if action:
        query = query.filter(AuditLog.action == action.strip())

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    dtos = [format_audit_dto(log) for log in logs]
    return ResponseEnvelope(data=dtos)


@router.post("", response_model=ResponseEnvelope[AuditLogDTO], status_code=status.HTTP_201_CREATED)
def record_client_audit_log(
    payload: AuditLogCreateDTO,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a client-side judicial navigation or research event into the tamper-evident audit trail."""
    client_ip = request.client.host if request.client else "127.0.0.1"

    meta = payload.metadata_payload or {}
    meta["target"] = payload.target

    log = AuditLog(
        user_id=current_user.id,
        action=payload.action.strip(),
        endpoint=payload.endpoint.strip() if payload.endpoint else "/api/v1/client-session",
        ip_address=client_ip,
        metadata_payload=sanitize_payload(meta),
        timestamp=datetime.now(timezone.utc),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return ResponseEnvelope(data=format_audit_dto(log, current_user))
