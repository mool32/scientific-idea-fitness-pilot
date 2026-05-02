"""Opus V2 inference per pre-reg v1.2 §4.4 frontier-model arm (generation protocol).

For each blinded paper, sends V2 prompt to claude-opus-4-7 via Anthropic API,
parses the four-dimension integer ratings, writes one record per paper with
the parsed scores plus raw response text for audit.

Resume-safe: skips blind_ids already in output JSONL.

Inference parameters per pre-reg §4.3:
- temperature 0.0
- max_tokens 400 (V2 generation budget)
- single sample, no resampling

Score extraction per pre-reg §4.4:
- V2: weighted average of (a, b, c, d) with weights (0.25, 0.25, 0.25, 0.25);
  retain (d) alone as primary score
- Lenient regex: extract first 1-10 integer in expected position per dimension
- Outputs that fail to parse → "_parsed_status": "unparseable" (per §4.4)

Requires: ANTHROPIC_API_KEY environment variable.

Usage:
    python3 scripts/07_pull_opus_v2.py --max-papers 5  # smoke test
    python3 scripts/07_pull_opus_v2.py                 # full Pilot 1A (paused per moratorium)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import anthropic

from lib.cache import append_jsonl, existing_ids, read_jsonl
from lib.config import CORPUS_BLIND_DIR, PREDICTIONS_DIR

INPUT_PATH = CORPUS_BLIND_DIR / "stratified_500_blind.jsonl"
OUTPUT_PATH = PREDICTIONS_DIR / "opus_v2_predictions.jsonl"

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

MODEL = "claude-opus-4-7"
TEMPERATURE = 0.0
MAX_TOKENS = 400

# Lenient parsers for V2 output. Looks for "(a) ... NUMBER" patterns where
# NUMBER is 1-10 (capturing 10 explicitly to handle two-digit case). Justification
# text between dimensions is ignored.
DIM_PATTERNS = {
    "a": re.compile(r"\(?a\)?[^0-9]*?(10|[1-9])(?!\d)", re.IGNORECASE | re.DOTALL),
    "b": re.compile(r"\(?b\)?[^0-9]*?(10|[1-9])(?!\d)", re.IGNORECASE | re.DOTALL),
    "c": re.compile(r"\(?c\)?[^0-9]*?(10|[1-9])(?!\d)", re.IGNORECASE | re.DOTALL),
    "d": re.compile(r"\(?d\)?[^0-9]*?(10|[1-9])(?!\d)", re.IGNORECASE | re.DOTALL),
}


def load_prompt_files() -> tuple[str, str]:
    system = (PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8").strip()
    v2 = (PROMPTS_DIR / "v2.txt").read_text(encoding="utf-8").strip()
    return system, v2


def build_user_message(title: str, abstract: str, v2_prompt: str) -> str:
    return f"Title: {title}\n\nAbstract: {abstract}\n\n{v2_prompt}"


def parse_v2_output(text: str) -> dict[str, int | str]:
    """Extract integer ratings 1-10 for dimensions a, b, c, d from raw output.

    Per pre-reg §4.4: "lenient regex (extracting first 1-10 integer in expected
    position)". Treats output as unparseable if any dimension is missing.
    """
    parsed: dict[str, int | str] = {}
    for dim, pat in DIM_PATTERNS.items():
        m = pat.search(text)
        if m:
            try:
                parsed[dim] = int(m.group(1))
            except ValueError:
                parsed[dim] = "PARSE_ERROR"
        else:
            parsed[dim] = "MISSING"
    return parsed


def opus_call(client: anthropic.Anthropic, system: str, user: str) -> dict:
    backoff = 4.0
    last_err: Exception | None = None
    for attempt in range(6):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in resp.content if hasattr(b, "text"))
            return {
                "ok": True,
                "text": text,
                "stop_reason": resp.stop_reason,
                "usage": {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                },
            }
        except (anthropic.RateLimitError, anthropic.APIStatusError) as e:
            last_err = e
            time.sleep(backoff)
            backoff = min(backoff * 2, 120)
    return {"ok": False, "error": str(last_err)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="input", type=Path, default=INPUT_PATH)
    p.add_argument("--out", type=Path, default=OUTPUT_PATH)
    p.add_argument("--max-papers", type=int, default=None, help="cap for smoke tests")
    args = p.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[error] ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 2

    system, v2 = load_prompt_files()
    print(f"[info] system prompt loaded ({len(system)} chars), V2 prompt loaded ({len(v2)} chars)", file=sys.stderr)

    targets = list(read_jsonl(args.input))
    already = existing_ids(args.out, "blind_id") if args.out.exists() else set()
    pending = [r for r in targets if r["blind_id"] not in already]
    if args.max_papers is not None:
        pending = pending[: args.max_papers]

    print(f"[info] {len(targets)} blinded targets; {len(already)} already done; {len(pending)} pending", file=sys.stderr)

    if not pending:
        print(json.dumps({"status": "nothing_to_do", "already_done": len(already)}))
        return 0

    client = anthropic.Anthropic()
    pulled_at = dt.datetime.now(dt.timezone.utc).isoformat()
    n_done = 0
    n_unparseable = 0
    total_input_tok = 0
    total_output_tok = 0

    args.out.parent.mkdir(parents=True, exist_ok=True)

    for i, rec in enumerate(pending, start=1):
        user_msg = build_user_message(rec["title"], rec["abstract"], v2)
        result = opus_call(client, system, user_msg)
        if not result["ok"]:
            row = {
                "blind_id": rec["blind_id"],
                "_status": "api_error",
                "_error": result.get("error"),
                "_pulled_at": pulled_at,
            }
            append_jsonl(args.out, [row])
            n_done += 1
            continue

        parsed = parse_v2_output(result["text"])
        unparseable = any(v in ("MISSING", "PARSE_ERROR") for v in parsed.values())
        if unparseable:
            n_unparseable += 1

        score_d = parsed.get("d") if isinstance(parsed.get("d"), int) else None
        score_avg = (
            sum(v for v in parsed.values() if isinstance(v, int)) / 4
            if all(isinstance(v, int) for v in parsed.values())
            else None
        )

        row = {
            "blind_id": rec["blind_id"],
            "_status": "ok",
            "_pulled_at": pulled_at,
            "_unparseable": unparseable,
            "model": MODEL,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "raw_text": result["text"],
            "stop_reason": result.get("stop_reason"),
            "parsed_a": parsed.get("a"),
            "parsed_b": parsed.get("b"),
            "parsed_c": parsed.get("c"),
            "parsed_d": parsed.get("d"),
            "score_v2_overall": score_d,  # primary, per §4.4
            "score_v2_average": score_avg,  # secondary, weighted average
            "input_tokens": result.get("usage", {}).get("input_tokens"),
            "output_tokens": result.get("usage", {}).get("output_tokens"),
        }
        append_jsonl(args.out, [row])
        total_input_tok += result.get("usage", {}).get("input_tokens", 0) or 0
        total_output_tok += result.get("usage", {}).get("output_tokens", 0) or 0
        n_done += 1
        if i % 25 == 0 or i == len(pending):
            print(f"[progress] {i}/{len(pending)} done (unparseable={n_unparseable})", file=sys.stderr, flush=True)

    summary = {
        "input": str(args.input),
        "output": str(args.out),
        "model": MODEL,
        "newly_done": n_done,
        "unparseable_count": n_unparseable,
        "total_input_tokens": total_input_tok,
        "total_output_tokens": total_output_tok,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
