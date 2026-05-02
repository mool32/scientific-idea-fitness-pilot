# Pre-Registration: Retrodictive Calibration Pilot

**Status:** v1.2 — pre-data revision of v1.1 (2026-05-02)
**Hash-lock:** recorded in `HASH.md`
**Pre-registered author:** Theodor Spiro (tspiro@vaika.org)
**Reviewer commitment:** results published regardless of direction (positive, null, or negative)
**Stage:** Pilot 1A specified in full; Pilot 1B contingent on 1A success criterion (see §11)
**Version history:** v1.0 (commit 613c0be), v1.1 (commit 2765401) — both preserved with original tags and OpenTimestamps proofs; revisions documented in `CHANGELOG.md`. Pilot 1A corpus, Semantic Scholar enrichment, citation pull, and composite Impact computation completed before v1.2 — descriptive Phase 1 measurements informing this revision; no LLM predictions or test outcomes computed.

---

## 0. Revision policy

This pre-registration may be revised only under all of the following conditions:

1. **No data has been collected since the prior version.** Once data collection begins, the pre-registration is fully locked; subsequent design changes become deviations (`DEVIATIONS.md` per §9), not revisions.
2. **The revision corrects a factual error or clarifies ambiguity, not a strategic adjustment.** Changes motivated by reasoning about expected outcomes are forbidden; changes correcting a misstated fact, an underspecified protocol, or a discovered impossibility are permitted.
3. **The prior version remains in git history with its original hash, ots stamp, and tag.** Older versions are never deleted or rewritten; they remain independently verifiable artifacts.
4. **The new version atomically replaces the prior in the working file (`02_pre_registration.md`), with new SHA-256 hash, new OpenTimestamps proof, and new tag (`prereg-v1.x`).**
5. **`CHANGELOG.md` documents the transition with a dated entry, the rationale, and an explicit attestation that no data has been collected.**

This policy is itself part of the pre-registration: any future revision must conform to it or openly violate it (a violation would be a major credibility failure documented in the writeup). The policy makes the discipline enforceable by structure rather than by intent.

The discipline pre-registration enforces is against post-hoc adjustment under pressure of seen data. Pre-data factual correction is not the failure mode pre-registration exists to prevent; insisting on strict immutability against pre-data error correction would be cargo-cult discipline rather than substantive epistemic safeguarding.

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

**Rationale for flipped weights.** Per the project's theoretical framework (Smaldino-McElreath, Hong-Henrich), pure transmission signals (citations) systematically diverge from truth-fitness under realistic incentives. Method-reuse is closer to truth-tracking — methods that work get reused, methods that don't get abandoned — and so receives the largest weight. Replication mentions and inverse retraction are weaker but more direct truth-tracking signals. Raw normalized citation is retained as a substantial component (25%) because it is the most-measurable and least-noisy single signal.

**Empirical characterization (added v1.2, post-Phase-1 corpus diagnostic; see §6).** Earlier versions (v1.0, v1.1) framed the flipped formula as moving "substantially away from transmission-fitness toward truth-tracking." Phase 1 corpus diagnostics show this framing was overstated. Measured on the Pilot 1A NLP corpus (n=500, see DECISIONS D-007):

- ρ(Impact_primary, raw citationCount) = **0.865**
- ρ(Impact_sensitivity, raw citationCount) = **0.964**
- Effective movement between transmission-weighted (sensitivity) and flipped (primary) formulas: **Δρ = 0.099** — modest, not substantial.
- Decomposition: NormalizedCitation alone has ρ=0.978 with citations (mechanical, by construction at 25% weight); MethodReuseSignal alone has ρ=0.528 (moderate independent signal); ReplicationSignal alone has ρ=0.286 (weak independent signal).
- Approximately 25% of Impact_primary variance is **non-citation residual** — that is the variance space in which the discrimination test (§5.1) operates.

The formula's discriminative purpose is therefore narrower than the original "substantial movement" framing implied: it tests whether LLM-as-judge can capture the residual ~25% of impact variance that is *not* explained by raw citation count. This is a high but defensible bar, addressed directly by the partial-correlation test added in v1.2 §5.1.

