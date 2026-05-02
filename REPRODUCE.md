# Reproducing the Pilot

This document is the operational counterpart to `02_pre_registration.md`. The pre-reg specifies *what* the pilot tests; this file specifies *how to actually run it* — exact commands, expected outputs, environment, and verification points.

Status: **Phase 2 setup complete, execution paused** pending external metascience review (per `DECISIONS.md` D-009) or 5-day timeout.

- Phase 1 done: corpus, citations, composite Impact for 500 papers
- Phase 2 setup done: prompts frozen, log-likelihood scoring unit-tested, citation-velocity baseline computed, Opus and Pythia inference scripts written and pipeline-verified end-to-end on smoke tests
- Phase 2 execution: paused per D-008 moratorium and D-009 stage-gate-binding commitments. Cannot launch until external review feedback received or 5-day timeout reached, AND user sets ANTHROPIC_API_KEY (Opus arm) and deploys HF Inference Endpoint or local Pythia setup (Pythia arm).

## Environment

- Python 3.12+
- macOS (Darwin) or Linux. Windows untested.
- Stdlib only for arXiv pull (no external packages required for Phase 1 corpus construction).
- Later phases require: `requests` (for Semantic Scholar with API key), `numpy`/`scipy` (for analysis), `transformers` + HF Inference Endpoint access (for Pythia arm).

## Directory layout

```
scripts/
  lib/
    config.py         — single source of truth for paths, dates, sample sizes
    cache.py          — atomic JSONL write/read utilities (auto-handles .gz on read)
    arxiv_client.py   — rate-limited arXiv API client (stdlib only, 429/503 retry)
    s2_client.py      — Semantic Scholar batch + per-paper API client
    pythia_score.py   — log-likelihood scoring per pre-reg §4.4 pseudocode
  01_pull_arxiv.py    — pull arXiv papers per category × month
  02_enrich_s2.py     — Semantic Scholar enrichment (citation count, venue, etc.)
  03_stratify_sample.py — stratified 500-paper sample per §2.3 (within-year percentile)
  04_blind_corpus.py  — strip metadata for prediction-blinded variant per §2.5
  05_pull_citations.py — per-paper /citations pull with intents + citing-paper text
                         + publicationDate (added 2026-05-02 for citation-velocity baseline)
  06_compute_impact.py — composite Impact per §3.1 (primary + sensitivity formulas)
  07_pull_opus_v2.py  — claude-opus-4-7 V2 inference (frontier-model arm, generation
                        protocol per §4.4); requires ANTHROPIC_API_KEY
  08_pull_pythia_v2.py — Pythia 6.9b-deduped V2 inference (contamination-control arm,
                         log-likelihood protocol per §4.4); requires either
                         HF_INFERENCE_URL+HF_TOKEN (production) or local model
                         (verification only, 6.9b needs >16 GB)
  09_compute_citation_velocity.py — citation-velocity baseline per §5.1.A
                                    (12-month-post-submission citation count)
  test_pythia_score.py — unit test for log-likelihood scoring (uses pythia-70m-deduped
                         locally, ~140 MB; verifies tokenization + chain rule)

corpus_outcomes/      — outcome-side data. NEVER read by prediction-generating code.
  arxiv_raw/          — per-month JSONL pulls from arXiv API (36 files for cs.CL 2020-2022)
  s2_enriched.jsonl   — Semantic Scholar metadata joined per arxiv_id_base
  stratified_500.jsonl — sampled 500-paper corpus with full S2 fields
  blind_id_mapping.jsonl — blind_id ↔ arxiv_id_base mapping
  citations_for_500.jsonl.gz — per-paper citations (intents, contexts, citing-paper
    title/abstract). Committed gzipped (38MB) because uncompressed (144MB) exceeds
    GitHub's 100MB per-file limit. cache.read_jsonl() auto-detects .gz fallback.
  impact_scored_500.jsonl — composite Impact + components per paper

corpus_blind/         — blinded data for prediction-generating code only. NO author,
                        affiliation, venue, year, citation count, outcome.
  stratified_500_blind.jsonl — 500 records with only blind_id, title, abstract,
    primary_category, categories. Order randomized with seed 0.

  citation_velocity_500.jsonl — per-paper 12-month-post-submission citation
    count for §5.1.A baseline. Resolution audit: 87.6% via full date,
    10.4% via year fallback, 2.0% no date.

prompts/              — frozen prompt template files per pre-reg §4.2
  system_prompt.txt   — uniform blinding-context system message
  v1.txt, v2.txt, v3.txt, v4.txt — verbatim prompt variants

predictions/          — model outputs. Populated during Phase 2 EXECUTION
  opus_v2_predictions.jsonl — (TODO) frontier-model arm
  pythia_v2_predictions.jsonl — (TODO) contamination-control arm

analysis/             — statistical analyses + plots. Populated during Phase 4.

_outreach/            — communication drafts for human reviewer to adapt
  recruit_message_draft.md — draft for external reviewer outreach (D-009)
```

