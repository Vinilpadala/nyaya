from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict

from app.services.rag.base import PassageSearchResult
from app.schemas.research import (
    RetrievedAuthorityDTO,
    PinpointPassageDTO,
)


def get_court_hierarchy_weight(court: str, requested_jurisdiction: str = "ALL") -> float:
    """Computes Indian judicial court hierarchy weight.
    
    - Supreme Court of India: Article 141 nationwide binding authority (weight 1.00).
    - Local High Court: Territorially binding on Commercial Courts in that State (weight 0.90).
    - Other High Courts: Persuasive nationwide value in commercial law (weight 0.72).
    - Commercial Appellate / District: Territorial commercial courts (weight 0.55).
    """
    c_lower = court.lower()
    req_lower = requested_jurisdiction.lower().strip()

    if "supreme court" in c_lower:
        return 1.00

    if "high court" in c_lower:
        if req_lower != "all" and (
            req_lower in c_lower or any(word in c_lower for word in req_lower.split() if len(word) > 3)
        ):
            return 0.90  # Territorially binding
        return 0.72  # Persuasive sister High Court

    if "commercial appellate" in c_lower or "commercial division" in c_lower:
        return 0.65
    return 0.55


def get_bench_strength_weight(bench_strength: int) -> float:
    """Computes bench strength weight adhering to Indian precedent doctrine.
    
    Larger benches bind smaller benches; Constitution Benches (5+, 7+) possess highest authority.
    """
    if bench_strength >= 7:
        return 1.35  # 7-Judge Landmark Constitution Bench
    elif bench_strength >= 5:
        return 1.25  # 5-Judge Constitution Bench
    elif bench_strength >= 3:
        return 1.10  # Full / 3-Judge Bench
    elif bench_strength == 2:
        return 1.00  # Division Bench
    else:
        return 0.85  # Single Judge


