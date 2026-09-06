import math
import re
from typing import List, Optional, Dict, Set, Tuple
from collections import Counter
from sqlalchemy.orm import Session

from app.models.case import Case, CasePassage
from app.models.statute import Statute, StatuteSection
from app.services.rag.base import BaseRetriever, PassageSearchResult, StatuteSearchResult


LEGAL_STOPWORDS: Set[str] = {
    "the", "a", "an", "and", "or", "in", "on", "of", "to", "for", "with", "by", "at",
    "from", "is", "was", "are", "were", "be", "been", "being", "that", "this", "which",
    "it", "as", "vs", "versus", "etc", "i.e", "e.g", "per", "re", "matter", "under",
    "between", "having", "has", "had", "shall", "will", "would", "should", "could",
    "whether", "court", "courts", "act", "acts", "where", "when", "any", "all", "such",
    "said", "before", "after", "against", "into", "over", "upon", "about"
}


def tokenize(text: str) -> List[str]:
    """Tokenize legal text preserving statutory provisions and hyphenated terms."""
    if not text:
        return []
    # Replace slashes and brackets with space while keeping alphanumeric and hyphens
    cleaned = re.sub(r"[^\w\s\-]", " ", text.lower())
    tokens = [t.strip("-") for t in cleaned.split() if len(t.strip("-")) > 1]
    return [t for t in tokens if t not in LEGAL_STOPWORDS]


def compute_bm25_score(
    query_tokens: List[str],
    doc_tokens: List[str],
    doc_freqs: Dict[str, int],
    total_docs: int,
    avg_doc_len: float,
    k1: float = 1.2,
    b: float = 0.75,
) -> Tuple[float, List[str]]:
    """Calculates BM25 relevance score and returns matched terms."""
    if not doc_tokens or not query_tokens:
        return 0.0, []

    doc_len = len(doc_tokens)
    term_counts = Counter(doc_tokens)
    score = 0.0
    matched = []

    for qt in query_tokens:
        if qt in term_counts:
            matched.append(qt)
            tf = term_counts[qt]
            df = doc_freqs.get(qt, 1)
            # Standard Lucene/BM25 IDF
            idf = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))
            numerator = tf * (k1 + 1.0)
            denominator = tf + k1 * (1.0 - b + b * (doc_len / (avg_doc_len or 1.0)))
            score += idf * (numerator / denominator)

    return score, matched


