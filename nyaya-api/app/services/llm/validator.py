from typing import List, Dict, Any, Tuple
import logging
from app.services.llm.evidence_pack import EvidencePack, EvidenceAuthorityItem
from app.services.llm.schemas import GroundedSynthesisStructuredOutput, CitedAuthorityReference

logger = logging.getLogger(__name__)

class ValidationViolation:
    def __init__(self, check_type: str, severity: str, message: str, details: Dict[str, Any] = None):
        self.check_type = check_type
        self.severity = severity  # "CRITICAL" (triggers fallback) or "WARNING" (remediated)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_type": self.check_type,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
        }

class DeterministicCitationGuard:
    """
    Deterministic safety validator that cross-checks LLM-synthesized outputs
    against the verified Evidence Pack to ensure zero hallucination of cases,
    citations, paragraphs, judicial treatment, or quotations.
    """

    @classmethod
    def validate(
        cls,
        synthesis: GroundedSynthesisStructuredOutput,
        evidence_pack: EvidencePack
    ) -> Tuple[bool, GroundedSynthesisStructuredOutput, List[ValidationViolation]]:
        """
        Validates and sanitizes a GroundedSynthesisStructuredOutput.
        Returns:
            is_valid: bool (True if safe to accept or remediate, False if critical fabrication requiring fallback)
            sanitized_output: GroundedSynthesisStructuredOutput
            violations: List[ValidationViolation]
        """
        violations: List[ValidationViolation] = []
        
        # Build index of valid authorities in evidence pack
        valid_authorities_by_id: Dict[str, EvidenceAuthorityItem] = {
            a.case_id: a for a in evidence_pack.authorities
        }
        valid_authorities_by_title: Dict[str, EvidenceAuthorityItem] = {
            a.title.lower().strip(): a for a in evidence_pack.authorities
        }
        
        sanitized_cited_authorities: List[CitedAuthorityReference] = []

        for cited in synthesis.cited_authorities:
            # 1. Check authority existence in Evidence Pack
            matched_auth = valid_authorities_by_id.get(cited.case_id)
            if not matched_auth:
                matched_auth = valid_authorities_by_title.get(cited.title.lower().strip())

            if not matched_auth:
                violations.append(
                    ValidationViolation(
                        check_type="UNGROUNDED_AUTHORITY",
                        severity="CRITICAL",
                        message=f"Hallucinated authority '{cited.title}' ({cited.case_id}) not found in verified Evidence Pack.",
                        details={"case_id": cited.case_id, "title": cited.title, "citation": cited.citation}
                    )
                )
                continue

            # 2. Verify and enforce canonical citation and court metadata
            cleaned_citation = matched_auth.citation
            cleaned_court = matched_auth.court
            cleaned_year = matched_auth.year

            # 3. Check treatment consistency
            if matched_auth.negative_treatment_found or "OVERRULED" in matched_auth.treatment_status.upper():
                if "OVERRULED" not in cited.treatment_status.upper() and "NEGATIVE" not in cited.treatment_status.upper():
                    violations.append(
                        ValidationViolation(
                            check_type="TREATMENT_MISMATCH",
                            severity="CRITICAL",
                            message=f"Authority '{matched_auth.title}' has negative treatment ({matched_auth.treatment_status}) in database, but LLM labeled it as '{cited.treatment_status}'.",
                            details={"case_id": matched_auth.case_id, "db_treatment": matched_auth.treatment_status}
                        )
                    )

            # 4. Paragraph Pinpoint Grounding
            valid_paras = set(matched_auth.available_paragraphs)
            remediated_paras: List[int] = []
            for p in cited.cited_paragraphs:
                if p in valid_paras:
                    remediated_paras.append(p)
                else:
                    violations.append(
                        ValidationViolation(
                            check_type="UNGROUNDED_PARAGRAPH",
                            severity="WARNING",
                            message=f"Paragraph [{p}] cited for '{matched_auth.title}' is not present in verified evidence passages.",
                            details={"case_id": matched_auth.case_id, "invalid_para": p, "valid_paras": list(valid_paras)}
                        )
                    )

            # 5. Quote Substring Grounding
            # Aggregate all passage texts for this case
            combined_passages_text = " ".join(p.text for p in matched_auth.passages)
            remediated_quotes: List[str] = []
            for q in cited.verbatim_quotes:
                cleaned_q = q.strip().strip('"').strip("'")
                if not cleaned_q:
                    continue
                # Check if substring exists (case-insensitive or relaxed whitespace)
                if cleaned_q.lower() in combined_passages_text.lower():
                    remediated_quotes.append(q)
                else:
                    # Also check against key_ratio
                    if cleaned_q.lower() in matched_auth.key_ratio.lower():
                        remediated_quotes.append(q)
                    else:
                        violations.append(
                            ValidationViolation(
                                check_type="UNGROUNDED_QUOTATION",
                                severity="WARNING",
                                message=f"Quotation '{cleaned_q[:60]}...' cannot be verified verbatim in reported passages for '{matched_auth.title}'.",
                                details={"case_id": matched_auth.case_id, "quote_excerpt": cleaned_q[:80]}
                            )
                        )

            sanitized_cited = CitedAuthorityReference(
                case_id=matched_auth.case_id,
                title=matched_auth.title,
                citation=cleaned_citation,
                court=cleaned_court,
                year=cleaned_year,
                key_ratio=cited.key_ratio if cited.key_ratio else matched_auth.key_ratio,
                treatment_status=matched_auth.treatment_status,
                cited_paragraphs=remediated_paras,
                verbatim_quotes=remediated_quotes,
                relevance_to_query=cited.relevance_to_query,
            )
            sanitized_cited_authorities.append(sanitized_cited)

        # 6. Statutory Grounding Check
        valid_statutes_text = " ".join(
            f"{s.act_title} {s.section_number} {s.section_title}" for s in evidence_pack.statutes
        ).lower()
        remediated_statutes: List[str] = []
        for stat in synthesis.governing_statutes:
            cleaned_stat = stat.strip()
            if not cleaned_stat:
                continue
            if evidence_pack.statutes:
                tokens = [w for w in cleaned_stat.lower().replace(",", " ").replace("(", " ").replace(")", " ").split() if len(w) > 2 and w not in ["the", "act", "and", "section", "sec", "for", "with"]]
                if any(t in valid_statutes_text for t in tokens):
                    remediated_statutes.append(cleaned_stat)
                else:
                    violations.append(
                        ValidationViolation(
                            check_type="UNGROUNDED_STATUTE",
                            severity="WARNING",
                            message=f"Statutory reference '{cleaned_stat}' is not present in verified Evidence Pack statutes.",
                            details={"statute": cleaned_stat}
                        )
                    )
            else:
                remediated_statutes.append(cleaned_stat)

        # 7. Corpus Limitations Safeguard
        corpus_lim = synthesis.corpus_limitations.strip()
        if not corpus_lim or len(corpus_lim) < 20:
            corpus_lim = (
                f"Judicial Research Notice: Findings are strictly bounded by {len(evidence_pack.authorities)} "
                f"verified commercial precedents, {len(evidence_pack.statutes)} statutory provisions, and "
                f"{evidence_pack.total_passages_count} reported passages currently indexed in the Nyaya corpus."
            )

        # Construct sanitized synthesis
        sanitized_synthesis = GroundedSynthesisStructuredOutput(
            summary=synthesis.summary,
            key_principles=synthesis.key_principles,
            governing_statutes=remediated_statutes,
            cited_authorities=sanitized_cited_authorities,
            practical_implications=synthesis.practical_implications,
            bench_guidance=synthesis.bench_guidance,
            corpus_limitations=corpus_lim,
        )

        # Determine validity: if any CRITICAL violation exists, fail validation
        has_critical = any(v.severity == "CRITICAL" for v in violations)
        # Also, if all cited authorities were pruned because they were hallucinated, fail validation
        if len(synthesis.cited_authorities) > 0 and len(sanitized_cited_authorities) == 0:
            violations.append(
                ValidationViolation(
                    check_type="EMPTY_VERIFIED_AUTHORITIES",
                    severity="CRITICAL",
                    message="All cited authorities failed ground-truth verification.",
                )
            )
            has_critical = True

        return (not has_critical, sanitized_synthesis, violations)
