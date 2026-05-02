# Reproducing the Pilot

This document is the operational counterpart to `02_pre_registration.md`. The pre-reg specifies *what* the pilot tests; this file specifies *how to actually run it* — exact commands, expected outputs, environment, and verification points.

Status: **Phase 1 complete** (corpus, citations, composite Impact scored for 500 papers). Phase 2 (model inference) pending.

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
  01_pull_arxiv.py    — pull arXiv papers per category × month
  02_enrich_s2.py     — Semantic Scholar enrichment (citation count, venue, etc.)
  03_stratify_sample.py — stratified 500-paper sample per §2.3 (within-year percentile)
  04_blind_corpus.py  — strip metadata for prediction-blinded variant per §2.5
  05_pull_citations.py — per-paper /citations pull with intents + citing-paper text
  06_compute_impact.py — composite Impact per §3.1 (primary + sensitivity formulas)

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

predictions/          — model outputs. Populated during Phase 2.
analysis/             — statistical analyses + plots. Populated during Phase 4.
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
