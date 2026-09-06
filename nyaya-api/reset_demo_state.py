"""
Nyaya AI — Demo Session Reset Utility
Safely resets transient demo rehearsal data (transient bookmarks, ad-hoc dossiers)
without altering the verified benchmark corpus (Cases, Passages, Citations, Statutes).
"""
import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.saved_research import SavedResearch
from app.models.dossier import Dossier, DossierItem
from app.models.audit import AuditLog
from app.models.case import Case
from app.models.statute import Statute
from app.db.init_db import seed_saved_research, seed_dossiers, seed_users


def reset_demo_state():
    db: Session = SessionLocal()
    try:
        print("==================================================")
        print("NYAYA AI — DEMO SESSION STATE RESET")
        print("==================================================")

        # 0. Sync Demo Account User Display Names
        seed_users(db)

        # 1. Verify Corpus Integrity Before Reset
        case_count = db.query(Case).count()
        statute_count = db.query(Statute).count()
        print(f"Verified Corpus: {case_count} cases, {statute_count} statutes. (Protected - Unaltered)")

        # 2. Clean transient saved research (retain demo bookmark)
        deleted_saved = db.query(SavedResearch).filter(SavedResearch.is_demo_data == False).delete()
        print(f"Transient Saved Research Bookmarks Purged: {deleted_saved}")

        # Ensure standard demo saved research exists
        seed_saved_research(db)

        # 3. Clean transient dossiers created during ad-hoc testing
        # Keep only the foundational seed dossier
        seed_suit = "CS(COMM) 412/2026"
        non_seed_dossiers = db.query(Dossier).filter(Dossier.suit_number != seed_suit).all()
        deleted_dossiers = 0
        for d in non_seed_dossiers:
            db.query(DossierItem).filter(DossierItem.dossier_id == d.id).delete()
            db.delete(d)
            deleted_dossiers += 1
        print(f"Transient Ad-hoc Dossiers Purged: {deleted_dossiers}")

        # Ensure foundational dossiers are seeded
        seed_dossiers(db)

        db.commit()
        print("--------------------------------------------------")
        print("Demo State Reset Complete: Clean chambers workspace restored.")
        print("Ready for live Smart India Hackathon judge demonstration.")
        print("==================================================")
    except Exception as e:
        db.rollback()
        print(f"Error resetting demo state: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_demo_state()
