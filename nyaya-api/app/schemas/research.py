from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ResearchQueryRequest(BaseModel):
    query: str = Field(..., description="Natural-language legal issue or commercial query")
    case_context: Optional[str] = Field(None, description="Factual context of the ongoing commercial matter")
    jurisdiction: str = Field("ALL", description="Target court jurisdiction or 'ALL'")
    statute_filter: Optional[str] = Field(None, description="Filter by statute (e.g., Commercial Courts Act, 2015)")
    include_overruled: bool = Field(False, description="Whether to include overruled authorities in historical analysis")
    min_bench_strength: Optional[int] = Field(None, description="Minimum bench quorum strength (e.g. 2 for DB, 5 for CB)")
    language: str = Field("en", description="ISO language code for research interface (e.g., 'en', 'hi', 'te')")
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Research query must contain at least 2 non-whitespace characters")
        return cleaned



class PinpointPassageDTO(BaseModel):
    paragraph_number: int
    text: str
    significance: str
    source_provenance: Optional[str] = "Supreme Court Reports (SCR) / Official Record"


class CitationTreatmentRecord(BaseModel):
    treatment: str  # AFFIRMED, OVERRULED, DISTINGUISHED, CONSIDERED, APPLIED
    citing_case: str
    citation: str
    year: int
    court: str
    bench_strength: int


class CitationVerificationDTO(BaseModel):
    case_id: str
    case_title: str
    standard_citation: str
    neutral_citation: str
    court: str
    judgment_date: str
    bench_quorum: str
    bench_strength: int
    law_reporter_verified: bool = True
    official_reporter: str = "Supreme Court Cases (SCC) / Supreme Court Reports (SCR)"
    good_law_status: str = "Good Law"  # "Good Law", "Caution: Distinguished / Modified", "Overruled Precedent", "Presumed Good Law (No Treatment Data in Corpus)", "Unverified: Insufficient Corpus Coverage"
    is_good_law: bool = True
    treatment_history: List[CitationTreatmentRecord] = []
    verification_notes: str = ""
    corpus_coverage_status: str = "VERIFIED_IN_CORPUS"  # "VERIFIED_IN_CORPUS", "NO_TREATMENT_FOUND", "NEGATIVE_TREATMENT_FOUND", "INSUFFICIENT_CORPUS"
    is_demo_data: bool = False


class RetrievedAuthorityDTO(BaseModel):
    id: str
    title: str
    standard_citation: str
    neutral_citation: str
    court: str
    judgment_date: str
    bench_quorum: str
    bench_strength: int
    jurisdiction: Optional[str] = "ALL"
    source_provenance: Optional[str] = "Supreme Court Cases (SCC) / Official Law Reports"
    is_good_law: bool
    status_summary: str
    relevance_score: float
    why_relevant: str
    ratio_extract: str
    pinpoint_passages: List[PinpointPassageDTO] = []
    citation_verification: Optional[CitationVerificationDTO] = None
    is_demo_data: bool = True


class RetrievedStatuteDTO(BaseModel):
    id: str
    statute_title: str
    section_number: str
    heading: str
    content: str
    amendment_notes: Optional[str] = None
    why_relevant: str
    is_demo_data: bool = True


class ResearchTrailStep(BaseModel):
    step_number: int
    stage: str  # "QUERY_ANALYSIS", "SOURCE_RETRIEVAL", "PASSAGE_EXTRACTION", "AI_SYNTHESIS"
    title: str
    description: str
    items_count: int
    timestamp: str
    details: List[str] = []


class ResearchTrailDTO(BaseModel):
    query_analysis_step: ResearchTrailStep
    retrieval_step: ResearchTrailStep
    passage_extraction_step: ResearchTrailStep
    ai_synthesis_step: ResearchTrailStep


class UncertaintyAssessmentDTO(BaseModel):
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    uncertainty_level: str  # "LOW", "MEDIUM", "HIGH"
    is_ambiguous: bool
    has_conflicting_authorities: bool
    reason: str
    cautionary_guidance: str
    corpus_limitation_note: Optional[str] = (
        "Analysis grounded strictly in the curated commercial repository. "
        "This repository contains benchmark commercial precedents and central statutes; "
        "it is not an exhaustive national legal database."
    )
    retrieval_quality_score: Optional[float] = None
    score_margin: Optional[float] = None


