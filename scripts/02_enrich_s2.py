"""Enrich arXiv corpus with Semantic Scholar metadata for stratification.

Fields pulled (Phase 1, for stratification): citationCount, publicationDate,
externalIds, citationCount-derived metrics. Per-citation intent/context (needed
for MethodReuseSignal §3.2) deferred to a later script — this one only fetches
what's needed for impact-tier stratification.

Resume-safe: skips arxiv_ids already present in the output JSONL.

Set S2_API_KEY env var for authenticated rate (recommended for >1k papers).

Usage:
    python3 scripts/02_enrich_s2.py
    python3 scripts/02_enrich_s2.py --max-papers 50  # smoke test
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cache import append_jsonl, existing_ids, read_jsonl
from lib.config import ARXIV_RAW_DIR, CORPUS_OUTCOMES_DIR
from lib.s2_client import S2Client

S2_FIELDS = [
    "externalIds",
    "title",
    "publicationDate",
    "year",
    "citationCount",
    "referenceCount",
    "influentialCitationCount",
    "venue",
    "publicationVenue",
    "fieldsOfStudy",
]

OUTPUT_PATH = CORPUS_OUTCOMES_DIR / "s2_enriched.jsonl"


def collect_arxiv_ids(category_prefix: str) -> list[str]:
    """Walk corpus_outcomes/arxiv_raw/ for files matching the category prefix; collect arxiv_id_base."""
    ids: list[str] = []
    seen: set[str] = set()
    for path in sorted(ARXIV_RAW_DIR.glob(f"{category_prefix}_*.jsonl")):
        for rec in read_jsonl(path):
            base = rec.get("arxiv_id_base")
            if base and base not in seen:
                seen.add(base)
                ids.append(base)
    return ids


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--category", default="cs_CL", help="filename prefix for input files (e.g. cs_CL)")
    p.add_argument("--max-papers", type=int, default=None, help="cap for smoke tests")
    p.add_argument("--out", type=Path, default=OUTPUT_PATH)
    args = p.parse_args()

    all_ids = collect_arxiv_ids(args.category)
    if not all_ids:
        print(f"[error] no arXiv records found under {ARXIV_RAW_DIR} matching {args.category}_*", file=sys.stderr)
        return 1

    already_done = existing_ids(args.out, "arxiv_id_base") if args.out.exists() else set()
    pending = [i for i in all_ids if i not in already_done]
    if args.max_papers is not None:
        pending = pending[: args.max_papers]

    print(f"[info] {len(all_ids)} arXiv ids total; {len(already_done)} already enriched; {len(pending)} pending", file=sys.stderr)

    if not pending:
        print(json.dumps({"category": args.category, "already_done": len(already_done), "newly_enriched": 0}))
        return 0

    client = S2Client()
    s2_ids = [f"ARXIV:{i}" for i in pending]
    arxiv_by_s2 = dict(zip(s2_ids, pending))

    n_ok = 0
    n_missing = 0
    batch_size_log = 0
    pulled_at = dt.datetime.now(dt.timezone.utc).isoformat()
    buffer: list[dict] = []

    try:
        for sid, paper in client.batch_papers_chunked(s2_ids, S2_FIELDS):
            arxiv_base = arxiv_by_s2[sid]
            if paper is None:
                buffer.append({"arxiv_id_base": arxiv_base, "_s2_found": False, "_pulled_at": pulled_at})
                n_missing += 1
            else:
                buffer.append({
                    "arxiv_id_base": arxiv_base,
                    "_s2_found": True,
                    "_pulled_at": pulled_at,
                    **paper,
                })
                n_ok += 1
            batch_size_log += 1
            if batch_size_log >= 500:
                append_jsonl(args.out, buffer)
                buffer = []
                print(f"[progress] {n_ok + n_missing}/{len(pending)} processed (ok={n_ok}, missing={n_missing})", file=sys.stderr)
                batch_size_log = 0
    finally:
        if buffer:
            append_jsonl(args.out, buffer)

    summary = {
        "category": args.category,
        "newly_enriched": n_ok + n_missing,
        "found_in_s2": n_ok,
        "missing_from_s2": n_missing,
        "output": str(args.out),
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
