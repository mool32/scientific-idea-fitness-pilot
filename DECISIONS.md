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

**Update (2026-05-02, post-Phase-1 + post-citation re-pull):** Impact_scored_500.jsonl recomputed using the citations file re-pulled with citingPaper.publicationDate (added for citation-velocity baseline computation §5.1.A). New ρ values vs. v1.2-cited values: ρ(Impact_primary, citations) 0.865 → 0.8611 (Δ=0.0039); ρ(Impact_sensitivity, citations) 0.964 → 0.9639 (Δ=0.0001); Δρ between formulas 0.099 → 0.1028 (Δ=0.0038). All shifts well below the pre-specified 0.02 cosmetic threshold. New Impact ground truth used for Phase 2 tests is now internally consistent with the citations file used for the citation-velocity baseline (eliminates data-vintage inconsistency between Impact target and baseline predictor).

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

## D-007 — Phase 1 diagnostic, framing correction, and partial-correlation test addition (2026-05-02)

**Trigger.** Phase 1 corpus construction completed end-to-end (24K arXiv, S2 enrichment, stratified 500, 68K citations, composite Impact computed). Initial agent reporting of Impact distribution included framing that the flipped formula "moves substantially away from transmission-fitness toward truth-tracking" with a top-paper case as illustration. Human reviewer flagged this framing as overstated, noting that ρ(Impact_primary, citations) = 0.865 is high and might mean the primary test (§5.1 marginal Spearman ρ) is approximately measuring "LLM vs. citations" with a small additional component. Three explanations to discriminate:
- (a) Components naturally correlate with citations in this corpus
- (b) Implementation collapses signal (e.g., sparse intent classification)
- (c) Test relevance is in residual variance after controlling for citations

**Diagnostic findings (full numerical detail in commit ccdb61b...931ad33 analysis output, summarized here):**

Component decomposition vs. raw citationCount on the Pilot 1A NLP corpus (n=500):
- NormalizedCitation: ρ = +0.978 (mechanical, by construction at 25% weight)
- MethodReuseSignal (cell-normalized): ρ = +0.528 (moderate independent signal)
- ReplicationSignal (cell-normalized): ρ = +0.286 (weak independent signal)
- Impact_primary (composite): ρ = +0.865
- Impact_sensitivity (composite): ρ = +0.964
- Effective movement primary vs. sensitivity formula: Δρ = 0.099

Cross-correlations (independence of components):
- ρ(MethodReuseSignal, ReplicationSignal) = +0.013 — components are essentially orthogonal, capturing different things
- ρ(MethodReuseSignal, NormalizedCitation) = +0.497
- ρ(ReplicationSignal, NormalizedCitation) = +0.268

Implementation correctness (b vs. a/c discriminator):
- Per-paper intent-classification rate vs. citationCount: ρ = +0.041 — uncorrelated. Denominator of MethodReuseSignal is honest; classification rate is not biased by paper popularity. Implementation is correct.
- Raw count of method-reuse-classified citations (numerator only) vs. total citations: ρ = +0.887 — confirms that count-based signal would have been pathologically citation-driven; the pre-reg's choice of fraction was correct.

Top/bottom tier overlap (formula vs. raw citation ranking):
- Top-30% Impact_primary vs. top-30% citations: 119/150 (79%) overlap
- Bottom-30% Impact_primary vs. bottom-30% citations: 136/150 (91%) overlap (largely tied at 0 citations)
- Top-10 vs. top-10: 4/10 — substantive disagreement at the head of the distribution
- Top-10 by Impact_primary that are NOT top-10 by citations are typically papers with moderate citation counts (340–1280) but high method-reuse fraction (0.24–0.37) and moderate replication-mention counts

InverseRetractionScore as constant 1.0 (rank effect):
- ρ(Impact_primary, Impact_no_IRR_renormalized) = 1.000
- ρ(Impact_no_IRR_renormalized, citations) = 0.865 — identical to original
- IRR's role is purely a constant 0.15 floor; rank-based primary tests are unaffected. Component is bookkeeping only.