The separation between `corpus_outcomes/` and `corpus_blind/` is required by pre-reg §2.5. Code reviewer must verify the separation: prediction-generating code reads only from `corpus_blind/`; outcome-measurement code reads only from `corpus_outcomes/`.

## Phase 1 — Corpus construction

### Smoke test (verify pipeline works)

Run a 50-paper pull from cs.CL January 2020 to a throwaway directory:

```bash
python3 scripts/01_pull_arxiv.py \
    --category cs.CL --from 2020-01 --to 2020-01 \
    --max-results 50 \
    --out-dir /tmp/arxiv_smoke
```

Expected: ~3-4 second wall time, JSONL file at `/tmp/arxiv_smoke/cs_CL_2020-01.jsonl` with 50 records. Each record has fields `arxiv_id`, `arxiv_id_base`, `title`, `abstract`, `submitted_date`, `primary_category`, `categories`, `authors`, `doi`, `journal_ref`, `pdf_url`, `_pulled_at`.

### Full Pilot 1A pipeline (NLP, 2020-2022)

```bash
# Step 1: pull arXiv corpus (~10-15 min, 24K papers, 36 monthly files)
python3 scripts/01_pull_arxiv.py --category cs.CL --from 2020-01 --to 2022-12

# Step 2: enrich with Semantic Scholar metadata (~3-5 min, 99.8% coverage)
python3 scripts/02_enrich_s2.py --category cs_CL

# Step 3: stratified sample of 500 (within-year percentile, seed 0)
python3 scripts/03_stratify_sample.py

# Step 4: blind the sample for prediction-side use
python3 scripts/04_blind_corpus.py

# Step 5: per-paper citation pull (~30 min unauthenticated, faster with S2 API key)
python3 scripts/05_pull_citations.py
gzip -9 corpus_outcomes/citations_for_500.jsonl    # compress for git (uncompressed ~144 MB)

# Step 6: compute composite Impact per §3.1 (primary + sensitivity formulas)
python3 scripts/06_compute_impact.py
```

Set `S2_API_KEY` environment variable for authenticated S2 rate limits (recommended for steps 2 and 5; faster + fewer 429 retries).

If a script fails midway: most are resume-safe (per-month skip for arXiv pull; per-record dedupe for S2 enrichment and citations pull). The exception is the gzipped citations file — to resume the citations pull after compression, first run `gunzip -k corpus_outcomes/citations_for_500.jsonl.gz`.

## Phase 2 — Model inference (EXECUTION PAUSED per D-008/D-009)

Pre-reg v1.2 §4.4 specifies two arms: frontier-model arm (Opus, generation protocol)
and contamination-control arm (Pythia, log-likelihood protocol). Pythia restricted
to Pythia-eligible subset (arXiv v1 ≥ 2020-08-01, n≈419 of 500).

### Setup verification (allowed during execution pause)

```bash
# 1. Verify log-likelihood scoring + tokenizer audit (uses pythia-70m-deduped, ~140MB local)
python3 scripts/test_pythia_score.py

# 2. Compute citation-velocity baseline (uses re-pulled citations file)
python3 scripts/09_compute_citation_velocity.py

# 3. End-to-end pipeline smoke test for Pythia arm with tiny model (no API needed)
python3 scripts/08_pull_pythia_v2.py --mode local --model-name EleutherAI/pythia-70m-deduped --max-papers 5

# 4. End-to-end pipeline smoke test for Opus arm (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=... python3 scripts/07_pull_opus_v2.py --max-papers 5
```

