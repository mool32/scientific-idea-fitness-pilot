"""Blind the stratified 500-paper corpus per pre-reg §2.5.

Stripped fields (anything that could leak prestige, venue, year, or outcome):
  - arxiv_id, arxiv_id_base (encodes year via the YYMM.NNNNN convention)
  - submitted_date, updated_date
  - authors, doi, journal_ref, pdf_url
  - all s2_* fields (citation count, venue, publication date, paperId)
  - sampling metadata (_sampled_at, _seed)

Retained fields (technical content the LLM needs to assess the idea):
  - title
  - abstract
  - primary_category (constant within Pilot 1A, no leak)
  - categories (cross-listed cats may carry minor signal but kept for technical context)

Each blinded record gets a fresh opaque ID `blind_NNNN`. The mapping
`{blind_id: arxiv_id_base}` is written to `corpus_outcomes/blind_id_mapping.jsonl`,
NOT to `corpus_blind/`, so prediction-generating code that reads only
`corpus_blind/` cannot recover identity.

Acknowledged residual leakage: year/dates may appear inside abstracts (e.g.,
"we evaluate on the GLUE benchmark released in 2018") and cannot be safely
stripped without damaging semantic content. Author/affiliation leakage via
self-citations or distinctive writing style is also possible but is the kind
of signal the test specifically aims to bound. Reported in writeup.

Output ordering randomized with seed 0 (so blind_NNNN order does not encode
input ordering, which would otherwise correlate with sampling tier).

Usage:
    python3 scripts/04_blind_corpus.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cache import read_jsonl, write_jsonl
from lib.config import CORPUS_BLIND_DIR, CORPUS_OUTCOMES_DIR, RANDOM_SEED

INPUT_PATH = CORPUS_OUTCOMES_DIR / "stratified_500.jsonl"
BLIND_OUTPUT_PATH = CORPUS_BLIND_DIR / "stratified_500_blind.jsonl"
MAPPING_OUTPUT_PATH = CORPUS_OUTCOMES_DIR / "blind_id_mapping.jsonl"


def blind_record(rec: dict, blind_id: str) -> dict:
    return {
        "blind_id": blind_id,
        "title": rec["title"],
        "abstract": rec["abstract"],
        "primary_category": rec["primary_category"],
        "categories": rec.get("categories") or [],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="input", type=Path, default=INPUT_PATH)
    p.add_argument("--blind-out", type=Path, default=BLIND_OUTPUT_PATH)
    p.add_argument("--mapping-out", type=Path, default=MAPPING_OUTPUT_PATH)
    p.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = p.parse_args()

    records = list(read_jsonl(args.input))
    if not records:
        print(f"[error] no records in {args.input}", file=sys.stderr)
        return 1

    rng = random.Random(args.seed)
    rng.shuffle(records)

    blinded: list[dict] = []
    mapping: list[dict] = []
    pulled_at = dt.datetime.now(dt.timezone.utc).isoformat()
    for i, rec in enumerate(records, start=1):
        blind_id = f"blind_{i:04d}"
        blinded.append(blind_record(rec, blind_id))
        mapping.append({
            "blind_id": blind_id,
            "arxiv_id_base": rec["arxiv_id_base"],
            "_blinded_at": pulled_at,
            "_seed": args.seed,
        })

    write_jsonl(args.blind_out, blinded)
    write_jsonl(args.mapping_out, mapping)
    summary = {
        "input": str(args.input),
        "blind_out": str(args.blind_out),
        "mapping_out": str(args.mapping_out),
        "n_records": len(blinded),
        "seed": args.seed,
        "completed_at": pulled_at,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
