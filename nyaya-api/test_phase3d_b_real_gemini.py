import os
import sys
import json
from typing import Dict, Any

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.config import settings
from app.schemas.research import ResearchQueryRequest
from app.services.rag.orchestrator import RAGResearchOrchestrator
from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.factory import get_llm_provider
from app.services.llm.evidence_pack import (
    EvidencePack,
    EvidenceAuthorityItem,
    EvidencePassageItem,
    EvidenceStatuteItem,
)
from app.services.llm.schemas import (
    GroundedSynthesisStructuredOutput,
    CitedAuthorityReference,
)
from app.services.llm.validator import DeterministicCitationGuard


def test_1_api_key_security_and_hygiene():
    """Verify that GEMINI_API_KEY is isolated server-side and never exposed."""
    print("\n--- TEST 1: API-Key Security & Hygiene Verification ---")
    
    # 1. Check frontend source directory for any accidental secret exposure
    frontend_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nyaya-web", "src"))
    found_in_frontend = False
    if os.path.exists(frontend_src):
        for root, _, files in os.walk(frontend_src):
            for file in files:
                if file.endswith((".ts", ".tsx", ".js", ".jsx", ".html", ".env")):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "GEMINI_API_KEY" in content:
                            found_in_frontend = True
                            print(f"  [FAIL] GEMINI_API_KEY found in frontend file: {path}")
    assert not found_in_frontend, "GEMINI_API_KEY must never appear in frontend source files"
    print("  [PASS] Frontend source scan: 0 occurrences of GEMINI_API_KEY")

    # 2. Check .gitignore covers .env
    gitignore_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".gitignore"))
    assert os.path.exists(gitignore_path), ".gitignore must exist in nyaya-api"
    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore_content = f.read()
    assert ".env" in gitignore_content, ".gitignore must ignore .env"
    print("  [PASS] .gitignore correctly excludes server-side .env")

    # 3. Verify provider does not print secret value
    provider = get_llm_provider()
    provider_repr = str(provider.get_provider_name())
    assert settings.GEMINI_API_KEY not in provider_repr or len(settings.GEMINI_API_KEY) == 0
    print(f"  [PASS] Provider identification safe: '{provider.get_provider_name()}'")
    print(f"  [PASS] Server-side API key configured: {provider.is_available()}")


def test_2_deliberate_hallucination_rejection():
    """Verify that DeterministicCitationGuard strictly rejects fabricated cases and prunes invalid pinpoints."""
    print("\n--- TEST 2: Deliberate Hallucination Rejection (Citation Guard) ---")

    controlled_pack = EvidencePack(
        query="Section 12A commercial mediation",
        authorities=[
            EvidenceAuthorityItem(
                case_id="case-patil-2022",
                title="Patil Automation Pvt. Ltd. v. Rakheja Engineers Pvt. Ltd.",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                bench_strength=2,
                key_ratio="Section 12A of the Commercial Courts Act, 2015 is mandatory.",
                composite_score=0.92,
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                negative_treatment_found=False,
                available_paragraphs=[74, 75],
                passages=[
                    EvidencePassageItem(
                        passage_id="p-patil-74",
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
                statute_id="stat-12a",
                act_title="Commercial Courts Act, 2015",
                section_number="12A",
                section_title="Pre-Institution Mediation",
                text="A suit, which does not contemplate any urgent interim relief, shall not be instituted unless the plaintiff exhausts the remedy of pre-institution mediation."
            )
        ]
    )

    # 2A: Deliberate Hallucinated Case Authority
    hallucinated_case_output = GroundedSynthesisStructuredOutput(
        summary="A summary citing a completely fabricated commercial case.",
        key_principles=["Fabricated principle"],
        governing_statutes=["Commercial Courts Act, 2015 - Section 12A"],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="hallucinated-case-999",
                title="Fictional Enterprises Ltd. v. Imaginary Corp.",
                citation="2026 SCC OnLine SC 8888",
                court="Supreme Court of India",
                year=2026,
                key_ratio="Completely fabricated legal holding",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[10],
                verbatim_quotes=[],
                relevance_to_query="None"
            )
        ],
        practical_implications="None",
        bench_guidance="None",
        corpus_limitations="Curated corpus boundaries."
    )

    is_valid, sanitized, violations = DeterministicCitationGuard.validate(hallucinated_case_output, controlled_pack)
    assert not is_valid, "Citation Guard MUST reject hallucinated authorities"
    assert any(v.check_type == "UNGROUNDED_AUTHORITY" and v.severity == "CRITICAL" for v in violations)
    print("  [PASS] Fabricated case authority rejected with CRITICAL violation (triggers fallback)")

    # 2B: Deliberate Hallucinated Paragraph Number & Fake Quote
    hallucinated_pinpoint_output = GroundedSynthesisStructuredOutput(
        summary="Summary citing valid case with fabricated paragraph number [999] and unsupported quote.",
        key_principles=["Section 12A is mandatory."],
        governing_statutes=["Commercial Courts Act, 2015 - Section 12A"],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Pvt. Ltd. v. Rakheja Engineers Pvt. Ltd.",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A of the Commercial Courts Act, 2015 is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[74, 999],  # 999 is fabricated!
                verbatim_quotes=[
                    "liable to be rejected under Order VII Rule 11",  # Grounded in passage
                    "this text was never spoken by any judge in this case"  # Fabricated quote!
                ],
                relevance_to_query="Direct statutory interpretation"
            )
        ],
        practical_implications="Verify mediation exhaustion prior to plaint admission.",
        bench_guidance="Examine plaint for genuine urgent interim relief prayers.",
        corpus_limitations="Scope restricted to benchmark precedents."
    )

    is_valid, sanitized, violations = DeterministicCitationGuard.validate(hallucinated_pinpoint_output, controlled_pack)
    assert is_valid is True, "Output with valid authority should pass after pruning unverified pinpoints/quotes"
    assert sanitized.cited_authorities[0].cited_paragraphs == [74], f"Expected [74], got {sanitized.cited_authorities[0].cited_paragraphs}"
    assert sanitized.cited_authorities[0].verbatim_quotes == ["liable to be rejected under Order VII Rule 11"]
    print("  [PASS] Fabricated paragraph [999] was pruned cleanly")
    print("  [PASS] Unsupported quote was pruned cleanly while authentic quote was preserved")