### Tokenization audit (one-time, recorded for reproducibility)

GPT-NeoX BPE tokenizer (used by Pythia 70M / 160M / ... / 6.9B) treats all of
`"1"` through `"10"` as **single tokens**:

| Candidate | Token IDs |
|---|---|
| `"1"` | `[18]` |
| `"2"` | `[19]` |
| `"3"` | `[20]` |
| `"4"` | `[21]` |
| `"5"` | `[22]` |
| `"6"` | `[23]` |
| `"7"` | `[24]` |
| `"8"` | `[25]` |
| `"9"` | `[26]` |
| `"10"` | `[740]` |

Therefore the chain-rule provision in pre-reg §4.4 pseudocode for multi-token
candidates is implemented but never exercised in practice for our rating set.
Single-forward-pass and per-token-loop implementations agree to `|diff|=0.0`
to numerical precision.

Note on dtype: the unit test loads pythia-70m-deduped explicitly with
`dtype=torch.float32` to avoid NaN logits that appeared with default loading on
this tiny model (likely precision instability). Production inference on
pythia-6.9b-deduped should use the same precision the deployed endpoint uses;
documented at execution time per actual deployment.

### Production execution (PAUSED — do not run until explicit Phase 2 sign-off)

```bash
# Frontier arm (Opus, all 500 papers, V2 generation)
ANTHROPIC_API_KEY=sk-ant-... python3 scripts/07_pull_opus_v2.py
# Estimated cost ~$5-10 per pre-reg §4.5 v1.2

# Contamination-control arm (Pythia 6.9b-deduped, ~419 Pythia-eligible papers, V2 log-likelihood)
# Production path: deploy HF Inference Endpoint with custom handler.py
HF_INFERENCE_URL=https://... HF_TOKEN=... python3 scripts/08_pull_pythia_v2.py --mode hf-endpoint
# Estimated cost ~$1-2 per pre-reg §4.5 v1.2 (A10G GPU, on-demand)
```

### Pythia HF Endpoint setup (user-side action required before execution)

Hugging Face Inference Endpoints do not expose per-token log-probabilities
out of the box. To enable the chain-rule scoring per pre-reg §4.4, deploy
`EleutherAI/pythia-6.9b-deduped` with a custom `handler.py` implementing the
endpoint contract that `08_pull_pythia_v2.py` expects:

- POST body: `{"inputs": {"prompt": <str>, "candidates": [<str>, ...]}}`
- Response: `{"log_probs": {"<cand>": <float>, ...}}`

Reference handler logic (drop into endpoint deployment):

```python
# handler.py for HF Inference Endpoint (paste into endpoint repo)
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class EndpointHandler:
    def __init__(self, path=""):
        self.tok = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float16, device_map="auto")
        self.model.eval()

    def __call__(self, data):
        inputs = data["inputs"]
        prompt, candidates = inputs["prompt"], inputs["candidates"]
        base = self.tok.encode(prompt, add_special_tokens=False)
        log_probs = {}
        with torch.no_grad():
            for c in candidates:
                cand_ids = self.tok.encode(c, add_special_tokens=False)
                full = torch.tensor([base + cand_ids], device=self.model.device)
                logits = self.model(full).logits[0]
                lp = 0.0
                for i, tok_id in enumerate(cand_ids):
                    pos = len(base) + i - 1
                    lp += torch.log_softmax(logits[pos], dim=-1)[tok_id].item()
                log_probs[c] = lp
        return {"log_probs": log_probs}
```

Deploy steps:
1. Create new HF Inference Endpoint at https://endpoints.huggingface.co
2. Select `EleutherAI/pythia-6.9b-deduped`, A10G hardware
3. Custom container with the `handler.py` above
4. Set `HF_INFERENCE_URL` to the deployed URL
5. Set `HF_TOKEN` to a personal access token with read scope

### Local Pythia execution (M1, alternative to HF endpoint)

