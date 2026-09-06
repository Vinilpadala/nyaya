from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.case import Case
from app.schemas.research import (
    ResearchQueryRequest,
    ResearchSynthesisResponse,
    CitationVerificationDTO,
    RetrievedAuthorityDTO,
    PinpointPassageDTO,
)
from app.services.rag.orchestrator import RAGResearchOrchestrator
from app.services.rag.citation_verifier import CitationVerifier


class ResearchEngineService:
    """High-level service interface for judicial research and citation verification.
    
    Delegates retrieval, ranking, and grounded synthesis to RAGResearchOrchestrator,
    guaranteeing zero-fabrication, explainability, and a modular retriever backend.
    """

    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = RAGResearchOrchestrator(db)
        self.citation_verifier = CitationVerifier(db)

    def execute_research(self, req: ResearchQueryRequest) -> ResearchSynthesisResponse:
        """Executes grounded research query via modular RAG orchestrator."""
        return self.orchestrator.execute_research(req)

    def _build_citation_verification(self, case: Case) -> CitationVerificationDTO:
        """Authentic citation verification for single case authority."""
        # Wrap into RetrievedAuthorityDTO for CitationVerifier
        auth_dto = RetrievedAuthorityDTO(
            id=case.id,
            title=case.title,
            standard_citation=case.standard_citation,
            neutral_citation=case.neutral_citation,
            court=case.court,
            judgment_date=str(case.judgment_date),
            bench_quorum=case.bench_quorum,
            bench_strength=case.bench_strength or 2,
            is_good_law=case.is_good_law,
            status_summary=case.status_summary,
            relevance_score=10.0,
            why_relevant="Direct database authority lookup",
            ratio_extract=case.ratio_decidendi,
            pinpoint_passages=[],
            citation_verification=None,
            is_demo_data=False,
        )
        return self.citation_verifier.verify_authority(auth_dto)
