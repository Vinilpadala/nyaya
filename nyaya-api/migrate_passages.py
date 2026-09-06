import os
import sys

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.case import Case, CasePassage, Citation
from app.models.dossier import DossierItem
from app.db.init_db import seed_passages

def migrate_and_deduplicate():
    print("Running Phase 3E.1 database cleanup and passage migration...")
    db = SessionLocal()
    try:
        # 1. Clean up duplicate cases
        # Duplicate Cheran Properties
        dupe_cheran = db.query(Case).filter(
            Case.standard_citation == "(2018) 16 SCC 413",
            Case.id == "2faa0366-e558-49fe-a028-0d020ed5ccc4"
        ).first()
        if dupe_cheran:
            print(f"Deleting orphan duplicate Cheran Properties: {dupe_cheran.id}")
            db.delete(dupe_cheran)

        # Duplicate Popular Construction
        dupe_popular = db.query(Case).filter(
            Case.standard_citation == "(2001) 8 SCC 470",
            Case.id == "6590ec9c-448a-4ae2-a806-bf1dd243d514"
        ).first()
        if dupe_popular:
            print(f"Deleting orphan duplicate Popular Construction: {dupe_popular.id}")
            db.delete(dupe_popular)

        db.flush()

        # 2. Run seed_passages to populate passages for Cheran Properties and Popular Construction
        seed_passages(db)
        db.commit()

        # 3. Verification
        all_cases = db.query(Case).all()
        print(f"\nMigration Complete. Total Cases: {len(all_cases)}")
        for c in all_cases:
            p_count = db.query(CasePassage).filter(CasePassage.case_id == c.id).count()
            print(f"  - [{c.id[:8]}] {c.title} ({c.standard_citation}) -> {p_count} Passages")
            assert p_count > 0, f"Case {c.title} must have at least 1 passage!"

        print("\nAll benchmark authorities have verified passages in case_passages!")

    finally:
        db.close()

if __name__ == "__main__":
    migrate_and_deduplicate()