**Acknowledged limitations of flipped weights.** Method-reuse has its own bias toward usability — easy-to-implement methods get reused even if not the most rigorous. NormalizedCitation by construction tracks citations and dominates the weighted sum's correlation with raw citations. The multi-component composite plus sensitivity analyses (§3.4) and the partial-correlation test (§5.1) are intended to address these biases together rather than dilute them in isolation.

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
- **`EleutherAI/pythia-6.9b-deduped`** (revision: `main` branch == `step143000`) — contamination control. Trained on The Pile (deduplicated variant). The Pile's arXiv subset was constructed from the **July 2020 arXiv dump** ([Gao et al. 2020 / Pile paper](https://arxiv.org/abs/2101.00027); [Biderman et al. 2022 / Pile datasheet](https://arxiv.org/abs/2201.07311)), so papers submitted on or after **2020-08-01** are temporally clean of direct arXiv inclusion in Pythia's training data. The deduplicated variant is preferred over the non-deduped to reduce verbatim memorization confound; it shares the same temporal cutoff. Apache 2.0 license.

**Pilot 1B additional models (if 1A passes gate):**
- `claude-sonnet-4-6` (mid-tier, scaling check)
- **`openai-community/gpt2-xl` (1.5B)** — strict pre-2020 cutoff floor reference. WebText training data has Reddit-link cutoff December 2017, scrape cutoff approximately 2018. Much weaker model overall, but cleanest temporal-cutoff guarantee for the entire 2020-2022 corpus. If even GPT-2 shows above-baseline discrimination, that strongly bounds contamination as the explanation.

**Subset restriction for Pythia comparison.** Because the Pile arXiv subset cuts off at the July 2020 dump, Pythia's training data overlaps the first ~7 months of our 2020-01-01 to 2022-12-31 corpus. Any analysis involving the Pythia arm therefore uses the **Pythia-eligible subset**: papers with arXiv v1 submission date ≥ 2020-08-01. This drops approximately 19% of the NLP corpus (~95 papers from 500), leaving ~405 for the Pythia comparison. Frontier-model analyses (Opus-only, and frontier vs. baseline) use the full 500-paper corpus — frontier models' training cutoffs are post-2022 and thus not subject to the same contamination concern (Opus has potentially seen all 2020-2022 papers; this contamination affects the test as discussed below, but it is uniform across the corpus rather than time-asymmetric, so subset restriction does not address it).

**Secondary contamination via Pile-CC and OpenWebText2.** Even after 2020-08-01, papers heavily discussed on the web before the full Pile freeze (late 2020) could leak into Pythia's training via the Common Crawl and OpenWebText2 components. This is bounded by reporting Pythia performance stratified by submission month and looking for a discontinuity at the 2020-08-01 cutoff. If Pythia performance on Aug-Dec 2020 papers differs sharply from 2021-2022 papers in the same direction as the contamination hypothesis predicts, we treat the leakage as material; otherwise, we report it as small.

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

**Frontier-model arm (Opus, Sonnet — generation protocol).** For V1: parsed integer. For V2: weighted average of (a, b, c, d) with weights (0.25, 0.25, 0.25, 0.25); also retain (d) alone. For V3: parsed final integer. For V4: mean of confidence ratings, weighted by 1 (uniform). Outputs that fail to parse after lenient regex (extracting first 1-10 integer in expected position) are flagged as "unparseable" and discarded symmetrically across all models in the same comparison; rate of unparseables reported.

**Contamination-control arm (Pythia 6.9B-deduped, GPT-2 1.5B — log-likelihood protocol).** Base models without instruction-tuning are unreliable at producing structured generated output. To eliminate the format-failure confound from the contamination test, score is computed directly from token log-probabilities rather than by parsing generated text:

For each rating position (V2 dimensions a, b, c, d), the prompt is constructed up to and including the dimension prefix (e.g., `"...(d) overall promise: "`), then for each candidate rating *k* ∈ {1, 2, ..., 10}, compute P(`str(k)` | prompt) using the model's forward pass. The argmax-*k* is taken as the predicted rating.

**Pseudocode (binding specification):**

