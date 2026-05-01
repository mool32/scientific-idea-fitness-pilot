# Pre-Registration: Retrodictive Calibration Pilot

**Status:** v1.0 — final, ready for hash-lock (2026-05-01)
**Hash-lock:** to be recorded in `HASH.md` after this commit
**Pre-registered author:** Theodor Spiro (tspiro@vaika.org)
**Reviewer commitment:** results published regardless of direction (positive, null, or negative)
**Stage:** Pilot 1A specified in full; Pilot 1B contingent on 1A success criterion (see §11)

---

## 1. Hypothesis

**H1 (primary):** An LLM, given only a paper's abstract and stripped technical content, predicts the paper's composite impact score (measured 4 years post-publication, see §3) at a level exceeding a non-semantic bibliometric baseline (citation velocity at year 1 predicting year 4, computed on the same papers).

Operationally: Spearman ρ between LLM score and composite Impact exceeds Spearman ρ between citation-velocity baseline and composite Impact, by at least 0.05 (point estimate), and the bootstrapped 95% CI of the difference (ρ_LLM − ρ_baseline) excludes zero.

**Why baseline-anchored.** Round AUC thresholds (>0.6, >0.7) are arbitrary. Citation velocity at year 1 already predicts year-4 impact reasonably well — papers gaining citations early tend to continue. If LLM-prediction does not exceed this trivial bibliometric signal, the LLM adds no semantic value over a one-line heuristic. A baseline-anchored threshold tests the substantive claim "LLM extracts predictive signal beyond what trivial bibliometrics already provide" rather than "LLM beats coin flip."

**Theoretical note (acknowledged, not actioned in primary).** The citation-velocity baseline is itself a transmission-fitness signal. With the flipped composite formula (§3.1) which de-emphasizes raw citations, the baseline's predictive ceiling is lower than it would be against pure-citation targets. So the test "LLM beats citation-velocity baseline at predicting flipped-composite Impact" is *more demanding* than "LLM beats baseline at predicting raw citations" — and a positive result there is correspondingly stronger evidence that LLM picks up something beyond pure transmission proxies. Reported explicitly in §5.2 as a comparative test.

**H0:** ρ_LLM ≤ ρ_baseline + 0.05, OR the 95% CI of (ρ_LLM − ρ_baseline) overlaps zero.

**Falsification:** if H0 holds, the LLM-as-judge fitness-function approach is falsified for the tested operationalization, and the project must pivot to alternative signal sources (formal predictive testing, replication outcomes, human arbitration ensembles).

**Secondary metric (interpretable).** AUC for top-30% vs. bottom-30% dichotomization (§5.2). Reported alongside ρ for interpretability but not the gate criterion.

---

## 2. Corpus

### 2.1 Source
arXiv papers in three subfields, restricted to v1 submissions between **2020-01-01 and 2022-12-31** (so that ΔT = 4 years from submission to outcome measurement in 2026).

### 2.2 Subfields
- **Primary:** NLP (arXiv category `cs.CL`)
- **Robustness check 1:** Computer Vision (`cs.CV`)
- **Robustness check 2:** Reinforcement Learning (`cs.LG` filtered for RL keywords + `cs.AI` cross-listed; specific filter in code)

### 2.3 Sampling
For each subfield: stratified sample of 500 papers, drawn from impact tiers measured in 2026:
- 150 papers from top 10% impact tier
- 200 papers from middle 40-60% impact tier
- 150 papers from bottom 10% impact tier

Total corpus: **1500 papers** (500 × 3 subfields).

Stratification uses outcome data — this is a known and disclosed limitation; absolute base rates from this sample do not generalize to a uniform random draw.

### 2.4 Exclusion criteria (applied before stratification)
- Papers withdrawn before 2026-01-01
- Papers with abstracts < 200 characters or > 3000 characters (anomalous)
- Papers by arXiv accounts with > 100 submissions per year (likely auto-generated or aggregator accounts)
- Papers without DOI / Semantic Scholar ID resolvable as of 2026-04-01

### 2.5 Blinding
Two separate code paths with separate data files:
- `corpus_blind/` — abstracts, titles, technical content; **no** author names, **no** affiliations, **no** venue, **no** year (replaced with placeholder), **no** citation count, **no** outcome data
- `corpus_outcomes/` — paper IDs joined to citation data, replication mentions, citation intents

