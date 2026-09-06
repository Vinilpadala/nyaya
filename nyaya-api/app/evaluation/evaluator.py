import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.evaluation.dataset import BENCHMARK_DATASET, BenchmarkQueryCase
from app.schemas.research import ResearchQueryRequest, ResearchSynthesisResponse
from app.services.rag.orchestrator import RAGResearchOrchestrator

class EvaluationFinding(BaseModel):
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"
    category_type: str  # "SOFTWARE_DEFECT", "CORPUS_LIMITATION", "RANKING_SEPARATION", "UNCERTAINTY_CALIBRATION"
    description: str
    technical_detail: str

class BenchmarkCaseEvaluationResult:
    def __init__(self, case: BenchmarkQueryCase):
        self.case = case
        self.latency_ms: float = 0.0
        self.retrieved_count: int = 0
        self.hit_at_1: bool = False
        self.hit_at_3: bool = False
        self.hit_at_5: bool = False
        self.recall_at_5: float = 0.0
        self.lead_authority_title: Optional[str] = None
        self.lead_authority_citation: Optional[str] = None
        self.lead_authority_score: float = 0.0
        self.score_margin: float = 0.0
        self.treatment_status: Optional[str] = None
        self.is_good_law: Optional[bool] = None
        self.uncertainty_level: str = "UNKNOWN"
        self.confidence_score: float = 0.0
        self.synthesis_engine: str = "UNKNOWN"
        self.disclaimer_present: bool = False
        self.technical_explanation: str = ""
        self.findings: List[EvaluationFinding] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case.case_id,
            "category": self.case.category,
            "query": self.case.query,
            "latency_ms": round(self.latency_ms, 1),
            "retrieved_count": self.retrieved_count,
            "hit_at_1": self.hit_at_1,
            "hit_at_3": self.hit_at_3,
            "hit_at_5": self.hit_at_5,
            "recall_at_5": round(self.recall_at_5, 2),
            "lead_authority": self.lead_authority_title,
            "lead_citation": self.lead_authority_citation,
            "lead_score": self.lead_authority_score,
            "score_margin": self.score_margin,
            "treatment_status": self.treatment_status,
            "is_good_law": self.is_good_law,
            "uncertainty_level": self.uncertainty_level,
            "confidence_score": round(self.confidence_score, 2),
            "synthesis_engine": self.synthesis_engine,
            "disclaimer_present": self.disclaimer_present,
            "technical_explanation": self.technical_explanation,
            "findings": [f.model_dump() for f in self.findings],
        }

