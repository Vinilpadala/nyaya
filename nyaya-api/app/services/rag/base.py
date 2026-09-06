from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class PassageSearchResult:
    """Represents a retrieved verbatim passage from a reported judicial authority."""
    passage_id: str
    case_id: str
    case_title: str
    standard_citation: str
    neutral_citation: str
    court: str
    bench_quorum: str
    bench_strength: int
    judgment_date: str
    is_good_law: bool
    status_summary: str
    paragraph_number: Optional[int]
    passage_text: str
    significance: str
    is_ratio: bool
    score: float
    matched_terms: List[str] = field(default_factory=list)
    jurisdiction: str = "ALL"
    source_provenance: str = "Supreme Court Reports (SCR) / Official Record"


@dataclass
class StatuteSearchResult:
    """Represents a retrieved statutory section or procedural rule."""
    section_id: str
    statute_title: str
    section_number: str
    heading: str
    content: str
    amendment_notes: Optional[str]
    score: float
    why_relevant: str
    matched_terms: List[str] = field(default_factory=list)


class BaseRetriever(ABC):
    """Abstract modular retrieval interface for Nyaya AI legal research.
    
    Implementations (Lexical BM25, Dense Vector, or Hybrid) adhere to this contract,
    allowing dense embeddings or vector databases to be swapped in seamlessly without
    changing the upstream orchestrator, API schema, or frontend.
    """

    @abstractmethod
    def search_passages(
        self,
        query: str,
        case_context: Optional[str] = None,
        jurisdiction: str = "ALL",
        min_bench_strength: Optional[int] = None,
        include_overruled: bool = False,
        limit: int = 10,
    ) -> List[PassageSearchResult]:
        """Retrieve authentic case passages matching the legal query."""
        pass

    @abstractmethod
    def search_statutes(
        self,
        query: str,
        case_context: Optional[str] = None,
        limit: int = 4,
    ) -> List[StatuteSearchResult]:
        """Retrieve relevant statutory sections or rules matching the legal query."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this retriever implementation is operational."""
        pass
