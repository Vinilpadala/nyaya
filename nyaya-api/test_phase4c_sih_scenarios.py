import os
import sys

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.schemas.research import ResearchQueryRequest
from app.services.rag.orchestrator import RAGResearchOrchestrator


def run_sih_scenarios_validation():
    print("=================================================================")
    print("NYAYA AI — PHASE 4C: SMART INDIA HACKATHON DEMO VALIDATION SUITE")
    print("=================================================================")

    db = SessionLocal()
    orchestrator = RAGResearchOrchestrator(db)

    try:
        # -------------------------------------------------------------
        # SCENARIO 1: Commercial Courts Act — Mandatory Mediation (Patil Automation)
        # -------------------------------------------------------------
        print("\n--- SCENARIO 1: Commercial Courts Act — Mandatory Mediation ---")
        req1 = ResearchQueryRequest(
            query="Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory and consequences of non-exhaustion under Order VII Rule 11 CPC",
            case_context="Commercial suit for breach of software license agreement; defendant moved application for rejection of plaint on ground that no urgent interim relief was contemplated.",
            jurisdiction="Supreme Court of India",
            include_overruled=False,
        )
        res1 = orchestrator.execute_research(req1)
        assert len(res1.retrieved_authorities) > 0, "Scenario 1: No authorities retrieved"
        lead1 = res1.retrieved_authorities[0]
        print(f"  [PASS] Lead Authority: {lead1.title} ({lead1.standard_citation})")
        print(f"  [PASS] Relevance Score: {lead1.relevance_score}")
        assert "Patil Automation" in lead1.title, f"Expected Patil Automation at Rank 1, got {lead1.title}"
        assert lead1.is_good_law is True, "Patil Automation must be evaluated as Good Law"

        pinpoints1 = [p.paragraph_number for p in lead1.pinpoint_passages]
        print(f"  [PASS] Pinpoint Paragraphs: {pinpoints1}")
        assert 91 in pinpoints1, "Expected authentic paragraph 91 pinpoint in Patil Automation"

        unc1 = res1.uncertainty_assessment
        print(f"  [PASS] Uncertainty: {unc1.uncertainty_level} (Confidence: {unc1.confidence_score})")
        assert unc1.uncertainty_level == "LOW", f"Expected LOW uncertainty, got {unc1.uncertainty_level}"
        assert unc1.confidence_score >= 0.85, f"Expected confidence >= 0.85, got {unc1.confidence_score}"

        # -------------------------------------------------------------
        # SCENARIO 2: Legal Evolution & Overruled Precedent (Stamping)
        # -------------------------------------------------------------
        print("\n--- SCENARIO 2: Legal Evolution & Overruled Precedent Handling ---")
        req2 = ResearchQueryRequest(
            query="Arbitration clause unstamped document enforceability Section 11 Appointment of Arbitrator",
            case_context="Commercial concession agreement containing arbitration clause not stamped in accordance with State Stamp Act; respondent objects to Section 11 appointment.",
            jurisdiction="ALL",
            include_overruled=True,
        )
        res2 = orchestrator.execute_research(req2)
        assert len(res2.retrieved_authorities) >= 2, "Scenario 2: Expected at least 2 authorities"

        lead2 = res2.retrieved_authorities[0]
        second2 = res2.retrieved_authorities[1]
        print(f"  [PASS] Rank 1: {lead2.title} ({lead2.standard_citation}) | Good Law: {lead2.is_good_law}")
        print(f"  [PASS] Rank 2: {second2.title} ({second2.standard_citation}) | Good Law: {second2.is_good_law}")

        assert "In Re: Interplay" in lead2.title, f"Expected 7-Judge Bench In Re Interplay at Rank 1, got {lead2.title}"
        assert lead2.is_good_law is True, "In Re Interplay must be Good Law"

        assert "SMS Tea Estates" in second2.title, f"Expected overruled SMS Tea Estates at Rank 2, got {second2.title}"
        assert second2.is_good_law is False, "SMS Tea Estates must be evaluated as Overruled Precedent (is_good_law=False)"

        unc2 = res2.uncertainty_assessment
        print(f"  [PASS] Uncertainty: {unc2.uncertainty_level} (Confidence: {unc2.confidence_score})")
        assert unc2.uncertainty_level == "HIGH", f"Expected HIGH uncertainty due to overruled precedent, got {unc2.uncertainty_level}"
        assert unc2.has_conflicting_authorities is True, "Expected conflicting authorities flag to be True"

        # -------------------------------------------------------------
        # SCENARIO 3: Responsible AI & Out-of-Corpus Query (Anticipatory Bail)
        # -------------------------------------------------------------
        print("\n--- SCENARIO 3: Responsible AI & Insufficient Corpus Coverage ---")
        req3 = ResearchQueryRequest(
            query="Anticipatory bail Section 438 CrPC criminal trial arrest protection",
            case_context="Accused seeking pre-arrest bail in non-commercial criminal proceeding.",
            jurisdiction="ALL",
            include_overruled=False,
        )
        res3 = orchestrator.execute_research(req3)
        unc3 = res3.uncertainty_assessment
        print(f"  [PASS] Lead Score: {res3.retrieved_authorities[0].relevance_score if res3.retrieved_authorities else 0.0}")
        print(f"  [PASS] Uncertainty: {unc3.uncertainty_level} (Confidence: {unc3.confidence_score})")
        assert unc3.uncertainty_level == "HIGH", f"Expected HIGH uncertainty, got {unc3.uncertainty_level}"
        assert unc3.confidence_score <= 0.45, f"Expected confidence <= 0.45, got {unc3.confidence_score}"
        assert "INSUFFICIENT CORPUS EVIDENCE" in unc3.reason or "WEAK RETRIEVAL" in unc3.reason
        print("  [PASS] Transparent boundary refusal triggered without fabricating criminal law")

        # -------------------------------------------------------------
        # SCENARIO 4: Commercial Contract & Damages (Liquidated Damages Interplay)
        # -------------------------------------------------------------
        print("\n--- SCENARIO 4: Commercial Contract & Damages (Section 74 Interplay) ---")
        req4 = ResearchQueryRequest(
            query="Whether Section 74 Indian Contract Act requires proof of actual commercial loss for liquidated damages or forfeiture",
            case_context="Dispute regarding forfeiture of earnest money deposit and recovery of pre-estimated liquidated damages under commercial supply agreement.",
            jurisdiction="Supreme Court of India",
            include_overruled=False,
        )
        res4 = orchestrator.execute_research(req4)
        auth_titles4 = [a.title for a in res4.retrieved_authorities]
        print(f"  [PASS] Top Authorities: {auth_titles4[:2]}")
        has_ongc = any("ONGC" in t or "Saw Pipes" in t for t in auth_titles4)
        has_kn = any("Kailash Nath" in t for t in auth_titles4)
        assert has_ongc and has_kn, f"Expected both ONGC and Kailash Nath in top authorities, got {auth_titles4}"
        print("  [PASS] Complementary Section 74 precedents successfully retrieved")

        # -------------------------------------------------------------
        # SCENARIO 5: Commercial Arbitrability — Four-Fold Test (Vidya Drolia)
        # -------------------------------------------------------------
        print("\n--- SCENARIO 5: Commercial Arbitrability Four-Fold Test ---")
        req5 = ResearchQueryRequest(
            query="Arbitrability of dispute four-fold test actions in rem sovereign functions Section 8 Section 11",
            case_context="Commercial dispute where respondent contends the subject matter involves rights in rem and is excluded from arbitration.",
            jurisdiction="Supreme Court of India",
            include_overruled=False,
        )
        res5 = orchestrator.execute_research(req5)
        lead5 = res5.retrieved_authorities[0]
        print(f"  [PASS] Lead Authority: {lead5.title} ({lead5.standard_citation})")
        assert "Vidya Drolia" in lead5.title, f"Expected Vidya Drolia at Rank 1, got {lead5.title}"
        pinpoints5 = [p.paragraph_number for p in lead5.pinpoint_passages]
        print(f"  [PASS] Pinpoints: {pinpoints5}")
        assert 76 in pinpoints5, "Expected Paragraph 76 four-fold test pinpoint in Vidya Drolia"

        print("\n=================================================================")
        print("ALL 5 SMART INDIA HACKATHON DEMONSTRATION SCENARIOS VERIFIED 100%!")
        print("=================================================================")

    finally:
        db.close()


if __name__ == "__main__":
    run_sih_scenarios_validation()
