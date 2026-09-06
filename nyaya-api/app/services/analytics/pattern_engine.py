"""
Nyaya AI — Historical Pattern Analytics Service (Phase 5B)

Deterministic, transparent aggregation of authentic precedent patterns,
procedural postures, and substantive dispositions from the verified commercial corpus.

STRICT SAFEGUARDS:
1. Does NOT derive litigant outcome, case disposition, or success/failure from `is_good_law`.
2. Only displays procedural/substantive outcomes explicitly and authentically represented in the corpus with provenance.
3. If an authority's actual outcome is not available, displays "Outcome data not available in curated corpus".
4. Does NOT infer win/loss probabilities from authority counts.
5. Strictly maintains semantic distinction between:
   - Legal status of an authority (Good Law vs Overruled)
   - Treatment of an authority (Affirmed, Overruled, Applied, Distinguished)
   - Procedural posture (Application stage/type)
   - Actual case disposition/outcome (Explicit holding result)
   - Historical pattern (Aggregate precedent observations)
"""
from typing import List, Dict, Any, Optional
from datetime import date
from app.schemas.research import (
    RetrievedAuthorityDTO,
    CitationVerificationDTO,
    HistoricalPatternAnalysisDTO,
    PrecedentDispositionItem,
)

# Authentic, manually curated procedural posture and disposition records derived from official law reports (SCC/SCR).
# PROVENANCE GUARANTEE: Never inferred from `is_good_law`.
AUTHENTIC_PRECEDENT_METADATA = {
    "(2022) 10 SCC 1": {
        "procedural_posture": "Order VII Rule 11 CPC Application for rejection of commercial plaint",
        "actual_disposition": "Plaint Rejected for non-compliance with mandatory Section 12A pre-institution mediation",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2022) 10 SCC 1, paras 84, 91, 93",
        "legal_regime": "Post-Commercial Courts (Amendment) Act, 2018 (Act 28 of 2018)",
    },
    "(2024) 6 SCC 1": {
        "procedural_posture": "Constitution Bench Reference on Section 11(6) Arbitration Application",
        "actual_disposition": "Unstamped arbitration agreement held enforceable at referral stage; referral court examines prima facie existence only",
        "disposition_provenance": "Supreme Court of India (7-Judge Bench): (2024) 6 SCC 1, paras 184, 224 [2023 INSC 1066]",
        "legal_regime": "7-Judge Constitution Bench (Current Governing Law)",
    },
    "(2011) 14 SCC 66": {
        "procedural_posture": "Section 11(6) Arbitration Application for appointment of arbitrator",
        "actual_disposition": "Appointment of arbitrator denied on ground of unstamped agreement (HISTORICAL PRECEDENT — OVERRULED)",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2011) 14 SCC 66, paras 12, 16",
        "legal_regime": "Pre-2023 Interplay Doctrine (Superseded by 7-Judge Constitution Bench)",
    },
    "(2021) 2 SCC 1": {
        "procedural_posture": "Section 11(6) Arbitration Reference on Arbitrability",
        "actual_disposition": "Four-fold non-arbitrability test formulated; tenancy dispute held arbitrable; referral to arbitration directed",
        "disposition_provenance": "Supreme Court of India (Full Bench): (2021) 2 SCC 1, paras 76, 154 [2020 INSC 697]",
        "legal_regime": "Full Bench Settled Law (When in doubt, refer)",
    },
    "(2003) 5 SCC 705": {
        "procedural_posture": "Section 34 Arbitral Award Challenge",
        "actual_disposition": "Liquidated damages pre-estimate upheld under Section 74 without requiring proof of actual loss where loss is difficult to quantify",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2003) 5 SCC 705, paras 67, 68 [2003 INSC 214]",
        "legal_regime": "Contract Act Section 74 Doctrine (Harmonized by Kailash Nath)",
    },
    "(2015) 4 SCC 136": {
        "procedural_posture": "Civil Appeal on Forfeiture of Earnest Money Deposit",
        "actual_disposition": "Forfeiture of earnest money set aside; proof of actual commercial loss held mandatory where damage is ascertainable",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2015) 4 SCC 136, paras 43, 44 [2015 INSC 26]",
        "legal_regime": "Contract Act Section 74 Settled Precedent",
    },
    "(2001) 8 SCC 470": {
        "procedural_posture": "Section 34(3) Application to Set Aside Arbitral Award",
        "actual_disposition": "Application dismissed as barred by limitation; Section 5 Limitation Act held inapplicable to Section 34(3)",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2001) 8 SCC 470, paras 12, 16",
        "legal_regime": "Arbitration Act Section 34(3) Limitation Doctrine",
    },
    "(2018) 16 SCC 413": {
        "procedural_posture": "Section 35/36 Execution Petition against Non-Signatory",
        "actual_disposition": "Arbitral award enforced against non-signatory under Group of Companies doctrine",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2018) 16 SCC 413, paras 23, 27",
        "legal_regime": "Group of Companies Enforcement Doctrine",
    },
    "(2024) 4 SCC 1": {
        "procedural_posture": "Constitution Bench Reference on Group of Companies under Section 9 & 11",
        "actual_disposition": "Group of Companies doctrine affirmed with strict requirement of common mutual intention to bind non-signatory",
        "disposition_provenance": "Supreme Court of India (5-Judge Bench): (2024) 4 SCC 1, paras 165, 172 [2023 INSC 1051]",
        "legal_regime": "5-Judge Constitution Bench (Current Law)",
    },
    "(2020) 15 SCC 585": {
        "procedural_posture": "Commercial Suit Jurisdiction Objection under Section 2(1)(c)(vii)",
        "actual_disposition": "Commercial suit returned; immovable property transaction held non-commercial without actual present commercial trade use",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2020) 15 SCC 585, paras 14, 15 [2019 INSC 1113]",
        "legal_regime": "Commercial Courts Act Jurisdiction Doctrine",
    },
    "(2021) 13 SCC 399": {
        "procedural_posture": "Commercial Suit Order XI Rule 1 CPC Application for Additional Documents",
        "actual_disposition": "Leave to place additional documents on record denied for failure to establish reasonable cause",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2021) 13 SCC 399, paras 8, 10 [2021 INSC 534]",
        "legal_regime": "Commercial Courts Act Strict Disclosure Doctrine",
    },
    "(2021) 6 SCC 436": {
        "procedural_posture": "Section 8 Arbitration Application vs Section 7 IBC Petition",
        "actual_disposition": "Section 8 application allowed; dispute pre-admission held arbitrable in personam",
        "disposition_provenance": "Supreme Court of India Official Judgment: (2021) 6 SCC 436, paras 27, 28 [2021 INSC 226]",
        "legal_regime": "IBC - Arbitration Interplay Settled Doctrine",
    },
    "2022 SCC OnLine Del 969": {
        "procedural_posture": "Commercial IP Suit Interlocutory Injunction Application under Order XXXIX",
        "actual_disposition": "Injunction denied; comparative advertising held non-disparaging",
        "disposition_provenance": "High Court of Delhi Official Judgment: 2022 SCC OnLine Del 969, paras 41, 42",
        "legal_regime": "Commercial Division IP Disparagement Precedent",
    },
    "2023 SCC OnLine Del 401": {
        "procedural_posture": "Commercial Division IP Appeal against Interlocutory Injunction",
        "actual_disposition": "Injunction granted; patent infringement restrained",
        "disposition_provenance": "High Court of Delhi Official Judgment: 2023 SCC OnLine Del 401, paras 34, 38",
        "legal_regime": "Commercial Division Patent Injunction Precedent",
    },
}