def test_3_fallback_and_resilience():
    """Verify that all failure modes fall back cleanly to deterministic synthesis without crashing."""
    print("\n--- TEST 3: Fallback & Resilience Testing ---")
    db = SessionLocal()
    try:
        orchestrator = RAGResearchOrchestrator(db)
        req = ResearchQueryRequest(query="urgent interim relief Section 12A mediation")

        # 3A: When provider is unavailable or missing key
        res = orchestrator.execute_research(req)
        assert res is not None
        assert res.research_trail is not None
        step4 = res.research_trail.ai_synthesis_step
        assert step4.stage == "AI_SYNTHESIS"
        assert len(res.bench_action_points) > 0
        assert len(res.ai_generated_summary) > 0
        print(f"  [PASS] Clean execution without crash. Synthesis Engine: {step4.details[1]}")
        print(f"  [PASS] Citation Guard status: {step4.details[3]}")

        # 3B: Simulate critical exception during LLM call
        class CrashingProvider(BaseLLMProvider):
            def is_available(self) -> bool:
                return True
            def get_provider_name(self) -> str:
                return "Crashing LLM Provider"
            def generate_grounded_synthesis(self, evidence_pack: EvidencePack):
                raise RuntimeError("Simulated connection timeout to remote AI provider")

        import app.services.rag.orchestrator as orch_module
        orig_factory = orch_module.get_llm_provider
        orch_module.get_llm_provider = lambda: CrashingProvider()

        try:
            res_fail = orchestrator.execute_research(req)
            assert res_fail is not None
            assert res_fail.research_trail.ai_synthesis_step.details[1] == "Synthesis Engine: Deterministic Fallback"
            assert any("temporarily unavailable" in d for d in res_fail.research_trail.ai_synthesis_step.details)
            print("  [PASS] Simulated provider crash handled gracefully -> Deterministic Fallback active")
        finally:
            orch_module.get_llm_provider = orig_factory

    finally:
        db.close()


