"""Log-likelihood scoring per pre-reg v1.2 §4.4 contamination-arm pseudocode.

For each rating position k ∈ {1, ..., 10}:
    P(str(k) | prompt) computed by chain rule over candidate's BPE tokenization
        log P(c_1, c_2, ..., c_n | prompt) = sum_i log P(c_i | prompt + c_1..c_{i-1})

argmax-k → predicted rating in {1, ..., 10}.

Implementation notes:
- Multi-token candidates (e.g., "10" tokenizes to ["1", "0"] in GPT-NeoX BPE)
  use chain rule by extending context one token at a time.
- A single forward pass over (prompt + candidate_tokens[:-1]) returns logits at
  every position; per-position next-token log-probs are then summed for the
  candidate. This is more efficient than one pass per token but equivalent.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F


def score_dimension(
    model,
    tokenizer,
    prompt: str,
    candidates: tuple[str, ...] = tuple(str(i) for i in range(1, 11)),
    device: str = "cpu",
) -> dict[str, float]:
    """Compute log P(candidate | prompt) for each candidate using chain rule.

    Returns {candidate: log_prob} for all candidates. Caller does argmax.

    Equivalent to per-token chain rule but uses one forward pass per candidate
    rather than per token (efficient for short candidates).
    """
    base_ids: list[int] = tokenizer.encode(prompt, add_special_tokens=False)
    base_t = torch.tensor(base_ids, dtype=torch.long, device=device)
    log_probs: dict[str, float] = {}
    with torch.no_grad():
        for cand in candidates:
            cand_ids: list[int] = tokenizer.encode(cand, add_special_tokens=False)
            if not cand_ids:
                log_probs[cand] = float("-inf")
                continue
            full = torch.cat([base_t, torch.tensor(cand_ids, dtype=torch.long, device=device)])
            logits = model(full.unsqueeze(0)).logits[0]  # [seq_len, vocab]
            # log P(cand_i | prompt + cand_1..cand_{i-1}) is the next-token log-prob
            # at position (len(base_ids) + i - 1) for token cand_i.
            log_p = 0.0
            for i, tok_id in enumerate(cand_ids):
                pos = len(base_ids) + i - 1
                log_p += F.log_softmax(logits[pos], dim=-1)[tok_id].item()
            log_probs[cand] = log_p
    return log_probs


def predicted_rating(log_probs: dict[str, float]) -> int:
    """argmax-k from log_probs keyed by str(k)."""
    return int(max(log_probs.keys(), key=lambda k: log_probs[k]))


def verify_tokenization(tokenizer, candidates: tuple[str, ...] = tuple(str(i) for i in range(1, 11))) -> dict:
    """Audit: how does the tokenizer tokenize each rating candidate?

    Returns {candidate: {ids, tokens, is_single_token, n_tokens}} for documentation
    in REPRODUCE.md per pre-reg §4.4.
    """
    audit: dict[str, dict] = {}
    for c in candidates:
        ids = tokenizer.encode(c, add_special_tokens=False)
        toks = tokenizer.convert_ids_to_tokens(ids) if hasattr(tokenizer, "convert_ids_to_tokens") else ["?"] * len(ids)
        audit[c] = {
            "ids": ids,
            "tokens": toks,
            "is_single_token": len(ids) == 1,
            "n_tokens": len(ids),
        }
    return audit