```
def score_dimension(model, tokenizer, prompt: str, dim_label: str) -> int:
    # prompt = full V2 prompt up to and including "(<dim_label>): "
    base_ids = tokenizer.encode(prompt, add_special_tokens=False)
    log_probs = {}
    for k in range(1, 11):
        candidate_ids = tokenizer.encode(str(k), add_special_tokens=False)
        # Chain rule over candidate token sequence:
        #   log P(c_1, c_2, ..., c_n | prompt)
        #   = sum_i log P(c_i | prompt + c_1..c_{i-1})
        log_p = 0.0
        ctx_ids = base_ids[:]
        for tok_id in candidate_ids:
            logits = model(ctx_ids).logits[-1]          # next-token logits
            log_p += log_softmax(logits)[tok_id]
            ctx_ids = ctx_ids + [tok_id]
        log_probs[k] = log_p
    return argmax(log_probs)                            # predicted rating in {1..10}
```

Tokenization is verified at launch via `tokenizer.encode()` for each k ∈ {1,...,10}; the verification result (which k are single-token, which are multi-token) and the exact tokenizer revision SHA are recorded in `REPRODUCE.md` before any data is collected. The pseudocode above handles both cases uniformly via the chain rule, so single-token vs multi-token does not change the protocol — it only affects compute cost.

**Why log-likelihood for the contamination arm.** This protocol (a) sidesteps Pythia's instruction-following weakness entirely, (b) matches the standard evaluation protocol in the Pythia paper itself, (c) produces deterministic integer ratings with no parse failures, and (d) preserves the parity of the discrimination test — both arms produce a 1-10 integer per dimension, both are normalized to ranks before computing Spearman ρ, and the test is rank-based throughout. Justifications (the "briefly justify each" portion of V2) are not required from the contamination arm; they are not load-bearing for the discrimination test, and asking a base model to produce them invites the format-failure mode the protocol is designed to avoid.

**Asymmetry acknowledgment and scale-comparability.** This is a meaningful protocol asymmetry between arms (frontier = generation, contamination = log-likelihood). The two protocols produce nominally on the same 1–10 scale but via different elicitation mechanisms, so the *distributions* of scores are not directly comparable in absolute terms — Pythia's argmax-from-logits and Opus's free-form generation will not in general yield the same calibration even on identical inputs. Two consequences:

