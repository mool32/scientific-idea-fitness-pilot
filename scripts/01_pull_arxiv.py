"""Pull arXiv papers in a category over a date window. JSONL output, one file per month.

Per-month files keep individual outputs small enough to inspect manually and make
resume-after-interruption trivial — just skip months whose file already exists.

Usage:
    python3 scripts/01_pull_arxiv.py --category cs.CL --from 2020-01 --to 2022-12
    python3 scripts/01_pull_arxiv.py --category cs.CL --from 2020-01 --to 2020-01 --max-results 50  # smoke test
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.arxiv_client import ArxivClient
from lib.cache import write_jsonl
from lib.config import ARXIV_RAW_DIR


def month_iter(start: str, end: str):
    """Yield (year, month) pairs from start to end inclusive. Args in YYYY-MM."""
    y, m = (int(x) for x in start.split("-"))
    ey, em = (int(x) for x in end.split("-"))
    while (y, m) <= (ey, em):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def month_bounds(year: int, month: int) -> tuple[str, str]:
    first = dt.date(year, month, 1)
    if month == 12:
        last = dt.date(year, 12, 31)
    else:
        last = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
    return first.isoformat(), last.isoformat()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--category", required=True, help="arXiv category, e.g. cs.CL")
    p.add_argument("--from", dest="date_from", required=True, help="YYYY-MM start month inclusive")
    p.add_argument("--to", dest="date_to", required=True, help="YYYY-MM end month inclusive")
    p.add_argument("--max-results", type=int, default=None, help="cap per-month, for smoke tests")
    p.add_argument("--force", action="store_true", help="re-pull even if month file already exists")
    p.add_argument("--out-dir", type=Path, default=ARXIV_RAW_DIR, help="output dir for per-month JSONL")
    args = p.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    client = ArxivClient()

    total_papers = 0
    total_months = 0
    for year, month in month_iter(args.date_from, args.date_to):
        out_path = args.out_dir / f"{args.category.replace('.', '_')}_{year:04d}-{month:02d}.jsonl"
        if out_path.exists() and not args.force:
            n = sum(1 for _ in out_path.open())
            print(f"[skip] {out_path.name} exists ({n} records)", file=sys.stderr)
            total_papers += n
            total_months += 1
            continue

        date_from, date_to = month_bounds(year, month)
        print(f"[pull] {args.category} {date_from} → {date_to}", file=sys.stderr)
        t0 = time.monotonic()
        papers = list(client.search(
            category=args.category,
            date_from=date_from,
            date_to=date_to,
            max_results=args.max_results,
        ))
        elapsed = time.monotonic() - t0

        records = [{**p.to_dict(), "_pulled_at": dt.datetime.now(dt.timezone.utc).isoformat()} for p in papers]
        n_written = write_jsonl(out_path, records)
        total_papers += n_written
        total_months += 1
        print(f"[ok]   {out_path.name}: {n_written} records in {elapsed:.1f}s", file=sys.stderr)

    summary = {
        "category": args.category,
        "date_from": args.date_from,
        "date_to": args.date_to,
        "months": total_months,
        "papers": total_papers,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
