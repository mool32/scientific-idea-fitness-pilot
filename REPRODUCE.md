# Reproducing the Pilot

This document is the operational counterpart to `02_pre_registration.md`. The pre-reg specifies *what* the pilot tests; this file specifies *how to actually run it* — exact commands, expected outputs, environment, and verification points.

Status: **Phase 1 scaffolding** (in progress). Full corpus and prediction pipelines being built.

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
    cache.py          — atomic JSONL write/read utilities
    arxiv_client.py   — rate-limited arXiv API client (stdlib only)
  01_pull_arxiv.py    — pull papers per category × month
  02_enrich_s2.py     — (TODO) Semantic Scholar enrichment
  03_compute_impact.py — (TODO) composite Impact per pre-reg §3.1
  04_stratify_sample.py — (TODO) stratified 500-paper sample per §2.3
  05_blind_corpus.py  — (TODO) strip metadata for prediction-blinded variant per §2.5

corpus_outcomes/      — outcome-side data (citation counts, replications, etc.). NEVER read by prediction-generating code.
  arxiv_raw/          — per-month JSONL pulls from arXiv API
  s2_enriched.jsonl   — (TODO) joined Semantic Scholar data
  impact_scored.jsonl — (TODO) composite Impact per paper
  stratified_500.jsonl — (TODO) sampled 500-paper corpus with outcomes

corpus_blind/         — blinded data for prediction-generating code only. NO author, affiliation, venue, year, citation count, outcome.
  stratified_500_blind.jsonl — (TODO)

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

### Full Pilot 1A pull (NLP, 2020-2022)

```bash
python3 scripts/01_pull_arxiv.py --category cs.CL --from 2020-01 --to 2022-12
```

Expected: per-month JSONL files in `corpus_outcomes/arxiv_raw/`. Wall time ~3 minutes per month due to arXiv 3-second rate limit, ~2 hours total. Files are skipped on resume if they already exist (use `--force` to re-pull).

(Subsequent steps to be documented as scripts are written.)

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
