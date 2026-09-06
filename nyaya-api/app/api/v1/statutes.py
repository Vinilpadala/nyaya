from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.statute import Statute, StatuteSection
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.schemas.statute import StatuteDTO, StatuteDetailDTO, StatuteSectionDTO
from app.schemas.common import ResponseEnvelope
from app.core.errors import NotFoundException

router = APIRouter(prefix="/statutes", tags=["Commercial Statutes & Provisions"])


@router.get("", response_model=ResponseEnvelope[List[StatuteDTO]])
def list_statutes(
    search: Optional[str] = Query(None, description="Search statute title"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve catalog of commercial statutes in the repository."""
    query = db.query(Statute)
    if search:
        query = query.filter(Statute.short_title.ilike(f"%{search}%"))
    statutes = query.all()
    return ResponseEnvelope(data=[StatuteDTO.model_validate(s) for s in statutes])


@router.get("/{statute_id}", response_model=ResponseEnvelope[StatuteDetailDTO])
def get_statute(
    statute_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve statute details including all commercial provisions and sections."""
    statute = db.query(Statute).filter(Statute.id == statute_id).first()
    if not statute:
        raise NotFoundException(f"Statute with ID '{statute_id}' not found")
    return ResponseEnvelope(data=StatuteDetailDTO.model_validate(statute))


@router.get("/sections/{section_id}", response_model=ResponseEnvelope[StatuteSectionDTO])
def get_section(
    section_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve specific statutory section content and legislative amendments."""
    section = db.query(StatuteSection).filter(StatuteSection.id == section_id).first()
    if not section:
        raise NotFoundException(f"Statutory section with ID '{section_id}' not found")
    return ResponseEnvelope(data=StatuteSectionDTO.model_validate(section))
