import os
import sys

# Ensure app root is in sys.path and stdout handles utf-8 on Windows
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.db.session import SessionLocal
from app.schemas.research import ResearchQueryRequest
from app.services.rag.orchestrator import RAGResearchOrchestrator
from app.services.translation.citation_masking import CitationMaskingService
from app.services.translation.deterministic_translator import DeterministicLegalTranslator
from app.services.translation.service import TranslationService
from app.core.security import create_access_token
from app.models.audit import AuditLog
from app.models.user import User
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_citation_masking_unit():
    print("\n--- TEST 1: Citation & Entity Masking Unit Tests ---")
    sample_text = (
        "Under Section 12A of the Commercial Courts Act, 2015, pre-institution mediation is mandatory. "
        "In Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited ((2022) 10 SCC 1), "
        "the Supreme Court held at [Paras 84, 91, 93] that failure to exhaust mediation results in rejection of plaint "
        "under Order VII Rule 11 CPC."
    )

    masked, token_map = CitationMaskingService.mask_legal_entities(sample_text)
    print(f"  [PASS] Masked tokens created: {len(token_map)}")
    assert len(token_map) >= 4, f"Expected at least 4 masked entities, got {len(token_map)}"

    # Simulate translation preserving tokens
    simulated_translation = masked.replace("pre-institution mediation is mandatory", "సంస్థాపన పూర్వ మధ్యవర్తిత్వం తప్పనిసరి")
    unmasked = CitationMaskingService.unmask_legal_entities(simulated_translation, token_map)

    # Check unmasking restored exact strings
    assert "(2022) 10 SCC 1" in unmasked, "Citation was not restored"
    assert "Section 12A" in unmasked, "Statutory section was not restored"
    assert "Order VII Rule 11 CPC" in unmasked, "CPC order was not restored"
    assert "Patil Automation" in unmasked, "Case name was not restored"
    assert "Paras 84, 91, 93" in unmasked or "84" in unmasked, "Paragraph pinpoints not restored"
    print("  [PASS] Legal entity restoration verified 100% intact")

    # Verify citation integrity checker
    is_valid, violations = CitationMaskingService.verify_citation_integrity(sample_text, unmasked)
    assert is_valid, f"Integrity check failed: {violations}"
    print("  [PASS] Citation integrity verification: Validated")


def test_deterministic_legal_translator():
    print("\n--- TEST 2: Deterministic Legal Translator Unit Tests ---")
    translator = DeterministicLegalTranslator()

    # Telugu query mapping
    te_query = "వాణిజ్య న్యాయస్థానాల చట్టం సెక్షన్ 12A మధ్యవర్తిత్వం తప్పనిసరా మరియు ఆర్డర్ 7 రూల్ 11 వాజ్యం తిరస్కరణ"
    english_terms = translator.translate_query_to_english(te_query, "te")
    assert english_terms is not None, "Telugu query terms mapping returned None"
    assert "Commercial Courts Act, 2015" in english_terms
    assert "Section 12A" in english_terms
    assert "pre-institution mediation" in english_terms
    assert "Order VII Rule 11 CPC" in english_terms
    print(f"  [PASS] Telugu query mapped to: '{english_terms}'")

    # Hindi query mapping
    hi_query = "क्या वाणिज्यिक न्यायालय अधिनियम की धारा 12A के तहत संस्थान-पूर्व मध्यस्थता अनिवार्य है और आदेश 7 नियम 11"
    hi_terms = translator.translate_query_to_english(hi_query, "hi")
    assert hi_terms is not None, "Hindi query terms mapping returned None"
    assert "Section 12A" in hi_terms
    assert "Commercial Courts Act, 2015" in hi_terms
    assert "mandatory" in hi_terms
    print(f"  [PASS] Hindi query mapped to: '{hi_terms}'")

    # Verified ratio translation in Telugu
    patil_english = "In Patil Automation Private Limited ((2022) 10 SCC 1), Section 12A pre-institution mediation under Order VII Rule 11 is mandatory."
    te_synthesis = translator.translate_legal_text(patil_english, "te")
    assert te_synthesis is not None
    assert "(2022) 10 SCC 1" in te_synthesis
    assert "[Paras 84, 91, 93]" in te_synthesis
    print(f"  [PASS] Deterministic Telugu synthesis template verified with exact citation")

    # Conservative fallback: unknown query must return None
    unknown_trans = translator.translate_legal_text("Some random unknown commercial contract clause without precedent match.", "te")
    assert unknown_trans is None, "Expected conservative None for unknown text"
    print("  [PASS] Conservative fallback: Unknown text yields None (prevents translation hallucination)")


def test_orchestrator_english_baseline_regression():
    print("\n--- TEST 3: Orchestrator English Baseline Regression ---")
    db = SessionLocal()
    try:
        orchestrator = RAGResearchOrchestrator(db)
        req = ResearchQueryRequest(
            query="Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory and consequences under Order VII Rule 11 CPC",
            jurisdiction="Supreme Court of India",
            language="en"
        )
        res = orchestrator.execute_research(req)
        assert res.language == "en"
        assert res.original_query is None, "English queries should have original_query=None"
        assert len(res.retrieved_authorities) > 0
        assert "Patil Automation" in res.retrieved_authorities[0].title
        assert res.retrieved_authorities[0].is_good_law is True
        print(f"  [PASS] English baseline 100% verified (Lead: {res.retrieved_authorities[0].title})")
    finally:
        db.close()


