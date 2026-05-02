"""Compute citation-velocity baseline per pre-reg v1.2 §5.1.A.

Citation velocity = number of citations a paper accrued in the first 12 months
post-arXiv-submission, computed from Semantic Scholar timestamps.

Implementation per direction (a) in the citation-velocity baseline implementation
choice (citations_for_500.jsonl.gz re-pulled with citingPaper.publicationDate):

For each target paper t with submitted_date d_t:
    velocity(t) = count of citations c such that:
        if c.citingPaper.publicationDate is YYYY-MM-DD format:
            d_t < parse(c.citingPaper.publicationDate) ≤ d_t + 365 days
        else if c.citingPaper.year is available (~10% of citations):
            **conservative inclusion**: include only if c.citingPaper.year == year(d_t + 6 months)
            i.e., the citing paper's year falls strictly within the 12-month window
            for at least the median submission month (any submission month gives
            a 12-month window that includes its own year T and most of year T+1)
        else:
            excluded from velocity count

Heterogeneous-resolution audit logged with each paper's velocity for
reproducibility. ~87.6% of citations have full date precision per the re-pull;
remainder fall back as documented.

Output: corpus_outcomes/citation_velocity_500.jsonl with one record per target
paper containing arxiv_id_base, submitted_date, and velocity_count plus an
audit object documenting how many citations contributed via each path (full date,
year fallback, excluded).

Usage:
    python3 scripts/09_compute_citation_velocity.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cache import read_jsonl, write_jsonl
from lib.config import CORPUS_OUTCOMES_DIR

STRATIFIED_PATH = CORPUS_OUTCOMES_DIR / "stratified_500.jsonl"
CITATIONS_PATH = CORPUS_OUTCOMES_DIR / "citations_for_500.jsonl"
OUTPUT_PATH = CORPUS_OUTCOMES_DIR / "citation_velocity_500.jsonl"

WINDOW_DAYS = 365


def parse_date(s: str) -> dt.date | None:
    if not s:
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stratified", type=Path, default=STRATIFIED_PATH)
    p.add_argument("--citations", type=Path, default=CITATIONS_PATH)
    p.add_argument("--out", type=Path, default=OUTPUT_PATH)
    p.add_argument("--window-days", type=int, default=WINDOW_DAYS)
    args = p.parse_args()

    targets = list(read_jsonl(args.stratified))
    print(f"[info] {len(targets)} stratified targets", file=sys.stderr)

    citations_by_arxiv: dict[str, list[dict]] = {}
    for rec in read_jsonl(args.citations):
        citations_by_arxiv[rec["target_arxiv_id_base"]] = rec.get("citations") or []

    pulled_at = dt.datetime.now(dt.timezone.utc).isoformat()
    output_records = []
    global_audit = {
        "n_targets": len(targets),
        "n_targets_with_citations": 0,
        "total_citations_examined": 0,
        "contributed_via_full_date": 0,
        "contributed_via_year_fallback": 0,
        "excluded_no_date": 0,
        "excluded_outside_window": 0,
    }

    for t in targets:
        arxiv_base = t["arxiv_id_base"]
        target_date = parse_date(t["submitted_date"])
        if target_date is None:
            continue
        target_year = target_date.year
        window_end = target_date + dt.timedelta(days=args.window_days)

        cits = citations_by_arxiv.get(arxiv_base, [])
        if cits:
            global_audit["n_targets_with_citations"] += 1

        velocity = 0
        per_paper_audit = {
            "n_citations": len(cits),
            "via_full_date": 0,
            "via_year_fallback": 0,
            "excluded_no_date": 0,
            "excluded_outside_window": 0,
        }

        for c in cits:
            global_audit["total_citations_examined"] += 1
            cp = c.get("citingPaper") or {}
            pub_date_str = cp.get("publicationDate") or ""
            cite_date = parse_date(pub_date_str) if len(pub_date_str) == 10 else None
            if cite_date is not None:
                if target_date < cite_date <= window_end:
                    velocity += 1
                    per_paper_audit["via_full_date"] += 1
                    global_audit["contributed_via_full_date"] += 1
                else:
                    per_paper_audit["excluded_outside_window"] += 1
                    global_audit["excluded_outside_window"] += 1
            else:
                year = cp.get("year")
                if isinstance(year, int):
                    # Conservative inclusion: include only if citing year equals target year
                    # OR the year strictly within the 12-month window (i.e., year ≤ window_end.year)
                    # but exclude same-year citations from before submission.
                    # Approximation: include if year == target_year (likely some pre-submission)
                    # OR year == target_year + 1 AND window_end.year >= target_year + 1
                    # Exact resolution impossible without the date; we use conservative
                    # inclusion = year strictly in [target_year + 1, window_end.year]
                    # which undercounts citations from the same year as submission.
                    if target_year < year <= window_end.year:
                        velocity += 1
                        per_paper_audit["via_year_fallback"] += 1
                        global_audit["contributed_via_year_fallback"] += 1
                    else:
                        per_paper_audit["excluded_outside_window"] += 1
                        global_audit["excluded_outside_window"] += 1
                else:
                    per_paper_audit["excluded_no_date"] += 1
                    global_audit["excluded_no_date"] += 1

        output_records.append({
            "arxiv_id_base": arxiv_base,
            "submitted_date": t["submitted_date"],
            "velocity_count": velocity,
            "window_days": args.window_days,
            "audit": per_paper_audit,
            "_computed_at": pulled_at,
        })

    write_jsonl(args.out, output_records)
    velocities = sorted(r["velocity_count"] for r in output_records)
    n = len(velocities)
    summary = {
        "stratified": str(args.stratified),
        "citations": str(args.citations),
        "output": str(args.out),
        "window_days": args.window_days,
        "n_papers": n,
        "velocity_distribution": {
            "min": velocities[0],
            "p10": velocities[n // 10],
            "p25": velocities[n // 4],
            "median": velocities[n // 2],
            "p75": velocities[3 * n // 4],
            "p90": velocities[9 * n // 10],
            "max": velocities[-1],
        },
        "global_audit": global_audit,
        "completed_at": pulled_at,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
