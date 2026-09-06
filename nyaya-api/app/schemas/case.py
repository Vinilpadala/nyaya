from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class CitationDTO(BaseModel):
    id: str
    source_case_id: str
    cited_case_name: str
    cited_case_citation: str
    treatment: str
    pinpoint_paragraph: str

    class Config:
        from_attributes = True


class CaseDTO(BaseModel):
    id: str
    title: str
    neutral_citation: str
    standard_citation: str
    court: str
    judgment_date: date
    bench_quorum: str
    bench_strength: int
    commercial_category: str
    jurisdiction: str = "ALL"
    source_provenance: str = "Supreme Court Cases (SCC) / Official Law Reports"
    ratio_decidendi: str
    is_good_law: bool
    status_summary: str
    is_demo_data: bool

    class Config:
        from_attributes = True


class CaseDetailDTO(CaseDTO):
    full_text_snippet: str
    citations_made: List[CitationDTO] = []