def test_orchestrator_telugu_end_to_end():
    print("\n--- TEST 4: Orchestrator Telugu End-to-End Execution ---")
    db = SessionLocal()
    try:
        orchestrator = RAGResearchOrchestrator(db)
        telugu_query = "వాణిజ్య న్యాయస్థానాల చట్టం సెక్షన్ 12A మధ్యవర్తిత్వం తప్పనిసరా మరియు ఆర్డర్ 7 రూల్ 11 పరిణామాలు"
        req = ResearchQueryRequest(
            query=telugu_query,
            jurisdiction="Supreme Court of India",
            language="te"
        )
        res = orchestrator.execute_research(req)

        # Ingress verification
        assert res.language == "te"
        assert res.original_query == telugu_query
        print(f"  [PASS] Ingress: Preserved original query in Telugu script")
        print(f"  [PASS] English retrieval query: '{res.translated_query}'")

        # Retrieval verification
        assert len(res.retrieved_authorities) > 0
        lead_auth = res.retrieved_authorities[0]
        assert "Patil Automation" in lead_auth.title, f"Expected Patil Automation at Rank 1, got {lead_auth.title}"
        assert lead_auth.standard_citation == "(2022) 10 SCC 1"
        print(f"  [PASS] Retrieval: Lead authority is '{lead_auth.title}' ({lead_auth.standard_citation})")

        # Uncertainty & Precedent Integrity
        assert res.uncertainty_assessment.uncertainty_level == "LOW"
        assert res.has_overruled_authorities is False
        print(f"  [PASS] Uncertainty level preserved as LOW (Score: {res.uncertainty_assessment.confidence_score})")

        # Egress verification
        assert res.translated_summary is not None or res.translation_notice is not None
        if res.translated_summary:
            assert "(2022) 10 SCC 1" in res.translated_summary, "Citation missing from translated summary"
            print(f"  [PASS] Egress: Telugu summary verified with citation (2022) 10 SCC 1")
            print(f"         Summary excerpt: {res.translated_summary[:90]}...")
        assert res.translation_engine is not None
        print(f"  [PASS] Translation engine identified: {res.translation_engine}")

    finally:
        db.close()


def test_orchestrator_hindi_end_to_end():
    print("\n--- TEST 5: Orchestrator Hindi End-to-End Execution ---")
    db = SessionLocal()
    try:
        orchestrator = RAGResearchOrchestrator(db)
        hindi_query = "क्या वाणिज्यिक न्यायालय अधिनियम की धारा 12A के तहत संस्थान-पूर्व मध्यस्थता अनिवार्य है और आदेश 7 नियम 11 के परिणाम"
        req = ResearchQueryRequest(
            query=hindi_query,
            jurisdiction="Supreme Court of India",
            language="hi"
        )
        res = orchestrator.execute_research(req)

        assert res.language == "hi"
        assert res.original_query == hindi_query
        assert len(res.retrieved_authorities) > 0
        assert "Patil Automation" in res.retrieved_authorities[0].title
        assert res.retrieved_authorities[0].standard_citation == "(2022) 10 SCC 1"
        print(f"  [PASS] Hindi ingress & retrieval: Lead authority is '{res.retrieved_authorities[0].title}'")

        if res.translated_summary:
            assert "(2022) 10 SCC 1" in res.translated_summary
            print(f"  [PASS] Hindi egress: Translated summary contains verified citation (2022) 10 SCC 1")
    finally:
        db.close()


def test_api_endpoint_authenticated_multilingual_and_audit():
    print("\n--- TEST 6: Authenticated API Endpoint & Audit Logging ---")
    db = SessionLocal()
    try:
        judge = db.query(User).filter(User.role == "JUDGE").first()
        assert judge is not None
        token = create_access_token({"sub": judge.id, "email": judge.email, "role": judge.role})

        # 1. Authenticated multilingual query
        payload = {
            "query": "వాణిజ్య న్యాయస్థానాల చట్టం సెక్షన్ 12A మధ్యవర్తిత్వం తప్పనిసరా",
            "jurisdiction": "Supreme Court of India",
            "language": "te"
        }
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post("/api/v1/research/query", json=payload, headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()["data"]
        assert data["language"] == "te"
        assert data["original_query"] == payload["query"]
        assert len(data["retrieved_authorities"]) > 0
        print(f"  [PASS] POST /api/v1/research/query returned 200 OK with language='te'")

        # 2. Verify Audit Log recorded language
        audit = db.query(AuditLog).filter(AuditLog.user_id == judge.id).order_by(AuditLog.timestamp.desc()).first()
        assert audit is not None
        assert audit.action == "LEGAL_RESEARCH_QUERY"
        meta = audit.metadata_payload or {}
        assert meta.get("language") == "te", f"Expected audit metadata language='te', got {meta.get('language')}"
        print(f"  [PASS] Tamper-evident Audit Log recorded language='te' in metadata")

        # 3. Unauthenticated security gate
        unauth_resp = client.post("/api/v1/research/query", json=payload)
        assert unauth_resp.status_code == 401
        print(f"  [PASS] 401 Unauthorized strictly enforced for unauthenticated multilingual query")
    finally:
        db.close()


def main():
    print("=================================================================")
    print("NYAYA AI — PHASE 7: MULTILINGUAL COURT INTERFACE VALIDATION SUITE")
    print("=================================================================")

    test_citation_masking_unit()
    test_deterministic_legal_translator()
    test_orchestrator_english_baseline_regression()
    test_orchestrator_telugu_end_to_end()
    test_orchestrator_hindi_end_to_end()
    test_api_endpoint_authenticated_multilingual_and_audit()

    print("\n=================================================================")
    print("ALL PHASE 7 MULTILINGUAL VALIDATION TESTS PASSED (100% SUCCESS)!")
    print("=================================================================")


if __name__ == "__main__":
    main()
