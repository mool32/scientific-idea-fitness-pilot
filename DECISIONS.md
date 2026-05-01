# Decision trace

This file captures arbitration moments in the design of this project. It exists for two reasons: (1) intellectual honesty — the pre-registration is the *output* of decisions, this file shows the *process* by which it was reached; (2) the project itself is about capturing exactly this kind of trace as a first-class data type for scientific work, and this is the first canonical instance.

Entries are append-only. Each entry records: the moment, what was initially proposed, what objection was raised, how it was resolved, and what residual concern (if any) remains acknowledged.

---

## D-001 — Success threshold framing (2026-05-01)

**Initial proposal.** Round-number AUC thresholds: > 0.7 = strong evidence, > 0.6 = modest evidence, < 0.55 = null. Dichotomization at top-30% / bottom-30%.

**Objection raised.** Round numbers without principled basis are exactly the kind of arbitrary choice that pre-registered designs should justify. The thresholds carried no anchor to anything substantively meaningful — what does AUC = 0.6 *mean* in this context? Furthermore, dichotomization throws away the middle 40% of papers and makes the test artificially easier than the actual use case (rank-ordering ideas).

**Resolution.** Primary metric switched to Spearman ρ between LLM score and composite Impact, anchored against citation-velocity baseline (year-1 citations predicting year-4 impact, computed on the same papers). Success criterion: ρ_LLM − ρ_baseline ≥ 0.05 with bootstrapped 95% CI excluding zero. AUC retained as secondary for interpretability with same baseline-anchored threshold.

**Residual concern acknowledged.** The 0.05 minimum gap is itself a round number. It is anchored relative to a meaningful baseline rather than to chance, which is a real improvement, but the magnitude of "meaningful improvement" remains a judgment call. Documented as a known limitation rather than resolved.

**Bonus structural prediction.** With the flipped composite formula (D-002), the citation-velocity baseline becomes a *weaker* predictor (since target is no longer pure transmission). This means the LLM-vs-baseline gap should *widen* against flipped target relative to citation-only target — added as a clean theoretical prediction in §5.2 #3.

---

## D-002 — Composite impact formula weights (2026-05-01)

**Initial proposal.** 50% normalized citation, 25% replication mentions, 15% method-reuse, 10% inverse retraction. Recommendation came from initial planning intuition about which signals are most measurable.

**Objection raised.** This formula inherits the Smaldino-McElreath problem the project is explicitly trying to escape. 50% weight on citations means 50% of the ground-truth signal is pure transmission-fitness — exactly the signal documented to systematically diverge from truth-fitness under realistic incentives. If the project's theoretical framework asserts that transmission-only signal is biased, the project's own ground truth shouldn't be transmission-dominated.

**Resolution.** Weights flipped to 25% citation / 35% method-reuse / 25% replication / 15% inverse retraction. Method-reuse takes the largest weight because it is the most direct truth-tracking proxy (methods that work get reused, methods that don't get abandoned). Original transmission-weighted formula retained as sensitivity analysis (§5.2 #3).

**Residual concern acknowledged.** Method-reuse has its own bias toward usability — easy-to-implement methods get reused even when not most rigorous. Real but bounded; documented in §3.1 and §6.

---

## D-003 — Stage gate vs. monolithic pilot (2026-05-01)

**Initial proposal.** Single sweep: 1500 papers (3 subfields × 500) × 4 prompts × 3 models = 18,000 inferences, ~$400-700, 2-3 weeks.

**Objection raised.** Scope creep risk. Each addition individually justified, but cumulative scope raises probability of pilot-paralysis — projects that grow to cover every check often don't get done. Known failure mode for this kind of work.

**Resolution.** Split into Pilot 1A (minimum viable: NLP only, 500 papers, V2 prompt only, 2 models, ~$150, ~1 week) with hard binary gate. Pilot 1B (expanded: CV + RL, all prompts, additional models, author-unblinding sub-experiment) launches only if 1A meets primary success criterion. Stop-and-write-up if 1A fails.

**Why this is principled, not just resource-saving.** If 1A fails — strongest model, easiest subfield (NLP, where LLMs have most exposure) — the absence of signal is not rescued by adding weaker models or noisier subfields. The stage structure reflects the actual epistemic structure of the test.

**Residual concern acknowledged.** None substantive. Trade-off is statistical power in 1A (smaller sample) vs. resource exposure (larger sample sweep). 500 papers in 1A gives Spearman ρ standard error around 0.04, which is sufficient to discriminate the pre-registered 0.05 minimum gap with reasonable power.

---

## D-004 — Pre-2020 contamination control choice (2026-05-01, draft)

**Initial framing.** Contamination of frontier models on 2020-2022 papers is a real risk. Need a control model with training cutoff strictly before 2020 to bound this.

**Trade-off identified.** Strict pre-2020 cutoff (GPT-2, early Pythia checkpoints on early Pile snapshots) gives rigorous contamination control but weak model capability. Late-2020/early-2021 cutoff gives stronger model but some 2020 corpus papers may be in training data.

**Provisional resolution.** Pythia 6.9B trained on the Pile (Pile cutoff approximately late 2019/early 2020) as primary contamination control in Pilot 1A. GPT-2 1.5B as floor reference in Pilot 1B for stricter cutoff guarantee. Verification of exact Pile snapshot date for the chosen Pythia checkpoint is a Phase 0 dependency.

**Residual concern acknowledged.** Pythia 6.9B is significantly weaker than `claude-opus-4-7` in general capability. If Pythia discriminates poorly while Opus discriminates well, gap could reflect (a) contamination of Opus, or (b) Pythia's weaker baseline capability. Cannot cleanly disentangle. Mitigation: fame-stratified analysis (§5.2 #4) — if Opus-Pythia gap concentrates in high-fame papers, contamination plausible; if uniform, capability gap more likely. Bounding test, not clean isolation. Documented honestly in §4.1 and §6.

---

## Convention for future entries

When a new arbitration moment occurs (during execution, analysis, or write-up), append a new D-NNN entry with the same structure. If the moment leads to a deviation from pre-registration, *also* document in `DEVIATIONS.md` per §9 procedure, with cross-reference between the two files.

The intent is that someone reading this file in 6 months can reconstruct not just *what* was decided but *why* and *what residual uncertainty was acknowledged*. This is the data type that the project's larger infrastructure aims to capture systematically.
