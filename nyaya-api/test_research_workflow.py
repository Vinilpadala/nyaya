import sys
from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.services.research_engine import ResearchEngineService
from app.schemas.research import ResearchQueryRequest
from app.models.case import Case
from app.models.statute import Statute
from app.models.audit import AuditLog
from app.models.saved_research import SavedResearch

def run_tests():
    print("Initializing DB schema and seed data...")
    init_db()
    db = SessionLocal()

    try:
        case_count = db.query(Case).count()
        statute_count = db.query(Statute).count()
        print(f"Verified Database: {case_count} cases, {statute_count} statutes.")

        # TEST 1: Mandatory Section 12A Mediation query with Trust & Explainability
        print("\n--- TEST 1: Section 12A Mediation Query & Explainability ---")
        req1 = ResearchQueryRequest(
            query="Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory",
            case_context="Commercial suit for breach of software license agreement; defendant moved application under Order VII Rule 11 CPC.",
            jurisdiction="Supreme Court of India",
            include_overruled=False,
            min_bench_strength=2,
        )
        service = ResearchEngineService(db)
        res1 = service.execute_research(req1)

        # 1.1 Citation Verification
        print("\n1.1 Verifying Citation Verification & Source Attribution:")
        assert len(res1.citation_verifications) > 0, "Expected citation verifications"
        lead_cv = res1.citation_verifications[0]
        print(f"Verified Citation: {lead_cv.standard_citation} [{lead_cv.neutral_citation}]")
        print(f"Official Reporter: {lead_cv.official_reporter}")
        print(f"Status: {lead_cv.good_law_status}, Bench Strength: {lead_cv.bench_strength}")
        print(f"Treatment History entries: {len(lead_cv.treatment_history)}")
        assert lead_cv.law_reporter_verified is True
        assert len(lead_cv.treatment_history) > 0

        # 1.2 4-Step Research Trail
        print("\n1.2 Verifying 4-Step Research Trail (User Query -> Retrieved Sources -> Relevant Passages -> AI Analysis):")
        trail = res1.research_trail
        assert trail.query_analysis_step.stage == "QUERY_ANALYSIS"
        assert trail.retrieval_step.stage == "SOURCE_RETRIEVAL"
        assert trail.passage_extraction_step.stage == "PASSAGE_EXTRACTION"
        assert trail.ai_synthesis_step.stage == "AI_SYNTHESIS"
        print(f"Step 1: {trail.query_analysis_step.title} -> {trail.query_analysis_step.items_count} items")
        print(f"Step 2: {trail.retrieval_step.title} -> {trail.retrieval_step.items_count} items")
        print(f"Step 3: {trail.passage_extraction_step.title} -> {trail.passage_extraction_step.items_count} items")
        print(f"Step 4: {trail.ai_synthesis_step.title} -> {trail.ai_synthesis_step.items_count} items")

        # 1.3 Uncertainty Assessment
        print("\n1.3 Verifying Uncertainty Assessment:")
        unc = res1.uncertainty_assessment
        print(f"Confidence Score: {unc.confidence_score}, Uncertainty Level: {unc.uncertainty_level}")
        print(f"Reason: {unc.reason[:70]}...")
        assert unc.confidence_score >= 0.9, "Settled law should have high confidence"
        assert unc.uncertainty_level == "LOW"

        # TEST 2: Query with High Legal Uncertainty (Unstamped contract)
        print("\n--- TEST 2: Ambiguous/Uncertain Legal Query ---")
        req_unc = ResearchQueryRequest(
            query="Enforceability of an arbitration clause in an unstamped commercial contract at the Section 11 stage",
            case_context="Dispute regarding unstamped lease deed with arbitration clause",
            jurisdiction="ALL",
        )
        res_unc = service.execute_research(req_unc)
        unc2 = res_unc.uncertainty_assessment
        print(f"Uncertainty Level: {unc2.uncertainty_level}, Ambiguity: {unc2.is_ambiguous}")
        print(f"Cautionary Guidance: {unc2.cautionary_guidance[:80]}...")
        assert unc2.is_ambiguous is True
        assert unc2.uncertainty_level in ["MEDIUM", "HIGH"]

        # TEST 3: Saved Research & Portfolio Bookmarks
        print("\n--- TEST 3: Saved Research Persistence ---")
        saved_items = db.query(SavedResearch).all()
        print(f"Existing Saved Research items in DB: {len(saved_items)}")
        assert len(saved_items) > 0, "Expected at least 1 seeded saved research item"

        # Create new bookmark
        user = db.query(Case).first() # to ensure db is active
        new_saved = SavedResearch(
            user_id="test-user-id",
            matter_id="CS(COMM) 999/2026",
            query_text=req_unc.query,
            case_context=req_unc.case_context,
            jurisdiction=req_unc.jurisdiction,
            lead_citation="In Re: Interplay",
            lead_title="Curative Petition (C) No. 44 of 2023",
            summary_extract="Unstamped agreement does not render arbitration clause void ab initio.",
            confidence_score=unc2.confidence_score,
            uncertainty_level=unc2.uncertainty_level,
            notes="Requires oral examination on whether original document was impounded.",
            tags="Arbitration, Stamp Act, Curative Bench",
            is_demo_data=True,
        )
        db.add(new_saved)
        db.commit()

        retrieved_saved = db.query(SavedResearch).filter(SavedResearch.id == new_saved.id).first()
        assert retrieved_saved is not None
        assert retrieved_saved.lead_citation == "In Re: Interplay"
        print(f"Successfully saved and retrieved bookmark: {retrieved_saved.id}")

        print("\n>>> ALL PHASE 4 BACKEND TRUST & EXPLAINABILITY TESTS PASSED! <<<")
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
