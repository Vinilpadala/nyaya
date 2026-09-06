from typing import List, Optional, Set

from app.schemas.research import (
    RetrievedAuthorityDTO,
    RetrievedStatuteDTO,
    UncertaintyAssessmentDTO,
)
from app.services.rag.lexical_retriever import tokenize


GENERIC_LEGAL_TERMS: Set[str] = {
    "commercial", "dispute", "disputes", "court", "act", "section", "suit", "case",
    "matter", "order", "rule", "proceedings", "stage", "claim", "relief", "application",
    "whether", "courts", "acts"
}

CORPUS_LIMITATION_DISCLAIMER = (
    "NOTICE TO BENCH: Legal grounding is strictly confined to the curated commercial court repository "
    "(benchmark precedents and foundational central statutes). This is an assistive decision-support engine "
    "and not an exhaustive national legal database. Formal citation verification with official law reports "
    "(SCC / SCR / ILR) is required prior to judicial orders."
)


class UncertaintyEngine:
    """Advanced judicial uncertainty assessment engine.
    
    Evaluates:
    - Retrieval quality and term coverage
    - Number and bench strength of relevant authorities
    - Score separation / margin between top results
    - Conflicting treatments and overruled authorities
    - Jurisdictional relevance (Article 141 binding vs territorial persuasive)
    - Missing or insufficient source data in corpus
    
    Operates with conservative confidence calibration and transparent reasoning,
    explicitly acknowledging curated corpus scope and limitations.
    """

    @staticmethod
    def assess(
        query: str,
        case_context: Optional[str],
        authorities: List[RetrievedAuthorityDTO],
        statutes: List[RetrievedStatuteDTO],
        requested_jurisdiction: str = "ALL",
    ) -> UncertaintyAssessmentDTO:
        # ---------------------------------------------------------
        # 1. Zero Results / Insufficient Corpus Evidence
        # ---------------------------------------------------------
        if not authorities and not statutes:
            return UncertaintyAssessmentDTO(
                confidence_score=0.25,
                uncertainty_level="HIGH",
                is_ambiguous=True,
                has_conflicting_authorities=False,
                reason=(
                    "INSUFFICIENT CORPUS EVIDENCE: No applicable statutory provisions or binding precedents "
                    "were identified in the curated commercial repository for this query."
                ),
                cautionary_guidance=(
                    "Corpus limitation alert: The local database contains benchmark commercial precedents. "
                    "Direct counsel to produce certified copies of controlling authorities from comprehensive national databases."
                ),
                corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                retrieval_quality_score=0.0,
                score_margin=0.0,
            )

        # ---------------------------------------------------------
        # 2. Conflicting & Overruled Precedents
        # ---------------------------------------------------------
        overruled_list = [
            a for a in authorities
            if not a.is_good_law or (a.citation_verification and a.citation_verification.good_law_status == "Overruled Precedent")
        ]

        if overruled_list:
            lead_overruled = overruled_list[0]
            return UncertaintyAssessmentDTO(
                confidence_score=0.45,
                uncertainty_level="HIGH",
                is_ambiguous=True,
                has_conflicting_authorities=True,
                reason=(
                    f"CONFLICTING / OVERRULED PRECEDENT DETECTED: Retrieved authority '{lead_overruled.title}' "
                    f"({lead_overruled.standard_citation}) has been formally overruled ({lead_overruled.status_summary}). "
                    f"Corpus contains conflicting historical and current jurisprudence on this subject."
                ),
                cautionary_guidance=(
                    "CRITICAL CITATION ALERT: Submissions or pleadings relying on the overruled holding must be rejected. "
                    "Ensure adjudication proceeds strictly on current Constitution Bench jurisprudence."
                ),
                corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                retrieval_quality_score=round(lead_overruled.relevance_score, 2),
                score_margin=0.0,
            )

        # Check for limiting / distinguished treatments
        distinguished_list = [
            a for a in authorities
            if a.citation_verification and "Caution" in a.citation_verification.good_law_status
        ]

        # ---------------------------------------------------------
        # 3. Domain Concept Alignment & Term Coverage
        # ---------------------------------------------------------
        q_tokens = tokenize(query)
        key_query_tokens = [t for t in q_tokens if t not in GENERIC_LEGAL_TERMS]
        top_authority = authorities[0] if authorities else None
        top_score = top_authority.relevance_score if top_authority else 0.0

        # Calculate score margin
        if len(authorities) >= 2:
            score_margin = round(authorities[0].relevance_score - authorities[1].relevance_score, 2)
        else:
            score_margin = round(top_score, 2)

        if top_authority and key_query_tokens:
            matched_in_top: Set[str] = set()
            for cp in top_authority.pinpoint_passages:
                matched_in_top.update(tokenize(cp.text))
            matched_in_top.update(tokenize(top_authority.title))
            matched_in_top.update(tokenize(top_authority.ratio_extract))

            unmatched_key = [t for t in key_query_tokens if t not in matched_in_top]

            has_unmatched_critical = any(
                t in unmatched_key for t in [
                    "unstamped", "stamp", "stamped", "stamping", "impounding", "defect",
                    "deficient", "forgery", "fraud", "limitation", "time-barred",
                    "moratorium", "insolvency", "admiralty", "maritime", "bail",
                    "crpc", "criminal", "arrest", "penal", "ipc", "bns"
                ]
            )

            matched_count = len([t for t in key_query_tokens if t in matched_in_top])
            match_ratio = matched_count / len(key_query_tokens) if key_query_tokens else 1.0
            unmatched_display = ", ".join(list(dict.fromkeys(unmatched_key))[:4]) if unmatched_key else "none"

            # 3A. Extremely Weak Retrieval / Out-of-Scope Query Signal
            if top_score < 3.5 or match_ratio < 0.25 or (match_ratio < 0.40 and top_score < 15.0):
                return UncertaintyAssessmentDTO(
                    confidence_score=0.40,
                    uncertainty_level="HIGH",
                    is_ambiguous=True,
                    has_conflicting_authorities=False,
                    reason=(
                        f"INSUFFICIENT CORPUS EVIDENCE / WEAK RETRIEVAL: Retrieval score is very low (score: {top_score:.2f}) "
                        f"and substantive query concepts ({unmatched_display}) are absent from verified commercial holdings. "
                        f"The absence of negative citation treatment does not indicate legal validity for weakly matched "
                        f"or out-of-domain submissions."
                    ),
                    cautionary_guidance=(
                        "Exercise strict judicial caution. The retrieved passages have marginal lexical overlap and "
                        "do not establish controlling authority for this issue. Require counsel to present authoritative "
                        "certified citations from primary legal reports."
                    ),
                    corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                    retrieval_quality_score=round(top_score, 2),
                    score_margin=score_margin,
                )

            # 3B. Partial Coverage / Missing Critical Legal Doctrine
            if has_unmatched_critical or (match_ratio < 0.40 and top_score < 10.0):
                return UncertaintyAssessmentDTO(
                    confidence_score=0.45 if has_unmatched_critical else 0.58,
                    uncertainty_level="HIGH" if (has_unmatched_critical or match_ratio < 0.30) else "MEDIUM",
                    is_ambiguous=True,
                    has_conflicting_authorities=False,
                    reason=(
                        f"PARTIAL CORPUS COVERAGE: Distinctive query concepts ({unmatched_display}) "
                        f"are not directly decided by the retrieved good-law precedents ({top_authority.title}). "
                        f"Match relies on broad procedural or commercial terms."
                    ),
                    cautionary_guidance=(
                        "EVIDENTIARY CAUTION: The retrieved authorities provide broad analogical principles "
                        "but do not decide the specific factual/statutory defect. Direct counsel to submit direct citations."
                    ),
                    corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                    retrieval_quality_score=round(top_score, 2),
                    score_margin=score_margin,
                )

        # ---------------------------------------------------------
        # 4. Limiting / Distinguished Precedent Check
        # ---------------------------------------------------------
        if distinguished_list and distinguished_list[0] == top_authority:
            lead_dist = distinguished_list[0]
            return UncertaintyAssessmentDTO(
                confidence_score=0.68,
                uncertainty_level="MEDIUM",
                is_ambiguous=True,
                has_conflicting_authorities=True,
                reason=(
                    f"QUALIFIED / DISTINGUISHED PRECEDENT: Top authority '{lead_dist.title}' ({lead_dist.standard_citation}) "
                    f"has recorded limiting treatment ({lead_dist.status_summary}). Its doctrine is not unconditionally applicable."
                ),
                cautionary_guidance=(
                    "Scrutinize factual pleadings closely to determine whether the narrow parameters of this distinguished "
                    "precedent apply to the current matter."
                ),
                corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                retrieval_quality_score=round(top_score, 2),
                score_margin=score_margin,
            )

        # ---------------------------------------------------------
        # 5. Score Separation & Jurisdictional Authority Evaluation
        # ---------------------------------------------------------
        has_constitution_bench = any(a.bench_strength >= 5 for a in authorities)
        has_statute_match = len(statutes) > 0

        # Check territorial / jurisdictional binding status
        jurisdiction_note = ""
        if requested_jurisdiction != "ALL" and top_authority:
            if "supreme court" in top_authority.court.lower():
                jurisdiction_note = " Binding nationwide authority under Article 141 of the Constitution."
            elif requested_jurisdiction.lower() in top_authority.court.lower():
                jurisdiction_note = f" Territorially binding authority in {top_authority.court}."
            else:
                jurisdiction_note = f" Persuasive territorial authority from {top_authority.court} (outside {requested_jurisdiction})."

        # Case A: High Certainty (Settled Landmark Precedent + Clear Score Margin)
        if (top_score >= 10.0 or (has_constitution_bench and top_score >= 6.0)) and (score_margin >= 3.0 or has_statute_match):
            # Calibrated conservatively: max 0.90 to 0.92, acknowledging curated corpus
            confidence = min(0.92, 0.86 + (top_score / 200.0))
            reason = (
                f"Settled landmark commercial jurisprudence established by {top_authority.court} "
                f"({top_authority.standard_citation}), supported by decisive score separation (Δ {score_margin} pts).{jurisdiction_note}"
            )
            if has_constitution_bench:
                reason += " Backed by 5-Judge Constitution Bench authority."

            guidance = (
                "Controlling principles are firmly established within the available corpus. "
                "Scrutinize factual pleadings strictly against the verbatim pinpoint paragraphs before granting orders."
            )

            return UncertaintyAssessmentDTO(
                confidence_score=round(confidence, 2),
                uncertainty_level="LOW",
                is_ambiguous=False,
                has_conflicting_authorities=False,
                reason=reason,
                cautionary_guidance=guidance,
                corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                retrieval_quality_score=round(top_score, 2),
                score_margin=score_margin,
            )

        # Case B: Moderate Certainty (Narrow Score Margin or Persuasive Only)
        elif top_score >= 4.0 or has_statute_match:
            confidence = 0.74 if score_margin >= 2.0 else 0.68
            reason = (
                f"Moderate legal certainty. Relevant statutory framework and persuasive authorities identified "
                f"(top authority: {top_authority.title if top_authority else 'Statutory Section'}, margin Δ {score_margin} pts).{jurisdiction_note}"
            )
            guidance = (
                "Application depends on specific contractual clauses and factual pleadings. "
                "Require parties to file joint compendium of citations addressing the points of divergence."
            )

            return UncertaintyAssessmentDTO(
                confidence_score=confidence,
                uncertainty_level="MEDIUM",
                is_ambiguous=False,
                has_conflicting_authorities=False,
                reason=reason,
                cautionary_guidance=guidance,
                corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                retrieval_quality_score=round(top_score, 2),
                score_margin=score_margin,
            )

        # Case C: Low Score / Weak Evidence
        else:
            return UncertaintyAssessmentDTO(
                confidence_score=0.42,
                uncertainty_level="HIGH",
                is_ambiguous=True,
                has_conflicting_authorities=False,
                reason=(
                    f"WEAK CORPUS EVIDENCE: Retrieval scores are low (top score: {top_score:.1f}) and score separation is negligible. "
                    f"The curated repository lacks definitive authorities directly on point."
                ),
                cautionary_guidance=(
                    "Exercise judicial caution. Require counsel to present authoritative certified citations and "
                    "test whether principles from other High Courts are applicable."
                ),
                corpus_limitation_note=CORPUS_LIMITATION_DISCLAIMER,
                retrieval_quality_score=round(top_score, 2),
                score_margin=score_margin,
            )
