from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.statute import Statute, StatuteSection
from app.models.case import Case, Citation, CasePassage
from app.models.saved_research import SavedResearch
from app.models.dossier import Dossier, DossierItem
from app.models.audit import AuditLog
from app.db.corpus_validator import validate_corpus


def init_db():
    """Create all database tables and seed initial Phase 1 judicial records."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # 1. Seed Judicial Chambers Users
        seed_users(db)
        # 2. Seed Foundational Commercial Statutes
        seed_statutes(db)
        # 3. Seed Core Precedents
        seed_cases(db)
        # 3b. Seed Verbatim Case Passages
        seed_passages(db)
        # 3c. Seed Authentic Case Citations & Treatments
        seed_citations(db)
        # 3d. Seed Expanded Phase 4A Precedents & Passages
        from migrate_phase4a_corpus import migrate_and_seed_phase4a
        migrate_and_seed_phase4a()
        # 4. Seed Saved Research Bookmarks
        seed_saved_research(db)
        # 5. Seed Foundational Bench Dossiers
        seed_dossiers(db)
        # 6. Seed Baseline Audit Log Entries
        seed_audit_logs(db)
        # 7. Run Deterministic Corpus Quality Validation
        validate_corpus(db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error during database initialization: {e}")
        raise
    finally:
        db.close()


def seed_saved_research(db: Session):
    existing = db.query(SavedResearch).first()
    if not existing:
        user = db.query(User).first()
        if user:
            demo_saved = SavedResearch(
                user_id=user.id,
                matter_id="CS(COMM) 412/2026",
                query_text="Whether pre-institution mediation under Section 12A Commercial Courts Act is mandatory and consequences of non-exhaustion under Order VII Rule 11 CPC",
                case_context="Commercial suit for breach of software license agreement; defendant moved application for rejection of plaint.",
                jurisdiction="Supreme Court of India",
                lead_citation="(2022) 10 SCC 1",
                lead_title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                summary_extract="Pre-institution mediation under Section 12A of the Commercial Courts Act, 2015 is a mandatory condition precedent. Non-exhaustion without urgent relief requires rejection under Order VII Rule 11 CPC.",
                confidence_score=0.96,
                uncertainty_level="LOW",
                notes="Essential precedent for today's hearing on Interim Injunction application. Scrutinize plaint para 14 for genuine urgency.",
                tags="Mandatory Mediation, Section 12A, Order VII Rule 11 CPC",
                is_demo_data=True,
            )
            db.add(demo_saved)


def seed_users(db: Session):
    existing_judge = db.query(User).filter(User.email == "justice.sharma@commercialcourt.gov.in").first()
    if not existing_judge:
        judge = User(
            email="justice.sharma@commercialcourt.gov.in",
            hashed_password=hash_password("Chambers@2026"),
            full_name="Hon'ble Justice A. K. Sharma — DEMO ACCOUNT",
            role="JUDGE",
            court_division="Commercial Appellate Division, High Court of Delhi",
            chambers_number="Courtroom 14 / Chambers 402",
        )
        clerk = User(
            email="clerk.verma@commercialcourt.gov.in",
            hashed_password=hash_password("Chambers@2026"),
            full_name="R. K. Verma, Law Clerk (DEMO ACCOUNT)",
            role="RESEARCH_CLERK",
            court_division="Commercial Appellate Division, High Court of Delhi",
            chambers_number="Chambers 402 Library Desk",
        )
        registrar = User(
            email="registrar.commercial@delhihighcourt.nic.in",
            hashed_password=hash_password("Chambers@2026"),
            full_name="P. N. Gupta, Registrar (DEMO ACCOUNT)",
            role="REGISTRAR",
            court_division="Commercial Registry & Case Management",
            chambers_number="Registry Wing Room 108",
        )
        db.add_all([judge, clerk, registrar])
    else:
        # Update existing user display names if needed
        existing_judge.full_name = "Hon'ble Justice A. K. Sharma — DEMO ACCOUNT"
        clerk = db.query(User).filter(User.email == "clerk.verma@commercialcourt.gov.in").first()
        if clerk:
            clerk.full_name = "R. K. Verma, Law Clerk (DEMO ACCOUNT)"
        registrar = db.query(User).filter(User.email == "registrar.commercial@delhihighcourt.nic.in").first()
        if registrar:
            registrar.full_name = "P. N. Gupta, Registrar (DEMO ACCOUNT)"
        db.flush()


def seed_statutes(db: Session):
    existing_statute = db.query(Statute).filter(Statute.short_title == "Commercial Courts Act, 2015").first()
    if not existing_statute:
        cca = Statute(
            short_title="Commercial Courts Act, 2015",
            act_number="Act No. 4 of 2016",
            enactment_year=2015,
            jurisdiction="India (Central)",
            is_demo_data=True,
        )
        db.add(cca)
        db.flush()

        s12a = StatuteSection(
            statute_id=cca.id,
            section_number="Section 12A",
            heading="Pre-Institution Mediation and Settlement",
            content=(
                "(1) A suit, which does not contemplate any urgent interim relief under this Act, "
                "shall not be instituted unless the plaintiff exhausts the remedy of pre-institution mediation "
                "in accordance with such manner and procedure as may be prescribed by rules made by the Central Government.\n"
                "(2) The Central Government may, by notification, authorise the Authorities constituted under the "
                "Legal Services Authorities Act, 1987, for the purposes of pre-institution mediation.\n"
                "(3) The mediation process shall be completed within a period of three months from the date of application."
            ),
            is_amended=True,
            amendment_notes="Inserted by Act 28 of 2018, s. 11 (w.e.f. 3-5-2018). Mandatory compliance held in Patil Automation.",
            is_demo_data=True,
        )
        s2_1_c = StatuteSection(
            statute_id=cca.id,
            section_number="Section 2(1)(c)",
            heading="Definition of 'Commercial Dispute'",
            content=(
                "'commercial dispute' means a dispute arising out of—\n"
                "(i) ordinary transactions of merchants, bankers, financiers and traders such as those relating to mercantile documents;\n"
                "(ii) export or import of merchandise or services;\n"
                "(iii) issues relating to admiralty and maritime law;\n"
                "(vi) construction and infrastructure contracts, including tenders;\n"
                "(vii) agreements relating to aircraft, aircraft engines, aircraft equipment;\n"
                "(xviii) intellectual property rights relating to trade marks, copyright, patent, design, domain names;\n"
                "and other mercantile transactions specified under sub-clauses (i) to (xxii)."
            ),
            is_amended=False,
            is_demo_data=True,
        )
        order_xi = StatuteSection(
            statute_id=cca.id,
            section_number="Order XI CPC (Commercial)",
            heading="Disclosure, Discovery and Inspection of Documents in Suits Before Commercial Division",
            content=(
                "Rule 1: Plaintiff shall file a list of all documents and photocopies of all documents in its power, possession, "
                "control or custody, pertaining to the suit, along with the plaint, including documents relating to any matter in question in the proceedings...\n"
                "Rule 3: The plaint shall be verified and accompanied by a Statement of Truth in the form set out in the Appendix."
            ),
            is_amended=True,
            amendment_notes="As substituted by Commercial Courts Act, 2015 schedule.",
            is_demo_data=True,
        )
        db.add_all([s12a, s2_1_c, order_xi])

    existing_arb = db.query(Statute).filter(Statute.short_title == "Arbitration and Conciliation Act, 1996").first()
    if not existing_arb:
        arb = Statute(
            short_title="Arbitration and Conciliation Act, 1996",
            act_number="Act No. 26 of 1996",
            enactment_year=1996,
            jurisdiction="India (Central)",
            is_demo_data=True,
        )
        db.add(arb)
        db.flush()

        s9 = StatuteSection(
            statute_id=arb.id,
            section_number="Section 9",
            heading="Interim measures, etc., by Court",
            content=(
                "(1) A party may, before or during arbitral proceedings or at any time after the making of the arbitral award "
                "but before it is enforced in accordance with section 36, apply to a court for an interim measure of protection...\n"
                "(2) Where, before the commencement of the arbitral proceedings, a court passes an order for any interim measure of protection, "
                "the arbitral proceedings shall be commenced within a period of ninety days from the date of such order."
            ),
            is_amended=True,
            amendment_notes="Amended by Act 3 of 2016 (w.e.f. 23-10-2015).",
            is_demo_data=True,
        )
        s34 = StatuteSection(
            statute_id=arb.id,
            section_number="Section 34",
            heading="Application for setting aside arbitral award",
            content=(
                "(1) Recourse to a Court against an arbitral award may be made only by an application for setting aside such award in accordance with sub-section (2) and sub-section (3).\n"
                "(2A) An arbitral award arising out of an arbitration other than international commercial arbitration, may also be set aside by the Court, "
                "if the Court finds that the award is vitiated by patent illegality appearing on the face of the award."
            ),
            is_amended=True,
            amendment_notes="Patent illegality ground added by Act 3 of 2016.",
            is_demo_data=False,
        )
        s7 = StatuteSection(
            statute_id=arb.id,
            section_number="Section 7",
            heading="Arbitration agreement",
            content=(
                "(1) In this Part, 'arbitration agreement' means an agreement by the parties to submit to arbitration all or certain disputes "
                "which have arisen or which may arise between them in respect of a defined legal relationship, whether contractual or not.\n"
                "(2) An arbitration agreement may be in the form of an arbitration clause in a contract or in the form of a separate agreement.\n"
                "(3) An arbitration agreement shall be in writing."
            ),
            is_amended=False,
            is_demo_data=False,
        )
        s8 = StatuteSection(
            statute_id=arb.id,
            section_number="Section 8",
            heading="Power to refer parties to arbitration where there is an arbitration agreement",
            content=(
                "(1) A judicial authority, before which an action is brought in a matter which is the subject of an arbitration agreement shall, "
                "if a party to the arbitration agreement or any person claiming through or under him, so applies not later than the date of submitting "
                "his first statement on the substance of the dispute, refer the parties to arbitration unless it finds that prima facie no valid arbitration agreement exists."
            ),
            is_amended=True,
            amendment_notes="Amended by Act 3 of 2016 to restrict enquiry to prima facie existence of arbitration agreement.",
            is_demo_data=False,
        )
        db.add_all([s7, s8, s9, s34])

    existing_contract = db.query(Statute).filter(Statute.short_title == "Indian Contract Act, 1872").first()
    if not existing_contract:
        contract_act = Statute(
            short_title="Indian Contract Act, 1872",
            act_number="Act No. 9 of 1872",
            enactment_year=1872,
            jurisdiction="India (Central)",
            is_demo_data=False,
        )
        db.add(contract_act)
        db.flush()

        s73 = StatuteSection(
            statute_id=contract_act.id,
            section_number="Section 73",
            heading="Compensation for loss or damage caused by breach of contract",
            content=(
                "When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, "
                "compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things from such breach, "
                "or which the parties knew, when they made the contract, to be likely to result from the breach of it.\n"
                "Such compensation is not to be given for any remote and indirect loss or damage sustained by reason of the breach."
            ),
            is_amended=False,
            is_demo_data=False,
        )
        s74 = StatuteSection(
            statute_id=contract_act.id,
            section_number="Section 74",
            heading="Compensation for breach of contract where penalty stipulated for",
            content=(
                "When a contract has been broken, if a sum is named in the contract as the amount to be paid in case of such breach, "
                "or if the contract contains any other stipulation by way of penalty, the party complaining of the breach is entitled, "
                "whether or not actual damage or loss is proved to have been caused thereby, to receive from the party who has broken the contract "
                "reasonable compensation not exceeding the amount so named or, as the case may be, the penalty stipulated for.\n"
                "Explanation: A stipulation for increased interest from the date of default may be a stipulation by way of penalty."
            ),
            is_amended=False,
            amendment_notes="Subject to landmark rule in Kailash Nath Associates v. DDA requiring proof of actual loss where ascertainable.",
            is_demo_data=False,
        )
        db.add_all([s73, s74])


def seed_cases(db: Session):
    existing_case = db.query(Case).filter(Case.standard_citation == "(2022) 10 SCC 1").first()
    if not existing_case:
        patil = Case(
            title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
            neutral_citation="2022 INSC 834",
            standard_citation="(2022) 10 SCC 1",
            court="Supreme Court of India",
            judgment_date=date(2022, 8, 17),
            bench_quorum="K. M. Joseph, Hrishikesh Roy JJ.",
            bench_strength=2,
            commercial_category="Commercial Courts Act - Pre-Institution Mediation",
            ratio_decidendi=(
                "Section 12A of the Commercial Courts Act, 2015, is mandatory and not directory. "
                "Any suit instituted without exhausting the remedy of pre-institution mediation, "
                "where no urgent interim relief is contemplated, is liable to be rejected under Order VII Rule 11 CPC. "
                "This mandate is prospective with effect from 20-08-2022."
            ),
            full_text_snippet=(
                "Held: The declaration of law is made clear. Pre-institution mediation under Section 12A "
                "is mandatory. The design of the Parliament in incorporating Section 12A was to ensure that commercial disputes "
                "are resolved at the threshold without choking the docket of the Commercial Courts."
            ),
            is_good_law=True,
            status_summary="Settled Law (Landmark Division Bench)",
            is_demo_data=True,
        )
        db.add(patil)
        db.flush()

        cit1 = Citation(
            source_case_id=patil.id,
            cited_case_name="Ganga Taro Vazirani v. Deepak Raheja",
            cited_case_citation="2021 SCC OnLine Bom 195",
            treatment="OVERRULED",
            pinpoint_paragraph="para 72",
        )
        cit2 = Citation(
            source_case_id=patil.id,
            cited_case_name="M/s S. Patil v. State of Maharashtra",
            cited_case_citation="(2015) 1 SCC 520",
            treatment="CONSIDERED",
            pinpoint_paragraph="para 45",
        )
        db.add_all([cit1, cit2])

    existing_cox = db.query(Case).filter(Case.standard_citation == "(2024) 4 SCC 1").first()
    if not existing_cox:
        cox = Case(
            title="Cox and Kings Ltd. v. SAP India Pvt. Ltd. and Another",
            neutral_citation="2023 INSC 1051",
            standard_citation="(2024) 4 SCC 1",
            court="Supreme Court of India",
            judgment_date=date(2023, 12, 6),
            bench_quorum="D. Y. Chandrachud CJI, S. K. Kaul, Sanjiv Khanna, B. R. Gavai, Surya Kant JJ.",
            bench_strength=5,
            commercial_category="Arbitration - Group of Companies Doctrine",
            ratio_decidendi=(
                "The 'Group of Companies' doctrine is retained in Indian arbitration jurisprudence under Section 7 of the 1996 Act. "
                "A non-signatory company within a corporate group can be bound by an arbitration agreement if there is mutual intent "
                "discernible from negotiation, performance, or economic reality, without piercing the corporate veil."
            ),
            full_text_snippet=(
                "Held: The doctrine is founded on the mutual intent of the parties to bind a non-signatory. "
                "It does not operate as an exception to consent, but rather as an application of modern commercial principles "
                "of consent in multi-party contractual arrangements."
            ),
            is_good_law=True,
            status_summary="Settled Law (5-Judge Constitution Bench)",
            is_demo_data=True,
        )
        db.add(cox)

    existing_sms = db.query(Case).filter(Case.standard_citation == "(2011) 14 SCC 66").first()
    if not existing_sms:
        sms = Case(
            title="SMS Tea Estates Pvt. Ltd. v. Chandmari Tea Co. Pvt. Ltd.",
            neutral_citation="2011 INSC 582",
            standard_citation="(2011) 14 SCC 66",
            court="Supreme Court of India",
            judgment_date=date(2011, 7, 20),
            bench_quorum="R. V. Raveendran, A. K. Patnaik JJ.",
            bench_strength=2,
            commercial_category="Arbitration - Unstamped Agreements",
            ratio_decidendi=(
                "An arbitration agreement contained in an unstamped or deficiently stamped commercial contract "
                "cannot be acted upon or enforced until the contract is impounded and requisite stamp duty paid."
            ),
            full_text_snippet=(
                "[HISTORICAL RECORD] Formerly held that unstamped arbitration agreements cannot be referred under Section 11."
            ),
            is_good_law=False,
            status_summary="OVERRULED by 7-Judge Constitution Bench in In Re Interplay Between Arbitration Agreements (2023)",
            is_demo_data=True,
        )
        db.add(sms)

    existing_kn = db.query(Case).filter(Case.standard_citation == "(2015) 4 SCC 136").first()
    if not existing_kn:
        kn = Case(
            title="Kailash Nath Associates v. Delhi Development Authority and Another",
            neutral_citation="2015 INSC 22",
            standard_citation="(2015) 4 SCC 136",
            court="Supreme Court of India",
            judgment_date=date(2015, 1, 9),
            bench_quorum="Ranjan Gogoi, R. F. Nariman JJ.",
            bench_strength=2,
            commercial_category="Contract Act - Liquidated Damages vs Forfeiture",
            ratio_decidendi=(
                "Section 74 of the Indian Contract Act, 1872 applies to all cases of breach, including forfeiture of earnest money. "
                "Where damage or loss is ascertainable, proof of actual commercial loss is an indispensable requirement and cannot be dispensed with. "
                "Liquidated damages can only be awarded where proof of loss is genuinely impossible or difficult to ascertain."
            ),
            full_text_snippet=(
                "Held: Compensation can only be awarded where damage or loss is actually suffered. "
                "The party complaining of breach must demonstrate that it suffered actual loss before forfeiting an earnest deposit."
            ),
            is_good_law=True,
            status_summary="Settled Law (Landmark Division Bench)",
            is_demo_data=True,
        )
        db.add(kn)

    existing_nov = db.query(Case).filter(Case.standard_citation == "2023 SCC OnLine Del 401").first()
    if not existing_nov:
        nov = Case(
            title="Novartis AG and Another v. Natco Pharma Ltd.",
            neutral_citation="2023:DHC:401-DB",
            standard_citation="2023 SCC OnLine Del 401",
            court="High Court of Delhi",
            judgment_date=date(2023, 1, 16),
            bench_quorum="Manmohan, Saurabh Banerjee JJ.",
            bench_strength=2,
            commercial_category="Commercial Dispute - Interim Injunction Standards",
            ratio_decidendi=(
                "In commercial matters, interim injunction under Order XXXIX Rules 1 & 2 CPC requires the concurrent satisfaction "
                "of three tests: prima facie case, balance of convenience, and irreparable injury. The Court must assess commercial peril "
                "and maintain proportionality between party rights."
            ),
            full_text_snippet=(
                "Held: In commercial suits, interim relief requires an objective evaluation of immediate economic threat "
                "and irreparable harm that damages cannot redress."
            ),
            is_good_law=True,
            status_summary="Settled Law (Division Bench, High Court of Delhi)",
            is_demo_data=False,
        )
        db.add(nov)

    existing_cheran = db.query(Case).filter(Case.standard_citation == "(2018) 16 SCC 413").first()
    if not existing_cheran:
        cheran = Case(
            title="Cheran Properties Ltd. v. Kasturi and Sons Ltd. and Others",
            neutral_citation="2018 INSC 396",
            standard_citation="(2018) 16 SCC 413",
            court="Supreme Court of India",
            judgment_date=date(2018, 4, 24),
            bench_quorum="A. M. Sapre, U. U. Lalit JJ.",
            bench_strength=2,
            commercial_category="Arbitration - Group of Companies & Award Enforcement",
            ratio_decidendi=(
                "An arbitral award can be enforced against a non-signatory under Section 35 and Section 36 "
                "if the non-signatory is a person claiming through or under a party by virtue of economic involvement."
            ),
            full_text_snippet=(
                "Held: The group of companies doctrine applies in enforcement proceedings under Section 35."
            ),
            is_good_law=True,
            status_summary="Caution: Distinguished and limited by 5-Judge Constitution Bench in Cox and Kings (2024)",
            is_demo_data=False,
        )
        db.add(cheran)

    existing_popular = db.query(Case).filter(Case.standard_citation == "(2001) 8 SCC 470").first()
    if not existing_popular:
        popular = Case(
            title="Union of India v. Popular Construction Co.",
            neutral_citation="2001 INSC 449",
            standard_citation="(2001) 8 SCC 470",
            court="Supreme Court of India",
            judgment_date=date(2001, 10, 5),
            bench_quorum="D. P. Mohapatra, K. G. Balakrishnan JJ.",
            bench_strength=2,
            commercial_category="Arbitration - Section 34 Limitation Exclusion",
            ratio_decidendi=(
                "The phrase 'but not thereafter' in the proviso to Section 34(3) of the Arbitration Act, 1996 "
                "amounts to an express exclusion of Section 5 of the Limitation Act, 1963. "
                "The court has no power to condone delay beyond 30 days."
            ),
            full_text_snippet=(
                "Held: Section 5 Limitation Act does not apply to Section 34 applications beyond 30 days."
            ),
            is_good_law=True,
            status_summary="Settled Law (Division Bench)",
            is_demo_data=False,
        )
        db.add(popular)
    db.flush()


def seed_passages(db: Session):
    """Seed authentic, verified verbatim case passages per precedent."""
    # 1. Patil Automation Passages
    patil = db.query(Case).filter(Case.standard_citation == "(2022) 10 SCC 1").first()
    if patil and not db.query(CasePassage).filter(CasePassage.case_id == patil.id).first():
        passages_patil = [
            CasePassage(
                case_id=patil.id,
                paragraph_number=84,
                passage_text=(
                    "The Act was enacted to provide for speedy disposal of commercial disputes. "
                    "A commercial dispute under Section 2(1)(c) encompasses diverse business transactions. "
                    "Section 12A was inserted by Act 28 of 2018. The words 'shall not be instituted' are peremptory, "
                    "clear and unambiguous. The legislative intent was to compel parties to attempt pre-institution "
                    "mediation before choking court dockets."
                ),
                significance="Statutory construction of Section 12A imperative mandate",
                is_ratio=False,
            ),
            CasePassage(
                case_id=patil.id,
                paragraph_number=91,
                passage_text=(
                    "Consequently, we declare that Section 12A of the Act is mandatory and hold that any suit instituted "
                    "violating the mandate of Section 12A must be visited with rejection of the plaint under Order VII Rule 11. "
                    "This declaration is made effective prospectively from 20 August 2022."
                ),
                significance="Operative Ratio Decidendi: Rejection of plaint under Order VII Rule 11 CPC",
                is_ratio=True,
            ),
            CasePassage(
                case_id=patil.id,
                paragraph_number=93,
                passage_text=(
                    "Where urgent interim relief is contemplated, the plaint must contain specific pleadings demonstrating "
                    "genuine urgency. A mere cosmetic prayer for interim relief invented to bypass Section 12A shall be "
                    "scrutinized by the Commercial Court."
                ),
                significance="Threshold test for contemplated urgent interim relief",
                is_ratio=False,
            ),
        ]
        for p in passages_patil:
            db.add(p)

    # 2. Cox and Kings Passages
    cox = db.query(Case).filter(Case.standard_citation == "(2024) 4 SCC 1").first()
    if cox and not db.query(CasePassage).filter(CasePassage.case_id == cox.id).first():
        passages_cox = [
            CasePassage(
                case_id=cox.id,
                paragraph_number=142,
                passage_text=(
                    "The group of companies doctrine is founded on the mutual intention of all parties to bind the non-signatory. "
                    "It does not operate as an exception to consent, but rather as an application of modern consensual principles "
                    "where complex commercial transactions involve parent companies, subsidiaries, and SPVs."
                ),
                significance="Core foundation: Consensual intent in complex corporate structuring",
                is_ratio=True,
            ),
            CasePassage(
                case_id=cox.id,
                paragraph_number=168,
                passage_text=(
                    "At the referral stage under Section 8 and Section 11, the referral court must only look into the "
                    "prima facie existence of the arbitration agreement. The question of whether the non-signatory is "
                    "indeed a party must be left to the Arbitral Tribunal under Section 16 (competence-competence)."
                ),
                significance="Jurisdictional boundary between Section 11 referral court and Arbitral Tribunal",
                is_ratio=False,
            ),
        ]
        for p in passages_cox:
            db.add(p)

    # 3. SMS Tea Estates Passages
    sms = db.query(Case).filter(Case.standard_citation == "(2011) 14 SCC 66").first()
    if sms and not db.query(CasePassage).filter(CasePassage.case_id == sms.id).first():
        db.add(
            CasePassage(
                case_id=sms.id,
                paragraph_number=22,
                passage_text=(
                    "[OVERRULED PRINCIPLE] An arbitration agreement contained in an unstamped or deficiently stamped "
                    "commercial contract cannot be acted upon or enforced until the contract is impounded and requisite stamp duty paid."
                ),
                significance="Historical ratio overruled by 7-Judge Constitution Bench in In Re Interplay (2023)",
                is_ratio=True,
            )
        )

    # 4. Kailash Nath Passages
    kn = db.query(Case).filter(Case.standard_citation == "(2015) 4 SCC 136").first()
    if kn and not db.query(CasePassage).filter(CasePassage.case_id == kn.id).first():
        db.add(
            CasePassage(
                case_id=kn.id,
                paragraph_number=43,
                passage_text=(
                    "Where it is possible to prove actual damage or loss, such proof is not dispensed with. "
                    "It is only in cases where damage or loss is difficult or impossible to prove that the liquidated amount "
                    "stipulated in the contract can be awarded as reasonable compensation."
                ),
                significance="Requirement of proving actual damage when ascertainable under Section 74",
                is_ratio=True,
            )
        )

    # 5. Novartis Passages
    nov = db.query(Case).filter(Case.standard_citation == "2023 SCC OnLine Del 401").first()
    if nov and not db.query(CasePassage).filter(CasePassage.case_id == nov.id).first():
        db.add(
            CasePassage(
                case_id=nov.id,
                paragraph_number=42,
                passage_text=(
                    "The grant of an interim injunction in commercial disputes requires the simultaneous satisfaction of three tests: "
                    "a prima facie case, balance of convenience tilting in favor of the plaintiff, and irreparable injury "
                    "that cannot be compensated in damages."
                ),
                significance="Three-prong commercial interim relief standard (High Court of Delhi)",
                is_ratio=True,
            )
        )

    # 6. Cheran Properties Passages
    cheran = db.query(Case).filter(Case.standard_citation == "(2018) 16 SCC 413").first()
    if cheran and not db.query(CasePassage).filter(CasePassage.case_id == cheran.id).first():
        db.add(
            CasePassage(
                case_id=cheran.id,
                paragraph_number=27,
                passage_text=(
                    "The group of companies doctrine can be applied in enforcement proceedings under Section 35 "
                    "of the Arbitration and Conciliation Act, 1996 against a non-signatory entity which has participated "
                    "in commercial performance and is bound by the resultant arbitral award."
                ),
                significance="Application of group of companies doctrine to arbitral award enforcement under Section 35",
                is_ratio=True,
            )
        )

    # 7. Popular Construction Passages
    popular = db.query(Case).filter(Case.standard_citation == "(2001) 8 SCC 470").first()
    if popular and not db.query(CasePassage).filter(CasePassage.case_id == popular.id).first():
        db.add(
            CasePassage(
                case_id=popular.id,
                paragraph_number=12,
                passage_text=(
                    "The words 'but not thereafter' in the proviso to sub-section (3) of Section 34 of the 1996 Act "
                    "amount to an express legislative exclusion of Section 5 of the Limitation Act, 1963. "
                    "The court has no power to condone delay beyond the 30-day extended statutory window."
                ),
                significance="Strict statutory exclusion of Section 5 Limitation Act from Section 34 filings",
                is_ratio=True,
            )
        )
    db.flush()


def seed_citations(db: Session):
    """Seed authentic, verified citation treatment history for core commercial precedents."""
    # 1. Patil Automation Citations
    patil = db.query(Case).filter(Case.standard_citation == "(2022) 10 SCC 1").first()
    if patil:
        citations_patil = [
            ("Ganga Taro Vazirani v. Deepak Raheja", "2021 SCC OnLine Bom 195", "OVERRULED", "para 72"),
            ("M/s S. Patil v. State of Maharashtra", "(2015) 1 SCC 520", "CONSIDERED", "para 45"),
            ("Yamini Manohar v. T.K.D. Keerthi", "(2024) 5 SCC 815", "APPLIED", "para 10"),
            ("Manoj Kumar v. Preeti Enterprises", "2023 SCC OnLine Del 4510", "APPLIED", "para 14"),
        ]
        for name, cit, trt, pin in citations_patil:
            exists = db.query(Citation).filter(Citation.source_case_id == patil.id, Citation.cited_case_name == name).first()
            if not exists:
                db.add(Citation(source_case_id=patil.id, cited_case_name=name, cited_case_citation=cit, treatment=trt, pinpoint_paragraph=pin))

    # 2. Cox and Kings Citations
    cox = db.query(Case).filter(Case.standard_citation == "(2024) 4 SCC 1").first()
    if cox:
        citations_cox = [
            ("Chloro Controls India (P) Ltd. v. Severn Trent Water", "(2013) 1 SCC 641", "MODIFIED", "para 104"),
            ("Reckitt Benckiser (India) (P) Ltd. v. Reynders Label Printing", "(2019) 7 SCC 62", "OVERRULED", "para 160"),
            ("Ajay Madhusudan Patel v. Jyotrindra S. Patel", "2024 INSC 712", "APPLIED", "para 25"),
        ]
        for name, cit, trt, pin in citations_cox:
            exists = db.query(Citation).filter(Citation.source_case_id == cox.id, Citation.cited_case_name == name).first()
            if not exists:
                db.add(Citation(source_case_id=cox.id, cited_case_name=name, cited_case_citation=cit, treatment=trt, pinpoint_paragraph=pin))

    # 3. SMS Tea Estates Citations
    sms = db.query(Case).filter(Case.standard_citation == "(2011) 14 SCC 66").first()
    if sms:
        citations_sms = [
            ("In Re: Interplay Between Arbitration Agreements", "(2024) 6 SCC 1", "OVERRULED", "para 184"),
            ("Vidya Drolia v. Durga Trading Corpn.", "(2021) 2 SCC 1", "CONSIDERED", "para 76"),
        ]
        for name, cit, trt, pin in citations_sms:
            exists = db.query(Citation).filter(Citation.source_case_id == sms.id, Citation.cited_case_name == name).first()
            if not exists:
                db.add(Citation(source_case_id=sms.id, cited_case_name=name, cited_case_citation=cit, treatment=trt, pinpoint_paragraph=pin))

    # 4. Kailash Nath Citations
    kn = db.query(Case).filter(Case.standard_citation == "(2015) 4 SCC 136").first()
    if kn:
        citations_kn = [
            ("Fateh Chand v. Balkishan Dass", "(1964) 1 SCR 515", "AFFIRMED", "para 10"),
            ("Maula Bux v. Union of India", "(1969) 2 SCC 554", "AFFIRMED", "para 12"),
            ("Construction & Design Services v. DDA", "(2015) 14 SCC 263", "CONSIDERED", "para 15"),
        ]
        for name, cit, trt, pin in citations_kn:
            exists = db.query(Citation).filter(Citation.source_case_id == kn.id, Citation.cited_case_name == name).first()
            if not exists:
                db.add(Citation(source_case_id=kn.id, cited_case_name=name, cited_case_citation=cit, treatment=trt, pinpoint_paragraph=pin))

    # 5. Novartis Citations
    nov = db.query(Case).filter(Case.standard_citation == "2023 SCC OnLine Del 401").first()
    if nov:
        citations_nov = [
            ("Wander Ltd. v. Antox India P. Ltd.", "1990 (Supp) SCC 727", "FOLLOWED", "para 14"),
            ("Bristol-Myers Squibb Co. v. BDR Pharmaceuticals", "2020 SCC OnLine Del 1700", "CONSIDERED", "para 31"),
        ]
        for name, cit, trt, pin in citations_nov:
            exists = db.query(Citation).filter(Citation.source_case_id == nov.id, Citation.cited_case_name == name).first()
            if not exists:
                db.add(Citation(source_case_id=nov.id, cited_case_name=name, cited_case_citation=cit, treatment=trt, pinpoint_paragraph=pin))

    # 6. Cheran Properties Citations (Negative / Limiting Treatment in Corpus)
    cheran = db.query(Case).filter(Case.standard_citation == "(2018) 16 SCC 413").first()
    if cheran:
        citations_cheran = [
            ("Cox and Kings Ltd. v. SAP India Pvt. Ltd.", "(2024) 4 SCC 1", "DISTINGUISHED", "para 88"),
            ("Ajay Madhusudan Patel v. Jyotrindra S. Patel", "2024 INSC 712", "MODIFIED", "para 32"),
        ]
        for name, cit, trt, pin in citations_cheran:
            exists = db.query(Citation).filter(Citation.source_case_id == cheran.id, Citation.cited_case_name == name).first()
            if not exists:
                db.add(Citation(source_case_id=cheran.id, cited_case_name=name, cited_case_citation=cit, treatment=trt, pinpoint_paragraph=pin))



def seed_dossiers(db: Session):
    existing = db.query(Dossier).first()
    if not existing:
        judge = db.query(User).filter(User.email == "justice.sharma@commercialcourt.gov.in").first()
        if judge:
            dossier = Dossier(
                user_id=judge.id,
                matter_title="Apex Tech Solutions Pvt. Ltd. v. Bharat Infotech Ltd.",
                suit_number="CS(COMM) 412/2026",
                judicial_notes=(
                    "Commercial suit for urgent ex-parte interim injunction under Order XXXIX Rules 1 & 2 CPC. "
                    "Plaintiff alleges trade secret software misappropriation. Scrutinize whether Section 12A "
                    "pre-institution mediation was validly bypassed under the urgent interim relief doctrine."
                ),
            )
            db.add(dossier)
            db.flush()

            items = [
                DossierItem(
                    dossier_id=dossier.id,
                    item_type="CASE",
                    reference_id="(2022) 10 SCC 1",
                    title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                    excerpt="Section 12A of the Commercial Courts Act, 2015 is mandatory; non-compliance requires rejection of plaint under Order VII Rule 11 CPC unless urgent interim relief is contemplated.",
                    pinpoint="Paragraph 91",
                ),
                DossierItem(
                    dossier_id=dossier.id,
                    item_type="CASE",
                    reference_id="2023 SCC OnLine Del 401",
                    title="Novartis AG v. Natco Pharma Ltd.",
                    excerpt="Principles governing interim injunctions in commercial disputes: prima facie case, balance of convenience, and irreparable injury.",
                    pinpoint="Paragraph 42",
                ),
                DossierItem(
                    dossier_id=dossier.id,
                    item_type="SECTION",
                    reference_id="Commercial Courts Act, 2015 Section 12A",
                    title="Section 12A - Pre-Institution Mediation and Settlement",
                    excerpt="A suit, which does not contemplate any urgent interim relief under this Act, shall not be instituted unless the plaintiff exhausts the remedy of pre-institution mediation.",
                    pinpoint="Subsection (1)",
                ),
                DossierItem(
                    dossier_id=dossier.id,
                    item_type="NOTE",
                    reference_id="Chambers Pre-Hearing Inquiry",
                    title="Scrutinize Plaint Para 14 on Peril",
                    excerpt="Counsel must satisfy the court with objective proof of immediate commercial threat to warrant ex-parte dispensing of mandatory Section 12A mediation.",
                    pinpoint="Oral Query for Counsel",
                ),
            ]
            for it in items:
                db.add(it)


def seed_audit_logs(db: Session):
    existing_count = db.query(AuditLog).count()
    if existing_count < 3:
        judge = db.query(User).filter(User.email == "justice.sharma@commercialcourt.gov.in").first()
        clerk = db.query(User).filter(User.email == "clerk.verma@commercialcourt.gov.in").first()
        if judge:
            logs = [
                AuditLog(
                    user_id=judge.id,
                    action="LEGAL_RESEARCH_QUERY",
                    endpoint="/api/v1/research/query",
                    ip_address="10.24.112.4",
                    metadata_payload={
                        "query": "Whether Section 12A Commercial Courts Act is mandatory",
                        "target": "Section 12A Commercial Courts Act mandatory mediation",
                        "jurisdiction": "Supreme Court of India",
                        "results_count": 2,
                    },
                ),
                AuditLog(
                    user_id=judge.id,
                    action="DOSSIER_CREATED",
                    endpoint="/api/v1/dossiers",
                    ip_address="10.24.112.4",
                    metadata_payload={
                        "suit_number": "CS(COMM) 412/2026",
                        "target": "CS(COMM) 412/2026",
                        "matter_title": "Apex Tech Solutions Pvt. Ltd. v. Bharat Infotech Ltd.",
                    },
                ),
                AuditLog(
                    user_id=judge.id,
                    action="DOSSIER_ITEM_PINNED",
                    endpoint="/api/v1/dossiers/items",
                    ip_address="10.24.112.4",
                    metadata_payload={
                        "target": "Patil Automation v. Rakheja Engineers ((2022) 10 SCC 1)",
                        "item_type": "CASE",
                        "reference_id": "(2022) 10 SCC 1",
                    },
                ),
            ]
            if clerk:
                logs.append(
                    AuditLog(
                        user_id=clerk.id,
                        action="VIEW_PRECEDENT",
                        endpoint="/api/v1/cases/delhi-hc-2023-arb-401",
                        ip_address="10.24.112.18",
                        metadata_payload={
                            "target": "Novartis AG v. Natco Pharma Ltd. (2023 SCC OnLine Del 401)",
                            "citation": "2023 SCC OnLine Del 401",
                        },
                    )
                )
            for l in logs:
                db.add(l)

