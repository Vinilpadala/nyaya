"""
Nyaya AI — Phase 5B: Transparent Historical-Pattern Analytics Test Suite
Direct execution via: python test_phase5b_pattern_analytics.py

Verifies:
1. Strict semantic separation of:
   - Legal status of an authority
   - Treatment of an authority
   - Procedural posture
   - Actual case disposition/outcome
   - Historical pattern
2. Dispositions are NOT derived from `is_good_law`.
3. Fallback to "Outcome data not available in curated corpus" when provenance is absent.
4. Data-Readiness Criterion exact match.
5. Judicial Independence Disclaimer exact match.
6. Scenario 1 (Patil Automation: Plaint Rejection posture & disposition).
7. Scenario 2 (In Re Interplay active vs SMS Tea Estates isolated overruled disposition).
8. Scenario 3 (Out-of-domain criminal query refusal).
9. Scenario 4 (Section 74 ONGC pre-estimate vs Kailash Nath actual loss proof).
"""
import os
import sys

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.schemas.research import ResearchQueryRequest, RetrievedAuthorityDTO
from app.services.rag.orchestrator import RAGResearchOrchestrator
from app.services.analytics.pattern_engine import HistoricalPatternService, AUTHENTIC_PRECEDENT_METADATA


def run_phase5b_pattern_analytics_suite():
    print("=================================================================")
    print("NYAYA AI — PHASE 5B: HISTORICAL-PATTERN ANALYTICS VALIDATION SUITE")
    print("=================================================================")

    db = SessionLocal()
    orchestrator = RAGResearchOrchestrator(db)

    try:
        # -------------------------------------------------------------
        # 1. SEMANTIC SEPARATION & NO DERIVATION FROM is_good_law
        # -------------------------------------------------------------
        print("\n[TEST 1] Semantic Separation & Independent Dispositions...")
        # Patil Automation: is_good_law = True, but Plaint was REJECTED
        patil_meta = AUTHENTIC_PRECEDENT_METADATA.get("(2022) 10 SCC 1")
        assert patil_meta is not None
        assert "Plaint Rejected" in patil_meta["actual_disposition"]
        print("  [PASS] Verified: Good-law precedent (Patil Automation) records substantive 'Plaint Rejected' outcome (not derived from is_good_law)")

        # SMS Tea Estates: is_good_law = False, but outcome is authentic historical holding
        sms_meta = AUTHENTIC_PRECEDENT_METADATA.get("(2011) 14 SCC 66")
        assert sms_meta is not None
        assert "Appointment of arbitrator denied" in sms_meta["actual_disposition"]
        print("  [PASS] Verified: Overruled precedent (SMS Tea) records authentic historical posture, NOT an arbitrary failure label")

        # -------------------------------------------------------------
        # 2. PROVENANCE FALLBACK FOR UNINDEXED AUTHORITIES
        # -------------------------------------------------------------
        print("\n[TEST 2] Provenance Fallback for Unindexed Authorities...")
        dummy_auth = RetrievedAuthorityDTO(
            id="dummy-case-999",
            title="Unindexed Commercial Case Ltd. v. Generic Corp",
            standard_citation="2026 INSC 0000",
            neutral_citation="2026 INSC 0000",
            court="Supreme Court of India",
            judgment_date="2026-01-01",
            bench_quorum="Bench 2",
            bench_strength=2,
            is_good_law=True,
            status_summary="Settled Law",
            relevance_score=10.0,
            why_relevant="Direct lookup",
            ratio_extract="Generic commercial ratio.",
            pinpoint_passages=[],
            is_demo_data=False,
        )
        res_dummy = HistoricalPatternService.analyze_precedents(
            authorities=[dummy_auth],
            citation_verifications=[],
            query="arbitration",
        )
        assert res_dummy is not None
        assert len(res_dummy.active_precedent_patterns) == 1
        item_dummy = res_dummy.active_precedent_patterns[0]
        assert item_dummy.actual_disposition == "Outcome data not available in curated corpus"
        assert item_dummy.disposition_provenance == "Not Indexed in Curated Corpus"
        print(f"  [PASS] Fallback triggered cleanly: '{item_dummy.actual_disposition}'")

        # -------------------------------------------------------------
        # 3. DATA-READINESS CRITERION & JUDICIAL DISCLAIMER VERIFICATION
        # -------------------------------------------------------------
        print("\n[TEST 3] Data-Readiness Criterion & Judicial Independence Disclaimer...")
        expected_criterion = (
            "Genuine predictive ML will be considered only after sufficient authentic, representative, "
            "labelled historical data is available and rigorous out-of-sample evaluation demonstrates "
            "statistical reliability, calibration, generalization, and acceptable uncertainty."
        )
        assert res_dummy.data_readiness_notice == expected_criterion
        assert "Judicial Independence Notice" in res_dummy.judicial_disclaimer
        print("  [PASS] Exact data-readiness criterion and judicial independence notice verified")

        # -------------------------------------------------------------
        # 4. SCENARIO 1: Commercial Courts Act Sec 12A Precedent Pattern
        # -------------------------------------------------------------
        print("\n[TEST 4] Scenario 1 — Commercial Courts Act Sec 12A Pattern...")
        req1 = ResearchQueryRequest(
            query="Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory and consequences of non-exhaustion under Order VII Rule 11 CPC",
            jurisdiction="Supreme Court of India",
            include_overruled=False,
        )
        res1 = orchestrator.execute_research(req1)
        assert res1.historical_pattern_analysis is not None
        hpa1 = res1.historical_pattern_analysis
        assert hpa1.comparable_authorities_count >= 1
        lead_pattern = hpa1.active_precedent_patterns[0]
        assert "Patil Automation" in lead_pattern.case_title
        assert "Order VII Rule 11" in lead_pattern.procedural_posture
        assert "Plaint Rejected" in lead_pattern.actual_disposition
        assert "2018" in hpa1.legal_regime_period
        print(f"  [PASS] Lead Pattern: {lead_pattern.case_title} ({lead_pattern.standard_citation})")
        print(f"  [PASS] Posture: {lead_pattern.procedural_posture}")
        print(f"  [PASS] Disposition: {lead_pattern.actual_disposition}")

        # -------------------------------------------------------------
        # 5. SCENARIO 2: Stamping & Regime Guard Overruling Isolation
        # -------------------------------------------------------------
        print("\n[TEST 5] Scenario 2 — Stamping & Regime Guard Isolation...")
        req2 = ResearchQueryRequest(
            query="Arbitration clause unstamped document enforceability Section 11 Appointment of Arbitrator",
            jurisdiction="ALL",
            include_overruled=True,
        )
        res2 = orchestrator.execute_research(req2)
        assert res2.historical_pattern_analysis is not None
        hpa2 = res2.historical_pattern_analysis

        # Active pattern must contain In Re Interplay
        active_titles = [p.case_title for p in hpa2.active_precedent_patterns]
        assert any("Interplay" in t for t in active_titles)
        interplay_pattern = next(p for p in hpa2.active_precedent_patterns if "Interplay" in p.case_title)
        assert "enforceable at referral stage" in interplay_pattern.actual_disposition

        # Overruled pattern must contain SMS Tea Estates isolated from active law
        overruled_titles = [p.case_title for p in hpa2.overruled_precedent_patterns]
        assert any("SMS Tea" in t for t in overruled_titles)
        sms_pattern = next(p for p in hpa2.overruled_precedent_patterns if "SMS Tea" in p.case_title)
        assert sms_pattern.legal_status == "OVERRULED_PRECEDENT"
        assert sms_pattern.is_active_law is False
        print(f"  [PASS] Active Governing Pattern: {interplay_pattern.case_title} (7-Judge Bench)")
        print(f"  [PASS] Isolated Overruled Pattern: {sms_pattern.case_title} (Regime Guard Active)")

        # -------------------------------------------------------------
        # 6. SCENARIO 3: Responsible AI & Out-of-Domain Criminal Boundary
        # -------------------------------------------------------------
        print("\n[TEST 6] Scenario 3 — Out-of-Domain Criminal Boundary Refusal...")
        req3 = ResearchQueryRequest(
            query="Anticipatory bail Section 438 CrPC criminal trial arrest protection",
            jurisdiction="ALL",
            include_overruled=False,
        )
        res3 = orchestrator.execute_research(req3)
        # Weak out-of-domain retrievals (score < 1.0) must return None for pattern analytics
        # Or have 0 comparable commercial precedent patterns
        if res3.historical_pattern_analysis is not None:
            assert res3.historical_pattern_analysis.comparable_authorities_count == 0
        print("  [PASS] Out-of-domain query safely refused: Zero commercial precedent patterns formed")

        # -------------------------------------------------------------
        # 7. SCENARIO 4: Section 74 Precedent Interplay Patterns
        # -------------------------------------------------------------
        print("\n[TEST 7] Scenario 4 — Contract Act Section 74 Interplay...")
        req4 = ResearchQueryRequest(
            query="Whether Section 74 Indian Contract Act requires proof of actual commercial loss for liquidated damages or forfeiture",
            jurisdiction="Supreme Court of India",
            include_overruled=False,
        )
        res4 = orchestrator.execute_research(req4)
        assert res4.historical_pattern_analysis is not None
        hpa4 = res4.historical_pattern_analysis
        citations = [p.standard_citation for p in hpa4.active_precedent_patterns]
        assert "(2003) 5 SCC 705" in citations or "(2015) 4 SCC 136" in citations
        print(f"  [PASS] Section 74 Complementary Patterns Retrieved: {citations}")

        print("\n=================================================================")
        print("ALL PHASE 5B HISTORICAL-PATTERN ANALYTICS TESTS PASSED (100%)")
        print("=================================================================")
    finally:
        db.close()


if __name__ == "__main__":
    run_phase5b_pattern_analytics_suite()
