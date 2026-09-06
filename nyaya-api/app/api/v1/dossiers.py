from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.dossier import Dossier, DossierItem
from app.models.audit import AuditLog
from app.schemas.dossier import DossierDTO, DossierCreateDTO, DossierItemCreateDTO, DossierUpdateDTO
from app.schemas.common import ResponseEnvelope
from app.api.v1.deps import get_current_user
from app.core.errors import NotFoundException

router = APIRouter(prefix="/dossiers", tags=["Chambers Research Dossiers & Bench Memos"])


@router.get("", response_model=ResponseEnvelope[List[DossierDTO]])
def list_dossiers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve private chambers research dossiers belonging to the active user."""
    dossiers = (
        db.query(Dossier)
        .filter(Dossier.user_id == current_user.id)
        .order_by(Dossier.updated_at.desc())
        .all()
    )
    return ResponseEnvelope(data=[DossierDTO.model_validate(d) for d in dossiers])


@router.post("", response_model=ResponseEnvelope[DossierDTO], status_code=status.HTTP_201_CREATED)
def create_dossier(
    payload: DossierCreateDTO,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new commercial bench memorandum / research dossier."""
    dossier = Dossier(
        user_id=current_user.id,
        matter_title=payload.matter_title,
        suit_number=payload.suit_number,
        judicial_notes=payload.judicial_notes,
    )
    db.add(dossier)
    db.flush()

    for item_data in payload.items:
        item = DossierItem(
            dossier_id=dossier.id,
            item_type=item_data.item_type,
            reference_id=item_data.reference_id,
            title=item_data.title,
            excerpt=item_data.excerpt,
            pinpoint=item_data.pinpoint,
        )
        db.add(item)

    # Record tamper-evident audit trail entry
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit = AuditLog(
        user_id=current_user.id,
        action="DOSSIER_CREATED",
        endpoint="/api/v1/dossiers",
        ip_address=client_ip,
        metadata_payload={
            "dossier_id": dossier.id,
            "suit_number": dossier.suit_number,
            "matter_title": dossier.matter_title,
            "items_count": len(payload.items),
        },
    )
    db.add(audit)

    db.commit()
    db.refresh(dossier)
    return ResponseEnvelope(data=DossierDTO.model_validate(dossier))


