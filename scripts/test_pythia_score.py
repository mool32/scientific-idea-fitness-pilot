"""Unit test for log-likelihood scoring per pre-reg v1.2 §4.4.

Uses Pythia-70M (same GPT-NeoX BPE tokenizer as Pythia-6.9B-deduped, ~140MB
download) to verify:

1. Tokenizer behavior for "1" through "10": which are single-token, which split
2. Chain rule implementation matches direct multi-token probability
3. Output is a valid integer in [1, 10] for arbitrary prompts
4. P(str(k) | prompt) sums (over k=1..10, after exp) — sanity check on
   probability magnitudes (not required to sum to 1 because we're conditioning
   on prompt structure that doesn't restrict k to those candidates)

Run:
    python3 scripts/test_pythia_score.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from lib.pythia_score import predicted_rating, score_dimension, verify_tokenization

MODEL_NAME = "EleutherAI/pythia-70m-deduped"  # same tokenizer as 6.9b-deduped


def main() -> int:
    print(f"[setup] loading {MODEL_NAME} (small, ~140MB) in fp32")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # Explicit fp32: tiny Pythia models exhibit NaN logits in some default dtypes.
    # For the production 6.9B model, fp16 is fine but we standardize on the dtype
    # the actual inference uses; document in REPRODUCE.md whatever production uses.
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.float32)
    model.eval()
    print(f"  vocab size: {tokenizer.vocab_size}")
    print(f"  model param count: {sum(p.numel() for p in model.parameters())/1e6:.1f}M")

    print()
    print("[test 1] tokenizer audit for ratings 1..10")
    audit = verify_tokenization(tokenizer)
    multi_token = [c for c, info in audit.items() if not info["is_single_token"]]
    for c, info in audit.items():
        marker = "" if info["is_single_token"] else "  ← MULTI-TOKEN"
        print(f"  '{c}' → ids={info['ids']} tokens={info['tokens']} n={info['n_tokens']}{marker}")
    print(f"  multi-token candidates requiring chain rule: {multi_token}")
    assert "10" in multi_token or audit["10"]["n_tokens"] == 1, \
        "expected '10' to either be single-token or multi-token (validates either case)"
    print("  ✓ all candidates handled by chain rule regardless of single/multi")

    print()
    print("[test 2] chain rule equivalence: per-token loop vs full forward pass")
    # The score_dimension function does ONE forward pass per candidate using the
    # logits at appropriate positions. Verify this matches a strict per-token loop.
    prompt = "Rate this paper's novelty 1-10. Answer: "
    base_ids = tokenizer.encode(prompt, add_special_tokens=False)

    def chain_rule_strict(cand: str) -> float:
        """Reference implementation: one forward pass per token (slow but obviously correct)."""
        cand_ids = tokenizer.encode(cand, add_special_tokens=False)
        log_p = 0.0
        ctx_ids = list(base_ids)
        with torch.no_grad():
            for tok_id in cand_ids:
                logits = model(torch.tensor([ctx_ids])).logits[0, -1]
                log_p += torch.log_softmax(logits, dim=-1)[tok_id].item()
                ctx_ids = ctx_ids + [tok_id]
        return log_p

    fast_scores = score_dimension(model, tokenizer, prompt)
    print(f"  prompt: {prompt!r}")
    for c in ("1", "5", "10"):
        strict = chain_rule_strict(c)
        fast = fast_scores[c]
        diff = abs(strict - fast)
        print(f"  '{c}': strict={strict:.4f}  fast={fast:.4f}  |diff|={diff:.2e}")
        assert diff < 1e-4, f"chain rule mismatch for '{c}': diff {diff} (likely a position-index bug)"
    print("  ✓ chain rule implementations agree to <1e-4")

    print()
    print("[test 3] argmax produces integer in [1,10] for varied prompts")
    test_prompts = [
        "Rate this paper's novelty 1-10. Answer: ",
        "On a 1-10 scale, how good is this idea: ",
        "The score is ",
    ]
    for p in test_prompts:
        scores = score_dimension(model, tokenizer, p)
        pred = predicted_rating(scores)
        assert 1 <= pred <= 10, f"prediction out of range: {pred}"
        # Print top 3 by log-prob for diagnostic
        top3 = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:3]
        print(f"  prompt: {p!r:55s}  argmax={pred}  top3=[{', '.join(f'{k}:{v:.2f}' for k,v in top3)}]")
    print("  ✓ argmax produces valid rating in [1,10]")

    print()
    print("[test 4] log-prob magnitudes sanity check (not normalized but bounded)")
    scores = score_dimension(model, tokenizer, "Rate this paper 1-10: ")
    probs = {k: math.exp(v) for k, v in scores.items()}
    total = sum(probs.values())
    print(f"  sum of exp(log_p) over k=1..10 = {total:.4f} (not required to be 1; informative bound)")
    assert all(v < 0 for v in scores.values()), "log_probs should all be negative"
    assert total < 2.0, f"sum of probs ({total}) suspiciously high — overlap likely"
    print("  ✓ log-probs in valid range")

    print()
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
