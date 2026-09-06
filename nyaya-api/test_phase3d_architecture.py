import sys
import os

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.config import settings
from app.schemas.research import ResearchQueryRequest
from app.services.rag.orchestrator import RAGResearchOrchestrator
from app.services.llm.evidence_pack import build_evidence_pack, EvidencePack, EvidenceAuthorityItem, EvidencePassageItem, EvidenceStatuteItem
from app.services.llm.schemas import GroundedSynthesisStructuredOutput, CitedAuthorityReference
from app.services.llm.validator import DeterministicCitationGuard
from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.factory import get_llm_provider

def test_evidence_pack_builder():
    print("\n--- TEST 1: Evidence Pack Construction ---")
    db = SessionLocal()
    try:
        orchestrator = RAGResearchOrchestrator(db)
        req = ResearchQueryRequest(query="Section 12A Commercial Courts Act mandatory pre-institution mediation")
        
        # Test full orchestrator run with builder
        res = orchestrator.execute_research(req)
        assert res is not None
        assert len(res.retrieved_authorities) > 0
        assert res.research_trail is not None
        assert res.research_trail.ai_synthesis_step.stage == "AI_SYNTHESIS"
        print(f"  [OK] Orchestrator executed cleanly. Synthesis Step: {res.research_trail.ai_synthesis_step.details}")
    finally:
        db.close()

def test_provider_abstraction_and_graceful_fallback():
    print("\n--- TEST 2: Provider Abstraction & Missing Key Fallback ---")
    provider = get_llm_provider()
    assert isinstance(provider, BaseLLMProvider)
    assert isinstance(provider, GeminiProvider)
    
    # When GEMINI_API_KEY is empty/unconfigured in dev environment:
    if not settings.GEMINI_API_KEY:
        assert provider.is_available() is False
        print("  [OK] Provider correctly reports is_available() == False when API key is not set")
        
        pack = EvidencePack(query="test query")
        output = provider.generate_grounded_synthesis(pack)
        assert output is None
        print("  [OK] generate_grounded_synthesis gracefully returns None without raising exceptions")
    else:
        print(f"  [INFO] GEMINI_API_KEY is configured. Provider available: {provider.is_available()}")

def test_citation_guard_detects_hallucinations():
    print("\n--- TEST 3: DeterministicCitationGuard Safety Enforcement ---")
    
    # Build a controlled EvidencePack with Patil Automation
    sample_pack = EvidencePack(
        query="Section 12A mediation",
        authorities=[
            EvidenceAuthorityItem(
                case_id="case-patil-2022",
                title="Patil Automation Pvt. Ltd. v. Rakheja Engineers Pvt. Ltd.",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                bench_strength=2,
                key_ratio="Pre-institution mediation under Section 12A of the Commercial Courts Act, 2015 is mandatory.",
                composite_score=0.92,
                treatment_status="VERIFIED_IN_CORPUS",
                negative_treatment_found=False,
                available_paragraphs=[74, 75, 84],
                passages=[
                    EvidencePassageItem(
                        passage_id="p1",
                        paragraph_number=74,
                        text="Section 12A of the Commercial Courts Act, 2015 is mandatory and any suit instituted violating the mandate is liable to be rejected under Order VII Rule 11.",
                        legal_topic="Commercial Courts Act",
                        score=0.95
                    )
                ]
            )
        ],
        statutes=[
            EvidenceStatuteItem(
                statute_id="s1",
                act_title="Commercial Courts Act, 2015",
                section_number="12A",
                section_title="Pre-Institution Mediation",
                text="A suit, which does not contemplate any urgent interim relief, shall not be instituted unless the plaintiff exhausts the remedy of pre-institution mediation."
            )
        ]
    )

    # 3A: Test perfectly grounded output
    valid_output = GroundedSynthesisStructuredOutput(
        summary="Section 12A is mandatory prior to instituting commercial suits unless urgent relief is contemplated.",
        key_principles=["Section 12A mandate is compulsory and non-compliance leads to rejection of plaint."],
        governing_statutes=["Commercial Courts Act, 2015 - Section 12A"],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Pvt. Ltd. v. Rakheja Engineers Pvt. Ltd.",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A of the Commercial Courts Act is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS",
                cited_paragraphs=[74],
                verbatim_quotes=["liable to be rejected under Order VII Rule 11"],
                relevance_to_query="Directly establishes the mandatory nature of Section 12A."
            )
        ],
        practical_implications="Commercial plaints without urgent interim applications must show exhaustion of mediation.",
        bench_guidance="Verify plaint averments regarding pre-institution mediation or urgent interim relief.",
        corpus_limitations="Scope bounded by verified Commercial Division precedents."
    )

    is_valid, sanitized, violations = DeterministicCitationGuard.validate(valid_output, sample_pack)
    assert is_valid is True, f"Expected valid output to pass guard, got violations: {violations}"
    assert len(sanitized.cited_authorities) == 1
    assert sanitized.cited_authorities[0].cited_paragraphs == [74]
    assert len(sanitized.cited_authorities[0].verbatim_quotes) == 1
    print("  [OK] Perfectly grounded output passes DeterministicCitationGuard cleanly (0 violations)")

    # 3B: Test detection of hallucinated case
    fake_case_output = GroundedSynthesisStructuredOutput(
        summary="Summary citing a fake case",
        key_principles=["Fake principle"],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="fake-case-id-999",
                title="Imaginary Tech Corp v. Hallucinated Ltd.",
                citation="2025 SCC OnLine SC 9999",
                court="Supreme Court of India",
                year=2025,
                key_ratio="Fabricated rule",
                treatment_status="VERIFIED_IN_CORPUS",
                cited_paragraphs=[12],
                verbatim_quotes=[],
                relevance_to_query="None"
            )
        ],
        practical_implications="None",
        bench_guidance="None",
        corpus_limitations="None"
    )

    is_valid, sanitized, violations = DeterministicCitationGuard.validate(fake_case_output, sample_pack)
    assert is_valid is False, "Expected hallucinated authority to be rejected by guard"
    assert any(v.check_type == "UNGROUNDED_AUTHORITY" and v.severity == "CRITICAL" for v in violations)
    print("  [OK] Hallucinated authority successfully rejected with CRITICAL severity")

    # 3C: Test pruning of hallucinated paragraph numbers and fake quotes
    bad_pinpoint_output = GroundedSynthesisStructuredOutput(
        summary="Summary with valid case but unverified paragraph number and fake quote",
        key_principles=["Principle"],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Pvt. Ltd. v. Rakheja Engineers Pvt. Ltd.",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS",
                cited_paragraphs=[74, 999],  # 999 is hallucinated!
                verbatim_quotes=["this specific sentence does not exist anywhere in the text of the judgment"],
                relevance_to_query="Relevance note"
            )
        ],
        practical_implications="Commercial implications",
        bench_guidance="Bench guidance",
        corpus_limitations="Boundaries of corpus"
    )

    is_valid, sanitized, violations = DeterministicCitationGuard.validate(bad_pinpoint_output, sample_pack)
    assert is_valid is True  # Non-critical: remediated by pruning bad pinpoint/quote!
    assert sanitized.cited_authorities[0].cited_paragraphs == [74], f"Expected [74], got {sanitized.cited_authorities[0].cited_paragraphs}"
    assert len(sanitized.cited_authorities[0].verbatim_quotes) == 0, f"Expected 0 quotes, got {sanitized.cited_authorities[0].verbatim_quotes}"
    assert any(v.check_type == "UNGROUNDED_PARAGRAPH" for v in violations)
    assert any(v.check_type == "UNGROUNDED_QUOTATION" for v in violations)
    print("  [OK] Hallucinated paragraph [999] and fake quote were successfully pruned while preserving valid data")