Prediction-generating agent reads only `corpus_blind/`. Outcome-measurement agent reads only `corpus_outcomes/`. Code reviewer must verify this separation before launch.

---

## 3. Outcome measure

### 3.1 Composite impact score

**Primary formula (flipped, truth-tracking-weighted):**

```
Impact = 0.25 × NormalizedCitation
       + 0.35 × MethodReuseSignal
       + 0.25 × ReplicationSignal
       + 0.15 × InverseRetractionScore
```

Each component is normalized to [0, 1] within the subfield × publication-year cell *before* combination.

**Rationale for flipped weights.** Per the project's theoretical framework (Smaldino-McElreath, Hong-Henrich), pure transmission signals (citations) systematically diverge from truth-fitness under realistic incentives. Method-reuse is closer to truth-tracking — methods that work get reused, methods that don't get abandoned — and so receives the largest weight. Replication mentions and inverse retraction are weaker but more direct truth-tracking signals. Raw normalized citation is retained as a substantial component (25%) because it is the most-measurable and least-noisy single signal, but it does not dominate.

**Acknowledged limitations of flipped weights.** Method-reuse has its own bias toward usability — easy-to-implement methods get reused even if not the most rigorous. This is a real but bounded weakness; the multi-component composite plus sensitivity analyses (§3.4) is intended to dilute any single component's bias.

**Sensitivity formula (original transmission-weighted, retained as secondary):**

```
Impact_orig = 0.50 × NormalizedCitation
            + 0.25 × ReplicationSignal
            + 0.15 × MethodReuseSignal
            + 0.10 × InverseRetractionScore
```

Reported alongside primary in §5.2. If primary and sensitivity formulas yield similar discriminative results, robustness is established. If they diverge substantially, the divergence itself is informative about what the LLM-judge picks up — transmission-correlated patterns vs. truth-tracking patterns.

### 3.2 Component definitions

**NormalizedCitation.** Percentile rank of total citations as of 2026-04-01 (Semantic Scholar API), within the cell defined by (arXiv primary category × year of v1 submission). Percentile rank chosen over log-z because citation distributions are extremely heavy-tailed; percentile is monotone-invariant and robust to outliers.

**ReplicationSignal.** Operationalized as a two-track measure:

- *Track A (regex):* For each citing paper found via Semantic Scholar, scan title + abstract for the pattern `(re-?implement(s|ed|ing|ation)?|repli(cat|cation)|reproduc(e|ed|ing|ibility)|re-?evaluat|re-?run)` with the target paper as referent (heuristically: target appears in immediate sentence context or in references-cited-with section). Count = number of distinct citing papers matching.
- *Track B (manual validation):* On a stratified 50-paper subsample (drawn before launch and held out for QA), human annotates true replication mentions. If Cohen's κ between Track A and Track B < 0.6, **discard Track A** and use manual annotation on the full corpus (cost: ~30 hours of human time). If κ ≥ 0.6, use Track A on the full corpus.

Score = log(1 + count), then min-max normalized within the (subfield × year) cell.

**MethodReuseSignal.** Use Semantic Scholar's citation-intent classification (`methodology`, `result_comparison`, `extension`) for each citing paper. Score = fraction of citations classified as `methodology` or `extension` (i.e., reuse-implying), then min-max normalized within the cell. Falls back to scite.ai if Semantic Scholar coverage < 70% for the paper's citations.

**InverseRetractionScore.** Binary, but extended: 1.0 if no retraction, no expression of concern, and no public correction documented (cross-checked against Retraction Watch database + arXiv withdrawal flag); 0.0 if retracted; 0.5 if expression of concern or major correction. Multiplied by inverse of (1 + count of citing papers that explicitly identify a flaw).

### 3.3 Dichotomization for primary analysis
Top 30% vs. bottom 30% of composite Impact within each subfield. Middle 40% **excluded from primary AUC computation** (used only for secondary continuous-score analyses).

### 3.4 Sensitivity analyses on weights
Re-run primary AUC with three alternative weight schemes:
- Equal weights (25/25/25/25)
- Citation-only (100/0/0/0)
- De-weighted citation (25/35/30/10)

If primary result holds across all three, robustness is strong. If it holds only under the pre-registered weights, robustness is weaker but does not invalidate the primary test.

---

