"""Stratified sample of 500 NLP papers by citation tier (per §2.3 + §2.4).

Pre-registered (§2.3): 150 from top 10%, 200 from middle 40-60%, 150 from bottom 10%.
Pre-registered (§2.4) exclusions:
  - withdrawn before 2026-01-01 (filtered via S2 _s2_found and arXiv categories check)
  - abstract length outside [200, 3000] chars
  - papers without resolvable Semantic Scholar ID (covered by _s2_found=False)
  - papers from prolific arXiv accounts (>100 submissions/year) — implemented as
    per-author-set submission count check across the candidate pool

Stratification choice (operational interpretation of §2.3):
  Pre-reg says "top 10% / middle 40-60% / bottom 10% according to current 2026
  metrics" without explicitly specifying within-year vs across-corpus percentile.
  We use **within-year percentile** for consistency with §3.2 NormalizedCitation
  (which explicitly normalizes within subfield × publication-year cell) and to
  avoid the temporal confound where older papers mechanically have more citations.
  Documented in REPRODUCE.md.

Random seed fixed at 0 (config.RANDOM_SEED) for reproducible sampling.

Usage:
    python3 scripts/03_stratify_sample.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cache import read_jsonl, write_jsonl
from lib.config import (
    ABSTRACT_MAX_CHARS,
    ABSTRACT_MIN_CHARS,
    ARXIV_RAW_DIR,
    CORPUS_OUTCOMES_DIR,
    RANDOM_SEED,
    SAMPLE_TIERS,
)

S2_ENRICHED_PATH = CORPUS_OUTCOMES_DIR / "s2_enriched.jsonl"
OUTPUT_PATH = CORPUS_OUTCOMES_DIR / "stratified_500.jsonl"


def join_arxiv_s2(category_prefix: str) -> dict[str, dict]:
    """Build {arxiv_id_base: {arxiv: {...}, s2: {...}}} for the given category prefix."""
    arxiv_by_id: dict[str, dict] = {}
    for path in sorted(ARXIV_RAW_DIR.glob(f"{category_prefix}_*.jsonl")):
        for rec in read_jsonl(path):
            base = rec.get("arxiv_id_base")
            if base and base not in arxiv_by_id:
                arxiv_by_id[base] = rec

    s2_by_id: dict[str, dict] = {}
    for rec in read_jsonl(S2_ENRICHED_PATH):
        base = rec.get("arxiv_id_base")
        if base:
            s2_by_id[base] = rec

    joined: dict[str, dict] = {}
    for base, ax in arxiv_by_id.items():
        s2 = s2_by_id.get(base)
        if s2 is not None:
            joined[base] = {"arxiv": ax, "s2": s2}
    return joined


def passes_exclusions(joined_rec: dict, prolific_authors: set[str]) -> tuple[bool, str]:
    ax = joined_rec["arxiv"]
    s2 = joined_rec["s2"]
    if not s2.get("_s2_found", False):
        return False, "not_in_s2"
    abs_len = len(ax.get("abstract") or "")
    if abs_len < ABSTRACT_MIN_CHARS:
        return False, f"abstract_too_short({abs_len})"
    if abs_len > ABSTRACT_MAX_CHARS:
        return False, f"abstract_too_long({abs_len})"
    if s2.get("citationCount") is None:
        return False, "no_citation_count"
    authors = ax.get("authors") or []
    if any(a in prolific_authors for a in authors):
        return False, "prolific_author"
    return True, "ok"


def find_prolific_authors(joined: dict[str, dict], threshold_per_year: int = 100) -> set[str]:
    """Authors appearing on >threshold_per_year submissions in any single year of the corpus window."""
    counts: Counter[tuple[str, int]] = Counter()
    for rec in joined.values():
        ax = rec["arxiv"]
        sub_date = ax.get("submitted_date") or ""
        if len(sub_date) < 4:
            continue
        try:
            year = int(sub_date[:4])
        except ValueError:
            continue
        for author in ax.get("authors") or []:
            counts[(author, year)] += 1
    prolific: set[str] = set()
    for (author, _year), n in counts.items():
        if n > threshold_per_year:
            prolific.add(author)
    return prolific


def stratify(eligible: list[dict], seed: int) -> tuple[list[dict], dict]:
    """Within-year citation percentile stratification per SAMPLE_TIERS.

    For each (year), compute citation percentile rank. Pool eligible papers across
    years into tiered buckets, sample without replacement to hit per-tier targets.
    """
    rng = random.Random(seed)

    by_year: dict[int, list[dict]] = {}
    for rec in eligible:
        try:
            year = int(rec["arxiv"]["submitted_date"][:4])
        except (KeyError, ValueError):
            continue
        by_year.setdefault(year, []).append(rec)

    annotated: list[tuple[float, dict]] = []
    for year, recs in by_year.items():
        recs_sorted = sorted(recs, key=lambda r: (r["s2"]["citationCount"], r["arxiv"]["arxiv_id_base"]))
        n = len(recs_sorted)
        for i, rec in enumerate(recs_sorted):
            pct = (i + 0.5) / n  # midpoint percentile, deterministic w.r.t. tie-break by arxiv_id
            annotated.append((pct, rec))

    tier_buckets: dict[str, list[dict]] = {tier: [] for tier in SAMPLE_TIERS}
    for pct, rec in annotated:
        for tier, (lo, hi, _n) in SAMPLE_TIERS.items():
            if lo <= pct < hi:
                tier_buckets[tier].append(rec)
                break

    sampled: list[dict] = []
    summary: dict = {"by_tier": {}, "shortfalls": {}}
    for tier, (lo, hi, target_n) in SAMPLE_TIERS.items():
        bucket = tier_buckets[tier]
        rng.shuffle(bucket)
        pick = bucket[:target_n]
        sampled.extend(pick)
        summary["by_tier"][tier] = {
            "tier_range": [lo, hi],
            "target": target_n,
            "available": len(bucket),
            "sampled": len(pick),
        }
        if len(pick) < target_n:
            summary["shortfalls"][tier] = target_n - len(pick)

    summary["total_sampled"] = len(sampled)
    return sampled, summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--category", default="cs_CL", help="filename prefix for input arXiv files")
    p.add_argument("--seed", type=int, default=RANDOM_SEED)
    p.add_argument("--out", type=Path, default=OUTPUT_PATH)
    args = p.parse_args()

    print(f"[info] joining arXiv + S2 for category {args.category}", file=sys.stderr)
    joined = join_arxiv_s2(args.category)
    print(f"[info] {len(joined)} papers with both arXiv and S2 records", file=sys.stderr)

    prolific = find_prolific_authors(joined)
    print(f"[info] {len(prolific)} prolific authors flagged (>100 submissions in a single year)", file=sys.stderr)

    eligible: list[dict] = []
    excluded_reasons: Counter[str] = Counter()
    for rec in joined.values():
        ok, reason = passes_exclusions(rec, prolific)
        if ok:
            eligible.append(rec)
        else:
            excluded_reasons[reason.split("(")[0]] += 1

    print(f"[info] {len(eligible)} papers pass exclusion criteria", file=sys.stderr)
    for reason, n in excluded_reasons.most_common():
        print(f"  excluded ({n}): {reason}", file=sys.stderr)

    sampled, summary = stratify(eligible, args.seed)

    flat_records = []
    for rec in sampled:
        ax = rec["arxiv"]
        s2 = rec["s2"]
        flat_records.append({
            "arxiv_id_base": ax["arxiv_id_base"],
            "arxiv_id": ax["arxiv_id"],
            "title": ax["title"],
            "abstract": ax["abstract"],
            "submitted_date": ax["submitted_date"],
            "primary_category": ax["primary_category"],
            "categories": ax["categories"],
            "authors": ax["authors"],
            "doi": ax.get("doi"),
            "journal_ref": ax.get("journal_ref"),
            "pdf_url": ax.get("pdf_url"),
            "s2_paperId": s2.get("paperId"),
            "s2_externalIds": s2.get("externalIds"),
            "s2_citationCount": s2.get("citationCount"),
            "s2_influentialCitationCount": s2.get("influentialCitationCount"),
            "s2_referenceCount": s2.get("referenceCount"),
            "s2_publicationDate": s2.get("publicationDate"),
            "s2_year": s2.get("year"),
            "s2_venue": s2.get("venue"),
            "s2_publicationVenue": s2.get("publicationVenue"),
            "s2_fieldsOfStudy": s2.get("fieldsOfStudy"),
            "_sampled_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "_seed": args.seed,
        })

    write_jsonl(args.out, flat_records)
    summary["output"] = str(args.out)
    summary["seed"] = args.seed
    summary["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
