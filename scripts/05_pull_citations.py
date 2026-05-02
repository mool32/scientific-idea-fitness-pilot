"""Pull all citations for the stratified 500 with intents and citing-paper text.

Per pre-reg §3.2: MethodReuseSignal needs citation intents; ReplicationSignal
Track A needs citing-paper titles + abstracts for regex matching.

S2 batch endpoint does not support nested field expansion for citations
(verified empirically — returns 400 on `citations.intents` etc.). So we use
the per-paper /paper/{id}/citations endpoint with offset pagination, one
target at a time, rate-limited per S2Client default (1.05s between requests).

Estimate for 500 papers: ~500-700 requests (most papers fit in one page of
1000), ~10-15 minutes wall time without API key.

Output: one JSONL record per target paper with all citations as a list.
Resume-safe (skips targets already pulled).

Usage:
    python3 scripts/05_pull_citations.py
    python3 scripts/05_pull_citations.py --max-papers 5  # smoke test
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cache import append_jsonl, existing_ids, read_jsonl
from lib.config import CORPUS_OUTCOMES_DIR, S2_API_BASE
from lib.s2_client import S2Client, S2Error

INPUT_PATH = CORPUS_OUTCOMES_DIR / "stratified_500.jsonl"
OUTPUT_PATH = CORPUS_OUTCOMES_DIR / "citations_for_500.jsonl"

CITATION_FIELDS = "intents,contexts,citingPaper.paperId,citingPaper.title,citingPaper.abstract,citingPaper.year,citingPaper.externalIds"

PAGE_SIZE = 1000


def fetch_all_citations(client: S2Client, paper_id: str) -> tuple[list[dict], str]:
    """Page through all citations for one paper. Returns (citations_list, status)."""
    citations: list[dict] = []
    offset = 0
    backoff = 5.0
    while True:
        url = f"{S2_API_BASE}/paper/{paper_id}/citations?fields={CITATION_FIELDS}&offset={offset}&limit={PAGE_SIZE}"
        for attempt in range(client.max_retries):
            client._wait()
            headers = {"User-Agent": "scientific-idea-fitness-pilot/0.1 (research)"}
            if client.api_key:
                headers["x-api-key"] = client.api_key
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    client._last_request_time = time.monotonic()
                    body = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                client._last_request_time = time.monotonic()
                if e.code == 429:
                    print(f"  [retry] 429 at offset {offset} (attempt {attempt + 1}), sleeping {backoff:.0f}s", file=sys.stderr, flush=True)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 120)
                    continue
                if e.code == 404:
                    return [], "not_found"
                try:
                    err_body = e.read().decode("utf-8", errors="replace")[:300]
                except Exception:
                    err_body = ""
                return citations, f"http_{e.code}_{err_body}"
            except (urllib.error.URLError, TimeoutError) as e:
                client._last_request_time = time.monotonic()
                print(f"  [retry] network error at offset {offset}: {e}, sleeping {backoff:.0f}s", file=sys.stderr, flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 2, 120)
        else:
            return citations, f"max_retries_at_offset_{offset}"

        page = body.get("data") or []
        if not page:
            break
        citations.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += len(page)
        backoff = 5.0  # reset backoff after success

    return citations, "ok"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="input", type=Path, default=INPUT_PATH)
    p.add_argument("--out", type=Path, default=OUTPUT_PATH)
    p.add_argument("--max-papers", type=int, default=None, help="cap for smoke tests")
    args = p.parse_args()

    targets = list(read_jsonl(args.input))
    if not targets:
        print(f"[error] no records in {args.input}", file=sys.stderr)
        return 1

    already = existing_ids(args.out, "target_arxiv_id_base") if args.out.exists() else set()
    pending = [r for r in targets if r["s2_paperId"] and r["arxiv_id_base"] not in already]
    if args.max_papers is not None:
        pending = pending[: args.max_papers]

    print(f"[info] {len(targets)} targets total; {len(already)} already pulled; {len(pending)} pending", file=sys.stderr)

    if not pending:
        print(json.dumps({"status": "nothing_to_do", "already_done": len(already)}))
        return 0

    client = S2Client()
    pulled_at = dt.datetime.now(dt.timezone.utc).isoformat()
    n_done = 0
    n_pages = 0

    for i, target_rec in enumerate(pending, start=1):
        target_id = target_rec["s2_paperId"]
        target_arxiv = target_rec["arxiv_id_base"]
        target_cite_count = target_rec.get("s2_citationCount") or 0

        try:
            citations, status = fetch_all_citations(client, target_id)
        except S2Error as e:
            citations, status = [], f"s2error_{e}"

        # Approximate page count from citation count (for progress reporting only)
        n_pages += max(1, (len(citations) + PAGE_SIZE - 1) // PAGE_SIZE)

        out_record = {
            "target_paperId": target_id,
            "target_arxiv_id_base": target_arxiv,
            "_status": status,
            "_pulled_at": pulled_at,
            "_citation_count_reported": target_cite_count,
            "_citations_pulled": len(citations),
            "citations": citations,
        }
        append_jsonl(args.out, [out_record])
        n_done += 1
        if i % 25 == 0 or i == len(pending):
            print(f"[progress] {i}/{len(pending)} pulled (status={status}, citations={len(citations)})", file=sys.stderr, flush=True)

    summary = {
        "input": str(args.input),
        "output": str(args.out),
        "newly_pulled": n_done,
        "approx_pages": n_pages,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