class HistoricalPatternService:
    """
    Service responsible for constructing transparent historical-pattern analytics
    over retrieved candidate precedent authorities.
    """

    @classmethod
    def analyze_precedents(
        cls,
        authorities: List[RetrievedAuthorityDTO],
        citation_verifications: List[CitationVerificationDTO],
        query: str,
    ) -> Optional[HistoricalPatternAnalysisDTO]:
        """
        Analyzes authentic precedent authorities to produce a structured, non-ML
        historical pattern analysis.
        """
        # Exclude weakly relevant or empty retrievals (e.g. out-of-domain criminal queries)
        meaningful_authorities = [a for a in authorities if a.relevance_score >= 1.0]
        if not meaningful_authorities:
            return None

        # Index citation verifications by case ID
        cv_map = {cv.case_id: cv for cv in citation_verifications if cv}

        active_patterns: List[PrecedentDispositionItem] = []
        overruled_patterns: List[PrecedentDispositionItem] = []
        courts_set = set()
        bench_distribution = {}
        years = []

        for auth in meaningful_authorities:
            courts_set.add(auth.court)
            
            # Quorum distribution
            bench_label = f"{auth.bench_strength}-Judge Bench"
            if auth.bench_strength >= 5:
                bench_label = f"Constitution Bench ({auth.bench_strength} Judges)"
            elif auth.bench_strength == 3:
                bench_label = "Full Bench (3 Judges)"
            elif auth.bench_strength == 2:
                bench_label = "Division Bench (2 Judges)"
            elif auth.bench_strength == 1:
                bench_label = "Single Judge"
            
            bench_distribution[bench_label] = bench_distribution.get(bench_label, 0) + 1

            # Extract year if possible
            try:
                yr = int(auth.judgment_date[:4])
                years.append(yr)
            except Exception:
                yr = 2022

            # Citator treatment
            cv = cv_map.get(auth.id)
            treatment_txt = cv.treatment_history[0].treatment if (cv and cv.treatment_history) else auth.status_summary

            # Legal status (independent of disposition)
            legal_status_str = "CURRENT_GOOD_LAW" if auth.is_good_law else "OVERRULED_PRECEDENT"

            # Lookup authentic posture and disposition
            # CRITICAL SAFEGUARD: Never infer disposition from is_good_law
            meta = AUTHENTIC_PRECEDENT_METADATA.get(auth.standard_citation)
            if meta:
                posture = meta["procedural_posture"]
                disposition = meta["actual_disposition"]
                provenance = meta["disposition_provenance"]
            else:
                posture = "Procedural posture details not indexed in curated corpus"
                disposition = "Outcome data not available in curated corpus"
                provenance = "Not Indexed in Curated Corpus"

            item = PrecedentDispositionItem(
                case_title=auth.title,
                standard_citation=auth.standard_citation,
                court=auth.court,
                year=yr,
                bench_strength=auth.bench_strength or 2,
                legal_status=legal_status_str,
                treatment_summary=treatment_txt,
                procedural_posture=posture,
                actual_disposition=disposition,
                disposition_provenance=provenance,
                ratio_summary=auth.ratio_extract,
                is_active_law=auth.is_good_law,
            )

            if auth.is_good_law:
                active_patterns.append(item)
            else:
                overruled_patterns.append(item)

        temporal_span = f"{min(years)} – {max(years)}" if years else "2001 – 2024"

        # Determine legal regime context
        lead_auth = meaningful_authorities[0]
        meta_lead = AUTHENTIC_PRECEDENT_METADATA.get(lead_auth.standard_citation, {})
        regime_period = meta_lead.get("legal_regime", "Commercial Courts Benchmark Corpus")

        if overruled_patterns:
            regime_status = "Historical Overruled Precedents Present (Separated by Regime Guard)"
        else:
            regime_status = "Settled Governing Precedent Regime"

        controlling_doctrine = lead_auth.ratio_extract

        return HistoricalPatternAnalysisDTO(
            query_issue=query[:120],
            comparable_authorities_count=len(meaningful_authorities),
            temporal_span=temporal_span,
            courts_represented=sorted(list(courts_set)),
            bench_strength_breakdown=bench_distribution,
            active_precedent_patterns=active_patterns,
            overruled_precedent_patterns=overruled_patterns,
            controlling_doctrine_summary=controlling_doctrine,
            legal_regime_period=regime_period,
            active_regime_status=regime_status,
        )
