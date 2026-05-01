"""Pipeline-wide configuration. Single source of truth for paths and corpus parameters.

Pre-registered constants per 02_pre_registration.md §2 — do not change without
documenting in DEVIATIONS.md (post-data) or CHANGELOG.md (pre-data per §0).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CORPUS_OUTCOMES_DIR = REPO_ROOT / "corpus_outcomes"
CORPUS_BLIND_DIR = REPO_ROOT / "corpus_blind"
ARXIV_RAW_DIR = CORPUS_OUTCOMES_DIR / "arxiv_raw"
PREDICTIONS_DIR = REPO_ROOT / "predictions"
ANALYSIS_DIR = REPO_ROOT / "analysis"

ARXIV_API_BASE = "http://export.arxiv.org/api/query"
ARXIV_RATE_LIMIT_SECONDS = 3.0
ARXIV_PAGE_SIZE = 1000

S2_API_BASE = "https://api.semanticscholar.org/graph/v1"

# Pre-registered corpus window (§2.1)
CORPUS_DATE_FROM = "2020-01-01"
CORPUS_DATE_TO = "2022-12-31"

# Pythia-eligible subset cutoff (§4.1, set in v1.1 from Pile July 2020 dump fact)
PYTHIA_ELIGIBLE_FROM = "2020-08-01"

# Pre-registered subfields (§2.2). Pilot 1A uses NLP only.
SUBFIELDS = {
    "nlp": "cs.CL",
    "cv": "cs.CV",
    "rl": "cs.LG",  # filtered for RL keywords post-pull; see DECISIONS / pre-reg
}
PILOT_1A_SUBFIELD = "nlp"

# Stratified sampling targets (§2.3)
SAMPLE_TIERS = {
    "high": (0.90, 1.00, 150),  # top 10%, target n
    "mid": (0.40, 0.60, 200),  # middle 40-60%, target n
    "low": (0.00, 0.10, 150),  # bottom 10%, target n
}
SAMPLE_TOTAL = sum(n for _, _, n in SAMPLE_TIERS.values())  # 500

# Exclusion criteria (§2.4)
ABSTRACT_MIN_CHARS = 200
ABSTRACT_MAX_CHARS = 3000

# Random seed for stratified sampling (§4.3)
RANDOM_SEED = 0
