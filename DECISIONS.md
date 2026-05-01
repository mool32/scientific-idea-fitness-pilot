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

**Update (2026-05-01, post-research):** the "Pile cutoff approximately late 2019/early 2020" characterization in this entry was wrong. Verified via Pile paper and datasheet that arXiv subset cutoff is the **July 2020 dump**. This factual error propagated into pre-registration v1.0 §4.1 and was the trigger for the v1.0 → v1.1 revision. See D-005 below.

---

## D-005 — Handling of factual error discovered in v1.0 pre-registration (2026-05-01)

**Trigger.** Research-agent investigation of the Pythia contamination control (D-004 dependency) surfaced that the Pile arXiv subset cuts off at the July 2020 dump, not "late 2019/early 2020" as I had stated in v1.0 §4.1 (and in D-004). Concretely: papers in the corpus submitted between 2020-01-01 and ~2020-07-31 (~19% of corpus) were in Pythia's training data, defeating the contamination-control purpose for that subset. Discovered ~30 minutes after v1.0 hash-lock and public push to GitHub. No data had been collected.

**Three options considered.**

- **A. Issue v1.1 (revised pre-registration with new hash, ots, tag), keeping v1.0 in git history.**
- **B. Keep v1.0 hash-locked as the canonical pre-registration; document implementation differences in DEVIATIONS.md as run-time deviations from pre-registration.**
- **C. Accept the contamination on the 19% subset; report as known limitation; run as written.**

**Resolution.** Option A. With formal revision policy committed simultaneously (v1.1 §0).

**Reasoning for A over B.** Pre-registration discipline exists to prevent post-hoc adjustment under pressure of seen data. The discovery was pre-data and the change corrects a factual error in a document that was meant to accurately specify the test, not strategic adjustment after seeing outcomes. Treating pre-data factual correction as a discipline violation would be cargo-cult — enforcing the form of pre-registration while undermining its substantive purpose (which is to *make the test interpretable*, not to be ritually immutable). Option B preserves strict immutability but creates worse incentive: discrepancies between pre-reg and what's actually run obscure rather than clarify. Option A preserves immutability *of the original artifact* (v1.0 stays in git history with its tag and ots stamp) while updating the canonical document to actually describe what will happen.

**Reasoning for A over C.** Option C runs the test with known contamination on 19% of the corpus. Positive Pythia performance on that subset becomes uninterpretable — could be discrimination, could be memorization. The whole purpose of the contamination control arm is to remove this ambiguity; accepting it back is self-defeating.

**Precedent constraint.** Option A establishes a precedent that pre-registrations can be revised. Without explicit constraint this would erode the discipline. Mitigated by formalizing a revision policy (v1.1 §0) with five conditions, all of which must be met: pre-data, factual correction not strategic adjustment, prior version preserved in git history, atomic replacement with new hash/ots/tag, CHANGELOG.md entry with attestation. The policy is itself part of the pre-registration — future revisions either conform or openly violate, both of which are visible to outside readers. This makes the discipline enforceable by structure rather than by intent.

**Residual concern acknowledged.** The line between "factual correction" and "strategic adjustment dressed as factual correction" is judgment-dependent. The policy reduces but does not eliminate this risk. Mitigation: every revision triggers a CHANGELOG entry with explicit data-collection attestation and rationale, and a DECISIONS entry with the reasoning trace. Inspectability creates the *possibility* of external check; in practice, at solo-researcher scale, primary discipline remains self-imposed, with retrospective external accountability only if and when the work is presented externally. The structural mechanisms reduce the cost of inspection but do not by themselves perform it.

**Meta-note on this entry.** This very arbitration is exactly the data type the larger project aims to capture as a first-class artifact in scientific work — the kind of "how did we decide what to do when we discovered something mid-design" trace that gets lost in conventional research outputs. Captured here at the moment of decision, with raw alternatives and reasoning preserved.

---

## D-006 — Adversarial line-by-line review of v1.1 before hash-lock (2026-05-01)

**Trigger.** v1.1 draft completed by AI agent following D-005 resolution. Before hash-lock, user (sole human reviewer) requested unified diff of `02_pre_registration.md` for direct inspection rather than relying on the agent's prose summary, on the grounds that hash-lock semantically requires inspection of the actual locked text.

**Structure.** Line-by-line review against four pre-articulated specific concerns: (1) §0 captures the proposed five revision-policy conditions without drift; (2) §4.4 protocol asymmetry (log-likelihood vs. generation) creates scale-comparability complications that need acknowledgment; (3) §4.4 log-likelihood scoring needs explicit pseudocode, not just narrative; (4) §5.2 #5a (new Pile-cutoff discontinuity test) needs formal statistical specification (null, statistic, decision threshold) on par with other pre-registered analyses. Plus a request for §6 contamination table to include a Pile-cutoff row for completeness.

**Outcome.** All four concerns identified as material and addressed pre-lock: pseudocode added as binding spec, asymmetry-and-scale-comparability paragraph added with two explicit consequences and Sonnet-as-mitigation pointer, §5.2 #5a given full statistical spec with trichotomy decision rule (later refined further during this same review pass — see below), §6 row added with citations. Sign-off given conditional on two final tightening edits: D-005 last sentence (inspectability claim weakened to accurately describe solo-researcher discipline), §5.2 #5a middle zone behavioral consequence made explicit (what to do with Pythia results when contamination test is inconclusive).

**Meta-note.** Adversarial review by an independent reviewer is one of the institutional features Hong-Henrich identify as making transmission of incorrect ideas costly enough that truth-tracking dominates over time. This review session is a miniature instance of exactly that mechanism — without it, the agent's summary would have been hash-locked unchecked, and several specific weaknesses (hand-wavy scale comparability, narrative-only pseudocode, underspecified statistical test) would have entered the locked text. The review imposed cost on incorrect transmission and prevented drift. Captured here to illustrate that the project's larger thesis (institutional features as cost-imposing mechanisms aligning transmission and truth-fitness) operates not just at the macro scale of scientific institutions but at the micro scale of individual document revisions. Adversarial review is not nicety — it is the mechanism.

**Limitation.** "Independent reviewer" here is the same human who authored the original design intent and is collaborating with the agent on the pre-registration. Adversarialness is asymmetric: the reviewer can challenge the agent's drafting, but no one challenges the reviewer's framing. At larger scale this would be addressed by genuinely independent reviewers (peer review, replication teams). At pilot scale, this is a real limit acknowledged.

---

## Convention for future entries

When a new arbitration moment occurs (during execution, analysis, or write-up), append a new D-NNN entry with the same structure. If the moment leads to a deviation from pre-registration, *also* document in `DEVIATIONS.md` per §9 procedure, with cross-reference between the two files.

The intent is that someone reading this file in 6 months can reconstruct not just *what* was decided but *why* and *what residual uncertainty was acknowledged*. This is the data type that the project's larger infrastructure aims to capture systematically.
