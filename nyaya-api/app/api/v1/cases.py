from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.case import Case
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.schemas.case import CaseDTO, CaseDetailDTO
from app.schemas.common import ResponseEnvelope
from app.core.errors import NotFoundException

router = APIRouter(prefix="/cases", tags=["Commercial Precedents & Authorities"])


@router.get("", response_model=ResponseEnvelope[List[CaseDTO]])
def list_cases(
    search: Optional[str] = Query(None, description="Search by case title or citation"),
    court: Optional[str] = Query(None, description="Filter by court jurisdiction"),
    category: Optional[str] = Query(None, description="Filter by commercial subject category"),
    good_law_only: Optional[bool] = Query(None, description="Filter only active 'good law'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve catalog of commercial court precedents with precedent treatment status."""
    query = db.query(Case)
    if search:
        query = query.filter(
            (Case.title.ilike(f"%{search}%")) |
            (Case.standard_citation.ilike(f"%{search}%")) |
            (Case.neutral_citation.ilike(f"%{search}%"))
        )
    if court:
        query = query.filter(Case.court.ilike(f"%{court}%"))
    if category:
        query = query.filter(Case.commercial_category.ilike(f"%{category}%"))
    if good_law_only is not None:
        query = query.filter(Case.is_good_law == good_law_only)

    cases = query.all()
    return ResponseEnvelope(data=[CaseDTO.model_validate(c) for c in cases])


@router.get("/{case_id}", response_model=ResponseEnvelope[CaseDetailDTO])
def get_case(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full precedent details, authoritative ratio decidendi, and cited authorities."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise NotFoundException(f"Precedent with ID '{case_id}' not found in registry")
    return ResponseEnvelope(data=CaseDetailDTO.model_validate(case))