S2 citation cap on InstructGPT paper:
- arXiv 2203.02155, 20,158 reported citations, 9,000 pulled before S2's offset+limit < 10000 cap
- S2 intent classifier sparse for this paper (raw_method_reuse = 0.001 — only ~9 of 9,000 sampled classified as methodology)
- Likely Impact_primary is understated for this paper; documented in §6 limitations table

**Verdict on (a) / (b) / (c).**
- (b) NO — implementation is correct, validated by intent-rate independence from citations
- (a) PARTIALLY — fraction-based components have moderate correlation with citations (0.528, 0.286), and NormalizedCitation has high correlation by design (0.978). The composite's high correlation is structural, not pathological.
- (c) YES — approximately 25% of Impact_primary variance is non-citation residual; the test's discriminative purpose lives in that residual.

**Action options considered:**

- **Option A (Path A in reviewer framing):** Revise pre-registration to v1.2. Specifically: (i) §3.1 framing correction to honestly characterize Δρ = 0.099 movement, (ii) §5.1 add partial-correlation test as co-primary alongside marginal test, (iii) §6 expansion with diagnostic findings, (iv) D-007 captures full diagnostic and revision rationale.

- **Option B (Path B in reviewer framing):** Keep pre-registration v1.1, document framing mismatch as honest limitation in DECISIONS.md only, plan to address in final report's limitations section. Add partial-correlation analysis as secondary via DEVIATIONS.md noting it's added pre-data based on Phase 1 diagnostic.

**Resolution.** Option A. Revised to v1.2.

**Reasoning.** §0 condition 1 ("no data has been collected since the prior version") is most naturally read as protecting against post-hoc adjustment driven by predictive results (LLM_pred vs. Impact). Phase 1 corpus construction yields descriptive properties of the measurement instrument, not predictive results. Realizing that the instrument's behavior differs from the pre-reg's framing claims is a factual correction parallel to the v1.0 → v1.1 Pile-cutoff correction: claim in pre-reg does not match reality, pre-data, correctable through revision per §0 conditions 2–5. The partial-correlation test is added because the marginal test (5.1.A) is now visibly confounded by the dominant citation component; partial test (5.1.B) directly addresses the project's substantive claim (LLM judgment adds value beyond raw citations). Adding it pre-data does not bias the test direction because no LLM outputs have been computed.

**Counter-argument acknowledged.** Pre-registration revisions accumulate credibility cost. v1.2 is the second revision in two days. The cost is real but bounded: each revision is fully documented (CHANGELOG entry, DECISIONS entry, hash, OpenTimestamps proof, public push), and the alternative (Option B) creates exactly the kind of pre-reg-vs-actual mismatch that revision policy exists to prevent. The v1.2 revision satisfies all five §0 conditions; if the policy is correctly designed, this is the case it permits.

**Conformance attestation.** v1.2 satisfies §0 conditions: (1) no LLM predictions or test outcomes computed; corpus construction is descriptive measurement, not predictive analysis (judgment call documented above); (2) revision is factual correction (§3.1 framing) plus analysis improvement informed by descriptive diagnostic (§5.1 partial test) — neither motivated by reasoning about expected test outcomes; (3) v1.0 and v1.1 preserved in git history at their tags with original ots proofs; (4) atomic replacement of working file with new SHA, ots, tag prereg-v1.2; (5) CHANGELOG entry documents transition with explicit attestation.

**Residual concern acknowledged.** The "descriptive vs. predictive data" distinction within §0 is a judgment call I introduced in this entry; future revisers could stretch it. Mitigation: the policy's wording remains literal ("no data has been collected") and any future revision that invokes this distinction must do so in DECISIONS with explicit reasoning showing why corpus-side data is non-bias-inducing. The structural protection is intact; the discretion lives in the public reasoning trace.

**Independent of the revision.** Even if the reviewer had chosen Option B, three operational facts surfaced by this diagnostic stand:
- The marginal test (§5.1 v1.1) is meaningfully confounded by citations and harder to interpret cleanly than originally framed
- The partial-correlation analysis is more directly relevant to the project's central claim
- IRR-as-constant has zero effect on the rank-based primary test; all 15% weight is absorbed as constant offset

