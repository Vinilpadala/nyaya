from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.research import (
    ResearchQueryRequest,
    ResearchSynthesisResponse,
    RetrievedAuthorityDTO,
    RetrievedStatuteDTO,
    CitationVerificationDTO,
    ResearchTrailDTO,
    ResearchTrailStep,
    UncertaintyAssessmentDTO,
)
from app.services.rag.lexical_retriever import LexicalBM25Retriever, tokenize
from app.services.rag.vector_retriever import VectorRetriever
from app.services.rag.authority_ranker import AuthorityRanker
from app.services.rag.citation_verifier import CitationVerifier
from app.services.rag.uncertainty_engine import UncertaintyEngine
from app.services.rag.synthesizer import LegalSynthesizer
from app.services.llm.evidence_pack import build_evidence_pack
from app.services.llm.factory import get_llm_provider
from app.services.llm.validator import DeterministicCitationGuard
from app.services.analytics.pattern_engine import HistoricalPatternService
from app.services.translation import TranslationService
import logging

logger = logging.getLogger(__name__)


class RAGResearchOrchestrator:
    """Orchestrates modular retrieval, precedent ranking, citator verification,
    uncertainty analysis, and explainable judicial synthesis.
    """

    def __init__(self, db: Session):
        self.db = db
        self.lexical_retriever = LexicalBM25Retriever(db)
        self.vector_retriever = VectorRetriever(db)
        self.citation_verifier = CitationVerifier(db)
        self.translation_service = TranslationService()

    def execute_research(self, req: ResearchQueryRequest) -> ResearchSynthesisResponse:
        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

        # ---------------------------------------------------------
        # Multilingual Query Conversion (Ingress)
        # ---------------------------------------------------------
        target_language = (getattr(req, "language", None) or "en").lower().strip()
        original_query = req.query
        effective_query = req.query
        translated_query_str = None
        query_trans_engine = None

        if target_language != "en":
            effective_query, query_trans_engine = self.translation_service.translate_query_to_english(
                query=req.query,
                language=target_language
            )
            if effective_query != req.query:
                translated_query_str = effective_query

        # ---------------------------------------------------------
        # STEP 1: Query Analysis
        # ---------------------------------------------------------
        query_tokens = tokenize(effective_query)
        if req.case_context:
            query_tokens.extend(tokenize(req.case_context))

        step1_details = []
        if target_language != "en":
            step1_details.append(f"Multilingual Input: {target_language.upper()} (Engine: {query_trans_engine})")
            if translated_query_str:
                step1_details.append(f"English Legal Conversion: '{translated_query_str}'")

        step1_details.extend([
            f"Extracted {len(query_tokens)} search terms from judicial query",
            f"Jurisdiction filter: {req.jurisdiction}",
            f"Include overruled precedents: {req.include_overruled}",
        ])
        if req.min_bench_strength:
            step1_details.append(f"Minimum bench strength requirement: {req.min_bench_strength} Judges")

        trail_step1 = ResearchTrailStep(
            step_number=1,
            stage="QUERY_ANALYSIS",
            title="Judicial Query Parsing & Filter Expansion",
            description=f"Parsed '{req.query[:60]}...' into legal keywords and statutory terms.",
            items_count=len(query_tokens),
            timestamp=now_str,
            details=step1_details,
        )

        # ---------------------------------------------------------
        # STEP 2: Modular Source Retrieval
        # ---------------------------------------------------------
        # Primary: Reliable Lexical BM25 retrieval over verified corpus
        retrieved_passages = self.lexical_retriever.search_passages(
            query=effective_query,
            case_context=req.case_context,
            jurisdiction=req.jurisdiction,
            min_bench_strength=req.min_bench_strength,
            include_overruled=req.include_overruled,
            limit=12,
        )

        retrieved_statutes_raw = self.lexical_retriever.search_statutes(
            query=effective_query,
            case_context=req.case_context,
            limit=4,
        )

        # Modular hook: If dense vector retriever is active, hybrid search would be invoked here
        vector_available = self.vector_retriever.is_available()
        if vector_available:
            # Future hybrid fusion: reciprocal rank fusion (RRF)
            pass

        # Convert statute search results to DTOs
        retrieved_statutes: List[RetrievedStatuteDTO] = [
            RetrievedStatuteDTO(
                id=s.section_id,
                statute_title=s.statute_title,
                section_number=s.section_number,
                heading=s.heading,
                content=s.content,
                amendment_notes=s.amendment_notes,
                why_relevant=s.why_relevant,
                is_demo_data=False,
            )
            for s in retrieved_statutes_raw
        ]

        trail_step2 = ResearchTrailStep(
            step_number=2,
            stage="SOURCE_RETRIEVAL",
            title="Modular Statutory & Precedent Retrieval",
            description=f"Retrieved {len(retrieved_passages)} verbatim passages and {len(retrieved_statutes)} statutory provisions.",
            items_count=len(retrieved_passages) + len(retrieved_statutes),
            timestamp=now_str,
            details=[
                f"Retrieved {len(retrieved_passages)} authoritative passages using Lexical BM25",
                f"Retrieved {len(retrieved_statutes)} statutory sections from verified central acts",
                f"Pluggable Vector Retriever Status: {'Active' if vector_available else 'Ready for dense embeddings (Modular Interface)'}",
            ],
        )

        # ---------------------------------------------------------
        # STEP 3: Precedent Authority Ranking & Verbatim Passage Extraction
        # ---------------------------------------------------------
        # Pre-fetch citation treatment status for distinct candidate cases
        candidate_case_ids = list(dict.fromkeys(p.case_id for p in retrieved_passages))
        candidate_treatments = {}
        for cid in candidate_case_ids:
            try:
                cv = self.citation_verifier.verify_by_case_id(cid)
                if cv:
                    candidate_treatments[cid] = cv
            except Exception:
                pass

        ranked_authorities = AuthorityRanker.rank_and_aggregate(
            passages=retrieved_passages,
            limit=5,
            requested_jurisdiction=req.jurisdiction,
            citation_verifications=candidate_treatments,
        )

        # Assemble verified citation verification DTOs in rank order
        citation_verifications = [
            candidate_treatments.get(a.id) or self.citation_verifier.verify_authority(a)
            for a in ranked_authorities
        ]
        citation_verifications = [cv for cv in citation_verifications if cv is not None]

        # Ensure authority DTOs have citation_verification attached
        for a in ranked_authorities:
            if not a.citation_verification:
                a.citation_verification = candidate_treatments.get(a.id)

        total_passages_extracted = sum(len(a.pinpoint_passages) for a in ranked_authorities)
        step3_details = [
            f"Ranked {len(ranked_authorities)} distinct judicial authorities based on Indian court hierarchy and bench quorum",
            f"Extracted {total_passages_extracted} verbatim pinpoint passages with exact reporter paragraph numbers",
            f"Verified citation treatment history for {len(citation_verifications)} authorities against official law reporters",
        ]

        trail_step3 = ResearchTrailStep(
            step_number=3,
            stage="PASSAGE_EXTRACTION",
            title="Precedent Hierarchy Ranking & Citation Verification",
            description=f"Evaluated bench quorums, court hierarchy, and verified reporter citations.",
            items_count=total_passages_extracted,
            timestamp=now_str,
            details=step3_details,
        )

        # ---------------------------------------------------------
        # STEP 4: Uncertainty Assessment & Grounded Synthesis
        # ---------------------------------------------------------
        uncertainty = UncertaintyEngine.assess(
            query=effective_query,
            case_context=req.case_context,
            authorities=ranked_authorities,
            statutes=retrieved_statutes,
            requested_jurisdiction=req.jurisdiction,
        )

        # 1. Historical Precedent Pattern Analysis (Non-ML Empirical Benchmark)
        historical_patterns = HistoricalPatternService.analyze_precedents(
            authorities=ranked_authorities,
            citation_verifications=citation_verifications,
            query=effective_query,
        )

        # 2. Build strongly-typed Evidence Pack from verified retrieval & citator
        evidence_pack = build_evidence_pack(
            query=effective_query,
            ranked_authorities=ranked_authorities,
            citation_verifications=citation_verifications,
            retrieved_passages=retrieved_passages,
            retrieved_statutes=retrieved_statutes,
            commercial_domain=req.jurisdiction or "Commercial Division / Commercial Appellate Division",
        )

        # 2. Attempt Grounded LLM Generation via Provider Abstraction
        llm_provider = get_llm_provider()
        structured_llm_output = None
        validation_violations = []
        provider_name = "Deterministic Fallback"
        llm_used = False
        fallback_notice = None

        if llm_provider.is_available():
            try:
                raw_llm_output = llm_provider.generate_grounded_synthesis(evidence_pack)
                if raw_llm_output:
                    is_valid, sanitized_output, violations = DeterministicCitationGuard.validate(
                        raw_llm_output, evidence_pack
                    )
                    validation_violations = violations
                    if is_valid:
                        structured_llm_output = sanitized_output
                        provider_name = llm_provider.get_provider_name()
                        llm_used = True
                    else:
                        fallback_notice = "AI synthesis is temporarily unavailable. Nyaya AI has returned the grounded deterministic research result."
                        logger.warning(
                            f"LLM synthesis rejected by DeterministicCitationGuard: "
                            f"{[v.to_dict() for v in violations]}. Falling back to deterministic synthesizer."
                        )
                else:
                    fallback_notice = "AI synthesis is temporarily unavailable. Nyaya AI has returned the grounded deterministic research result."
            except Exception as e:
                fallback_notice = "AI synthesis is temporarily unavailable. Nyaya AI has returned the grounded deterministic research result."
                logger.warning(f"Error in LLM synthesis pipeline: {type(e).__name__}. Falling back to deterministic synthesizer.")

        # 3. If LLM synthesis succeeded and passed citation guard, format synthesis
        if structured_llm_output and llm_used:
            analysis_lines = [
                "### Judicial Research Analysis: Commercial Bench Briefing",
                f"**Research Query:** *{req.query}*",
            ]
            if req.case_context:
                analysis_lines.append(f"**Matter Context:** *{req.case_context}*")
            analysis_lines.append("")

            if structured_llm_output.key_principles:
                analysis_lines.append("#### I. Controlling Legal Principles")
                for p in structured_llm_output.key_principles:
                    analysis_lines.append(f"- {p}")
                analysis_lines.append("")

            if structured_llm_output.governing_statutes:
                analysis_lines.append("#### II. Applicable Statutory Framework")
                for s in structured_llm_output.governing_statutes:
                    analysis_lines.append(f"- {s}")
                analysis_lines.append("")

            if structured_llm_output.cited_authorities:
                analysis_lines.append("#### III. Authoritative Precedents & Pinpoint Analysis")
                for ca in structured_llm_output.cited_authorities:
                    para_str = f" [Paras {', '.join(str(p) for p in ca.cited_paragraphs)}]" if ca.cited_paragraphs else ""
                    analysis_lines.append(f"- **{ca.title}** ({ca.citation}) — *{ca.court}* ({ca.year}){para_str}:")
                    analysis_lines.append(f"  *Ratio Decidendi:* {ca.key_ratio}")
                    if ca.treatment_status:
                        analysis_lines.append(f"  *Treatment:* `{ca.treatment_status}`")
                    if ca.verbatim_quotes:
                        for q in ca.verbatim_quotes:
                            analysis_lines.append(f"  > \"{q}\"")
                    if ca.relevance_to_query:
                        analysis_lines.append(f"  *Relevance:* {ca.relevance_to_query}")
                analysis_lines.append("")

            if structured_llm_output.practical_implications:
                analysis_lines.append("#### IV. Evidentiary Burden & Commercial Dispute Implications")
                analysis_lines.append(structured_llm_output.practical_implications)
                analysis_lines.append("")

            if structured_llm_output.corpus_limitations:
                analysis_lines.append("#### V. Corpus Boundary & Safeguards")
                analysis_lines.append(f"> {structured_llm_output.corpus_limitations}")

            # Format bench action points from guidance
            guidance_points = [
                pt.strip("- *").strip()
                for pt in structured_llm_output.bench_guidance.split("\n")
                if pt.strip() and len(pt.strip()) > 10
            ]
            if not guidance_points:
                guidance_points = [structured_llm_output.bench_guidance]

            synthesis_content = {
                "ai_generated_summary": structured_llm_output.summary,
                "ai_legal_analysis": "\n".join(analysis_lines),
                "cautious_inferences": structured_llm_output.key_principles[:5],
                "bench_action_points": guidance_points[:5],
            }
        else:
            # Fallback to deterministic synthesizer
            synthesis_content = LegalSynthesizer.generate_synthesis(
                query=effective_query,
                case_context=req.case_context,
                authorities=ranked_authorities,
                statutes=retrieved_statutes,
            )

        has_overruled = any(not a.is_good_law for a in ranked_authorities)

        # ---------------------------------------------------------
        # Multilingual Synthesis Translation (Egress)
        # ---------------------------------------------------------
        trans_result = self.translation_service.translate_synthesis(
            summary=synthesis_content["ai_generated_summary"],
            analysis=synthesis_content["ai_legal_analysis"],
            target_language=target_language,
        )

        step4_details = [
            f"Decision Confidence: {int(uncertainty.confidence_score * 100)}% ({uncertainty.uncertainty_level})",
            f"Synthesis Engine: {provider_name}",
            f"Evidence Pack: {len(evidence_pack.authorities)} authorities, {evidence_pack.total_passages_count} passages, {len(evidence_pack.statutes)} statutes",
            f"Citation Guard: {'Verified Grounded (Zero Fabrication)' if llm_used else 'Deterministic Rule-Based Baseline'}",
        ]
        if target_language != "en":
            step4_details.append(
                f"Translation: {trans_result.get('translation_engine')} ({target_language.upper()})"
            )
        if historical_patterns:
            step4_details.append(
                f"Pattern Analytics: {historical_patterns.comparable_authorities_count} authentic precedent(s) analyzed ({historical_patterns.active_regime_status})"
            )
        if not llm_used and fallback_notice:
            step4_details.append(f"Notice: {fallback_notice}")
        elif not llm_used:
            step4_details.append("Notice: Deterministic grounded research synthesis baseline applied.")
        if validation_violations:
            remediated_count = sum(1 for v in validation_violations if v.severity == "WARNING")
            critical_count = sum(1 for v in validation_violations if v.severity == "CRITICAL")
            if critical_count > 0:
                step4_details.append(f"Citation Guard: {critical_count} critical violation(s) flagged -> Safe Fallback Active")
            elif remediated_count > 0:
                step4_details.append(f"Citation Guard: {remediated_count} unverified quote/pinpoint(s) pruned")

        trail_step4 = ResearchTrailStep(
            step_number=4,
            stage="AI_SYNTHESIS",
            title="Source-Grounded Judicial Synthesis",
            description=f"Synthesized judicial briefing via {provider_name} with strict evidence pack grounding.",
            items_count=len(synthesis_content["bench_action_points"]),
            timestamp=now_str,
            details=step4_details,
        )

        research_trail = ResearchTrailDTO(
            query_analysis_step=trail_step1,
            retrieval_step=trail_step2,
            passage_extraction_step=trail_step3,
            ai_synthesis_step=trail_step4,
        )

        return ResearchSynthesisResponse(
            query=req.query,
            case_context=req.case_context,
            jurisdiction=req.jurisdiction,
            retrieved_authorities=ranked_authorities,
            retrieved_statutes=retrieved_statutes,
            citation_verifications=citation_verifications,
            research_trail=research_trail,
            uncertainty_assessment=uncertainty,
            ai_generated_summary=synthesis_content["ai_generated_summary"],
            ai_legal_analysis=synthesis_content["ai_legal_analysis"],
            cautious_inferences=synthesis_content["cautious_inferences"],
            bench_action_points=synthesis_content["bench_action_points"],
            has_overruled_authorities=has_overruled,
            synthesis_engine=provider_name,
            fallback_notice=fallback_notice,
            historical_pattern_analysis=historical_patterns,
            language=target_language,
            original_query=original_query if target_language != "en" else None,
            translated_query=translated_query_str,
            translated_summary=trans_result.get("translated_summary"),
            translated_analysis=trans_result.get("translated_analysis"),
            translation_engine=trans_result.get("translation_engine"),
            translation_notice=trans_result.get("translation_notice"),
            is_demo_data=False,
        )
