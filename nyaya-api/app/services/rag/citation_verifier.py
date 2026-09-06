import re
from typing import List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.case import Case, Citation
from app.schemas.research import (
    RetrievedAuthorityDTO,
    CitationVerificationDTO,
    CitationTreatmentRecord,
)


class CitationVerifier:
    """Dynamic, database-driven judicial citator and treatment verifier.
    
    Adheres strictly to the architectural constraints:
    - Queries database citation records dynamically.
    - Evaluates positive treatments (APPLIED, AFFIRMED, FOLLOWED), limiting treatments
      (DISTINGUISHED, MODIFIED), and negative treatments (OVERRULED).
    - Categorizes into 4 explicit coverage states:
      1. VERIFIED_IN_CORPUS: Positive treatment verified within the curated corpus.
      2. NEGATIVE_TREATMENT_FOUND: Precedent overruled or distinguished/modified.
      3. NO_TREATMENT_FOUND: Authority present with reporter citation, but 0 treatment records in corpus.
      4. INSUFFICIENT_CORPUS: Authority missing from curated repository.
    - Explicitly acknowledges corpus scope: Never claims an authority is universally good law
      merely because no negative treatment exists in this curated database.
    """

    def __init__(self, db: Session):
        self.db = db

    def verify_by_case_id(self, case_id: str) -> CitationVerificationDTO:
        """Verifies citation status directly by case UUID."""
        case = self.db.query(Case).filter(Case.id == case_id).first()
        return self._verify_case_entity(case, fallback_id=case_id)

    def verify_by_citation_string(self, citation_str: str) -> CitationVerificationDTO:
        """Verifies citation status by standard reporter citation (e.g. '(2022) 10 SCC 1')."""
        case = self.db.query(Case).filter(
            or_(
                Case.standard_citation.ilike(f"%{citation_str.strip()}%"),
                Case.neutral_citation.ilike(f"%{citation_str.strip()}%"),
            )
        ).first()
        return self._verify_case_entity(case, fallback_citation=citation_str)

    def verify_authority(self, auth: RetrievedAuthorityDTO) -> CitationVerificationDTO:
        """Verifies citation status for a RetrievedAuthorityDTO."""
        case = self.db.query(Case).filter(Case.id == auth.id).first()
        if not case:
            case = self.db.query(Case).filter(
                Case.standard_citation == auth.standard_citation
            ).first()

        return self._verify_case_entity(
            case,
            fallback_id=auth.id,
            fallback_title=auth.title,
            fallback_citation=auth.standard_citation,
            fallback_court=auth.court,
            fallback_quorum=auth.bench_quorum,
            fallback_strength=auth.bench_strength or 2,
            fallback_date=auth.judgment_date,
            fallback_good_law=auth.is_good_law,
            fallback_status=auth.status_summary,
        )

    def _verify_case_entity(
        self,
        case: Optional[Case],
        fallback_id: str = "",
        fallback_title: str = "Unknown Authority",
        fallback_citation: str = "",
        fallback_court: str = "Indian Judicial System",
        fallback_quorum: str = "Quorum Not Recorded",
        fallback_strength: int = 2,
        fallback_date: str = "",
        fallback_good_law: bool = True,
        fallback_status: str = "",
    ) -> CitationVerificationDTO:
        # Case 1: Insufficient Corpus Coverage
        if not case:
            return CitationVerificationDTO(
                case_id=fallback_id,
                case_title=fallback_title,
                standard_citation=fallback_citation,
                neutral_citation="",
                court=fallback_court,
                judgment_date=fallback_date,
                bench_quorum=fallback_quorum,
                bench_strength=fallback_strength,
                law_reporter_verified=False,
                official_reporter="Reporter Not Found in Local Repository",
                good_law_status="Unverified: Insufficient Corpus Coverage",
                is_good_law=False,
                treatment_history=[],
                verification_notes=(
                    "INSUFFICIENT CORPUS COVERAGE: The requested authority is not indexed in the curated "
                    "local commercial repository. Cannot verify legal validity or subsequent judicial treatment."
                ),
                corpus_coverage_status="INSUFFICIENT_CORPUS",
                is_demo_data=False,
            )

        # Case 2: In-corpus verification
        case_id = case.id
        title = case.title
        std_cit = case.standard_citation
        neu_cit = case.neutral_citation or ""
        court = case.court
        j_date = str(case.judgment_date)
        quorum = case.bench_quorum
        strength = case.bench_strength or 2
        is_good_law = case.is_good_law
        status_summary = case.status_summary

        # Determine official reporter designation
        reporter = (
            "Supreme Court Cases (SCC) / Supreme Court Reports (SCR)"
            if "supreme court" in court.lower()
            else "Delhi High Court Reports (ILR Del) / SCC OnLine Del"
        )

        # Fetch citation records where:
        # a) This case is the source case recording citations
        # b) This case is cited by other cases in the repository
        direct_citations = self.db.query(Citation).filter(Citation.source_case_id == case_id).all()
        referencing_citations = self.db.query(Citation).filter(
            or_(
                Citation.cited_case_citation == std_cit,
                Citation.cited_case_name.ilike(f"%{title[:25]}%"),
            )
        ).all()

        # Build treatment records
        treatment_records: List[CitationTreatmentRecord] = []
        seen_pairs: Set[Tuple[str, str]] = set()

        all_citations = direct_citations + referencing_citations

        for cit in all_citations:
            citing_name = cit.cited_case_name
            citing_cit = cit.cited_case_citation or ""
            treatment_str = cit.treatment.upper()

            pair = (citing_name, treatment_str)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            year_match = re.search(r"(?:19|20)\d{2}", citing_cit)
            year = int(year_match.group(0)) if year_match else 2023

            c_court = "Supreme Court of India"
            b_strength = 2
            if "SCC OnLine Del" in citing_cit or "DHC" in citing_cit:
                c_court = "High Court of Delhi"
                b_strength = 1
            elif "SCC OnLine Bom" in citing_cit:
                c_court = "High Court of Bombay"
                b_strength = 1
            elif "Cal" in citing_cit:
                c_court = "High Court of Calcutta"
                b_strength = 1
            elif "SCR" in citing_cit or "SCC" in citing_cit or "INSC" in citing_cit:
                c_court = "Supreme Court of India"

            treatment_records.append(
                CitationTreatmentRecord(
                    treatment=treatment_str,
                    citing_case=citing_name,
                    citation=citing_cit,
                    year=year,
                    court=c_court,
                    bench_strength=b_strength,
                )
            )

        # Distinguish the 4 states:
        treatments_set = {t.treatment for t in treatment_records}

        # Sub-case A: Overruled Authority
        if not is_good_law or "OVERRULED" in treatments_set and (not is_good_law or "overruled" in status_summary.lower()):
            good_law_status = "Overruled Precedent"
            corpus_coverage_status = "NEGATIVE_TREATMENT_FOUND"
            verification_notes = (
                f"OVERRULED IN SUBSEQUENT JURISPRUDENCE: Controlling judicial record indicates: {status_summary}. "
                f"This holding has been superseded and cannot be cited as binding commercial precedent."
            )
            is_good_law_result = False

        # Sub-case B: Negative / Limiting Treatment (Distinguished or Modified)
        elif any(t in treatments_set for t in ["DISTINGUISHED", "MODIFIED", "DOUBTED"]):
            good_law_status = "Caution: Distinguished / Modified"
            corpus_coverage_status = "NEGATIVE_TREATMENT_FOUND"
            limiting_treatments = [t for t in treatments_set if t in ["DISTINGUISHED", "MODIFIED", "DOUBTED"]]
            verification_notes = (
                f"LIMITING TREATMENT RECORDED ({'/'.join(limiting_treatments)}): "
                f"Subsequent judicial benches have distinguished or qualified the scope of this authority. "
                f"Scrutinize factual pleadings carefully against the limiting parameters before applying."
            )
            is_good_law_result = True

        # Sub-case C: Verified Good Law with Positive Treatments in Corpus
        elif any(t in treatments_set for t in ["APPLIED", "AFFIRMED", "FOLLOWED", "CONSIDERED"]):
            good_law_status = "Verified Good Law (Curated Corpus)"
            corpus_coverage_status = "VERIFIED_IN_CORPUS"
            positive_treatments = [t for t in treatments_set if t in ["APPLIED", "AFFIRMED", "FOLLOWED", "CONSIDERED"]]
            verification_notes = (
                f"VERIFIED WITHIN LOCAL CORPUS ({'/'.join(positive_treatments)}): "
                f"Precedent has received positive judicial treatment across {len(treatment_records)} recorded proceedings. "
                f"Caution: This verification reflects the curated commercial corpus and does not represent an exhaustive national citator search."
            )
            is_good_law_result = True

        # Sub-case D: No Treatment Data Found in Corpus
        else:
            good_law_status = "Presumed Good Law (No Treatment Data in Corpus)"
            corpus_coverage_status = "NO_TREATMENT_FOUND"
            verification_notes = (
                "NO CITATION TREATMENT DATA IN CORPUS: Authority exists in the commercial repository with verified reporter citation, "
                "but no subsequent citation treatment records exist in the current local database. "
                "Never assume universal good law without consulting comprehensive national law reports (SCC Online / Manupatra / e-SCR)."
            )
            is_good_law_result = is_good_law

        return CitationVerificationDTO(
            case_id=case_id,
            case_title=title,
            standard_citation=std_cit,
            neutral_citation=neu_cit,
            court=court,
            judgment_date=j_date,
            bench_quorum=quorum,
            bench_strength=strength,
            law_reporter_verified=True,
            official_reporter=reporter,
            good_law_status=good_law_status,
            is_good_law=is_good_law_result,
            treatment_history=treatment_records,
            verification_notes=verification_notes,
            corpus_coverage_status=corpus_coverage_status,
            is_demo_data=False,
        )

    def verify_all(self, authorities: List[RetrievedAuthorityDTO]) -> List[CitationVerificationDTO]:
        verifications: List[CitationVerificationDTO] = []
        for auth in authorities:
            cv = self.verify_authority(auth)
            auth.citation_verification = cv
            verifications.append(cv)
        return verifications