These facts inform Phase 2 interpretation regardless of whether they are reflected in the pre-reg document or only in the final report's limitations section.

---

## D-008 — Revision-frequency pattern, moratorium, and adversarial-review accountability (2026-05-02, post-v1.2)

**Trigger.** After v1.2 was hash-locked and pushed, human reviewer flagged a meta-concern that became visible only by zooming out: three pre-registration revisions in 48 hours, frequency increasing rather than decreasing, and §0 itself was effectively expanded in v1.2 by introducing a "descriptive vs. predictive data" distinction that wasn't in the original policy. Each revision individually defensible; cumulatively, the pattern matches the classic mode by which pre-registration discipline erodes — not through blatant violations but through cumulative reasonable-looking adjustments.

**The v1.2 split-vs-bundle problem.** v1.2 contained three changes: (a) §3.1 framing correction with measured Δρ=0.099 — clearly factual; (c) §6 row additions describing measured properties — clearly factual; (b) partial correlation as co-primary — borderline, closer to "improved analysis informed by descriptive corpus data" than to "factual correction or ambiguity clarification." The disciplined move would have been to split (b) from (a) and (c): commit (a) and (c) as v1.2 cleanly, treat (b) as a DEVIATIONS.md entry with full disclosure that it stretches §0. Bundling all three under (a)'s strong factual-correction justification let (b) inherit (a)'s defensibility. Done is done — v1.2 stands as committed — but the lesson is "split borderline from clear in multi-part proposals", not "v1.2 should be reverted."

**Adversarial-review failure mode (Claude side).** When (b) was being drafted, the agent internally noted "this stretches §0 condition 2 ... adding a new analysis isn't 'clarifying ambiguity' — it's a new test." That counter-argument was not surfaced as an external counter-proposal; it became an internal hedge that got swept under acceptance after the human reviewer leaned toward the bundled revision and provided coherent reasoning. This is the failure mode the project's own theoretical framework warns about: when adversarial pressure depends on a single source providing it, drift in that source compromises oversight.

**Three commitments, binding from this entry forward.**

1. **Moratorium on further pre-registration revisions during Phase 2.** Until Phase 2 inference is complete and primary-test results computed, no further revisions to `02_pre_registration.md` may be made except for strict factual error in the documented sense — e.g., discovery that the Pythia checkpoint has a different training cutoff than researched, or an implementation bug in the prediction code that misrepresents the test as specified. Optimization-style changes, framing improvements, or additional analyses are explicitly out of scope. Any such additions become DEVIATIONS or post-results exploratory analyses, never pre-registered, and are reported as such in the writeup.

2. **Stage-gate binding (§5.1.A AND §5.1.B both pass).** Both co-primary success criteria from v1.2 §5.1 must be met for the stage gate (§11) to pass. Mixed outcomes (one passes, one fails) are gate fails, reported as null-or-mixed, not relabeled as "success with caveats." This commitment forecloses the "results are nuanced therefore the gate is satisfied" failure mode.

3. **Adversarial-pressure mutual maintenance.** Both human reviewer and Claude-as-agent are now on notice that drift toward co-architect role compromises oversight. Two specific behavioral commitments:
   - **Claude:** when a multi-part proposal contains borderline elements, mark them explicitly as separable and propose splitting them out, even when the overall lean is to accept. Internal "but X is borderline" thoughts become external counter-proposals, not internal hedges. If finding myself agreeing easily with a proposed change, treat that as signal of possible alignment drift rather than as evidence the change is correct.
   - **Human reviewer:** if Claude is agreeing more readily than warranted, push back with explicit challenge ("this seems too easy a sign-off"). The reviewer is also encouraged to recruit external review by a competent metascience person before Phase 2 launch — even one independent 30-minute read provides oversight that no single internal reviewer can.