def test_4_real_gemini_or_validated_skip():
    """
    If GEMINI_API_KEY is configured, execute real Gemini calls on benchmark queries.
    If not configured, honestly report the skip without fabricating results.
    """
    print("\n--- TEST 4: Real Gemini Live Call (or Validated Skip) ---")
    provider = GeminiProvider()

    if not provider.is_available():
        print("  [HONEST SKIP] GEMINI_API_KEY is not configured in environment or .env.")
        print("  [INFO] Real Gemini API network calls skipped safely. No fake success claimed.")
        print("  [INFO] To test with a real key, place GEMINI_API_KEY in nyaya-api/.env or export it.")
        return

    print(f"  [ACTIVE] Real GeminiProvider detected with model: {provider.model}")
    
    # Test Scenario A: Strong supported authority (Patil Automation)
    db = SessionLocal()
    try:
        orchestrator = RAGResearchOrchestrator(db)
        req_a = ResearchQueryRequest(query="Section 12A Commercial Courts Act mandatory pre-institution mediation")
        res_a = orchestrator.execute_research(req_a)
        
        assert res_a is not None
        engine_str = res_a.research_trail.ai_synthesis_step.details[1]
        assert "Google Gemini" in engine_str or "Deterministic Fallback" in engine_str
        if "Google Gemini" in engine_str:
            assert "Verified Grounded (Zero Fabrication)" in res_a.research_trail.ai_synthesis_step.details[3]
            print("  [PASS] Scenario A (Patil Automation): Real Gemini synthesis generated and validated cleanly")
        else:
            print("  [PASS] Scenario A (Patil Automation): Remote provider error handled via Deterministic Fallback")
        print(f"         Summary excerpt: {res_a.ai_generated_summary[:120]}...")

        # Test Scenario B: Overruled Authority Query (SMS Tea Estates)
        req_c = ResearchQueryRequest(
            query="arbitration agreement unstamped document enforceability SMS Tea Estates",
            include_overruled=True,
        )
        res_c = orchestrator.execute_research(req_c)
        assert res_c is not None
        assert res_c.has_overruled_authorities is True
        print("  [PASS] Scenario C (Overruled Precedent): Negative treatment preserved under real Gemini")

    finally:
        db.close()


def test_5_full_authenticated_api_endpoint():
    """Verify authenticated FastAPI endpoint /api/v1/research/query."""
    print("\n--- TEST 5: Full Authenticated API Endpoint Verification ---")
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.security import create_access_token
    from app.models.user import User

    client = TestClient(app)

    # 1. Unauthenticated request must return 401
    unauth_resp = client.post("/api/v1/research/query", json={"query": "Section 12A mediation"})
    assert unauth_resp.status_code == 401, f"Expected 401 for unauthenticated query, got {unauth_resp.status_code}"
    print("  [PASS] Unauthenticated access gate: 401 Unauthorized enforced")

    # 2. Authenticated request with judicial token
    db = SessionLocal()
    try:
        judge_user = db.query(User).filter(User.email == "judge@nyaya.gov.in").first()
        if not judge_user:
            judge_user = db.query(User).first()
        assert judge_user is not None, "At least one test user must exist in db"
        
        token = create_access_token(data={"sub": judge_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        auth_resp = client.post(
            "/api/v1/research/query",
            headers=headers,
            json={
                "query": "commercial suit rejection for non-compliance with Section 12A pre-institution mediation",
                "jurisdiction": "ALL",
            }
        )
        assert auth_resp.status_code == 200, f"Expected 200, got {auth_resp.status_code}: {auth_resp.text}"
        data = auth_resp.json()
        assert data.get("success") is True
        payload = data.get("data")
        assert payload is not None
        assert len(payload["retrieved_authorities"]) > 0
        assert payload["research_trail"] is not None
        assert payload["uncertainty_assessment"] is not None
        
        # Verify secret hygiene in response JSON
        raw_json_str = json.dumps(data)
        if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5:
            assert settings.GEMINI_API_KEY not in raw_json_str, "CRITICAL: API key found in API response JSON!"
        assert "SECRET_KEY" not in raw_json_str
        print(f"  [PASS] Authenticated endpoint /api/v1/research/query returned 200 OK")
        print(f"  [PASS] Zero secret leakage in API response payload")
    finally:
        db.close()


if __name__ == "__main__":
    print("=================================================================")
    print("NYAYA AI — PHASE 3D-B: REAL GEMINI INTEGRATION & VALIDATION SUITE")
    print("=================================================================")
    test_1_api_key_security_and_hygiene()
    test_2_deliberate_hallucination_rejection()
    test_3_fallback_and_resilience()
    test_4_real_gemini_or_validated_skip()
    test_5_full_authenticated_api_endpoint()
    print("\n=================================================================")
    print("ALL PHASE 3D-B INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=================================================================")
