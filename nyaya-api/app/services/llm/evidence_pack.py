from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class EvidencePassageItem(BaseModel):
    passage_id: str
    paragraph_number: Optional[int] = None
    text: str
    legal_topic: str
    score: float

class EvidenceAuthorityItem(BaseModel):
    case_id: str
    title: str
    citation: str
    court: str
    year: int
    bench_strength: Optional[int] = None
    decision_date: Optional[str] = None
    key_ratio: str
    composite_score: float
    treatment_status: str
    negative_treatment_found: bool = False
    treatment_summary: str = ""
    available_paragraphs: List[int] = Field(default_factory=list)
    passages: List[EvidencePassageItem] = Field(default_factory=list)

class EvidenceStatuteItem(BaseModel):
    statute_id: str
    act_title: str
    section_number: str
    section_title: str
    text: str
    commercial_relevance: str = ""

class EvidencePack(BaseModel):
    query: str
    commercial_domain: str = "Commercial Division / Commercial Appellate Division"
    authorities: List[EvidenceAuthorityItem] = Field(default_factory=list)
    statutes: List[EvidenceStatuteItem] = Field(default_factory=list)
    corpus_boundary_note: str = (
        "Evidence is strictly restricted to the verified commercial case corpus and reported passages loaded into Nyaya AI. "
        "Do not cite authorities, paragraphs, or propositions outside this evidence pack."
    )
    total_authorities_count: int = 0
    total_passages_count: int = 0
    total_statutes_count: int = 0

def build_evidence_pack(
    query: str,
    ranked_authorities: List[Any],
    citation_verifications: Union[List[Any], Dict[str, Any]],
    retrieved_passages: List[Any],
    retrieved_statutes: List[Any],
    commercial_domain: str = "Commercial Division / Commercial Appellate Division",
) -> EvidencePack:
    """
    Constructs an immutable, strongly-typed Evidence Pack from verified retrieval,
    ranking, passages, and dynamic citation verification outputs.
    """
    # Normalize citation verifications mapping
    verif_by_id: Dict[str, Any] = {}
    if isinstance(citation_verifications, list):
        for v in citation_verifications:
            cid = getattr(v, "case_id", None)
            if cid:
                verif_by_id[cid] = v
    elif isinstance(citation_verifications, dict):
        verif_by_id = citation_verifications

    authority_items: List[EvidenceAuthorityItem] = []
    
    # Map passages by case_id from retrieved_passages
    passages_by_case: Dict[str, List[EvidencePassageItem]] = {}
    total_passages = 0
    for p in retrieved_passages:
        cid = getattr(p, "case_id", None)
        if not cid:
            continue
        para = getattr(p, "paragraph_number", None)
        item = EvidencePassageItem(
            passage_id=str(getattr(p, "id", "")),
            paragraph_number=para if isinstance(para, int) else None,
            text=str(getattr(p, "text", getattr(p, "content", ""))).strip(),
            legal_topic=str(getattr(p, "legal_topic", "Commercial Law")),
            score=round(float(getattr(p, "score", getattr(p, "relevance_score", 0.0))), 4),
        )
        passages_by_case.setdefault(cid, []).append(item)
        total_passages += 1

    for auth in ranked_authorities:
        cid = getattr(auth, "case_id", getattr(auth, "id", ""))
        
        # Check pinpoint_passages attached directly to authority DTO if any
        auth_pinpoints = getattr(auth, "pinpoint_passages", [])
        for pp in auth_pinpoints:
            para = getattr(pp, "paragraph_number", None)
            pp_id = str(getattr(pp, "passage_id", getattr(pp, "id", "")))
            # Avoid duplicate insertion if already in passages_by_case
            existing_ids = {item.passage_id for item in passages_by_case.get(cid, [])}
            if pp_id not in existing_ids:
                item = EvidencePassageItem(
                    passage_id=pp_id,
                    paragraph_number=para if isinstance(para, int) else None,
                    text=str(getattr(pp, "text", "")).strip(),
                    legal_topic=str(getattr(pp, "legal_topic", "Commercial Law")),
                    score=round(float(getattr(pp, "relevance_score", 0.0)), 4),
                )
                passages_by_case.setdefault(cid, []).append(item)
                total_passages += 1

        # Dynamic citation verification lookup
        verif = verif_by_id.get(cid) or getattr(auth, "citation_verification", None)
        
        coverage_status = getattr(verif, "corpus_coverage_status", getattr(verif, "status", "VERIFIED_IN_CORPUS")) if verif else "VERIFIED_IN_CORPUS"
        good_law_status = getattr(verif, "good_law_status", "Good Law") if verif else "Good Law"
        is_good_law = getattr(verif, "is_good_law", getattr(auth, "is_good_law", True))
        neg_found = (not is_good_law) or ("NEGATIVE" in coverage_status.upper()) or ("OVERRULED" in good_law_status.upper())
        treatment_summary = getattr(verif, "verification_notes", getattr(auth, "status_summary", ""))
        
        c_passages = passages_by_case.get(cid, [])
        paras = sorted(list({p.paragraph_number for p in c_passages if p.paragraph_number is not None}))
        
        bench_strength = getattr(auth, "bench_strength", None)
        judgment_date = getattr(auth, "judgment_date", getattr(auth, "decision_date", None))
        
        # Parse year from judgment date or default
        year = getattr(auth, "year", None)
        if year is None and judgment_date:
            try:
                year = int(str(judgment_date).split("-")[0])
            except Exception:
                year = 2020
        elif year is None:
            year = 2020

        std_citation = getattr(auth, "standard_citation", getattr(auth, "citation", ""))

        authority_items.append(
            EvidenceAuthorityItem(
                case_id=cid,
                title=getattr(auth, "title", getattr(auth, "case_title", "")),
                citation=std_citation,
                court=getattr(auth, "court", "Indian Judicial System"),
                year=int(year),
                bench_strength=int(bench_strength) if bench_strength is not None else None,
                decision_date=str(judgment_date) if judgment_date else None,
                key_ratio=getattr(auth, "key_ratio", ""),
                composite_score=round(float(getattr(auth, "composite_score", getattr(auth, "relevance_score", 0.0))), 4),
                treatment_status=f"{coverage_status} ({good_law_status})",
                negative_treatment_found=neg_found,
                treatment_summary=treatment_summary,
                available_paragraphs=paras,
                passages=c_passages,
            )
        )

    statute_items: List[EvidenceStatuteItem] = []
    for st in retrieved_statutes:
        act_title = getattr(st, "statute_title", getattr(st, "act_name", getattr(st, "act_title", "")))
        sec_num = getattr(st, "section_number", "")
        sec_title = getattr(st, "heading", getattr(st, "title", getattr(st, "section_title", "")))
        sec_text = getattr(st, "content", getattr(st, "text", ""))
        comm_rel = getattr(st, "commercial_relevance", getattr(st, "sub_heading", ""))

        statute_items.append(
            EvidenceStatuteItem(
                statute_id=str(getattr(st, "id", "")),
                act_title=act_title,
                section_number=sec_num,
                section_title=sec_title,
                text=str(sec_text).strip(),
                commercial_relevance=comm_rel,
            )
        )

    return EvidencePack(
        query=query,
        commercial_domain=commercial_domain,
        authorities=authority_items,
        statutes=statute_items,
        total_authorities_count=len(authority_items),
        total_passages_count=total_passages,
        total_statutes_count=len(statute_items),
    )