**What this entry does and does not do.**
- Does NOT revert v1.2. Reverting would be its own form of motivated process. Hash-locked, pushed, public. Stands.
- Does NOT change the §0 policy text. The "descriptive vs. predictive data" distinction introduced in D-007 remains the operative interpretation, but with explicit acknowledgment that it stretched §0 and that future invocations of the same distinction must justify the same way and meet stricter scrutiny.
- DOES make the moratorium binding for the duration of Phase 2.
- DOES make the stage gate's binary character explicit and pre-committed.
- DOES create a public record of the adversarial-review failure mode as a first-class artifact.

**Why this matters beyond bookkeeping.** The project's larger thesis (Hong-Henrich) is that institutional features matter only to the extent they impose actual cost on incorrect transmission. A pre-registration policy that bends in response to reasonable-looking pressure imposes less cost than its formal text suggests. Documenting the bend and committing to a moratorium is the institutional version of "we noticed the slope and put a stop on it." The slope itself is now part of the public record, which is exactly the kind of artifact the project says future epistemic infrastructure should capture.

**Independent of the three commitments above.** The "drift then catch" pattern in this very conversation is itself functioning evidence that the structural protections (public repo, hash-locks, decision traces, this entry) are doing their job. Drift was visible, correctable, and corrected before any irreversible harm. This does not excuse the drift, but the system surviving its own slip in a documented way is the kind of outcome the larger project is supposed to enable.

---

## D-009 — External review recruitment before Phase 2 execution (2026-05-02)

**Trigger.** D-008 closed by accepting external review as the structural fix to the adversarial-review degradation pattern that emerged in this conversation. This entry records the recruitment decision, the criteria, the framing of the ask, the timeout, and the operational distinction between Phase 2 setup (proceeds in parallel) and Phase 2 execution (paused pending reviewer feedback or timeout).

**Decision.** Recruit one independent metascience reviewer before launching Phase 2 inference. Reasoning:
- D-008 already established that adversarial-review function depends on a single source providing it; external review is the structural fix, not optional supplement.
- Cost-benefit asymmetry: 1–2 days delay vs. independent check on what neither human reviewer nor AI agent is positioned to see. Phase 2 inference is bounded and reversible but external review pre-launch is much cleaner than catching issues post-launch.
- Demonstrative value: external adversarial review at hash-lock points is exactly the institutional feature that the project's larger thesis (Hong-Henrich) identifies as making transmission-fitness align with truth-fitness. Doing it on this pilot demonstrates the principle rather than only claiming it.
- Solo-researcher trap: tight collaboration loop between human and AI agent is exactly how solo work becomes intellectually inbred without anyone noticing. External human reviewer breaks the loop. Even if they catch nothing, the loop being broken matters.

**Reviewer criteria.** Strong methodology background (metascience, pre-registration, replication research) plus enough skepticism about LLM/AI claims to push back hard. Not co-architects of the project, not people already invested in its success. Candidates the human reviewer will consider: Berkeley Initiative for Transparency in Social Sciences / COS network adjacents; computational metascience researchers (Smaldino, Bergstrom group people if accessible); skeptical AI/methodology researchers in the Sayash Kapoor / Arvind Narayanan ecosystem; local academic contacts with research-methodology expertise unobligated to be supportive. Recruit one good reviewer rather than three convenient ones.

**Framing of the ask.** Not "approve this." Specifically: "is this revision pattern sustainable, and is the bundling of the partial-correlation addition with the framing correction in v1.2 a structural problem I should worry about?" Frame the request such that "no, you have a problem" is the easy answer to give — reviewers tend to soften critique unless explicitly invited to be sharp.

**Materials to share.** Full revision trail, not only v1.2: original v1.0 + D-005 (Pile-cutoff revision rationale) + v1.1 + D-007 (framing-correction + partial-correlation rationale) + v1.2 + D-008 (pattern recognition + commitments). Pattern is visible only across revisions, not in any individual document; reviewer needs the full set to answer the pattern question.

**Timeout.** 5 days from recruitment outreach. If no reviewer engagement within that window, proceed to Phase 2 execution and document the unsuccessful recruit attempt in DECISIONS as a follow-up to this entry. Indefinite wait is its own form of drift — recruitment process cannot itself become procrastination dressed as rigor.