1. **Primary success criterion (§5.1) is robust to this asymmetry.** Spearman ρ depends only on within-arm rank order, not absolute calibration. The Opus arm primary test compares Opus ρ vs. citation-velocity baseline ρ — Pythia is not in this comparison at all. Subset restriction does not affect §5.1.
2. **Cross-arm comparisons in §5.2 (items 4, 5, 5a) are bounded by the asymmetry.** The Opus-vs-Pythia gap (§5.2 #4) confounds protocol choice with model capability and contamination. Mitigation: Pilot 1B includes a `claude-sonnet-4-6` log-likelihood-scored variant on the Pythia-eligible subset, so the Opus-vs-Sonnet gap (both via generation) and the Sonnet-via-generation-vs-Sonnet-via-log-likelihood gap can be computed separately. If protocol choice explains a substantial portion of the Opus-Pythia gap, that effect is visible in the Sonnet within-model comparison and the Opus-Pythia gap is interpreted accordingly. Calibration analyses on absolute scores (§5.2 #2 reliability diagram) are computed within-arm only — no cross-arm calibration is reported.

**Pre-specified primary score:** V2 (overall promise rating, dimension (d)) from `claude-opus-4-7`. All others are secondary.

### 4.5 Total inference scope

**Pilot 1A (gate decision):** 500 NLP papers for Opus arm (V2 generation) + ~405 papers for Pythia arm (V2 log-likelihood, restricted to Pythia-eligible subset per §4.1) = ~905 inferences. Estimated cost: **~$10-15 total** — Opus dominant via API (~$5-10 for ~500 inferences with V2 prompt), Pythia via Hugging Face Inference Endpoints A10G (on-demand spin-up, run, tear down: ~$1-2; minimum 1-hour billed; revision SHA pinned for reproducibility).

**Pilot 1B (contingent on 1A passing):** additional 1,000 papers (CV + RL, 500 each) × 4 prompts × 4 models (subject to log-likelihood protocol restriction for base-model arms) ≈ 12,000-16,000 additional inferences depending on which arms run on which subsets. Plus author-unblinding sub-experiment (§5.2 item 9) on 100 papers. Estimated additional cost: $30-60.

Total if both stages run: **~$50 worst case**. If 1A fails gate, project stops at ~$15. (Cost estimate revised downward from prior version after switching Pythia to Hugging Face Inference Endpoints from ad-hoc local inference; see CHANGELOG.md.)

---

## 5. Statistical analysis

### 5.1 Primary tests (gate criterion for Pilot 1A)

Two co-primary tests, both pre-specified, both required to pass for the stage gate (§11) to be met. Each addresses a distinct substantive question about LLM-as-judge.

#### 5.1.A Marginal test — does the LLM beat the trivial bibliometric baseline?

**Test:** Spearman ρ between V2-overall score from `claude-opus-4-7` and composite Impact (primary flipped formula, §3.1), computed on all 500 NLP papers in Pilot 1A.

**Baseline:** Spearman ρ between citation velocity (citations accrued in first 12 months post-arXiv-submission, computed from Semantic Scholar timestamps) and the same composite Impact, on the same 500 papers.

**Success criterion 5.1.A:** point estimate (ρ_LLM − ρ_baseline) ≥ 0.05 AND bootstrapped 95% CI of the difference excludes zero (10,000 bootstrap resamples, paired-paper resampling).

**What it measures.** Whether LLM-as-judge produces a more informative ranking of impact than the simplest possible non-semantic heuristic (year-1 citation count predicting year-4 impact).

#### 5.1.B Partial-correlation test — does the LLM add value beyond raw citations?

**Motivation (added v1.2 from §3.1 empirical characterization).** Phase 1 diagnostic showed Impact_primary correlates ρ=0.865 with raw citationCount; only ~25% of Impact variance is non-citation residual. The marginal test (5.1.A) can therefore be passed by an LLM that essentially recapitulates citation patterns. The partial-correlation test directly asks whether the LLM contributes *additional* discriminative information beyond what raw citations already encode.

**Test:** Partial Spearman ρ between V2-overall score from `claude-opus-4-7` and composite Impact_primary, controlling for raw citationCount (rank-residual approach: regress LLM rank on citation rank, regress Impact rank on citation rank, compute Spearman ρ between residuals; equivalent to standard partial Spearman).

**Success criterion 5.1.B:** partial ρ ≥ 0.15 AND bootstrapped 95% CI excludes zero (10,000 bootstrap resamples, paired-paper resampling on the underlying 500 papers).

**Why 0.15 threshold.** Partial Spearman ρ is bounded [-1, +1] but typically smaller in magnitude than marginal ρ. With n=500 and bootstrap CI width ~0.07, partial ρ ≥ 0.15 is non-trivially distinguishable from zero and represents ~2.25% of variance not shared with citations — small effect size that is nonetheless substantively meaningful for a discriminative test. Pre-committed to avoid post-hoc threshold tuning.

**What it measures.** Whether LLM-as-judge captures impact-relevant signal that is genuinely orthogonal to (not derivable from) raw citation counts. Directly tests the project's central claim that LLM judgment adds value beyond pure transmission proxies.

#### Combined gate

**Stage gate (§11) success requires BOTH 5.1.A AND 5.1.B to pass.** This preserves the discipline of the binary hard gate.

**Possible mixed outcomes (informative but gate fails):**
- 5.1.A passes, 5.1.B fails → LLM adds value over trivial baseline but not beyond raw citations; result is "LLM ≈ citation-count proxy with extra cost" — gate fails, no Pilot 1B.
- 5.1.A fails, 5.1.B passes → LLM captures non-citation signal but doesn't beat baseline; result is "LLM has independent signal but signal too weak to beat trivial heuristic" — gate fails, no Pilot 1B.
- Both fail → clean null. Gate fails, no Pilot 1B, project pivots.
- Both pass → discriminative, additive over citations. Gate passes, Pilot 1B launches.

All outcomes reported in writeup regardless of gate decision.

**Why ρ over AUC for primary.** AUC requires dichotomization which discards information from the middle 40% of impact tier and makes the task artificially easier (only extremes compared). ρ uses all 500 papers and the full impact distribution, providing higher statistical power and more directly reflecting the use-case (rank-ordering of ideas). AUC retained as secondary (§5.2 #1) for interpretability.

### 5.2 Secondary analyses (pre-specified)

All reported regardless of primary outcome.

1. **AUC for top-30% vs. bottom-30%** dichotomization, with same baseline-relative threshold (AUC_LLM − AUC_baseline ≥ 0.05, paired DeLong CI excludes zero). For interpretability.
2. **Calibration:** reliability diagram and Brier score for V2-overall as a probability proxy.
3. **Original (transmission-weighted) impact formula** (§3.1 sensitivity formula) as alternative target. Test: ρ_LLM − ρ_baseline on this target. *Hypothesis: gap is smaller against transmission-weighted target, since baseline (citation velocity) is itself a pure transmission signal and so its predictive ceiling rises against transmission-aligned targets. If LLM gap *narrows* against transmission-weighted target, this is evidence the LLM's signal goes beyond pure transmission-correlation.*
4. **Pythia vs. Opus discrimination gap.** ρ_Opus − ρ_Pythia, computed on the **Pythia-eligible subset** (papers with arXiv v1 submission ≥ 2020-08-01; ~405 papers, see §4.1). Stratify by paper fame (high/low citation percentile) — if gap concentrates in high-fame papers, contamination plausible; if uniform, capability gap more likely (§4.1).
5. **Inter-model disagreement signal.** Does |Opus − Pythia| score correlate with impact independently of mean? Tests whether disagreement itself carries information about idea novelty/risk. Computed on the Pythia-eligible subset.
5a. **Pile-cutoff discontinuity test.** Tests whether secondary contamination via Pile-CC / OpenWebText2 (web crawl components of The Pile, frozen late 2020) materially leaks 2020 papers into Pythia's training despite the arXiv subset cutoff at July 2020.

   - **Strata:** within the Pythia-eligible subset (arXiv v1 ≥ 2020-08-01), partition into S₁ = Aug-Dec 2020 papers (n ≈ 70-80 in NLP), S₂ = 2021-2022 papers (n ≈ 320-340 in NLP).
   - **Test statistic:** Δρ = ρ_Pythia(S₁) − ρ_Pythia(S₂), where each ρ is Spearman ρ between Pythia score and composite Impact within the stratum.
   - **Null hypothesis (H0_5a):** Δρ = 0 (no contamination-induced performance differential between strata).
   - **Alternative (H1_5a, contamination-direction):** Δρ > 0 (Pythia performs better on the contamination-suspect stratum S₁ than on the clean stratum S₂, consistent with secondary leakage giving Pythia an unfair advantage on Aug-Dec 2020 papers).
   - **Inference procedure:** 10,000 paired bootstrap resamples (papers within strata resampled with replacement); report point estimate Δρ, bootstrapped 95% CI of Δρ, and one-sided bootstrap p-value for H1_5a.
   - **Decision rule (trichotomy):**
     - **Material contamination:** Δρ ≥ 0.05 AND lower bound of 95% CI > 0. Pythia-arm results on Aug-Dec 2020 papers withheld from cross-arm comparisons; only 2021-2022 stratum used in §5.2 #4 and #5.
     - **Inconclusive:** 0.02 ≤ Δρ < 0.05 OR 95% CI overlaps zero. Pythia results on the full Pythia-eligible subset reported with explicit caveat that secondary contamination effect cannot be bounded as small; this caveat propagates to interpretation of §5.2 #4 (Pythia vs. Opus gap may include contamination component).
     - **Bounded as small:** |Δρ| < 0.02 AND 95% CI width < 0.10. Secondary contamination treated as not material; Pythia results on full Pythia-eligible subset interpreted at face value.
   - **Power note:** with n₁ ≈ 75 and n₂ ≈ 330, this test has limited power against small effects (Δρ ≈ 0.03-0.05 detection threshold roughly). A null result therefore bounds secondary leakage as small but cannot rule it out entirely. Acknowledged as a sensitivity test, not a definitive contamination check.

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
| LLM saw paper in training | Pythia 6.9B-deduped contamination control (1A); GPT-2 1.5B floor (1B); fame-stratified analysis (§5.2 #4) | Cannot cleanly isolate from capability gap; bounded only |
| Pile arXiv subset cutoff at July 2020 dump (Gao et al. 2020; Biderman et al. 2022) means Pythia training overlaps Jan–Jul 2020 papers in our corpus | Pythia analyses restricted to **Pythia-eligible subset** (arXiv v1 ≥ 2020-08-01), §4.1; secondary contamination via Pile-CC/OpenWebText2 tested via Pile-cutoff discontinuity test (§5.2 #5a) | Direct arXiv path eliminated for Pythia subset; secondary web-crawl path bounded but not eliminated |
| Citation count tracks prestige not quality | Flipped composite formula de-emphasizing citations to 25%; sensitivity test against original transmission-weighted formula (§5.2 #3) | Real but bounded |
| Stratified sampling distorts base rates | Disclosed; primary metric is rank-based (Spearman ρ) | None for ρ |
| Prompt sensitivity | V2 pre-specified for primary; V1/V3/V4 in 1B for sensitivity | Low |
| Outcome measure is itself biased | Multi-component composite, sensitivity analysis on weights (§3.4) | Real and acknowledged |
| Subfield-specific dynamics | NLP primary in 1A; CV/RL robustness in 1B | Mitigated, not eliminated |
| Method-reuse bias toward usability | Acknowledged in §3.1; component capped at 35% | Real, structural |
| Pythia weak capability confounds with no-contamination | Fame-stratified analysis (§5.2 #4); GPT-2 floor in 1B | Cannot fully resolve |
| Impact_primary correlates ρ=0.865 with raw citationCount on Pilot 1A corpus (added v1.2 from Phase 1 diagnostic; full decomposition in DECISIONS D-007) — only ~25% of Impact variance is non-citation residual | Partial-correlation test (§5.1.B) directly tests LLM contribution beyond raw citations, controlling for the dominant transmission component | Marginal test (§5.1.A) inevitably confounded with citation-velocity baseline; partial test bypasses the confound |
| InverseRetractionScore is constant 1.0 in current implementation (Retraction Watch + arXiv-withdrawal cross-check + flagged-by-citing-papers multiplier deferred per REPRODUCE.md known limitations) | Constant component contributes uniform 0.15 offset to all scores; rank-based primary tests (Spearman ρ, partial ρ) are invariant to constant offsets — discriminative power unchanged. Verified: ρ(Impact_primary, Impact_no_IRR_renormalized) = 1.000 | Component not contributing variance; if non-zero retraction count later verified for any sample paper, IRR can be recomputed without affecting Phase 2 outputs |
| Semantic Scholar `/citations` endpoint capped at offset+limit < 10000; one paper in Pilot 1A NLP corpus (arXiv 2203.02155, InstructGPT, 20,158 citations reported) has only its first 9,000 citations pulled. S2 intent-classifier is also empirically sparse for super-popular papers (this paper's raw_method_reuse = 0.001) | Documented as known per-paper limitation; that paper's Impact_primary likely understated relative to its actual influence. Sensitivity check: re-run primary tests with this paper excluded to verify it does not drive the gate decision | One outlier with biased Impact estimate; bounded effect on rank-based test (single rank position misplaced) |

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

For each version (v1.0, v1.1, ...):
1. Generate SHA-256 of this file: `shasum -a 256 02_pre_registration.md`
2. Record the hash and UTC timestamp in `HASH.md`
3. OpenTimestamps stamp: `ots stamp 02_pre_registration.md` and commit `02_pre_registration.md.ots`
4. Commit to git; tag the commit `prereg-v1.x`
5. Push to public remote (independent timestamp via host platform)

After hash-lock, this file is immutable for the locked version. Subsequent revisions follow §0 (Revision policy) — they atomically replace the working file and produce a new versioned hash, ots stamp, and tag, while the prior version remains in git history under its original tag. Once data collection begins, the file is fully locked and any subsequent design change becomes a deviation (§9, `DEVIATIONS.md`).

---

## 11. Stage gate: Pilot 1A → Pilot 1B contingency

The pilot is split into two stages with a hard gate between them, to bound resource commitment and reduce scope-creep risk.

### 11.1 Pilot 1A — minimum viable test

**Scope:**
- Subfield: NLP (`cs.CL`) only
- Corpus: 500 papers for Opus arm (stratified per §2.3); ~405 papers for Pythia arm (Pythia-eligible subset, arXiv v1 ≥ 2020-08-01, per §4.1)
- Prompt: V2 only (structured)
- Models: `claude-opus-4-7` (generation) + `EleutherAI/pythia-6.9b-deduped` (log-likelihood scoring, §4.4)
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
