import sys
import os

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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

def run_citation_guard_redteam():
    print("=================================================================")
    print("NYAYA AI — PHASE 3E: CITATION GUARD RED-TEAM ADVERSARIAL SUITE")
    print("=================================================================")

    # Controlled Evidence Pack containing one Good Law authority and one Overruled authority
    test_pack = EvidencePack(
        query="commercial dispute arbitration and Section 12A mediation",
        authorities=[
            EvidenceAuthorityItem(
                case_id="case-patil-2022",
                title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                bench_strength=2,
                key_ratio="Pre-institution mediation under Section 12A is mandatory.",
                composite_score=0.92,
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                negative_treatment_found=False,
                available_paragraphs=[74, 75, 84],
                passages=[
                    EvidencePassageItem(
                        passage_id="p-74",
                        paragraph_number=74,
                        text="Section 12A of the Commercial Courts Act, 2015 is mandatory and any suit instituted violating the mandate is liable to be rejected under Order VII Rule 11.",
                        legal_topic="Commercial Courts Act",
                        score=0.95,
                    ),
                    EvidencePassageItem(
                        passage_id="p-84",
                        paragraph_number=84,
                        text="The declaration of law is made effective from 20.08.2022 to prevent reopening of past suits.",
                        legal_topic="Prospective Application",
                        score=0.90,
                    ),
                ],
            ),
            EvidenceAuthorityItem(
                case_id="case-sms-2011",
                title="SMS Tea Estates Pvt. Ltd. v. Chandmari Tea Co. Pvt. Ltd.",
                citation="(2011) 14 SCC 66",
                court="Supreme Court of India",
                year=2011,
                bench_strength=2,
                key_ratio="Unstamped arbitration agreement cannot be acted upon.",
                composite_score=0.60,
                treatment_status="NEGATIVE_TREATMENT_FOUND (Overruled Precedent)",
                negative_treatment_found=True,
                available_paragraphs=[16],
                passages=[
                    EvidencePassageItem(
                        passage_id="p-16",
                        paragraph_number=16,
                        text="An unstamped agreement containing an arbitration clause cannot be acted upon until impounded.",
                        legal_topic="Stamp Act & Arbitration",
                        score=0.80,
                    ),
                ],
            ),
        ],
        statutes=[
            EvidenceStatuteItem(
                statute_id="stat-12a",
                act_title="Commercial Courts Act, 2015",
                section_number="12A",
                section_title="Pre-Institution Mediation",
                text="A suit which does not contemplate urgent interim relief shall not be instituted without mediation.",
            ),
        ],
    )

    # -------------------------------------------------------------
    # ATTACK 1: Completely Nonexistent Case ID / Fabricated Authority
    # -------------------------------------------------------------
    print("\n--- ATTACK 1: Nonexistent Case Authority Injected ---")
    attack1_output = GroundedSynthesisStructuredOutput(
        summary="A synthesis citing an imaginary precedent.",
        key_principles=["Fabricated principle"],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-phantom-999",
                title="Phantom Corp. v. Ghost Maritime Ltd.",
                citation="2026 SCC OnLine SC 1234",
                court="Supreme Court of India",
                year=2026,
                key_ratio="Fabricated rule on commercial jurisdiction.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[12],
                verbatim_quotes=[],
                relevance_to_query="None",
            )
        ],
        practical_implications="None",
        bench_guidance="None",
        corpus_limitations="Scope limitation",
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack1_output, test_pack)
    assert not is_valid, "Citation Guard MUST fail on nonexistent authority"
    assert any(v.check_type == "UNGROUNDED_AUTHORITY" and v.severity == "CRITICAL" for v in violations)
    print("  [PASS] Attack 1 Neutralized: Flagged as CRITICAL UNGROUNDED_AUTHORITY -> Triggers Fallback")

    # -------------------------------------------------------------
    # ATTACK 2: Nonexistent Paragraph Number (e.g. Para 999)
    # -------------------------------------------------------------
    print("\n--- ATTACK 2: Fabricated Paragraph Number Injected ---")
    attack2_output = GroundedSynthesisStructuredOutput(
        summary="Citing valid Patil Automation with fabricated paragraph 999.",
        key_principles=["Section 12A is mandatory."],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[999],  # Fabricated!
                verbatim_quotes=[],
                relevance_to_query="Statutory mandate",
            )
        ],
        practical_implications="Mediation check",
        bench_guidance="Examine plaint",
        corpus_limitations="Scope limitation",
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack2_output, test_pack)
    assert is_valid is True, "Valid case should be preserved after pruning invalid paragraph"
    assert len(sanitized.cited_authorities[0].cited_paragraphs) == 0, "Paragraph 999 must be pruned"
    assert any(v.check_type == "UNGROUNDED_PARAGRAPH" and v.severity == "WARNING" for v in violations)
    print("  [PASS] Attack 2 Neutralized: Fabricated paragraph [999] was pruned cleanly")

    # -------------------------------------------------------------
    # ATTACK 3: Unsupported / Fabricated Quotation
    # -------------------------------------------------------------
    print("\n--- ATTACK 3: Fabricated Quotation Injected ---")
    attack3_output = GroundedSynthesisStructuredOutput(
        summary="Citing valid case with fabricated quotation.",
        key_principles=["Section 12A is mandatory."],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[74],
                verbatim_quotes=["this particular phrase does not exist anywhere in the Supreme Court judgment"],
                relevance_to_query="Mandate",
            )
        ],
        practical_implications="Check",
        bench_guidance="Guidance",
        corpus_limitations="Scope",
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack3_output, test_pack)
    assert is_valid is True
    assert len(sanitized.cited_authorities[0].verbatim_quotes) == 0, "Fake quote must be pruned"
    assert any(v.check_type == "UNGROUNDED_QUOTATION" and v.severity == "WARNING" for v in violations)
    print("  [PASS] Attack 3 Neutralized: Fake quote was pruned cleanly")

    # -------------------------------------------------------------
    # ATTACK 4: Correct Case with Mixed Pinpoints (Authentic 74 + Fake 500)
    # -------------------------------------------------------------
    print("\n--- ATTACK 4: Mixed Authentic & Fabricated Pinpoints ---")
    attack4_output = GroundedSynthesisStructuredOutput(
        summary="Citing valid case with mixed pinpoints.",
        key_principles=["Section 12A is mandatory."],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[74, 500],  # 74 is authentic, 500 is fake!
                verbatim_quotes=[],
                relevance_to_query="Mandate",
            )
        ],
        practical_implications="Check",
        bench_guidance="Guidance",
        corpus_limitations="Scope",
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack4_output, test_pack)
    assert is_valid is True
    assert sanitized.cited_authorities[0].cited_paragraphs == [74], f"Expected [74], got {sanitized.cited_authorities[0].cited_paragraphs}"
    print("  [PASS] Attack 4 Neutralized: Authentic para [74] preserved, fake para [500] pruned")

    # -------------------------------------------------------------
    # ATTACK 5: Correct Case with Mixed Quotes (Authentic + Fake)
    # -------------------------------------------------------------
    print("\n--- ATTACK 5: Mixed Authentic & Fabricated Quotations ---")
    attack5_output = GroundedSynthesisStructuredOutput(
        summary="Citing valid case with mixed quotes.",
        key_principles=["Section 12A is mandatory."],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[74],
                verbatim_quotes=[
                    "liable to be rejected under Order VII Rule 11",  # Real substring from para 74
                    "all commercial judges must immediately dismiss without hearing"  # Fabricated
                ],
                relevance_to_query="Mandate",
            )
        ],
        practical_implications="Check",
        bench_guidance="Guidance",
        corpus_limitations="Scope",
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack5_output, test_pack)
    assert is_valid is True
    assert sanitized.cited_authorities[0].verbatim_quotes == ["liable to be rejected under Order VII Rule 11"]
    print("  [PASS] Attack 5 Neutralized: Authentic quote retained, fabricated quote pruned")

    # -------------------------------------------------------------
    # ATTACK 6: Overruled Precedent Falsely Labeled as Good Law
    # -------------------------------------------------------------
    print("\n--- ATTACK 6: Overruled Precedent Described as Unqualified Good Law ---")
    attack6_output = GroundedSynthesisStructuredOutput(
        summary="Citing SMS Tea Estates as binding valid law.",
        key_principles=["Unstamped arbitration clause cannot be acted upon."],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-sms-2011",
                title="SMS Tea Estates Pvt. Ltd. v. Chandmari Tea Co. Pvt. Ltd.",
                citation="(2011) 14 SCC 66",
                court="Supreme Court of India",
                year=2011,
                key_ratio="Unstamped agreement invalidates arbitration clause.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",  # FALSE! DB has OVERRULED
                cited_paragraphs=[16],
                verbatim_quotes=["An unstamped agreement containing an arbitration clause cannot be acted upon"],
                relevance_to_query="Referral stage",
            )
        ],
        practical_implications="Impounding mandatory",
        bench_guidance="Dismiss Section 11 petition",
        corpus_limitations="Scope",
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack6_output, test_pack)
    assert not is_valid, "Citation Guard MUST reject overruled case claimed as good law"
    assert any(v.check_type == "TREATMENT_MISMATCH" and v.severity == "CRITICAL" for v in violations)
    print("  [PASS] Attack 6 Neutralized: Flagged as CRITICAL TREATMENT_MISMATCH -> Triggers Fallback")

    # -------------------------------------------------------------
    # ATTACK 7: Missing Corpus Boundary Disclaimer
    # -------------------------------------------------------------
    print("\n--- ATTACK 7: Truncated or Missing Corpus Limitation Notice ---")
    attack7_output = GroundedSynthesisStructuredOutput(
        summary="A synthesis without any corpus limitations.",
        key_principles=["General proposition"],
        governing_statutes=[],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[74],
                verbatim_quotes=["liable to be rejected under Order VII Rule 11"],
                relevance_to_query="Mandate",
            )
        ],
        practical_implications="Check",
        bench_guidance="Guidance",
        corpus_limitations="",  # Empty!
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack7_output, test_pack)
    assert is_valid is True
    assert len(sanitized.corpus_limitations) > 30, "Citation Guard must restore mandatory boundary notice"
    assert "strictly bounded" in sanitized.corpus_limitations.lower()
    print("  [PASS] Attack 7 Neutralized: Missing disclaimer restored automatically by Citation Guard")

    # -------------------------------------------------------------
    # ATTACK 8: Hallucinated / Fabricated Statute Section Injected
    # -------------------------------------------------------------
    print("\n--- ATTACK 8: Fabricated Statute Injected ---")
    attack8_output = GroundedSynthesisStructuredOutput(
        summary="Citing valid Patil Automation but claiming authority under nonexistent statute.",
        key_principles=["Mandatory mediation requires summary rejection."],
        governing_statutes=[
            "Commercial Courts Act, 2015 (Section 12A)",  # Legitimate
            "Interplanetary Trade & Commerce Act, 2099 (Section 999A)",  # Fabricated!
        ],
        cited_authorities=[
            CitedAuthorityReference(
                case_id="case-patil-2022",
                title="Patil Automation Private Limited and Others v. Rakheja Engineers Private Limited",
                citation="(2022) 10 SCC 1",
                court="Supreme Court of India",
                year=2022,
                key_ratio="Section 12A is mandatory.",
                treatment_status="VERIFIED_IN_CORPUS (Good Law)",
                cited_paragraphs=[74],
                verbatim_quotes=["liable to be rejected under Order VII Rule 11"],
                relevance_to_query="Mandate",
            )
        ],
        practical_implications="Check",
        bench_guidance="Guidance",
        corpus_limitations="Scope limitation notice",
    )
    is_valid, sanitized, violations = DeterministicCitationGuard.validate(attack8_output, test_pack)
    assert is_valid is True
    assert len(sanitized.governing_statutes) == 1
    assert "Section 12A" in sanitized.governing_statutes[0]
    assert not any("2099" in s for s in sanitized.governing_statutes)
    assert any(v.check_type == "UNGROUNDED_STATUTE" and v.severity == "WARNING" for v in violations)
    print("  [PASS] Attack 8 Neutralized: Fabricated statute pruned cleanly, authentic statute retained")

    print("\n=================================================================")
    print("ALL 8 CITATION GUARD RED-TEAM ATTACKS SUCCESSFULLY NEUTRALIZED!")
    print("=================================================================")

if __name__ == "__main__":
    run_citation_guard_redteam()