class PrecedentDispositionItem(BaseModel):
    case_title: str
    standard_citation: str
    court: str
    year: int
    bench_strength: int
    legal_status: str  # e.g., "CURRENT_GOOD_LAW" or "OVERRULED_PRECEDENT"
    treatment_summary: str  # Citator treatment
    procedural_posture: str  # Procedural stage/application type
    actual_disposition: str  # Explicit authentic holding disposition or "Outcome data not available in curated corpus"
    disposition_provenance: str  # Source of disposition (e.g., "Official Law Report (SCC/SCR)")
    ratio_summary: str
    is_active_law: bool


class HistoricalPatternAnalysisDTO(BaseModel):
    query_issue: str
    comparable_authorities_count: int
    temporal_span: str
    courts_represented: List[str]
    bench_strength_breakdown: dict[str, int] = {}
    active_precedent_patterns: List[PrecedentDispositionItem] = []
    overruled_precedent_patterns: List[PrecedentDispositionItem] = []
    controlling_doctrine_summary: str
    legal_regime_period: str
    active_regime_status: str
    methodology_note: str = (
        "Non-ML Empirical Benchmark: Transparent aggregate analysis of authentic precedent authorities. "
        "Does not utilize probabilistic machine learning."
    )
    data_readiness_notice: str = (
        "Genuine predictive ML will be considered only after sufficient authentic, representative, "
        "labelled historical data is available and rigorous out-of-sample evaluation demonstrates "
        "statistical reliability, calibration, generalization, and acceptable uncertainty."
    )
    judicial_disclaimer: str = (
        "Judicial Independence Notice: Historical precedent patterns illustrate appellate jurisprudence. "
        "They do not predict, forecast, or prescribe the outcome of the present commercial matter."
    )


class ResearchSynthesisResponse(BaseModel):
    query: str
    case_context: Optional[str] = None
    jurisdiction: str
    retrieved_authorities: List[RetrievedAuthorityDTO]
    retrieved_statutes: List[RetrievedStatuteDTO]
    citation_verifications: List[CitationVerificationDTO] = []
    research_trail: ResearchTrailDTO
    uncertainty_assessment: UncertaintyAssessmentDTO
    ai_generated_summary: str
    ai_legal_analysis: str
    cautious_inferences: List[str]
    bench_action_points: List[str]
    has_overruled_authorities: bool
    synthesis_engine: str = "Deterministic Fallback"
    fallback_notice: Optional[str] = None
    historical_pattern_analysis: Optional[HistoricalPatternAnalysisDTO] = None
    language: str = "en"
    original_query: Optional[str] = None
    translated_query: Optional[str] = None
    translated_summary: Optional[str] = None
    translated_analysis: Optional[str] = None
    translation_engine: Optional[str] = None
    translation_notice: Optional[str] = None
    is_demo_data: bool = True


class SavedResearchCreate(BaseModel):
    matter_id: Optional[str] = None
    query_text: str
    case_context: Optional[str] = None
    jurisdiction: str = "ALL"
    lead_citation: str = ""
    lead_title: str = ""
    summary_extract: str = ""
    confidence_score: float = 0.95
    uncertainty_level: str = "LOW"
    notes: str = ""
    tags: str = "Pre-Institution Mediation, Commercial Courts Act"
    full_payload: Dict[str, Any] = {}
    is_demo_data: bool = True


class SavedResearchResponse(BaseModel):
    id: str
    user_id: str
    matter_id: Optional[str] = None
    query_text: str
    case_context: Optional[str] = None
    jurisdiction: str
    lead_citation: str
    lead_title: str
    summary_extract: str
    confidence_score: float
    uncertainty_level: str
    notes: str
    tags: str
    full_payload: Dict[str, Any] = {}
    is_demo_data: bool
    created_at: str


class ResearchSessionHistoryItem(BaseModel):
    id: str
    timestamp: str
    query: str
    jurisdiction: str
    results_count: int
    action: str
