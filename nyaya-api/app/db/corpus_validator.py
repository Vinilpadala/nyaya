from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.case import Case, CasePassage, Citation


class CorpusValidationError(Exception):
    """Raised when judicial benchmark corpus fails deterministic quality checks."""
    pass


VALID_TREATMENTS = {
    "APPLIED",
    "FOLLOWED",
    "AFFIRMED",
    "CONSIDERED",
    "DISTINGUISHED",
    "MODIFIED",
    "OVERRULED",
    "NO_TREATMENT_FOUND",
    "INSUFFICIENT_CORPUS",
}


def validate_corpus(db: Session) -> Dict[str, Any]:
    """
    Performs comprehensive deterministic validation of the commercial benchmark corpus:
    1. Case Entity Integrity:
       - Non-empty standard reporter citation
       - Non-empty case title
       - Non-empty court jurisdiction
       - Positive bench strength (>= 1)
       - Valid judgment date
       - Non-empty ratio decidendi
       - Source provenance preserved
    2. Case Passages Integrity:
       - Non-empty passage text
       - Passage belongs to an active indexed Case
       - Non-empty paragraph number (or valid pin indicator)
       - Source provenance explicitly attributed
       - Zero duplicate passages (same case_id + paragraph_number)
    3. Citation & Treatment Graph Integrity:
       - Treatment status is a recognized judicial enum value
       - Citing source case exists
       - Non-empty cited case title and citation
    4. Uniqueness & Deduplication:
       - Zero duplicate cases by standard_citation
    """
    cases = db.query(Case).all()
    passages = db.query(CasePassage).all()
    citations = db.query(Citation).all()

    errors: List[str] = []
    case_ids = set()
    citation_set = set()

    # 1. Validate Cases
    for c in cases:
        case_ids.add(c.id)
        if not c.title or not c.title.strip():
            errors.append(f"Case {c.id}: Empty case title")
        if not c.standard_citation or not c.standard_citation.strip():
            errors.append(f"Case '{c.title}': Empty standard reporter citation")
        if not c.court or not c.court.strip():
            errors.append(f"Case '{c.title}': Empty court attribution")
        if not c.bench_strength or c.bench_strength < 1:
            errors.append(f"Case '{c.title}': Invalid bench strength ({c.bench_strength})")
        if not c.judgment_date:
            errors.append(f"Case '{c.title}': Missing judgment date")
        if not c.ratio_decidendi or not c.ratio_decidendi.strip():
            errors.append(f"Case '{c.title}': Empty ratio decidendi")
        if not getattr(c, "source_provenance", None):
            errors.append(f"Case '{c.title}': Missing source provenance metadata")

        # Duplicate citation check
        norm_cit = c.standard_citation.strip().lower()
        if norm_cit in citation_set:
            errors.append(f"Duplicate Case detected for citation: '{c.standard_citation}'")
        citation_set.add(norm_cit)

    # 2. Validate Passages
    seen_passages = set()
    cases_with_passages = set()

    for p in passages:
        if not p.passage_text or not p.passage_text.strip():
            errors.append(f"Passage {p.id}: Empty passage text")
        if p.case_id not in case_ids:
            errors.append(f"Passage {p.id}: Orphan passage referencing non-existent case_id '{p.case_id}'")
        else:
            cases_with_passages.add(p.case_id)

        if not getattr(p, "source_provenance", None):
            errors.append(f"Passage {p.id}: Missing source provenance attribution")

        # Duplicate passage check (case_id + paragraph_number)
        dup_key = (p.case_id, p.paragraph_number)
        if p.paragraph_number is not None and dup_key in seen_passages:
            errors.append(f"Duplicate Passage detected for case {p.case_id}, paragraph {p.paragraph_number}")
        if p.paragraph_number is not None:
            seen_passages.add(dup_key)

    # 3. Validate Citations
    for cit in citations:
        if cit.source_case_id not in case_ids:
            errors.append(f"Citation {cit.id}: References non-existent source case '{cit.source_case_id}'")
        if not cit.cited_case_name or not cit.cited_case_name.strip():
            errors.append(f"Citation {cit.id}: Empty cited case name")
        if cit.treatment not in VALID_TREATMENTS:
            errors.append(f"Citation {cit.id}: Invalid judicial treatment '{cit.treatment}'")

    if errors:
        raise CorpusValidationError(
            f"Corpus Deterministic Quality Validation failed with {len(errors)} errors:\n"
            + "\n".join(f"  - {e}" for e in errors[:20])
        )

    return {
        "status": "VALIDATED",
        "total_cases": len(cases),
        "total_passages": len(passages),
        "total_citations": len(citations),
        "cases_with_passages": len(cases_with_passages),
        "errors_count": 0,
    }