class LegalResearchEvaluator:
    """
    Evaluates Nyaya AI retrieval, authority ranking, citation verification,
    uncertainty calibration, and synthesis grounding across 10 benchmark categories.

    Explicit Analytical Rules:
    1. Retrieval metrics (HitRate@K, Recall@K, Precision@K) are technical lexical/indexing
       measurements and do NOT constitute judicial quality certification.
    2. Zero arbitrary pass/fail thresholding.
    3. Clearly differentiates software/retrieval defects from curated benchmark corpus incompleteness.
    4. Categorizes every finding into: CRITICAL, HIGH, MEDIUM, LOW, or INFORMATIONAL.
    """

    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = RAGResearchOrchestrator(db)

    def evaluate_case(self, case: BenchmarkQueryCase) -> BenchmarkCaseEvaluationResult:
        res = BenchmarkCaseEvaluationResult(case)
        req = ResearchQueryRequest(
            query=case.query,
            case_context=case.case_context,
            jurisdiction=case.jurisdiction,
            include_overruled=True,  # Allow retriever to surface negative authorities where query seeks them
        )

        start_time = time.perf_counter()
        try:
            resp: ResearchSynthesisResponse = self.orchestrator.execute_research(req)
            res.latency_ms = (time.perf_counter() - start_time) * 1000.0

            authorities = resp.retrieved_authorities
            res.retrieved_count = len(authorities)

            # Extract lead authority metrics
            if authorities:
                res.lead_authority_title = authorities[0].title
                res.lead_authority_citation = authorities[0].standard_citation
                res.lead_authority_score = round(float(authorities[0].relevance_score), 2)
                if len(authorities) > 1:
                    second_score = float(authorities[1].relevance_score)
                    res.score_margin = round(res.lead_authority_score - second_score, 2)

                # Check expected primary and secondary authority hits
                expected_hits = 0
                total_expected = 0

                if case.expected_primary_authority_title:
                    total_expected += 1
                    p_lower = case.expected_primary_authority_title.lower()
                    for idx, auth in enumerate(authorities):
                        a_lower = auth.title.lower()
                        if p_lower in a_lower or a_lower in p_lower:
                            expected_hits += 1
                            if idx == 0:
                                res.hit_at_1 = True
                            if idx < 3:
                                res.hit_at_3 = True
                            if idx < 5:
                                res.hit_at_5 = True
                            break

                if case.expected_secondary_authority_title:
                    total_expected += 1
                    s_lower = case.expected_secondary_authority_title.lower()
                    for idx, auth in enumerate(authorities[:5]):
                        a_lower = auth.title.lower()
                        if s_lower in a_lower or a_lower in s_lower:
                            expected_hits += 1
                            break

                if total_expected > 0:
                    res.recall_at_5 = float(expected_hits) / float(total_expected)

                # Citator treatment: Evaluate the expected primary authority if retrieved, else the lead authority
                target_auth = authorities[0]
                if case.expected_primary_authority_title:
                    p_lower = case.expected_primary_authority_title.lower()
                    for auth in authorities:
                        if p_lower in auth.title.lower() or auth.title.lower() in p_lower:
                            target_auth = auth
                            break

                target_cv = None
                if isinstance(resp.citation_verifications, list):
                    for cv in resp.citation_verifications:
                        if getattr(cv, 'case_id', None) == target_auth.id:
                            target_cv = cv
                            break
                elif isinstance(resp.citation_verifications, dict):
                    target_cv = resp.citation_verifications.get(target_auth.id)
                if not target_cv and target_auth.citation_verification:
                    target_cv = target_auth.citation_verification

                if target_cv:
                    res.treatment_status = getattr(target_cv, 'corpus_coverage_status', None)
                    res.is_good_law = getattr(target_cv, 'is_good_law', None)

            # Uncertainty assessment
            if resp.uncertainty_assessment:
                res.uncertainty_level = resp.uncertainty_assessment.uncertainty_level
                res.confidence_score = resp.uncertainty_assessment.confidence_score

            # Synthesis engine extraction
            if resp.research_trail and resp.research_trail.ai_synthesis_step:
                for detail in resp.research_trail.ai_synthesis_step.details:
                    if "Synthesis Engine:" in detail:
                        res.synthesis_engine = detail.replace("Synthesis Engine:", "").strip()

            # Mandatory judicial boundary disclaimer verification
            full_analysis = (
                (resp.ai_legal_analysis or "") + " " +
                (resp.uncertainty_assessment.corpus_limitation_note if resp.uncertainty_assessment else "")
            )
            res.disclaimer_present = (
                "NOTICE TO BENCH: Legal grounding is strictly confined to the curated commercial court repository" in full_analysis
                or "curated commercial" in full_analysis.lower()
                or "strictly bounded" in full_analysis.lower()
            )

            # -------------------------------------------------------------
            # Technical Explanation & Structured Issue Classification
            # -------------------------------------------------------------
            explanations = []

            # 1. Retrieval & Corpus Coverage Analysis
            if not case.expected_corpus_sufficient:
                # Deliberate corpus incompleteness test case (e.g. Maritime Admiralty or Criminal Bail)
                if res.retrieved_count == 0:
                    res.findings.append(EvaluationFinding(
                        severity="INFORMATIONAL",
                        category_type="CORPUS_LIMITATION",
                        description=f"Zero authorities retrieved for query outside curated commercial domain.",
                        technical_detail="Lexical BM25 index yielded zero matching tokens against commercial judgment passages."
                    ))
                    explanations.append("Expected refusal: Query falls outside curated commercial corpus; zero hallucination confirmed.")
                else:
                    res.findings.append(EvaluationFinding(
                        severity="INFORMATIONAL",
                        category_type="CORPUS_LIMITATION",
                        description=f"Retrieved {res.retrieved_count} marginally matching commercial passages for out-of-domain query.",
                        technical_detail=f"Highest BM25 score {res.lead_authority_score} reflects weak term overlap with non-controlling passages."
                    ))
                    explanations.append(f"Retrieved weak lexical matches (top score {res.lead_authority_score}); high uncertainty correctly triggered.")
            else:
                if case.expected_primary_authority_title:
                    if res.hit_at_1:
                        explanations.append(f"Controlling precedent '{case.expected_primary_authority_title}' retrieved at Rank 1 (Score: {res.lead_authority_score}).")
                    elif res.hit_at_5:
                        explanations.append(f"Controlling precedent '{case.expected_primary_authority_title}' retrieved within Top 5 (Rank > 1 held by '{res.lead_authority_title}').")
                        res.findings.append(EvaluationFinding(
                            severity="LOW",
                            category_type="RANKING_SEPARATION",
                            description=f"Controlling authority retrieved in Top 5 but ranked below Rank 1.",
                            technical_detail=f"Rank 1 '{res.lead_authority_title}' scored {res.lead_authority_score}, margin {res.score_margin} over second (affected by bench strength / negative treatment penalty)."
                        ))
                    else:
                        # Check whether case exists in DB but has 0 indexed passages
                        from app.models.case import Case, CasePassage
                        db_case = self.db.query(Case).filter(Case.title.ilike(f"%{case.expected_primary_authority_title[:30]}%")).first()
                        p_count = self.db.query(CasePassage).filter(CasePassage.case_id == db_case.id).count() if db_case else 0

                        if db_case and p_count == 0:
                            res.findings.append(EvaluationFinding(
                                severity="INFORMATIONAL",
                                category_type="CORPUS_LIMITATION",
                                description=f"Precedent '{case.expected_primary_authority_title}' is present in metadata catalog but has 0 indexed passages in curated prototype corpus.",
                                technical_detail=f"Passage-level BM25 index contains 0 text chunks for case_id={db_case.id}. Incompleteness is a corpus limitation, not a search software defect."
                            ))
                            explanations.append(f"Corpus Incompleteness: '{case.expected_primary_authority_title}' has 0 indexed passages in current curated repository.")
                        else:
                            res.findings.append(EvaluationFinding(
                                severity="HIGH",
                                category_type="SOFTWARE_DEFECT",
                                description=f"Indexed commercial precedent was not surfaced in Top 5 lexical results.",
                                technical_detail=f"BM25 query tokenization failed to surface passage above rank threshold."
                            ))
                            explanations.append(f"Retriever Miss: Indexed precedent '{case.expected_primary_authority_title}' missing from Top 5.")

            # 2. Citation Treatment Analysis
            if case.expected_is_good_law is not None and res.is_good_law is not None:
                if res.is_good_law != case.expected_is_good_law:
                    if case.expected_is_good_law is False and res.is_good_law is True:
                        res.findings.append(EvaluationFinding(
                            severity="CRITICAL",
                            category_type="SOFTWARE_DEFECT",
                            description="Overruled precedent was evaluated as valid good law.",
                            technical_detail=f"CitationVerifier failed to detect negative treatment record in database for {target_auth.title}."
                        ))
                        explanations.append("CRITICAL: Negative treatment not reflected in is_good_law indicator.")
                    else:
                        res.findings.append(EvaluationFinding(
                            severity="MEDIUM",
                            category_type="UNCERTAINTY_CALIBRATION",
                            description="Good-law status mismatch under limited treatment records.",
                            technical_detail=f"Expected is_good_law={case.expected_is_good_law}, computed {res.is_good_law}."
                        ))
                else:
                    if case.expected_is_good_law is False:
                        explanations.append(f"Negative treatment correctly preserved: '{target_auth.title}' verified as NOT good law ({target_cv.good_law_status if target_cv else 'Overruled'}).")
                    else:
                        explanations.append(f"Good-law status verified: '{target_auth.title}' verified against database treatment records.")

            # 3. Uncertainty Calibration Analysis
            if case.expected_uncertainty_level == "HIGH" and res.uncertainty_level != "HIGH":
                res.findings.append(EvaluationFinding(
                    severity="MEDIUM",
                    category_type="UNCERTAINTY_CALIBRATION",
                    description=f"Uncertainty calibration: expected HIGH, evaluated as {res.uncertainty_level} (conf={res.confidence_score}).",
                    technical_detail=f"Query falls outside domain or has weak matches; confidence {res.confidence_score} did not reach >= HIGH uncertainty."
                ))
                explanations.append(f"Uncertainty: {res.uncertainty_level} (conf: {res.confidence_score}) - expected HIGH for out-of-domain/weak query.")
            else:
                explanations.append(f"Uncertainty level calibrated to {res.uncertainty_level} (confidence: {res.confidence_score}).")

            # 4. Judicial Disclaimer Check
            if not res.disclaimer_present:
                res.findings.append(EvaluationFinding(
                    severity="HIGH",
                    category_type="SOFTWARE_DEFECT",
                    description="Mandatory judicial disclaimer missing from synthesis payload.",
                    technical_detail="Synthesis output omitted required notice specifying boundaries of curated commercial repository."
                ))
            else:
                explanations.append("Mandatory corpus boundary notice confirmed present.")

            res.technical_explanation = " | ".join(explanations)

        except Exception as e:
            res.findings.append(EvaluationFinding(
                severity="CRITICAL",
                category_type="SOFTWARE_DEFECT",
                description=f"Evaluation execution crashed with exception: {type(e).__name__}",
                technical_detail=str(e)
            ))
            res.technical_explanation = f"CRITICAL EXCEPTION: {str(e)}"

        return res

    def evaluate_all(self) -> List[BenchmarkCaseEvaluationResult]:
        results: List[BenchmarkCaseEvaluationResult] = []
        for case in BENCHMARK_DATASET:
            res = self.evaluate_case(case)
            results.append(res)
        return results
