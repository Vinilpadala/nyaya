"""
Nyaya AI — Phase 4D: SIH Demonstration Hardening & Release Readiness Test Suite
Can be run directly via: python test_phase4d_hardening.py

Tests:
1. Scenario 1 Reliability (Commercial Courts Act Sec 12A & Patil Automation)
2. Scenario 2 Overruling Separation (In Re Interplay vs SMS Tea Estates)
3. Scenario 3 Responsible AI & Boundary Refusal (CrPC 438 Out-of-Domain Query)
4. Missing / Invalid API Key Graceful Fallback
5. Simulated Network Failure / Timeout Fallback
6. Deterministic Citation Guard Hallucination Attack Neutralization
7. Authentication & Multi-Tenant Dossier Isolation
"""
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.dossier import Dossier
from app.schemas.research import ResearchQueryRequest
from app.services.rag.orchestrator import RAGResearchOrchestrator
from app.services.llm.validator import DeterministicCitationGuard
from app.services.llm.schemas import GroundedSynthesisStructuredOutput, CitedAuthorityReference
from app.services.llm.evidence_pack import build_evidence_pack


def run_phase4d_hardening_suite():
    print("=================================================================")
    print("NYAYA AI — PHASE 4D: SIH DEMONSTRATION HARDENING & RELEASE READINESS")
    print("=================================================================")

    db: Session = SessionLocal()
    client = TestClient(app)
    orchestrator = RAGResearchOrchestrator(db)

    try:
        # -------------------------------------------------------------
        # 1. SCENARIO 1 RELIABILITY
        # -------------------------------------------------------------
        print("\n[TEST 1] Scenario 1 Reliability — Commercial Courts Act Sec 12A...")
        req1 = ResearchQueryRequest(
            query="Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory and consequences of non-exhaustion under Order VII Rule 11 CPC",
            jurisdiction="Supreme Court of India",
            include_overruled=False,
        )
        res1 = orchestrator.execute_research(req1)
        assert len(res1.retrieved_authorities) >= 1, "Scenario 1: No authorities retrieved"
        lead = res1.retrieved_authorities[0]
        assert "Patil Automation" in lead.title, f"Expected Patil Automation, got {lead.title}"
        assert "(2022) 10 SCC 1" in lead.standard_citation
        assert lead.is_good_law is True

        paras = [p.paragraph_number for p in lead.pinpoint_passages]
        assert 84 in paras or 91 in paras or 93 in paras, f"Missing expected paras in {paras}"
        assert res1.uncertainty_assessment.uncertainty_level == "LOW"
        assert res1.has_overruled_authorities is False
        assert res1.synthesis_engine is not None
        print(f"  [PASS] Lead: {lead.title} ({lead.standard_citation})")
        print(f"  [PASS] Pinpoints: {paras} | Uncertainty: {res1.uncertainty_assessment.uncertainty_level}")
        print(f"  [PASS] Synthesis Engine: {res1.synthesis_engine}")

        # -------------------------------------------------------------
        # 2. SCENARIO 2 OVERRULING SEPARATION
        # -------------------------------------------------------------
        print("\n[TEST 2] Scenario 2 Overruling Separation — Stamping & Sec 11...")
        req2 = ResearchQueryRequest(
            query="Arbitration clause unstamped document enforceability Section 11 Appointment of Arbitrator",
            jurisdiction="ALL",
            include_overruled=True,
        )
        res2 = orchestrator.execute_research(req2)
        assert len(res2.retrieved_authorities) >= 2, "Expected at least 2 authorities"
        rank1 = res2.retrieved_authorities[0]
        rank2 = res2.retrieved_authorities[1]

        assert "Interplay" in rank1.title, f"Expected Interplay at Rank 1, got {rank1.title}"
        assert rank1.is_good_law is True
        assert rank1.bench_strength == 7

        assert "SMS Tea" in rank2.title, f"Expected SMS Tea Estates at Rank 2, got {rank2.title}"
        assert rank2.is_good_law is False
        assert "OVERRULED" in rank2.status_summary.upper()
        assert res2.has_overruled_authorities is True
        print(f"  [PASS] Rank 1: {rank1.title} [7-Judge Bench, Good Law: {rank1.is_good_law}]")
        print(f"  [PASS] Rank 2: {rank2.title} [Good Law: {rank2.is_good_law}, Status: {rank2.status_summary}]")
        print(f"  [PASS] has_overruled_authorities Flag: {res2.has_overruled_authorities}")

        # -------------------------------------------------------------
        # 3. SCENARIO 3 DOMAIN BOUNDARY REFUSAL
        # -------------------------------------------------------------
        print("\n[TEST 3] Scenario 3 Domain Boundary Refusal — Anticipatory Bail CrPC 438...")
        req3 = ResearchQueryRequest(
            query="Anticipatory bail Section 438 CrPC criminal trial arrest protection",
            jurisdiction="ALL",
            include_overruled=False,
        )
        res3 = orchestrator.execute_research(req3)
        assert res3.uncertainty_assessment.uncertainty_level == "HIGH"
        assert res3.uncertainty_assessment.confidence_score <= 0.50
        titles = [a.title.lower() for a in res3.retrieved_authorities]
        assert not any("gurbaksh singh sibbia" in t for t in titles), "Hallucinated criminal authority detected!"
        print(f"  [PASS] Assessed Uncertainty: {res3.uncertainty_assessment.uncertainty_level} (Confidence: {res3.uncertainty_assessment.confidence_score})")
        print(f"  [PASS] Zero Criminal Hallucinations in Retrieved Authorities ({len(res3.retrieved_authorities)} low-relevance results)")

        # -------------------------------------------------------------
        # 4. MISSING / INVALID GEMINI API KEY FALLBACK
        # -------------------------------------------------------------
        print("\n[TEST 4] Missing / Invalid API Key Fallback...")
        with patch("app.core.config.settings.GEMINI_API_KEY", ""):
            req4 = ResearchQueryRequest(
                query="Section 74 Indian Contract Act liquidated damages proof of actual loss",
                jurisdiction="Supreme Court of India",
            )
            res4 = orchestrator.execute_research(req4)
            assert res4 is not None
            assert res4.synthesis_engine == "Deterministic Fallback"
            assert res4.ai_generated_summary != ""
            assert len(res4.retrieved_authorities) >= 1
            print(f"  [PASS] Clean Fallback to '{res4.synthesis_engine}' without exception")

        # -------------------------------------------------------------
        # 5. SIMULATED NETWORK TIMEOUT FALLBACK
        # -------------------------------------------------------------
        print("\n[TEST 5] Simulated Network Timeout / Provider Failure Fallback...")
        req5 = ResearchQueryRequest(
            query="Arbitrability four-fold test actions in rem Vidya Drolia",
            jurisdiction="Supreme Court of India",
        )
        with patch("app.services.rag.orchestrator.get_llm_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.is_available.return_value = True
            mock_provider.generate_grounded_synthesis.side_effect = TimeoutError("Simulated venue Wi-Fi timeout")
            mock_get_provider.return_value = mock_provider

            res5 = orchestrator.execute_research(req5)
            assert res5 is not None
            assert res5.synthesis_engine == "Deterministic Fallback"
            assert res5.fallback_notice is not None
            assert "temporarily unavailable" in res5.fallback_notice
            print(f"  [PASS] Engine: {res5.synthesis_engine} | Fallback Notice: {res5.fallback_notice[:65]}...")

        # -------------------------------------------------------------
        # 6. CITATION GUARD HALLUCINATION INJECTION
        # -------------------------------------------------------------
        print("\n[TEST 6] Citation Guard Hallucination Neutralization...")
        passages = orchestrator.lexical_retriever.search_passages(query="Section 12A Commercial Courts Act", limit=3)
        from app.services.rag.authority_ranker import AuthorityRanker
        ranked_auths = AuthorityRanker.rank_and_aggregate(passages, limit=2)
        ev_pack = build_evidence_pack("Section 12A Commercial Courts Act", ranked_auths, [], passages, [])

        adversarial_synthesis = GroundedSynthesisStructuredOutput(
            summary="Commercial dispute summary.",
            key_principles=["Mandatory mediation."],
            governing_statutes=["Section 12A, Commercial Courts Act, 2015"],
            cited_authorities=[
                CitedAuthorityReference(
                    case_id="fake-case-999",
                    title="Fabricated Pharma Ltd. v. Fake Corp",
                    citation="2026 INSC 9999",
                    court="Supreme Court of India",
                    year=2026,
                    key_ratio="Fabricated legal proposition.",
                    treatment_status="GOOD_LAW",
                    cited_paragraphs=[999],
                    verbatim_quotes=["Fabricated quotation that does not exist in corpus"],
                    relevance_to_query="Fabricated commercial applicability"
                )
            ],
            practical_implications="Trial implications.",
            bench_guidance="Verify Section 12A notice.",
            corpus_limitations="Curated corpus.",
        )
        is_valid, sanitized, violations = DeterministicCitationGuard.validate(adversarial_synthesis, ev_pack)
        assert is_valid is False
        critical_violations = [v for v in violations if v.severity == "CRITICAL"]
        assert len(critical_violations) > 0
        print(f"  [PASS] DeterministicCitationGuard flagged {len(critical_violations)} CRITICAL violations: {critical_violations[0].check_type}")

        # -------------------------------------------------------------
        # 7. AUTHENTICATION & MULTI-TENANT DOSSIER ISOLATION
        # -------------------------------------------------------------
        print("\n[TEST 7] Authentication & Multi-Tenant Dossier Isolation...")
        judge = db.query(User).filter(User.role == "JUDGE").first()
        clerk = db.query(User).filter(User.role == "RESEARCH_CLERK").first()
        assert judge and clerk

        j_token = create_access_token(
            data={"sub": judge.id, "email": judge.email, "role": judge.role, "full_name": judge.full_name, "division": judge.court_division}
        )
        c_token = create_access_token(
            data={"sub": clerk.id, "email": clerk.email, "role": clerk.role, "full_name": clerk.full_name, "division": clerk.court_division}
        )

        # 401 unauthenticated
        res = client.post("/api/v1/research/query", json={"query": "test query"})
        assert res.status_code == 401, f"Expected 401 unauthenticated, got {res.status_code}"
        res = client.get("/api/v1/dossiers")
        assert res.status_code == 401, f"Expected 401 unauthenticated, got {res.status_code}"
        res = client.get("/api/v1/research/saved")
        assert res.status_code == 401, f"Expected 401 unauthenticated, got {res.status_code}"
        print("  [PASS] 401 Unauthorized strictly enforced for unauthenticated requests")

        # Judge creates private dossier
        headers_judge = {"Authorization": f"Bearer {j_token}"}
        create_payload = {
            "matter_title": "Judge Private Benchmark Matter",
            "suit_number": "CS(COMM) PRIVATE/2026",
            "judicial_notes": "Highly confidential deliberation notes",
            "items": [],
        }
        res_dossier = client.post("/api/v1/dossiers", json=create_payload, headers=headers_judge)
        assert res_dossier.status_code == 201
        dossier_id = res_dossier.json()["data"]["id"]

        # Clerk attempts access -> 404
        headers_clerk = {"Authorization": f"Bearer {c_token}"}
        res_isolated = client.get(f"/api/v1/dossiers/{dossier_id}", headers=headers_clerk)
        assert res_isolated.status_code == 404, f"Expected 404 isolation, got {res_isolated.status_code}"
        print(f"  [PASS] Cross-user access blocked: Clerk received 404 for Judge's private dossier")

        # Cleanup
        d = db.query(Dossier).filter(Dossier.id == dossier_id).first()
        if d:
            db.delete(d)
            db.commit()

        print("\n=================================================================")
        print("ALL 7 PHASE 4D HARDENING TESTS PASSED (100% SUCCESS)")
        print("=================================================================")
    finally:
        db.close()


if __name__ == "__main__":
    run_phase4d_hardening_suite()