Pythia-6.9b-deduped at fp16 ~14 GB — won't fit on 16 GB M1 with OS overhead.
Options:
- Q4 quantization via llama.cpp: convert HF model → GGUF Q4_K_M (~4 GB), run
  via llama-cpp-python with same chain-rule logic. Pre-register the quantization
  scheme in `REPRODUCE.md` at execution time.
- bitsandbytes 4-bit: limited M1 support; skip.
- Cloud: HF endpoint above is cleanest.

### Phase 1 corpus characterization (added 2026-05-02 from diagnostic)

Pilot 1A NLP corpus (n=500) has the following composite-Impact properties, measured after Phase 1 ran end-to-end. These are descriptive of the measurement instrument; full diagnostic trace in `DECISIONS.md` D-007 and characterization paragraph in pre-reg v1.2 §3.1.

- ρ(Impact_primary, raw citationCount) = +0.865
- ρ(Impact_sensitivity, raw citationCount) = +0.964
- Δρ between formulas = 0.099 (modest movement)
- Component–citation ρ: NormalizedCitation +0.978 (mechanical), MethodReuseSignal +0.528, ReplicationSignal +0.286
- ~25% of Impact_primary variance is non-citation residual

Implications for the primary test (pre-reg v1.2 §5.1):
- Marginal test (5.1.A) is meaningfully confounded by citations — citation-velocity baseline will correlate strongly with Impact_primary
- Partial test (5.1.B), added in v1.2, directly tests "LLM adds value beyond raw citations"
- Stage gate (§11) requires BOTH primary tests to pass

### Known limitations of the current implementation

- **InverseRetractionScore** (§3.2 component, weight 15%) is currently constant 1.0
  for all papers. Pre-reg requires Retraction Watch + arXiv withdrawal cross-check
  + flagged-by-citing-papers multiplier. For 2020-2022 ML papers, retractions are
  extremely rare (likely 0 in our sample), so the component contributes a constant
  0.15 to all scores and has no discriminative power. A separate optional script can
  do per-DOI Crossref retraction lookup if non-zero retraction count needs verification.
- **ReplicationSignal Track A** (regex over citing-paper text) is implemented; **Track B**
  (manual annotation on 50-paper subsample for κ ≥ 0.6 validation per §3.2) is deferred
  to a separate manual annotation pass before primary analysis. If κ < 0.6, Track B
  must be run on the full corpus and Track A discarded.
- **Citations capped at 10K per paper** by S2 pagination limit (offset + limit < 10000).
  One paper in the sample has >10K citations; first 10K used. Documented in pull log.
- **Operational interpretation of §2.3** stratification chose within-year percentile
  rather than across-corpus percentile, for consistency with §3.2 NormalizedCitation.
  See script docstring in `03_stratify_sample.py`.

## Verification points

### Pre-registration integrity

```bash
shasum -a 256 02_pre_registration.md
# Expected: matches HASH.md "Current version" entry

git show prereg-v1.0:02_pre_registration.md | shasum -a 256
# Expected: matches HASH.md "Prior version: v1.0" entry

ots verify 02_pre_registration.md.ots
# Expected: verifies once Bitcoin attestation completes (~1-3 hours after stamp)
```

### Code-data separation (Phase 2 prerequisite)

Before launching prediction generation:

```bash
grep -rn "corpus_outcomes" scripts/ | grep -v "01_\|02_\|03_\|04_"
# Expected: empty. Only corpus-construction scripts (01-04) should reference corpus_outcomes/.

grep -rn "corpus_blind" scripts/ | grep -v "05_\|06_"
# Expected: only blinding script (05) writes corpus_blind/, only prediction script (06+, TBD) reads from it.
```

(Verification commands for later phases will be added as those phases are built.)

## Reproducibility notes

- All API queries log `_pulled_at` timestamp in each record. Re-pulls of the same arXiv ID may yield slightly different fields if the paper has been updated; comparing `_pulled_at` timestamps disambiguates.
- Random seed for stratified sampling is fixed at 0 (`scripts/lib/config.py:RANDOM_SEED`).
- All file writes are atomic (tempfile + rename) to avoid corruption on interruption.
- arXiv rate limit hard-coded to 3 seconds per the documented courtesy.