class LexicalBM25Retriever(BaseRetriever):
    """Reliable lexical legal retriever implementing BM25 ranking over verified judicial corpus.
    
    Zero fabrication: operates strictly over authenticated database records.
    """

    def __init__(self, db: Session):
        self.db = db

    def is_available(self) -> bool:
        return True

    def search_passages(
        self,
        query: str,
        case_context: Optional[str] = None,
        jurisdiction: str = "ALL",
        min_bench_strength: Optional[int] = None,
        include_overruled: bool = False,
        limit: int = 10,
    ) -> List[PassageSearchResult]:
        q_tokens = tokenize(query)
        if case_context:
            q_tokens.extend(tokenize(case_context))

        if not q_tokens:
            return []

        # 1. Fetch passages with case joins
        db_query = self.db.query(CasePassage).join(Case)

        if not include_overruled:
            db_query = db_query.filter(Case.is_good_law == True)

        if jurisdiction != "ALL":
            db_query = db_query.filter(Case.court.ilike(f"%{jurisdiction}%"))

        if min_bench_strength:
            db_query = db_query.filter(Case.bench_strength >= min_bench_strength)

        passages = db_query.all()
        if not passages:
            return []

        # 2. Build document token representations and document frequencies
        doc_tokens_list = []
        doc_freqs: Dict[str, int] = {}
        total_tokens = 0

        for p in passages:
            c = p.case
            # Weighted document representation
            passage_toks = tokenize(p.passage_text) * 2
            signif_toks = tokenize(p.significance) * 2
            title_toks = tokenize(c.title) * 3
            ratio_toks = tokenize(c.ratio_decidendi) * 2
            cit_toks = tokenize(f"{c.standard_citation} {c.neutral_citation}") * 2

            combined_doc = passage_toks + signif_toks + title_toks + ratio_toks + cit_toks
            doc_tokens_list.append(combined_doc)
            total_tokens += len(combined_doc)

            unique_terms = set(combined_doc)
            for t in unique_terms:
                doc_freqs[t] = doc_freqs.get(t, 0) + 1

        total_docs = len(passages)
        avg_doc_len = total_tokens / float(total_docs) if total_docs > 0 else 1.0

        # 3. Score each passage
        raw_query_str = f"{query} {case_context or ''}".lower()
        scored_results: List[PassageSearchResult] = []

        for i, p in enumerate(passages):
            c = p.case
            doc_toks = doc_tokens_list[i]
            bm25, matched = compute_bm25_score(
                query_tokens=q_tokens,
                doc_tokens=doc_toks,
                doc_freqs=doc_freqs,
                total_docs=total_docs,
                avg_doc_len=avg_doc_len,
            )

            # Boosts for legal relevance
            score = bm25
            if score > 0:
                # Ratio Decidendi boost: Core holding has higher legal weight than obiter
                if p.is_ratio:
                    score *= 1.25

                # Exact phrase matching in passage text or case title
                clean_passage = p.passage_text.lower()
                clean_title = c.title.lower()
                if any(phrase in clean_passage or phrase in clean_title for phrase in [
                    "section 12a", "pre-institution mediation", "group of companies",
                    "non-signatory", "section 74", "liquidated damages", "earnest money",
                    "interim injunction", "order xxxix", "order vii rule 11"
                ] if phrase in raw_query_str):
                    score *= 1.4

                # Standard citation exact match boost
                if c.standard_citation.lower() in raw_query_str or c.neutral_citation.lower() in raw_query_str:
                    score *= 1.5

                scored_results.append(
                    PassageSearchResult(
                        passage_id=p.id,
                        case_id=c.id,
                        case_title=c.title,
                        standard_citation=c.standard_citation,
                        neutral_citation=c.neutral_citation,
                        court=c.court,
                        bench_quorum=c.bench_quorum,
                        bench_strength=c.bench_strength,
                        judgment_date=c.judgment_date.isoformat() if c.judgment_date else "",
                        is_good_law=c.is_good_law,
                        status_summary=c.status_summary,
                        paragraph_number=p.paragraph_number,
                        passage_text=p.passage_text,
                        significance=p.significance,
                        is_ratio=p.is_ratio,
                        score=round(score, 3),
                        matched_terms=list(set(matched)),
                        jurisdiction=getattr(c, "jurisdiction", "ALL"),
                        source_provenance=getattr(p, "source_provenance", "Supreme Court Reports (SCR) / Official Record"),
                    )
                )

        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:limit]

    def search_statutes(
        self,
        query: str,
        case_context: Optional[str] = None,
        limit: int = 4,
    ) -> List[StatuteSearchResult]:
        q_tokens = tokenize(query)
        if case_context:
            q_tokens.extend(tokenize(case_context))

        if not q_tokens:
            return []

        sections = self.db.query(StatuteSection).join(Statute).all()
        if not sections:
            return []

        doc_tokens_list = []
        doc_freqs: Dict[str, int] = {}
        total_tokens = 0

        for sec in sections:
            sec_num_toks = tokenize(sec.section_number) * 3
            head_toks = tokenize(sec.heading) * 2
            content_toks = tokenize(sec.content)
            title_toks = tokenize(sec.statute.short_title) * 2
            notes_toks = tokenize(sec.amendment_notes or "")

            combined = sec_num_toks + head_toks + content_toks + title_toks + notes_toks
            doc_tokens_list.append(combined)
            total_tokens += len(combined)

            for t in set(combined):
                doc_freqs[t] = doc_freqs.get(t, 0) + 1

        total_docs = len(sections)
        avg_doc_len = total_tokens / float(total_docs) if total_docs > 0 else 1.0

        raw_query_str = f"{query} {case_context or ''}".lower()
        scored_statutes: List[StatuteSearchResult] = []

        for i, sec in enumerate(sections):
            doc_toks = doc_tokens_list[i]
            bm25, matched = compute_bm25_score(
                query_tokens=q_tokens,
                doc_tokens=doc_toks,
                doc_freqs=doc_freqs,
                total_docs=total_docs,
                avg_doc_len=avg_doc_len,
            )

            score = bm25
            if score > 0:
                # Boost if specific section number is referenced in query
                clean_sec_num = sec.section_number.lower()
                if any(num in raw_query_str for num in [clean_sec_num, clean_sec_num.replace("section", "").strip()]):
                    score *= 1.5

                why_parts = []
                if matched:
                    why_parts.append(f"Statutory text matched terms: {', '.join(sorted(set(matched))[:4])}")
                if sec.heading:
                    why_parts.append(f"Subject: {sec.heading}")
                why_text = ". ".join(why_parts)

                scored_statutes.append(
                    StatuteSearchResult(
                        section_id=sec.id,
                        statute_title=sec.statute.short_title,
                        section_number=sec.section_number,
                        heading=sec.heading,
                        content=sec.content,
                        amendment_notes=sec.amendment_notes,
                        score=round(score, 3),
                        why_relevant=why_text,
                        matched_terms=list(set(matched)),
                    )
                )

        scored_statutes.sort(key=lambda x: x.score, reverse=True)
        return scored_statutes[:limit]
