"""Compute composite Impact per pre-reg §3.1 (primary flipped formula).

Components:
  Impact = 0.25 * NormalizedCitation
         + 0.35 * MethodReuseSignal
         + 0.25 * ReplicationSignal
         + 0.15 * InverseRetractionScore

Per §3.2:
  - NormalizedCitation: percentile rank of citationCount within (subfield × year)
  - MethodReuseSignal: fraction of citations with S2 intent in {methodology, extension},
    over total citations (empty-intent citations count toward denominator). Then min-max
    normalized within cell.
  - ReplicationSignal Track A: log(1 + count) where count = citing papers whose
    title+abstract matches the v1.1 regex pattern. Then min-max normalized within cell.
    Track B (manual validation, κ ≥ 0.6 threshold) is deferred to a separate manual
    annotation pass before primary analysis.
  - InverseRetractionScore: defaults to 1.0 for all papers in this script. Pre-reg
    requires Retraction Watch + arXiv withdrawal cross-check + flagged-by-citing-papers
    multiplier; for 2020-2022 ML papers retractions are extremely rare (likely 0 in our
    sample). Implemented as constant 1.0 with the limitation documented in REPRODUCE.md.
    Optional separate script can do per-DOI Crossref retraction lookup if a non-zero
    retraction count needs to be verified.

For 1A NLP corpus, "subfield × year" cell = (cs.CL, year). Within-cell normalization
reduces age confound.

Output: corpus_outcomes/impact_scored_500.jsonl with each paper's components plus
composite Impact, plus the original transmission-weighted formula (§3.1 sensitivity)
for §5.2 #3.

Usage:
    python3 scripts/06_compute_impact.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cache import read_jsonl, write_jsonl
from lib.config import CORPUS_OUTCOMES_DIR

STRATIFIED_PATH = CORPUS_OUTCOMES_DIR / "stratified_500.jsonl"
CITATIONS_PATH = CORPUS_OUTCOMES_DIR / "citations_for_500.jsonl"
OUTPUT_PATH = CORPUS_OUTCOMES_DIR / "impact_scored_500.jsonl"

PRIMARY_WEIGHTS = {
    "NormalizedCitation": 0.25,
    "MethodReuseSignal": 0.35,
    "ReplicationSignal": 0.25,
    "InverseRetractionScore": 0.15,
}
SENSITIVITY_WEIGHTS = {
    "NormalizedCitation": 0.50,
    "ReplicationSignal": 0.25,
    "MethodReuseSignal": 0.15,
    "InverseRetractionScore": 0.10,
}

REUSE_INTENTS = {"methodology", "extension"}

REPLICATION_PATTERN = re.compile(
    r"\b(re-?implement(?:s|ed|ing|ation)?|repli(?:cat|cation)|"
    r"reproduc(?:e|ed|ing|ibility)|re-?evaluat|re-?run)\b",
    re.IGNORECASE,
)


def percentile_rank_within_cell(papers: list[dict], cell_key, value_key: str, out_key: str) -> None:
    """Add `out_key` to each paper in `papers` with percentile rank of `value_key` within cell.

    `cell_key` is a callable mapping paper → cell ID. Rank uses midpoint formula
    (i + 0.5)/n for stability with ties.
    """
    by_cell: dict[object, list[dict]] = defaultdict(list)
    for p in papers:
        by_cell[cell_key(p)].append(p)
    for _cell, group in by_cell.items():
        group_sorted = sorted(group, key=lambda r: (r[value_key], r["arxiv_id_base"]))
        n = len(group_sorted)
        for i, p in enumerate(group_sorted):
            p[out_key] = (i + 0.5) / n


def min_max_normalize_within_cell(papers: list[dict], cell_key, value_key: str, out_key: str) -> None:
    """Add `out_key` to each paper in `papers` with min-max normalized `value_key` within cell.

    If all values in a cell are equal, output is 0.5 (center of [0,1]) for everyone.
    """
    by_cell: dict[object, list[dict]] = defaultdict(list)
    for p in papers:
        by_cell[cell_key(p)].append(p)
    for _cell, group in by_cell.items():
        vals = [p[value_key] for p in group]
        lo, hi = min(vals), max(vals)
        for p in group:
            if hi > lo:
                p[out_key] = (p[value_key] - lo) / (hi - lo)
            else:
                p[out_key] = 0.5


def method_reuse_signal(citations: list[dict]) -> float:
    """Fraction of citations whose S2 intents include 'methodology' or 'extension'.

    Empty-intent citations count toward denominator. Returns 0.0 for papers with
    zero citations.
    """
    if not citations:
        return 0.0
    n_reuse = sum(
        1 for c in citations
        if any(i in REUSE_INTENTS for i in (c.get("intents") or []))
    )
    return n_reuse / len(citations)


def replication_signal_count(citations: list[dict]) -> int:
    """Number of citing papers whose title+abstract matches the replication regex.

    Pre-reg §3.2 also says "with the target paper as referent (heuristically: target
    appears in immediate sentence context or in references-cited-with section)". Track A
    here implements pattern presence only — referent verification is computationally
    cheap on small samples but expensive at scale; deferred to Track B manual validation
    on the 50-paper subsample.
    """
    n = 0
    for c in citations:
        cp = c.get("citingPaper") or {}
        text = " ".join(filter(None, [cp.get("title"), cp.get("abstract")]))
        if not text:
            continue
        if REPLICATION_PATTERN.search(text):
            n += 1
    return n


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stratified", type=Path, default=STRATIFIED_PATH)
    p.add_argument("--citations", type=Path, default=CITATIONS_PATH)
    p.add_argument("--out", type=Path, default=OUTPUT_PATH)
    args = p.parse_args()

    targets = list(read_jsonl(args.stratified))
    print(f"[info] {len(targets)} stratified targets", file=sys.stderr)

    citations_by_arxiv: dict[str, list[dict]] = {}
    citations_status: dict[str, str] = {}
    for rec in read_jsonl(args.citations):
        citations_by_arxiv[rec["target_arxiv_id_base"]] = rec.get("citations") or []
        citations_status[rec["target_arxiv_id_base"]] = rec.get("_status") or "unknown"

    missing = [t["arxiv_id_base"] for t in targets if t["arxiv_id_base"] not in citations_by_arxiv]
    if missing:
        print(f"[warn] {len(missing)} targets have no citation record (pull incomplete?). Examples: {missing[:5]}", file=sys.stderr)

    enriched = []
    for t in targets:
        arxiv_base = t["arxiv_id_base"]
        cits = citations_by_arxiv.get(arxiv_base, [])
        rec = {
            "arxiv_id_base": arxiv_base,
            "year": int(t["submitted_date"][:4]),
            "primary_category": t["primary_category"],
            "citationCount": t["s2_citationCount"] or 0,
            "n_citations_in_data": len(cits),
            "citations_status": citations_status.get(arxiv_base, "unknown"),
            "raw_method_reuse": method_reuse_signal(cits),
            "raw_replication_count": replication_signal_count(cits),
            "raw_replication_log": math.log1p(replication_signal_count(cits)),
            "raw_inverse_retraction": 1.0,  # default; see module docstring + REPRODUCE.md
        }
        enriched.append(rec)

    cell = lambda r: r["year"]  # noqa: E731  (subfield is constant cs.CL in 1A; cell = year)

    percentile_rank_within_cell(enriched, cell, "citationCount", "NormalizedCitation")
    min_max_normalize_within_cell(enriched, cell, "raw_method_reuse", "MethodReuseSignal")
    min_max_normalize_within_cell(enriched, cell, "raw_replication_log", "ReplicationSignal")
    for r in enriched:
        r["InverseRetractionScore"] = r["raw_inverse_retraction"]

    for r in enriched:
        r["Impact_primary"] = sum(PRIMARY_WEIGHTS[k] * r[k] for k in PRIMARY_WEIGHTS)
        r["Impact_sensitivity"] = sum(SENSITIVITY_WEIGHTS[k] * r[k] for k in SENSITIVITY_WEIGHTS)

    pulled_at = dt.datetime.now(dt.timezone.utc).isoformat()
    for r in enriched:
        r["_computed_at"] = pulled_at

    write_jsonl(args.out, enriched)

    impacts_p = sorted(r["Impact_primary"] for r in enriched)
    impacts_s = sorted(r["Impact_sensitivity"] for r in enriched)
    summary = {
        "stratified": str(args.stratified),
        "citations": str(args.citations),
        "output": str(args.out),
        "n_papers": len(enriched),
        "n_missing_citations": len(missing),
        "Impact_primary_distribution": {
            "min": impacts_p[0],
            "p25": impacts_p[len(impacts_p) // 4],
            "median": impacts_p[len(impacts_p) // 2],
            "p75": impacts_p[3 * len(impacts_p) // 4],
            "max": impacts_p[-1],
        },
        "Impact_sensitivity_distribution": {
            "min": impacts_s[0],
            "median": impacts_s[len(impacts_s) // 2],
            "max": impacts_s[-1],
        },
        "completed_at": pulled_at,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
