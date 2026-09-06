from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ResponseEnvelope
from app.schemas.research import (
    ResearchQueryRequest,
    ResearchSynthesisResponse,
    RetrievedAuthorityDTO,
    PinpointPassageDTO,
    SavedResearchCreate,
    SavedResearchResponse,
    ResearchSessionHistoryItem,
)
from app.services.research_engine import ResearchEngineService
from app.models.case import Case
from app.models.user import User
from app.models.audit import AuditLog
from app.models.saved_research import SavedResearch
from app.core.errors import NotFoundException
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/research", tags=["Judicial Legal Research & Synthesis Engine"])


@router.post("/query", response_model=ResponseEnvelope[ResearchSynthesisResponse])
def execute_research_query(
    payload: ResearchQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Execute grounded legal research query across commercial court precedents and statutes with trust & explainability."""
    service = ResearchEngineService(db)
    synthesis = service.execute_research(payload)

    # Record Audit Log for judicial integrity with authenticated user_id
    audit = AuditLog(
        user_id=current_user.id,
        action="LEGAL_RESEARCH_QUERY",
        endpoint="/api/v1/research/query",
        metadata_payload={
            "query": payload.query,
            "language": getattr(payload, "language", "en"),
            "jurisdiction": payload.jurisdiction,
            "results_count": len(synthesis.retrieved_authorities),
        },
    )
    db.add(audit)
    db.commit()

    return ResponseEnvelope(data=synthesis)


@router.get("/authority/{case_id}", response_model=ResponseEnvelope[RetrievedAuthorityDTO])
def get_authority_details(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve verified authority details, pinpoint paragraphs, and citation treatment verification."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise NotFoundException(f"Legal authority with ID '{case_id}' not found in court repository")

    service = ResearchEngineService(db)
    cv = service._build_citation_verification(case)

    dto = RetrievedAuthorityDTO(
        id=case.id,
        title=case.title,
        standard_citation=case.standard_citation,
        neutral_citation=case.neutral_citation,
        court=case.court,
        judgment_date=str(case.judgment_date),
        bench_quorum=case.bench_quorum,
        bench_strength=case.bench_strength,
        is_good_law=case.is_good_law,
        status_summary=case.status_summary,
        relevance_score=10.0,
        why_relevant="Direct authority lookup from commercial case repository",
        ratio_extract=case.ratio_decidendi,
        pinpoint_passages=[
            PinpointPassageDTO(
                paragraph_number=p.paragraph_number if p.paragraph_number is not None else 0,
                text=p.passage_text,
                significance=p.significance,
            )
            for p in sorted(case.passages, key=lambda x: x.paragraph_number or 0)
        ],
        citation_verification=cv,
        is_demo_data=False,
    )
    return ResponseEnvelope(data=dto)


@router.post("/save", response_model=ResponseEnvelope[SavedResearchResponse])
def save_research(
    payload: SavedResearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bookmark and persist verified legal research to the authenticated chambers portfolio."""
    saved = SavedResearch(
        user_id=current_user.id,
        matter_id=payload.matter_id,
        query_text=payload.query_text,
        case_context=payload.case_context,
        jurisdiction=payload.jurisdiction,
        lead_citation=payload.lead_citation,
        lead_title=payload.lead_title,
        summary_extract=payload.summary_extract,
        confidence_score=payload.confidence_score,
        uncertainty_level=payload.uncertainty_level,
        notes=payload.notes,
        tags=payload.tags,
        full_payload=payload.full_payload,
        is_demo_data=payload.is_demo_data,
    )
    db.add(saved)

    # Log audit entry for research bookmarking linked to current user
    audit = AuditLog(
        user_id=current_user.id,
        action="RESEARCH_BOOKMARKED",
        endpoint="/api/v1/research/save",
        metadata_payload={"saved_id": saved.id, "lead_citation": payload.lead_citation},
    )
    db.add(audit)
    db.commit()
    db.refresh(saved)

    resp = SavedResearchResponse(
        id=saved.id,
        user_id=saved.user_id,
        matter_id=saved.matter_id,
        query_text=saved.query_text,
        case_context=saved.case_context,
        jurisdiction=saved.jurisdiction,
        lead_citation=saved.lead_citation,
        lead_title=saved.lead_title,
        summary_extract=saved.summary_extract,
        confidence_score=saved.confidence_score,
        uncertainty_level=saved.uncertainty_level,
        notes=saved.notes,
        tags=saved.tags,
        full_payload=saved.full_payload or {},
        is_demo_data=saved.is_demo_data,
        created_at=saved.created_at.isoformat() if saved.created_at else "",
    )
    return ResponseEnvelope(data=resp)


@router.get("/saved", response_model=ResponseEnvelope[List[SavedResearchResponse]])
def get_saved_research(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch saved research bookmarks scoped to the active authenticated chambers portfolio."""
    items = (
        db.query(SavedResearch)
        .filter(SavedResearch.user_id == current_user.id)
        .order_by(SavedResearch.created_at.desc())
        .all()
    )
    result = [
        SavedResearchResponse(
            id=item.id,
            user_id=item.user_id,
            matter_id=item.matter_id,
            query_text=item.query_text,
            case_context=item.case_context,
            jurisdiction=item.jurisdiction,
            lead_citation=item.lead_citation,
            lead_title=item.lead_title,
            summary_extract=item.summary_extract,
            confidence_score=item.confidence_score,
            uncertainty_level=item.uncertainty_level,
            notes=item.notes,
            tags=item.tags,
            full_payload=item.full_payload or {},
            is_demo_data=item.is_demo_data,
            created_at=item.created_at.isoformat() if item.created_at else "",
        )
        for item in items
    ]
    return ResponseEnvelope(data=result)


@router.delete("/saved/{saved_id}", response_model=ResponseEnvelope[bool])
def delete_saved_research(
    saved_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a saved research bookmark from the authenticated chambers portfolio."""
    item = (
        db.query(SavedResearch)
        .filter(SavedResearch.id == saved_id, SavedResearch.user_id == current_user.id)
        .first()
    )
    if not item:
        raise NotFoundException(f"Saved research item '{saved_id}' not found in active chambers portfolio")

    db.delete(item)
    db.commit()
    return ResponseEnvelope(data=True)


@router.get("/session-history", response_model=ResponseEnvelope[List[ResearchSessionHistoryItem]])
def get_session_history(
    limit: int = 15,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve chronological query session history for research audits for the active user."""
    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "LEGAL_RESEARCH_QUERY",
            (AuditLog.user_id == current_user.id) | (AuditLog.user_id.is_(None)),
        )
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    history: List[ResearchSessionHistoryItem] = []
    for log in logs:
        payload = log.metadata_payload or {}
        ts = getattr(log, "timestamp", None) or getattr(log, "created_at", None)
        history.append(
            ResearchSessionHistoryItem(
                id=log.id,
                timestamp=ts.strftime("%d %b %Y, %H:%M:%S IST") if ts else "Recent",
                query=payload.get("query", "Legal query"),
                jurisdiction=payload.get("jurisdiction", "ALL"),
                results_count=payload.get("results_count", 0),
                action=log.action,
            )
        )
    return ResponseEnvelope(data=history)