class AuthorityRanker:
    """Ranks and aggregates retrieved judicial passages according to Indian precedent hierarchy."""

    @classmethod
    def rank_and_aggregate(
        cls,
        passages: List[PassageSearchResult],
        limit: int = 5,
        requested_jurisdiction: str = "ALL",
        citation_verifications: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedAuthorityDTO]:
        if not passages:
            return []

        # Group passages by case_id
        grouped_by_case: Dict[str, List[PassageSearchResult]] = defaultdict(list)
        for p in passages:
            grouped_by_case[p.case_id].append(p)

        authorities: List[RetrievedAuthorityDTO] = []

        for case_id, case_passages in grouped_by_case.items():
            lead = case_passages[0]

            court_weight = get_court_hierarchy_weight(lead.court, requested_jurisdiction)
            bench_weight = get_bench_strength_weight(lead.bench_strength)

            # Determine citation treatment weight and overruled status
            cv = citation_verifications.get(lead.case_id) if citation_verifications else None
            is_overruled = (
                not lead.is_good_law
                or "OVERRULED" in lead.status_summary.upper()
                or (cv and getattr(cv, "good_law_status", None) == "Overruled Precedent")
                or (cv and getattr(cv, "is_good_law", None) is False)
            )

            is_distinguished = (
                cv and "Caution" in getattr(cv, "good_law_status", "")
            ) or "Caution" in lead.status_summary or "Distinguished" in lead.status_summary

            if is_overruled:
                treatment_weight = 0.30  # Significant negative treatment penalty
            elif is_distinguished:
                treatment_weight = 0.85  # Moderate cautionary discount
            else:
                treatment_weight = 1.00  # Full settled precedent weight

            # Base score from top-scoring passage in this authority
            top_retrieval_score = max(p.score for p in case_passages)

            # Combined judicial relevance score
            combined_score = top_retrieval_score * court_weight * bench_weight * treatment_weight
            final_relevance_score = round(combined_score, 2)

            # Build authentic pinpoint passages (preserving verbatim paragraph numbers without fabrication)
            pinpoint_dtos: List[PinpointPassageDTO] = []
            for cp in case_passages:
                pinpoint_dtos.append(
                    PinpointPassageDTO(
                        paragraph_number=cp.paragraph_number if cp.paragraph_number is not None else 0,
                        text=cp.passage_text,
                        significance=cp.significance or "Judicial observation on commercial point of law",
                        source_provenance=getattr(cp, "source_provenance", "Supreme Court Reports (SCR) / Official Record"),
                    )
                )

            # Sort pinpoints by paragraph number
            pinpoint_dtos.sort(key=lambda x: x.paragraph_number)

            # Build why_relevant explanation based on matched terms and bench authority
            all_matched_terms = sorted(list(set(term for cp in case_passages for term in cp.matched_terms)))
            matched_terms_str = f"Matched query concepts: {', '.join(all_matched_terms[:4])}. " if all_matched_terms else ""

            if lead.bench_strength >= 7:
                quorum_label = "7-Judge Constitution Bench"
            elif lead.bench_strength >= 5:
                quorum_label = "Constitution Bench"
            else:
                quorum_label = f"{lead.bench_strength}-Judge Bench"

            why_relevant = (
                f"{matched_terms_str}"
                f"Binding {lead.court} authority ({quorum_label}). "
                f"Controlling status: {lead.status_summary}."
            )

            # Build ratio extract from the primary ratio passage if available, else first passage
            ratio_passage = next((cp for cp in case_passages if cp.is_ratio), lead)
            ratio_extract = ratio_passage.passage_text

            auth_dto = RetrievedAuthorityDTO(
                id=lead.case_id,
                title=lead.case_title,
                standard_citation=lead.standard_citation,
                neutral_citation=lead.neutral_citation,
                court=lead.court,
                judgment_date=lead.judgment_date,
                bench_quorum=lead.bench_quorum,
                bench_strength=lead.bench_strength,
                jurisdiction=getattr(lead, "jurisdiction", "ALL"),
                source_provenance=getattr(lead, "source_provenance", "Supreme Court Cases (SCC) / Official Law Reports"),
                is_good_law=False if is_overruled else lead.is_good_law,
                status_summary=lead.status_summary,
                relevance_score=final_relevance_score,
                why_relevant=why_relevant,
                ratio_extract=ratio_extract,
                pinpoint_passages=pinpoint_dtos,
                citation_verification=cv,
                is_demo_data=False,
            )
            authorities.append(auth_dto)

        # -------------------------------------------------------------
        # Doctrinal Precedent Ordering Rule:
        # 1. Overruled authorities must NEVER outrank active controlling/good-law
        #    authorities solely because of lexical similarity. Therefore, if any
        #    active good-law precedent exists, Rank 1 is strictly held by the
        #    highest-scoring good-law authority.
        # 2. Lower-court authority must not outrank controlling Supreme Court
        #    authority on nationwide matters solely because of lexical overlap.
        # 3. When include_overruled is active, relevant overruled authorities
        #    are preserved and surfaced in subsequent ranks according to their
        #    calibrated relevance scores.
        # -------------------------------------------------------------
        good_law_auths = [a for a in authorities if a.is_good_law]
        overruled_auths = [a for a in authorities if not a.is_good_law]

        good_law_auths.sort(key=lambda x: x.relevance_score, reverse=True)
        overruled_auths.sort(key=lambda x: x.relevance_score, reverse=True)

        # In nationwide queries (jurisdiction == ALL), ensure Supreme Court precedent leads
        # if a lower court has a higher raw score on partial lexical overlap
        if good_law_auths and requested_jurisdiction == "ALL":
            if "supreme court" not in good_law_auths[0].court.lower():
                sc_candidates = [
                    a for a in good_law_auths
                    if "supreme court" in a.court.lower()
                    and a.relevance_score >= 0.5 * good_law_auths[0].relevance_score
                ]
                if sc_candidates:
                    sc_lead = sc_candidates[0]
                    good_law_auths.remove(sc_lead)
                    good_law_auths.insert(0, sc_lead)

        if good_law_auths:
            lead_good = good_law_auths[0]
            remaining = good_law_auths[1:] + overruled_auths
            # When sorting remaining slots, preserve topical overruled precedents so they are not
            # squeezed out by unrelated authorities with weak generic overlap
            remaining.sort(
                key=lambda x: x.relevance_score if x.is_good_law else max(x.relevance_score, (x.relevance_score / 0.30) * 0.70),
                reverse=True
            )
            final_ordered = [lead_good] + remaining
        else:
            final_ordered = overruled_auths

        return final_ordered[:limit]