@router.get("/{dossier_id}", response_model=ResponseEnvelope[DossierDTO])
def get_dossier(
    dossier_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve details and pinned authorities of a specific chambers dossier."""
    dossier = db.query(Dossier).filter(
        Dossier.id == dossier_id,
        Dossier.user_id == current_user.id,
    ).first()
    if not dossier:
        raise NotFoundException(f"Chambers dossier with ID '{dossier_id}' not found")
    return ResponseEnvelope(data=DossierDTO.model_validate(dossier))


@router.post("/{dossier_id}/items", response_model=ResponseEnvelope[DossierDTO])
def add_dossier_item(
    dossier_id: str,
    payload: DossierItemCreateDTO,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a pinned precedent, statutory section, or bench note to an existing dossier with deduplication."""
    dossier = db.query(Dossier).filter(
        Dossier.id == dossier_id,
        Dossier.user_id == current_user.id,
    ).first()
    if not dossier:
        raise NotFoundException(f"Chambers dossier with ID '{dossier_id}' not found")

    # Deduplication check: avoid duplicate pins of the same authority or section
    normalized_ref = payload.reference_id.strip() if payload.reference_id else ""
    normalized_title = payload.title.strip()

    duplicate_query = db.query(DossierItem).filter(
        DossierItem.dossier_id == dossier.id,
        DossierItem.item_type == payload.item_type,
    )
    if normalized_ref:
        duplicate_query = duplicate_query.filter(DossierItem.reference_id == normalized_ref)
    else:
        duplicate_query = duplicate_query.filter(DossierItem.title == normalized_title)

    existing_item = duplicate_query.first()
    if existing_item:
        # Already pinned; return current dossier state without duplicate insertion
        return ResponseEnvelope(data=DossierDTO.model_validate(dossier))

    # Add new item
    item = DossierItem(
        dossier_id=dossier.id,
        item_type=payload.item_type,
        reference_id=normalized_ref,
        title=normalized_title,
        excerpt=payload.excerpt.strip() if payload.excerpt else "",
        pinpoint=payload.pinpoint.strip() if payload.pinpoint else "",
    )
    db.add(item)
    dossier.updated_at = datetime.now(timezone.utc)

    # Record audit log
    client_ip = request.client.host if request.client else "127.0.0.1"
    action_type = "BENCH_NOTE_RECORDED" if payload.item_type == "NOTE" else "DOSSIER_ITEM_PINNED"
    audit = AuditLog(
        user_id=current_user.id,
        action=action_type,
        endpoint=f"/api/v1/dossiers/{dossier_id}/items",
        ip_address=client_ip,
        metadata_payload={
            "dossier_id": dossier.id,
            "suit_number": dossier.suit_number,
            "item_type": payload.item_type,
            "title": payload.title,
            "reference_id": payload.reference_id,
        },
    )
    db.add(audit)

    db.commit()
    db.refresh(dossier)
    return ResponseEnvelope(data=DossierDTO.model_validate(dossier))


@router.delete("/{dossier_id}/items/{item_id}", response_model=ResponseEnvelope[DossierDTO])
def remove_dossier_item(
    dossier_id: str,
    item_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a pinned authority, statutory reference, or bench note from a dossier."""
    dossier = db.query(Dossier).filter(
        Dossier.id == dossier_id,
        Dossier.user_id == current_user.id,
    ).first()
    if not dossier:
        raise NotFoundException(f"Chambers dossier with ID '{dossier_id}' not found")

    item = db.query(DossierItem).filter(
        DossierItem.id == item_id,
        DossierItem.dossier_id == dossier.id,
    ).first()
    if not item:
        raise NotFoundException(f"Dossier item with ID '{item_id}' not found in this dossier")

    removed_title = item.title
    removed_type = item.item_type
    db.delete(item)
    dossier.updated_at = datetime.now(timezone.utc)

    # Audit trail
    client_ip = request.client.host if request.client else "127.0.0.1"
    audit = AuditLog(
        user_id=current_user.id,
        action="DOSSIER_ITEM_REMOVED",
        endpoint=f"/api/v1/dossiers/{dossier_id}/items/{item_id}",
        ip_address=client_ip,
        metadata_payload={
            "dossier_id": dossier.id,
            "suit_number": dossier.suit_number,
            "removed_title": removed_title,
            "removed_type": removed_type,
        },
    )
    db.add(audit)

    db.commit()
    db.refresh(dossier)
    return ResponseEnvelope(data=DossierDTO.model_validate(dossier))


@router.patch("/{dossier_id}", response_model=ResponseEnvelope[DossierDTO])
def update_dossier(
    dossier_id: str,
    payload: DossierUpdateDTO,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update judicial notes, suit title, or suit number for a private chambers dossier."""
    dossier = db.query(Dossier).filter(
        Dossier.id == dossier_id,
        Dossier.user_id == current_user.id,
    ).first()
    if not dossier:
        raise NotFoundException(f"Chambers dossier with ID '{dossier_id}' not found")

    if payload.matter_title is not None:
        dossier.matter_title = payload.matter_title.strip()
    if payload.suit_number is not None:
        dossier.suit_number = payload.suit_number.strip()
    if payload.judicial_notes is not None:
        dossier.judicial_notes = payload.judicial_notes

    dossier.updated_at = datetime.now(timezone.utc)

    client_ip = request.client.host if request.client else "127.0.0.1"
    audit = AuditLog(
        user_id=current_user.id,
        action="DOSSIER_UPDATED",
        endpoint=f"/api/v1/dossiers/{dossier_id}",
        ip_address=client_ip,
        metadata_payload={
            "dossier_id": dossier.id,
            "suit_number": dossier.suit_number,
        },
    )
    db.add(audit)

    db.commit()
    db.refresh(dossier)
    return ResponseEnvelope(data=DossierDTO.model_validate(dossier))


@router.delete("/{dossier_id}", response_model=ResponseEnvelope[dict])
def delete_dossier(
    dossier_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a commercial suit dossier and all its pinned materials."""
    dossier = db.query(Dossier).filter(
        Dossier.id == dossier_id,
        Dossier.user_id == current_user.id,
    ).first()
    if not dossier:
        raise NotFoundException(f"Chambers dossier with ID '{dossier_id}' not found")

    suit_number = dossier.suit_number
    db.delete(dossier)

    client_ip = request.client.host if request.client else "127.0.0.1"
    audit = AuditLog(
        user_id=current_user.id,
        action="DOSSIER_DELETED",
        endpoint=f"/api/v1/dossiers/{dossier_id}",
        ip_address=client_ip,
        metadata_payload={"dossier_id": dossier_id, "suit_number": suit_number},
    )
    db.add(audit)

    db.commit()
    return ResponseEnvelope(data={"deleted": True, "dossier_id": dossier_id})