## 4. Prediction generation

### 4.1 Models

**Pilot 1A models (gate-decision corpus):**
- `claude-opus-4-7` (current frontier) — primary judge
- **Pythia 6.9B** — contamination control. Trained on the Pile, which is overwhelmingly pre-2020 content. Gives a lower-bound on what pure-semantic discrimination is achievable without exposure to the 2020-2022 papers themselves.

**Pilot 1B additional models (if 1A passes gate):**
- `claude-sonnet-4-6` (mid-tier, scaling check)
- **GPT-2 1.5B** — strict pre-2020 cutoff floor reference. Much weaker model overall, but cleanest temporal-cutoff guarantee. If even GPT-2 shows above-baseline discrimination, that strongly bounds contamination as the explanation.

**Acknowledged confound on contamination control.** Pythia 6.9B is significantly weaker than `claude-opus-4-7` in general capability. If Pythia discriminates poorly while Opus discriminates well, the gap could reflect either (a) contamination of Opus, or (b) Pythia's weaker general capability even on uncontaminated tasks. We cannot cleanly disentangle these. The contamination control is therefore a *bounding* test, not a clean isolation: if Pythia's discrimination is roughly comparable to Opus's, contamination is unlikely to be the main driver. If Pythia is much worse, contamination remains plausible but not proven. We report this honestly in the writeup.

**Mitigation for the confound.** The contamination-control measurement is most informative on papers with low fame — papers where contamination would be least likely *a priori*. In secondary analysis (§5.2), we stratify the Opus-vs-Pythia gap by paper fame proxies (citation count percentile, venue prestige) to test whether the gap concentrates in high-fame papers (consistent with contamination) or is uniform (consistent with capability gap).

### 4.2 Prompts
Four prompt variants, applied uniformly:

- **V1 (naive):** "Rate the likely scientific impact of this idea on a 1-10 scale. Output only a single integer."
- **V2 (structured):** "Rate this paper on four dimensions, 1-10 each: (a) novelty, (b) technical soundness, (c) follow-up potential, (d) overall promise. Briefly justify each."
- **V3 (skeptical reviewer):** "You are a skeptical reviewer. List up to three weaknesses. Then rate likely impact 1-10."
- **V4 (predictive specifics):** "If this idea is correct, what 1-3 specific findings should appear in the next 3 years? Rate confidence in each prediction 1-10."

Exact prompt text (including system prompt) frozen in `prompts/v1.txt` ... `prompts/v4.txt` in the repo.

### 4.3 Inference parameters
- Temperature: 0.0
- Max tokens: V1=8, V2/V3/V4=400
- Single sample per (paper × prompt × model) — no resampling, no self-consistency aggregation in the primary analysis (though resampling on a 50-paper subsample is a secondary analysis to estimate within-model variance)
- Random seed (where supported): 0

### 4.4 Score extraction
For V1: parsed integer. For V2: weighted average of (a, b, c, d) with weights (0.25, 0.25, 0.25, 0.25); also retain (d) alone. For V3: parsed final integer. For V4: mean of confidence ratings, weighted by 1 (uniform).

**Pre-specified primary score:** V2 (overall promise rating, dimension (d)) from `claude-opus-4-7`. All others are secondary.

### 4.5 Total inference scope

**Pilot 1A (gate decision):** 500 NLP papers × 1 prompt (V2) × 2 models (Opus, Pythia 6.9B) = 1,000 inferences. Estimated cost: ~$150 (Opus dominant; Pythia run locally or on cheap inference).

**Pilot 1B (contingent on 1A passing):** additional 1,000 papers (CV + RL, 500 each) × 4 prompts × 4 models = 16,000 additional inferences. Plus author-unblinding sub-experiment (§5.2 item 6) on 100 papers. Estimated additional cost: $400-600.

Total if both stages run: ~17,000 inferences, ~$550-750. If 1A fails gate, project stops at ~$150.

---

## 5. Statistical analysis

### 5.1 Primary test (gate criterion for Pilot 1A)

**Test:** Spearman ρ between V2-overall score from `claude-opus-4-7` and composite Impact (primary flipped formula, §3.1), computed on all 500 NLP papers in Pilot 1A.

**Baseline:** Spearman ρ between citation velocity (citations accrued in first 12 months post-arXiv-submission, computed from Semantic Scholar timestamps) and the same composite Impact, on the same 500 papers.