**Operational distinction during recruitment wait.**
- **Phase 2 setup (allowed):** Pythia checkpoint verified loadable, log-likelihood scoring code written and unit-tested (per pre-reg §4.4 pseudocode), prompt template files finalized, inference scripts skeletoned, pipeline tested end-to-end on ≤5-paper smoke tests against both Anthropic API and HF Inference Endpoint. Citation-velocity baseline data pulled (citingPaper.publicationDate fields added if needed for accurate 12-month-post-submission computation). All reversible, none compromise test integrity.
- **Phase 2 execution (paused):** No full inference run on the 500-paper blinded corpus. No generation of predictions that would feed §5.1.A or §5.1.B tests. No comparison of any model output against composite Impact.

**Sign-off path.** After either reviewer feedback received and addressed, OR 5-day timeout reached, AND Phase 2 setup verified end-to-end on smoke tests, request explicit sign-off on Phase 2 execution. Sign-off conditional on no material reviewer concern surfacing that requires response.

**Dependency on the human reviewer.** Recruiting external reviewer is a social act with reputation consequences that the human reviewer owns and Claude cannot perform. Claude can draft a recruit message for the human reviewer to adapt; the actual outreach is the human reviewer's. If the human reviewer chooses not to recruit (for example, because no suitable candidate available within reasonable bandwidth), the moratorium reverts to "Phase 2 execution proceeds without external review, public artifact remains available for post-hoc inspection" with that decision documented as a follow-up to this entry.

---

## D-010 — Pythia §4.4 protocol pre-launch failure, decision to run-as-written, and pre-specified reporting language (2026-05-02)

**Trigger.** Pre-launch smoke test on the pre-registered §4.4 contamination-arm protocol surfaced that the log-likelihood scoring produces argmax=1 across all V2 dimensions for all 5 sample papers spanning the Impact_primary range, on both Pythia-70M-deduped and Pythia-1.4B-deduped (22× size difference). Log-prob margins of "1" over second-place candidates were 0.75-1.12 nats — strong, not noise. Triangulation across two model sizes with identical pathology argues structural prompt-format priming (`"(d) overall promise: "` invites `"1"` as natural numbered-list continuation in pretraining text) rather than capacity limitation. Pythia-6.9B almost certainly inherits the same pathology.

**What this means for the test as pre-registered.** §4.4 contamination-arm protocol produces uniform output for our V2 prompt construction. Implication: ρ(Pythia_score, Impact) = undefined-or-zero (constant has no rank); §5.2 #4 (Pythia-vs-Opus discrimination gap), §5.2 #5a (Pile-cutoff discontinuity test), and any other Pythia-involving analyses become null/meaningless. Frontier-arm tests (§5.1.A and §5.1.B) are unaffected — both compare Opus against citation-velocity baseline; neither depends on Pythia.

**Three options considered (decomposed per Q1-Q4 framing in human reviewer message).**
- Q1 (salvageable?) — Not without protocol revision (different prompt format, score normalization against neutral baseline, multiple-choice format, or fine-tuning). Each candidate fix would itself require validation.
- Q2 (moratorium permits revision?) — §0 condition 2 includes "discovered impossibility" in its permitted-revision list, which arguably covers a protocol that produces constant output. **However, D-008 explicitly tightened the operative exception list for Phase 2 to "strict factual error in the documented sense — e.g., wrong checkpoint cutoff, implementation bug" — narrower than §0.** Our case (faithful implementation of spec; spec produces constant output) fits §0 broadly but fits neither D-008 example narrowly. Under D-008's binding self-restriction, revision is not permitted unless we openly waive D-008, which would itself be a major credibility commitment.
- Q3 (which fix?) — moot if Q2 says no.
- Q4 (scope adjustment if no revision?) — two sub-options:
  - **A. Run as written, report documented null.** Pay HF endpoint cost (~$1-2), execute §4.4 protocol on Pythia-eligible subset, get predicted-null result, document with full transparency.
  - **C. Drop Pythia from Pilot 1A scope.** DECISIONS-level scope adjustment per pre-existing §11 staging structure; defer Pythia entirely to Pilot 1B.

