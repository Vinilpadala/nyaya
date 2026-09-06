from typing import List, Optional
from pydantic import BaseModel, Field

class CitedAuthorityReference(BaseModel):
    case_id: str = Field(description="Exact case ID from the evidence pack")
    title: str = Field(description="Exact reported title of the case")
    citation: str = Field(description="Exact law reporter citation")
    court: str = Field(description="Exact deciding court")
    year: int = Field(description="Year of judgment")
    key_ratio: str = Field(description="Key ratio decidendi relevant to the query")
    treatment_status: str = Field(description="Treatment status recorded in the evidence pack, e.g. VERIFIED_IN_CORPUS, NEGATIVE_TREATMENT_FOUND, OVERRULED")
    cited_paragraphs: List[int] = Field(default_factory=list, description="Specific paragraph numbers referenced, which MUST exist in the evidence pack or be empty if none recorded")
    verbatim_quotes: List[str] = Field(default_factory=list, description="Verbatim quotations, which MUST exist as substrings in the evidence passages")
    relevance_to_query: str = Field(description="Judicial explanation of how this authority answers the dispute")

class GroundedSynthesisStructuredOutput(BaseModel):
    summary: str = Field(description="Rigorous judicial synthesis of governing commercial legal principles based strictly on the provided evidence pack")
    key_principles: List[str] = Field(description="Distilled legal principles directly supported by the evidence authorities")
    governing_statutes: List[str] = Field(default_factory=list, description="Applicable statutory provisions present in the evidence pack")
    cited_authorities: List[CitedAuthorityReference] = Field(description="Authorities from the evidence pack relied upon for this synthesis")
    practical_implications: str = Field(description="Commercial implications: burden of proof, standards of review, and pleading requirements")
    bench_guidance: str = Field(description="Actionable bench guidance for Commercial Court judges on framing issues and disposing applications")
    corpus_limitations: str = Field(description="Explicit note stating the boundaries and limitations of the verified corpus analyzed")
