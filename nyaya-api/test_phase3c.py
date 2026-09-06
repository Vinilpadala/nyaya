import urllib.request
import urllib.error
import json

from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.models.case import Case, Citation
from app.models.statute import Statute
from app.schemas.research import ResearchQueryRequest
from app.services.rag.citation_verifier import CitationVerifier
from app.services.rag.uncertainty_engine import UncertaintyEngine
from app.services.research_engine import ResearchEngineService


def test_phase_3c_comprehensive():
    print("\n=======================================================")
    print("NYAYA AI — PHASE 3C COMPREHENSIVE VERIFICATION SUITE")
    print("=======================================================")

    init_db()
    db = SessionLocal()

    try:
        cv = CitationVerifier(db)
        svc = ResearchEngineService(db)

        # -------------------------------------------------------------
        # TEST 1: Valid authority with positive treatment (Patil Automation)
        # -------------------------------------------------------------
        print("\n--- TEST 1: Valid Authority with Positive Treatment ---")
        p_res = cv.verify_by_citation_string("(2022) 10 SCC 1")
        print(f"Case: {p_res.case_title}")
        print(f"Status: {p_res.good_law_status}")
        print(f"Coverage Status: {p_res.corpus_coverage_status}")
        print(f"Treatments Count: {len(p_res.treatment_history)}")
        print(f"Notes: {p_res.verification_notes[:80]}...")
        assert p_res.corpus_coverage_status == "VERIFIED_IN_CORPUS"
        assert "Verified Good Law" in p_res.good_law_status
        assert p_res.is_good_law is True
        assert p_res.law_reporter_verified is True
        assert len(p_res.treatment_history) > 0
        assert any(t.treatment == "APPLIED" for t in p_res.treatment_history)
        print("[PASS] Test 1: Positive treatment verified dynamically from DB.")

        # -------------------------------------------------------------
        # TEST 2: Authority with negative/limiting treatment (Cheran Properties)
        # -------------------------------------------------------------
        print("\n--- TEST 2: Authority with Negative/Limiting Treatment ---")
        c_res = cv.verify_by_citation_string("(2018) 16 SCC 413")
        print(f"Case: {c_res.case_title}")
        print(f"Status: {c_res.good_law_status}")
        print(f"Coverage Status: {c_res.corpus_coverage_status}")
        print(f"Treatments Count: {len(c_res.treatment_history)}")
        print(f"Notes: {c_res.verification_notes[:80]}...")
        assert c_res.corpus_coverage_status == "NEGATIVE_TREATMENT_FOUND"
        assert "Caution" in c_res.good_law_status or "Distinguished" in c_res.good_law_status
        assert any(t.treatment in ["DISTINGUISHED", "MODIFIED"] for t in c_res.treatment_history)
        print("[PASS] Test 2: Negative/limiting treatment (Distinguished/Modified) identified.")

        # -------------------------------------------------------------
        # TEST 3: Overruled authority (SMS Tea Estates)
        # -------------------------------------------------------------
        print("\n--- TEST 3: Overruled Authority ---")
        s_res = cv.verify_by_citation_string("(2011) 14 SCC 66")
        print(f"Case: {s_res.case_title}")
        print(f"Status: {s_res.good_law_status}")
        print(f"Coverage Status: {s_res.corpus_coverage_status}")
        print(f"Is Good Law: {s_res.is_good_law}")
        print(f"Notes: {s_res.verification_notes[:80]}...")
        assert s_res.corpus_coverage_status == "NEGATIVE_TREATMENT_FOUND"
        assert "Overruled" in s_res.good_law_status
        assert s_res.is_good_law is False
        print("[PASS] Test 3: Overruled authority explicitly flagged.")

        # -------------------------------------------------------------
        # TEST 4: Authority with NO treatment information (Popular Construction)
        # -------------------------------------------------------------
        print("\n--- TEST 4: Authority with No Treatment Information in Corpus ---")
        pop_res = cv.verify_by_citation_string("(2001) 8 SCC 470")
        print(f"Case: {pop_res.case_title}")
        print(f"Status: {pop_res.good_law_status}")
        print(f"Coverage Status: {pop_res.corpus_coverage_status}")
        print(f"Treatments Count: {len(pop_res.treatment_history)}")
        print(f"Notes: {pop_res.verification_notes[:90]}...")
        assert pop_res.corpus_coverage_status == "NO_TREATMENT_FOUND"
        assert len(pop_res.treatment_history) == 0
        assert "No Treatment Data" in pop_res.good_law_status
        # Crucial check: Verifier does NOT falsely claim universal good law
        assert "Never assume universal good law" in pop_res.verification_notes
        print("[PASS] Test 4: Authority with no treatment records cleanly distinguished without false claims.")

        # -------------------------------------------------------------
        # TEST 5: Authority missing from corpus (Insufficient Coverage)
        # -------------------------------------------------------------
        print("\n--- TEST 5: Authority Missing from Corpus ---")
        missing_res = cv.verify_by_case_id("non-existent-guid-999")
        print(f"Status: {missing_res.good_law_status}")
        print(f"Coverage Status: {missing_res.corpus_coverage_status}")
        print(f"Law Reporter Verified: {missing_res.law_reporter_verified}")
        assert missing_res.corpus_coverage_status == "INSUFFICIENT_CORPUS"
        assert "Insufficient Corpus" in missing_res.good_law_status
        assert missing_res.law_reporter_verified is False
        print("[PASS] Test 5: Missing authority returns Insufficient Corpus Coverage.")

        # -------------------------------------------------------------
        # TEST 6: Query with Insufficient Corpus Evidence
        # -------------------------------------------------------------
        print("\n--- TEST 6: Query with Insufficient Corpus Evidence ---")
        req_insufficient = ResearchQueryRequest(
            query="Admiralty arrest of foreign vessel under maritime lien and bunker supply contract collision",
            case_context="In rem action against vessel anchored at Mumbai port",
            jurisdiction="ALL",
        )
        res_insufficient = svc.execute_research(req_insufficient)
        unc_insufficient = res_insufficient.uncertainty_assessment
        print(f"Uncertainty: {unc_insufficient.uncertainty_level}")
        print(f"Confidence: {unc_insufficient.confidence_score}")
        print(f"Reason: {unc_insufficient.reason[:80]}...")
        print(f"Corpus Limitation Note: {unc_insufficient.corpus_limitation_note[:70]}...")
        assert unc_insufficient.uncertainty_level == "HIGH"
        assert unc_insufficient.confidence_score <= 0.60
        assert "CORPUS" in unc_insufficient.reason or "INSUFFICIENT" in unc_insufficient.reason
        assert unc_insufficient.corpus_limitation_note is not None
        print("[PASS] Test 6: Insufficient corpus evidence transparently communicated.")

        # -------------------------------------------------------------
        # TEST 7: Query with Conflicting Authorities (Unstamped Agreement)
        # -------------------------------------------------------------
        print("\n--- TEST 7: Query with Conflicting Authorities ---")
        req_conflict = ResearchQueryRequest(
            query="Enforceability of unstamped arbitration agreement under Section 11 stamp duty defect",
            case_context="Arbitration referral sought on unstamped memorandum of understanding",
            include_overruled=True,  # Deliberately include overruled precedents to test conflict detection
        )
        res_conflict = svc.execute_research(req_conflict)
        unc_conflict = res_conflict.uncertainty_assessment
        print(f"Uncertainty: {unc_conflict.uncertainty_level}")
        print(f"Confidence: {unc_conflict.confidence_score}")
        print(f"Has Conflicting Authorities: {unc_conflict.has_conflicting_authorities}")
        print(f"Reason: {unc_conflict.reason[:80]}...")
        assert unc_conflict.uncertainty_level == "HIGH"
        assert unc_conflict.has_conflicting_authorities is True
        assert unc_conflict.confidence_score <= 0.60
        print("[PASS] Test 7: Conflicting/overruled authorities properly trigger high uncertainty.")

        # -------------------------------------------------------------
        # TEST 8: Score Separation / Margin Evaluation
        # -------------------------------------------------------------
        print("\n--- TEST 8: Score Separation & Margin ---")
        req_margin = ResearchQueryRequest(
            query="Mandatory pre-institution mediation Section 12A rejection of plaint Order VII Rule 11",
            jurisdiction="Supreme Court of India",
        )
        res_margin = svc.execute_research(req_margin)
        unc_margin = res_margin.uncertainty_assessment
        print(f"Lead Authority: {res_margin.retrieved_authorities[0].title}")
        print(f"Lead Score: {res_margin.retrieved_authorities[0].relevance_score}")
        print(f"Score Margin: {unc_margin.score_margin}")
        print(f"Grounding Confidence: {unc_margin.confidence_score}")
        assert unc_margin.score_margin is not None
        assert unc_margin.confidence_score >= 0.85
        assert unc_margin.confidence_score <= 0.95  # Calibrated conservatively
        print("[PASS] Test 8: Conservative confidence calibration and score margin validated.")

        # -------------------------------------------------------------
        # TEST 9: Unauthenticated Research Endpoint Returns 401
        # -------------------------------------------------------------
        print("\n--- TEST 9: Unauthenticated API Access Protection ---")
        base_url = "http://127.0.0.1:8000/api/v1"
        try:
            req_http = urllib.request.Request(
                f"{base_url}/research/query",
                data=json.dumps({"query": "Commercial dispute Section 12A"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req_http)
            assert False, "Expected 401 Unauthorized for unauthenticated request"
        except urllib.error.HTTPError as e:
            print(f"HTTP Status: {e.code} (Expected 401)")
            assert e.code == 401
        print("[PASS] Test 9: Unauthenticated request securely rejected with 401.")

        print("\n=======================================================")
        print(">>> ALL PHASE 3C TESTS PASSED WITH 100% SUCCESS! <<<")
        print("=======================================================\n")
        return True

    finally:
        db.close()


if __name__ == "__main__":
    test_phase_3c_comprehensive()