**Resolution: Option A (run as written, document null).**

**Reasoning.** A produces lasting documented evidence that the §4.4 protocol fails for ML paper abstracts on accessible-capacity Pile-trained models — useful artifact for future researchers designing contamination protocols. C produces silence about Pythia from 1A and merely defers the protocol-design problem. The ~$1-2 cost differential is trivial; the documentation value asymmetry favors A.

**Pre-specified reporting language (binding before execution).** When reporting the documented null Pythia result, the writeup must include all of the following without overclaim:

1. **Statement of fact:** "On the Pythia-eligible subset (n≈419), the §4.4 log-likelihood scoring protocol produced argmax=1 for all V2 dimensions on all papers, yielding constant Pythia output. Per-paper log-prob margins of '1' over second-place candidates were [report median + range] nats."

2. **Pre-launch evidence cited:** "Pre-launch smoke testing on Pythia-70M-deduped and Pythia-1.4B-deduped (22× size range) showed identical pathology, indicating the constant output reflects structural prompt-format priming rather than model-size capacity limitation. The 6.9B run confirms the prediction."

3. **Two interpretations explicitly flagged:** "Two interpretations of this null are possible. (i) The §4.4 protocol's prompt format ('(d) overall promise: ') primes list-continuation prior toward '1' as natural completion, regardless of paper content. This interpretation predicts the protocol would fail at any model size on this prompt. (ii) Available open-model capacity (≤6.9B Pile-cutoff-pre-2020) is insufficient to override the list-continuation prior, but a hypothetical larger Pile-cutoff-pre-2020 model might succeed. Triangulation across 70M, 1.4B, and 6.9B with consistent pathology weakly favors (i), but (ii) cannot be definitively ruled out without testing a larger pre-2020-cutoff model — none readily available."

4. **Implications statement (no overclaim):** "This is a finding about the §4.4 protocol on this corpus and prompt format, not a claim about Pythia models' capacity for paper evaluation in general. Future contamination-control work on similar corpora should pre-validate the scoring protocol on small samples before committing pre-registered design."

5. **Test-impact statement:** "Pythia-involving analyses (§5.2 #4, #5a) are reported as inconclusive with the protocol-failure caveat. The frontier-arm primary tests (§5.1.A and §5.1.B) are reported on their own terms; their interpretation does not depend on Pythia output but inherits the limitation that contamination of Opus on 2020-2022 arXiv papers is not directly controlled within Pilot 1A."

This language is pre-specified before execution to prevent post-hoc drift in interpretation. Any deviation from the above structure in the actual writeup is itself a documented choice subject to its own justification.

**Rejected: Option C (drop Pythia from 1A).** Considered seriously; rejected after Claude's push-back highlighted that C produces no Pythia evidence from 1A and merely defers the protocol-design problem to 1B under similar pressures. Documented as rejected option per discipline of recording alternatives considered.

**Conformance with D-008.** This is not a pre-reg revision. §4.4 protocol runs as written. Scope is unchanged. The decision is purely about reporting language for the predicted-null result. Conforms with D-008 moratorium without invoking any exception.

**Counter-argument acknowledged.** A literal reading of pre-reg reads §4.4 as expecting variable output (otherwise the protocol's discriminative purpose makes no sense). Running a protocol the smoke tests predict will fail is arguably wasteful. But the documentation value (lasting evidence for future protocol design) and the discipline value (no pre-reg revision under crisis pressure) jointly outweigh the ~$1-2 inference cost. The waste is bounded; the benefit is durable.

---

## Convention for future entries

When a new arbitration moment occurs (during execution, analysis, or write-up), append a new D-NNN entry with the same structure. If the moment leads to a deviation from pre-registration, *also* document in `DEVIATIONS.md` per §9 procedure, with cross-reference between the two files.

The intent is that someone reading this file in 6 months can reconstruct not just *what* was decided but *why* and *what residual uncertainty was acknowledged*. This is the data type that the project's larger infrastructure aims to capture systematically.
