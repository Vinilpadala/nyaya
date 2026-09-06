import os
import sys
import json
import time
from typing import List, Dict, Any

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.evaluation.dataset import BENCHMARK_DATASET
from app.evaluation.evaluator import LegalResearchEvaluator, BenchmarkCaseEvaluationResult

def run_full_evaluation():
    print("=================================================================")
    print("NYAYA AI — PHASE 3E: BENCHMARK EVALUATION & STRESS TEST RUNNER")
    print("=================================================================")
    print(f"Total Benchmark Test Cases: {len(BENCHMARK_DATASET)}")
    print("Clarification: Reporting measured metrics as technical retrieval measurements,")
    print("distinguishing corpus incompleteness from software defects, with no arbitrary pass/fail thresholds.")
    print("=================================================================\n")

    db = SessionLocal()
    evaluator = LegalResearchEvaluator(db)

    results: List[BenchmarkCaseEvaluationResult] = []
    
    for i, case in enumerate(BENCHMARK_DATASET, 1):
        print(f"[{i:02d}/{len(BENCHMARK_DATASET):02d}] Evaluating {case.case_id} ({case.category})...")
        print(f"     Query: \"{case.query}\"")
        res = evaluator.evaluate_case(case)
        results.append(res)
        print(f"     -> Ret: {res.retrieved_count} | Lead: {res.lead_authority_title[:45] if res.lead_authority_title else 'None'} | Score: {res.lead_authority_score} (Margin: {res.score_margin})")
        print(f"     -> Citator: {res.treatment_status} (GoodLaw={res.is_good_law}) | Uncertainty: {res.uncertainty_level} (Conf={res.confidence_score})")
        print(f"     -> Engine: {res.synthesis_engine} | Latency: {res.latency_ms:.1f}ms")
        if res.findings:
            for f in res.findings:
                print(f"     [! {f.severity}] [{f.category_type}] {f.description}")
        print()

    db.close()

    # -------------------------------------------------------------
    # Aggregate Metrics Calculation
    # -------------------------------------------------------------
    corpus_sufficient_cases = [r for r in results if r.case.expected_corpus_sufficient]
    corpus_insufficient_cases = [r for r in results if not r.case.expected_corpus_sufficient]

    # Hit Rates (on cases where authority exists in corpus)
    cases_with_expected_lead = [r for r in corpus_sufficient_cases if r.case.expected_primary_authority_title]
    n_expected = len(cases_with_expected_lead)
    
    hits_at_1 = sum(1 for r in cases_with_expected_lead if r.hit_at_1)
    hits_at_3 = sum(1 for r in cases_with_expected_lead if r.hit_at_3)
    hits_at_5 = sum(1 for r in cases_with_expected_lead if r.hit_at_5)

    hit_rate_1 = hits_at_1 / n_expected if n_expected else 0.0
    hit_rate_3 = hits_at_3 / n_expected if n_expected else 0.0
    hit_rate_5 = hits_at_5 / n_expected if n_expected else 0.0

    avg_recall_5 = (
        sum(r.recall_at_5 for r in cases_with_expected_lead) / n_expected if n_expected else 0.0
    )

    avg_latency = sum(r.latency_ms for r in results) / len(results) if results else 0.0
    min_latency = min(r.latency_ms for r in results) if results else 0.0
    max_latency = max(r.latency_ms for r in results) if results else 0.0

    lead_scores = [r.lead_authority_score for r in results if r.lead_authority_score > 0]
    avg_lead_score = sum(lead_scores) / len(lead_scores) if lead_scores else 0.0
    score_margins = [r.score_margin for r in results if r.score_margin > 0]
    avg_score_margin = sum(score_margins) / len(score_margins) if score_margins else 0.0

    # Collect all findings across severity levels
    all_findings = []
    for r in results:
        for f in r.findings:
            all_findings.append({"case_id": r.case.case_id, **f.model_dump()})

    critical_findings = [f for f in all_findings if f["severity"] == "CRITICAL"]
    high_findings = [f for f in all_findings if f["severity"] == "HIGH"]
    medium_findings = [f for f in all_findings if f["severity"] == "MEDIUM"]
    low_findings = [f for f in all_findings if f["severity"] == "LOW"]
    info_findings = [f for f in all_findings if f["severity"] == "INFORMATIONAL"]

    print("=================================================================")
    print("PHASE 3E EVALUATION SUMMARY & MEASURED TECHNICAL METRICS")
    print("=================================================================")
    print(f"Corpus-Sufficient Benchmark Cases: {len(corpus_sufficient_cases)}")
    print(f"Corpus-Insufficient / Boundary Cases: {len(corpus_insufficient_cases)}")
    print(f"HitRate@1 (Controlling Authority at Rank 1): {hit_rate_1:.1%} ({hits_at_1}/{n_expected})")
    print(f"HitRate@3 (Controlling Authority in Top 3):  {hit_rate_3:.1%} ({hits_at_3}/{n_expected})")
    print(f"HitRate@5 (Controlling Authority in Top 5):  {hit_rate_5:.1%} ({hits_at_5}/{n_expected})")
    print(f"Mean Recall@5 (Authorities in Corpus):        {avg_recall_5:.1%}")
    print(f"Average Lead BM25 Score:                      {avg_lead_score:.2f}")
    print(f"Average Score Margin (Rank 1 vs Rank 2):      {avg_score_margin:.2f}")
    print(f"Latency Profile: Avg={avg_latency:.1f}ms, Min={min_latency:.1f}ms, Max={max_latency:.1f}ms")
    print(f"Mandatory Disclaimers Verified Present:       {sum(1 for r in results if r.disclaimer_present)}/{len(results)}")
    print("\n--- FINDINGS SEVERITY BREAKDOWN ---")
    print(f"  CRITICAL (Security / Hallucinated Law / Data Breach): {len(critical_findings)}")
    print(f"  HIGH     (Retriever Index Defect / Citation Blind):   {len(high_findings)}")
    print(f"  MEDIUM   (Ranking Separation / Tight Score Margin):   {len(medium_findings)}")
    print(f"  LOW      (Formatting Discrepancy / Minor Calibration):{len(low_findings)}")
    print(f"  INFORMATIONAL (Expected Curated Corpus Boundary):     {len(info_findings)}")
    print("=================================================================\n")

    # Export machine-readable results
    export_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": {
            "total_cases": len(results),
            "corpus_sufficient_cases": len(corpus_sufficient_cases),
            "corpus_insufficient_cases": len(corpus_insufficient_cases),
            "hit_rate_at_1": hit_rate_1,
            "hit_rate_at_3": hit_rate_3,
            "hit_rate_at_5": hit_rate_5,
            "mean_recall_at_5": avg_recall_5,
            "avg_lead_score": avg_lead_score,
            "avg_score_margin": avg_score_margin,
            "avg_latency_ms": avg_latency,
            "min_latency_ms": min_latency,
            "max_latency_ms": max_latency,
        },
        "findings_count": {
            "CRITICAL": len(critical_findings),
            "HIGH": len(high_findings),
            "MEDIUM": len(medium_findings),
            "LOW": len(low_findings),
            "INFORMATIONAL": len(info_findings),
        },
        "findings": all_findings,
        "cases": [r.to_dict() for r in results],
    }

    out_file = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)
    print(f"Detailed evaluation metrics exported to: {out_file}")

if __name__ == "__main__":
    run_full_evaluation()
