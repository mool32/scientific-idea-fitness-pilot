"""Pythia 6.9b-deduped V2 inference per pre-reg v1.2 §4.4 contamination-arm
(log-likelihood protocol).

Restricted to Pythia-eligible subset per pre-reg v1.2 §4.1: papers with arXiv v1
submission ≥ 2020-08-01 (papers temporally clean of direct Pile arXiv inclusion).

For each eligible blinded paper, computes log P(str(k) | prompt) for k ∈ {1..10}
at each V2 dimension prefix using the chain rule per the v1.2 §4.4 pseudocode.
Argmax-k → predicted rating per dimension. Score_v2_overall = predicted rating
on dimension (d) overall promise (mirrors §4.4 primary score for parity with
Opus arm).

Two execution modes (use whichever your environment supports):

  --mode local    : load EleutherAI/pythia-6.9b-deduped via transformers.
                    Requires ~14 GB RAM at fp16, ~28 GB at fp32. On 16 GB M1,
                    use 4-bit quantization via bitsandbytes (limited M1 support)
                    OR llama.cpp + GGUF Q4 conversion (recommended for M1).
                    For setup verification: use --mode local --model-name
                    EleutherAI/pythia-70m-deduped to test pipeline end-to-end
                    on a tiny model (same tokenizer family).

  --mode hf-endpoint : POST to a Hugging Face Inference Endpoint URL with
                      model loaded server-side. Requires HF_INFERENCE_URL env
                      var (the URL of your deployed endpoint) and HF_TOKEN.
                      Recommended production path per agent research:
                      A10G GPU, ~$1-2 for the Pythia-eligible subset
                      (~405 papers × 4 dimensions × 10 candidates = ~16k forward
                      passes).

Resume-safe: skips blind_ids already in output JSONL.

Pre-reg compliance:
- Frontier-arm uses different model (Opus); produced by 07_pull_opus_v2.py
- Pythia-eligible subset filter applied via blind_id_mapping.jsonl join
  (mapping is in corpus_outcomes/, NOT corpus_blind/, so prediction script
  reads only the blind_id list it should process; identity stays opaque)

Usage:
    # Pipeline verification with tiny model (no API needed):
    python3 scripts/08_pull_pythia_v2.py --mode local --model-name EleutherAI/pythia-70m-deduped --max-papers 5

    # Production with HF endpoint (paused per moratorium):
    HF_INFERENCE_URL=https://... HF_TOKEN=... python3 scripts/08_pull_pythia_v2.py --mode hf-endpoint
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cache import append_jsonl, existing_ids, read_jsonl
from lib.config import CORPUS_BLIND_DIR, CORPUS_OUTCOMES_DIR, PREDICTIONS_DIR, PYTHIA_ELIGIBLE_FROM

INPUT_PATH = CORPUS_BLIND_DIR / "stratified_500_blind.jsonl"
MAPPING_PATH = CORPUS_OUTCOMES_DIR / "blind_id_mapping.jsonl"
STRATIFIED_PATH = CORPUS_OUTCOMES_DIR / "stratified_500.jsonl"
OUTPUT_PATH = PREDICTIONS_DIR / "pythia_v2_predictions.jsonl"

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

DIMENSIONS = [
    ("a", "novelty"),
    ("b", "technical soundness"),
    ("c", "follow-up potential"),
    ("d", "overall promise"),
]


def load_prompt_files() -> tuple[str, str]:
    system = (PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8").strip()
    v2 = (PROMPTS_DIR / "v2.txt").read_text(encoding="utf-8").strip()
    return system, v2


def build_dimension_prefix(system: str, v2: str, title: str, abstract: str, dim_letter: str, dim_label: str) -> str:
    """Construct the prompt up to and including the dimension prefix per §4.4 pseudocode.

    Format: <system>\n\nTitle: ...\n\nAbstract: ...\n\n<v2 prompt>\n(<dim>) <label>:
    """
    return (
        f"{system}\n\n"
        f"Title: {title}\n\n"
        f"Abstract: {abstract}\n\n"
        f"{v2}\n"
        f"({dim_letter}) {dim_label}: "
    )


def get_eligible_blind_ids() -> set[str]:
    """Cross-join mapping with stratified to get blind_ids whose arxiv submitted_date >= PYTHIA_ELIGIBLE_FROM."""
    arxiv_to_date: dict[str, str] = {}
    for r in read_jsonl(STRATIFIED_PATH):
        arxiv_to_date[r["arxiv_id_base"]] = r["submitted_date"]
    eligible: set[str] = set()
    for r in read_jsonl(MAPPING_PATH):
        d = arxiv_to_date.get(r["arxiv_id_base"])
        if d and d >= PYTHIA_ELIGIBLE_FROM:
            eligible.add(r["blind_id"])
    return eligible


def score_local(model, tokenizer, prompt: str, device: str) -> dict[str, float]:
    from lib.pythia_score import score_dimension
    return score_dimension(model, tokenizer, prompt, device=device)


def score_hf_endpoint(prompt: str, candidates: tuple[str, ...]) -> dict[str, float]:
    """POST to HF Inference Endpoint that exposes log-prob computation.

    Default HF Inference Endpoints DO NOT expose per-token logprobs out of the
    box for causal-LM tasks — you need a custom handler.py in the endpoint
    deployment that implements the chain-rule scoring. Sample handler.py is
    documented in REPRODUCE.md under the "Pythia HF Endpoint setup" section.

    The endpoint contract this client expects:
        POST <HF_INFERENCE_URL>
        body: {"inputs": {"prompt": <str>, "candidates": [<str>, ...]}}
        returns: {"log_probs": {"<cand>": <float>, ...}}
    """
    import urllib.request
    url = os.environ["HF_INFERENCE_URL"]
    token = os.environ["HF_TOKEN"]
    body = json.dumps({"inputs": {"prompt": prompt, "candidates": list(candidates)}}).encode("utf-8")
    backoff = 4.0
    for attempt in range(6):
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "scientific-idea-fitness-pilot/0.1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read())
            if "log_probs" not in payload:
                raise RuntimeError(f"endpoint response missing log_probs: {payload}")
            return {k: float(v) for k, v in payload["log_probs"].items()}
        except Exception as e:
            if attempt < 5:
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue
            raise


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="input", type=Path, default=INPUT_PATH)
    p.add_argument("--out", type=Path, default=OUTPUT_PATH)
    p.add_argument("--mode", choices=["local", "hf-endpoint"], required=True)
    p.add_argument("--model-name", default="EleutherAI/pythia-6.9b-deduped",
                   help="HF model name; for setup verification can be pythia-70m-deduped")
    p.add_argument("--device", default="cpu", help="cpu / cuda / mps (local mode)")
    p.add_argument("--dtype", default="float32", choices=["float32", "float16", "bfloat16"])
    p.add_argument("--max-papers", type=int, default=None, help="cap for smoke tests")
    args = p.parse_args()

    targets = list(read_jsonl(args.input))
    eligible_ids = get_eligible_blind_ids()
    targets = [t for t in targets if t["blind_id"] in eligible_ids]
    print(f"[info] {len(targets)} Pythia-eligible blind_ids "
          f"(arxiv v1 ≥ {PYTHIA_ELIGIBLE_FROM})", file=sys.stderr)

    already = existing_ids(args.out, "blind_id") if args.out.exists() else set()
    pending = [t for t in targets if t["blind_id"] not in already]
    if args.max_papers is not None:
        pending = pending[: args.max_papers]
    print(f"[info] {len(already)} already done; {len(pending)} pending", file=sys.stderr)

    if not pending:
        print(json.dumps({"status": "nothing_to_do", "already_done": len(already)}))
        return 0

    system, v2 = load_prompt_files()

    model = None
    tokenizer = None
    if args.mode == "local":
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        dtype = {"float32": torch.float32, "float16": torch.float16, "bfloat16": torch.bfloat16}[args.dtype]
        print(f"[setup] loading {args.model_name} dtype={args.dtype} device={args.device}", file=sys.stderr)
        tokenizer = AutoTokenizer.from_pretrained(args.model_name)
        model = AutoModelForCausalLM.from_pretrained(args.model_name, dtype=dtype)
        model = model.to(args.device)
        model.eval()
    else:
        if not os.environ.get("HF_INFERENCE_URL") or not os.environ.get("HF_TOKEN"):
            print("[error] HF_INFERENCE_URL and HF_TOKEN required for hf-endpoint mode", file=sys.stderr)
            return 2

    candidates = tuple(str(i) for i in range(1, 11))
    pulled_at = dt.datetime.now(dt.timezone.utc).isoformat()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    n_done = 0

    for i, rec in enumerate(pending, start=1):
        per_dim_scores: dict[str, dict[str, float]] = {}
        per_dim_argmax: dict[str, int] = {}
        for dim_letter, dim_label in DIMENSIONS:
            prompt = build_dimension_prefix(system, v2, rec["title"], rec["abstract"], dim_letter, dim_label)
            if args.mode == "local":
                log_probs = score_local(model, tokenizer, prompt, args.device)
            else:
                log_probs = score_hf_endpoint(prompt, candidates)
            per_dim_scores[dim_letter] = log_probs
            per_dim_argmax[dim_letter] = int(max(log_probs.keys(), key=lambda k: log_probs[k]))

        score_d = per_dim_argmax["d"]
        score_avg = sum(per_dim_argmax.values()) / 4
        row = {
            "blind_id": rec["blind_id"],
            "_status": "ok",
            "_pulled_at": pulled_at,
            "model": args.model_name,
            "dtype": args.dtype if args.mode == "local" else "endpoint-dependent",
            "mode": args.mode,
            "parsed_a": per_dim_argmax["a"],
            "parsed_b": per_dim_argmax["b"],
            "parsed_c": per_dim_argmax["c"],
            "parsed_d": per_dim_argmax["d"],
            "score_v2_overall": score_d,
            "score_v2_average": score_avg,
            "log_probs_a": per_dim_scores["a"],
            "log_probs_b": per_dim_scores["b"],
            "log_probs_c": per_dim_scores["c"],
            "log_probs_d": per_dim_scores["d"],
        }
        append_jsonl(args.out, [row])
        n_done += 1
        if i % 25 == 0 or i == len(pending):
            print(f"[progress] {i}/{len(pending)} done", file=sys.stderr, flush=True)

    summary = {
        "input": str(args.input),
        "output": str(args.out),
        "model": args.model_name,
        "mode": args.mode,
        "n_pythia_eligible": len(targets),
        "newly_done": n_done,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