def test_full_pipeline_with_mock_llm():
    print("\n--- TEST 4: Full Pipeline Integration with Mock LLM Provider ---")
    
    class MockGroundedLLM(BaseLLMProvider):
        def is_available(self) -> bool:
            return True
        def get_provider_name(self) -> str:
            return "Mock Gemini Grounded Provider"
        def generate_grounded_synthesis(self, evidence_pack: EvidencePack):
            auth = evidence_pack.authorities[0]
            para = auth.available_paragraphs[0] if auth.available_paragraphs else None
            return GroundedSynthesisStructuredOutput(
                summary=f"Grounded synthesis established on {auth.title}.",
                key_principles=[f"Strict adherence to {auth.key_ratio}"],
                governing_statutes=[f"{s.act_title} Section {s.section_number}" for s in evidence_pack.statutes],
                cited_authorities=[
                    CitedAuthorityReference(
                        case_id=auth.case_id,
                        title=auth.title,
                        citation=auth.citation,
                        court=auth.court,
                        year=auth.year,
                        key_ratio=auth.key_ratio,
                        treatment_status=auth.treatment_status,
                        cited_paragraphs=[para] if para else [],
                        verbatim_quotes=[],
                        relevance_to_query="Authoritative precedent governing commercial bench."
                    )
                ],
                practical_implications="Pleadings must specifically establish the jurisdictional facts.",
                bench_guidance="Frame preliminary issues at the case management hearing under Order XV-A CPC.",
                corpus_limitations="Grounded solely in verified precedents."
            )

    import app.services.rag.orchestrator as orch_mod
    original_get_llm = orch_mod.get_llm_provider
    orch_mod.get_llm_provider = lambda: MockGroundedLLM()

    db = SessionLocal()
    try:
        orchestrator = orch_mod.RAGResearchOrchestrator(db)
        req = ResearchQueryRequest(query="urgent interim relief Section 12A mediation")
        res = orchestrator.execute_research(req)
        
        assert res is not None
        assert "Mock Gemini Grounded Provider" in res.research_trail.ai_synthesis_step.details[1]
        assert "Verified Grounded (Zero Fabrication)" in res.research_trail.ai_synthesis_step.details[3]
        assert len(res.bench_action_points) > 0
        assert "Grounded synthesis established on" in res.ai_generated_summary
        print(f"  [OK] Full pipeline generated synthesis via {res.research_trail.ai_synthesis_step.details[1]}")
        print(f"  [OK] ai_generated_summary: {res.ai_generated_summary}")
    finally:
        db.close()
        orch_mod.get_llm_provider = original_get_llm

if __name__ == "__main__":
    print("=================================================================")
    print("NYAYA AI - PHASE 3D-A: GROUNDED LLM ARCHITECTURE VERIFICATION")
    print("=================================================================")
    test_evidence_pack_builder()
    test_provider_abstraction_and_graceful_fallback()
    test_citation_guard_detects_hallucinations()
    test_full_pipeline_with_mock_llm()
    print("\n=================================================================")
    print("ALL PHASE 3D-A ARCHITECTURE TESTS PASSED SUCCESSFULLY!")
    print("=================================================================")