**Success criterion:** point estimate (ρ_LLM − ρ_baseline) ≥ 0.05 AND bootstrapped 95% CI of the difference excludes zero (10,000 bootstrap resamples, paired-paper resampling).

**Failure modes:**
- ρ_LLM ≤ ρ_baseline + 0.05 → H0 retained, gate fails, project stops
- 95% CI overlaps zero → inconclusive, gate fails (replication or design revision required)

This is the gate criterion for proceeding to Pilot 1B (§11).

**Why ρ over AUC for primary.** AUC requires dichotomization which discards information from the middle 40% of impact tier and makes the task artificially easier (only extremes compared). ρ uses all 500 papers and the full impact distribution, providing higher statistical power and more directly reflecting the use-case (rank-ordering of ideas).

### 5.2 Secondary analyses (pre-specified)

All reported regardless of primary outcome.

1. **AUC for top-30% vs. bottom-30%** dichotomization, with same baseline-relative threshold (AUC_LLM − AUC_baseline ≥ 0.05, paired DeLong CI excludes zero). For interpretability.
2. **Calibration:** reliability diagram and Brier score for V2-overall as a probability proxy.
3. **Original (transmission-weighted) impact formula** (§3.1 sensitivity formula) as alternative target. Test: ρ_LLM − ρ_baseline on this target. *Hypothesis: gap is smaller against transmission-weighted target, since baseline (citation velocity) is itself a pure transmission signal and so its predictive ceiling rises against transmission-aligned targets. If LLM gap *narrows* against transmission-weighted target, this is evidence the LLM's signal goes beyond pure transmission-correlation.*
4. **Pythia vs. Opus discrimination gap.** ρ_Opus − ρ_Pythia. Stratify by paper fame (high/low citation percentile) — if gap concentrates in high-fame papers, contamination plausible; if uniform, capability gap more likely (§4.1).
5. **Inter-model disagreement signal.** Does |Opus − Pythia| score correlate with impact independently of mean? Tests whether disagreement itself carries information about idea novelty/risk.

**Pilot 1B-only secondary analyses (run only if 1A passes gate):**

6. ρ by subfield separately (NLP, CV, RL): robustness across domains.
7. ρ by prompt variant (V1, V2, V3, V4): prompt-dependence.
8. ρ for additional models (Sonnet, GPT-2 1.5B floor reference).
9. **Author-unblinding sub-experiment:** on a 100-paper stratified subsample from Pilot 1A's NLP corpus, re-run V2 with author and affiliation included. Measure shift in V2-overall as proxy for prestige-bias contamination.

### 5.3 Multiple comparisons
Primary test is one comparison — no correction. Secondary analyses are explicitly exploratory; report uncorrected statistics with "exploratory" labeling. No selective reporting: every analysis listed in §5.2 is reported regardless of result.

### 5.4 Stopping rules
No interim peeking within Pilot 1A. Run all 1,000 1A-inferences and outcome measurement before computing primary statistic. The stage gate (§11) is the *only* decision point — Pilot 1B launches or doesn't based on 1A primary result, with no peeking at 1B-specific signals to influence the decision.

---

## 6. Contamination & confounding

Acknowledged sources of bias, with attempted mitigations:

| Source | Mitigation | Residual risk |
|---|---|---|
| LLM saw paper in training | Pythia 6.9B contamination control (1A); GPT-2 floor (1B); fame-stratified analysis (§5.2 #4) | Cannot cleanly isolate from capability gap; bounded only |
| Citation count tracks prestige not quality | Flipped composite formula de-emphasizing citations to 25%; sensitivity test against original transmission-weighted formula (§5.2 #3) | Real but bounded |
| Stratified sampling distorts base rates | Disclosed; primary metric is rank-based (Spearman ρ) | None for ρ |
| Prompt sensitivity | V2 pre-specified for primary; V1/V3/V4 in 1B for sensitivity | Low |
| Outcome measure is itself biased | Multi-component composite, sensitivity analysis on weights (§3.4) | Real and acknowledged |
| Subfield-specific dynamics | NLP primary in 1A; CV/RL robustness in 1B | Mitigated, not eliminated |
| Method-reuse bias toward usability | Acknowledged in §3.1; component capped at 35% | Real, structural |
| Pythia weak capability confounds with no-contamination | Fame-stratified analysis (§5.2 #4); GPT-2 floor in 1B | Cannot fully resolve |

---

## 7. Deliverables

Released regardless of result:
1. This pre-registration (hash-locked)
2. Full corpus (paper IDs, abstracts as fetched, outcome data snapshot) — `corpus/`
3. All prompts (verbatim) — `prompts/`
4. All raw model outputs — `predictions/`
5. Outcome data with timestamps — `outcomes/`
6. Analysis code — `analysis/`
7. Write-up (paper or preprint) — `writeup/`
8. Reproduction instructions — `REPRODUCE.md`

---

## 8. Publication commitment

Result will be published as preprint within 60 days of analysis completion, regardless of direction. Null results are explicitly part of the value of this pilot — a confirmed null bounds the design space and is reported with the same prominence as a positive result.

---

## 9. Authorship & changes

Any deviation from this pre-registration must be:
1. Documented in a `DEVIATIONS.md` file with timestamp and rationale
2. Distinguished in the write-up between pre-registered and post-hoc analyses
3. If the deviation affects the primary analysis, the pre-registered analysis is *also* reported alongside

---

## 10. Hash-lock procedure

Once §1–11 are finalized:
1. Generate SHA-256 of this file: `shasum -a 256 02_pre_registration.md`
2. Record the hash and UTC timestamp in `HASH.md`
3. Commit to git; tag the commit `prereg-v1.0`
4. Optional: post hash to a public timestamping service (OpenTimestamps) for third-party verifiability

After hash-lock, this file is immutable. Any changes go to `02_pre_registration_v1.1.md` etc., with deviations also in `DEVIATIONS.md`.

---

## 11. Stage gate: Pilot 1A → Pilot 1B contingency

The pilot is split into two stages with a hard gate between them, to bound resource commitment and reduce scope-creep risk.

### 11.1 Pilot 1A — minimum viable test

**Scope:**
- Subfield: NLP (`cs.CL`) only
- Corpus: 500 papers (stratified per §2.3)
- Prompt: V2 only (structured)
- Models: `claude-opus-4-7` + Pythia 6.9B
- Outcome formula: primary flipped composite (§3.1)
- No author-unblinding sub-experiment

**Total inferences:** 1,000. **Estimated cost:** ~$150. **Estimated wall-clock:** ~1 week.

**Gate criterion (= primary success criterion §5.1):** ρ_LLM − ρ_baseline ≥ 0.05 with bootstrapped 95% CI excluding zero.

### 11.2 Gate decision

After Pilot 1A completes and primary statistic is computed:

- **PASS (gate criterion met):** Proceed to Pilot 1B. Document the 1A result in writeup; 1B expands the test.
- **FAIL (gate criterion not met):** Stop. Write up Pilot 1A as a standalone result. Pivot to alternative pilot designs (NAS-bench-style narrow-domain evaluation, human-LLM agreement studies, or fitness-function approaches not based on LLM-as-judge).

The decision is binary and pre-committed. No ambiguous "let's try one more thing" — if 1A fails, expanded design will not rescue it because the underlying signal isn't there.

### 11.3 Pilot 1B — expanded test (if 1A passes)

**Additional scope:**
- Subfields: CV (`cs.CV`) + RL — 500 papers each
- Prompts: V1, V3, V4 added
- Models: `claude-sonnet-4-6` + GPT-2 1.5B added
- Author-unblinding sub-experiment on 100-paper subsample from 1A's NLP corpus

**Additional inferences:** ~16,000. **Additional cost:** $400-600. **Additional wall-clock:** ~2 weeks.

**Pilot 1B analyses:** §5.2 items 6-9. No new gate criterion — 1B is descriptive/robustness, not confirmatory.

### 11.4 Why this structure is principled (not just resource-saving)

Stage-gating addresses a known failure mode: pilots that grow in scope to cover every conceivable check often don't get done. By committing to a minimum viable test with a clear gate, the project ensures *some* result is reached even if expansion proves unjustified.

Equally importantly: if 1A fails, spending the full $550-750 on 1B yields no rescue — the absence of signal in the strongest model on the easiest subfield (NLP, where LLMs have most exposure) is not overcome by adding weaker models or noisier subfields. Stage-gating reflects the actual epistemic structure of the test, not just budget management.
