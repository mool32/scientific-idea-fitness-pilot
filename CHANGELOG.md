# Pre-Registration Changelog

This file documents version transitions of the pre-registration document (`02_pre_registration.md`). Each entry records the transition rationale, an attestation about data-collection state at time of revision, and pointers to the pre-existing version for verification.

Revisions are governed by the policy in `02_pre_registration.md` §0 (Revision policy). Once data collection begins, the pre-registration is fully locked and any subsequent design change becomes a deviation (see `DEVIATIONS.md`), not a revision.

---

## v1.0 → v1.1 (2026-05-01)

**Trigger.** Pre-launch research on pre-2020 contamination control surfaced two material errors and one design improvement in v1.0:

1. **Factual error in §4.1.** v1.0 characterized The Pile as "overwhelmingly pre-2020 content." This was incorrect. The Pile's arXiv subset was constructed from the **July 2020 arXiv dump** (Pile paper [arXiv:2101.00027](https://arxiv.org/abs/2101.00027); Pile datasheet [arXiv:2201.07311](https://arxiv.org/abs/2201.07311)). Pythia, trained on The Pile, therefore had direct exposure to arXiv papers submitted between 2020-01-01 and approximately 2020-07-31 — roughly 19% of the v1.0 corpus. This contamination would have invalidated the contamination-control purpose for that subset of the corpus.

2. **Design improvement in §4.4.** Pythia 6.9B is a base model without instruction tuning and is unlikely to reliably produce structured generation output as required by the V2 prompt. v1.0 implicitly assumed it could. Without correction, low Pythia performance would have been ambiguous between "model cannot discriminate ideas" and "model cannot follow output format" — not a failure mode the contamination test exists to assess.

3. **Cost estimation error in §4.5.** v1.0 estimated ~$150 for Pilot 1A. Inference costs at current API rates and the availability of Hugging Face Inference Endpoints for Pythia bring the true estimate to ~$10-15. This is a calibration error, not material to design, but worth correcting.

**Changes in v1.1.**

- **§0 (new):** Revision policy formalized. Future revisions allowed only pre-data, only for factual correction or ambiguity clarification (not strategic adjustment), with prior version preserved in git history under its original tag, and atomic replacement with new hash, OTS stamp, and tag. The policy is itself part of the pre-registration; future revisions must conform or openly violate it.
- **§4.1:** Pile cutoff stated correctly with citation. Switched from `EleutherAI/pythia-6.9b` to `EleutherAI/pythia-6.9b-deduped` (same temporal cutoff, reduces verbatim-memorization confound). Added explicit Pythia-eligible subset definition (papers with arXiv v1 ≥ 2020-08-01, ~405 papers from 500). Added secondary contamination discussion (Pile-CC and OpenWebText2). GPT-2 1.5B updated to specific HF reference (`openai-community/gpt2-xl`) with WebText cutoff stated. Frontier-model arm uses full 500-paper corpus (no time-asymmetric contamination concern).
- **§4.4:** Score extraction split into frontier-model arm (generation, parsed) and contamination-control arm (log-likelihood scoring via P(token | prompt) argmax over rating tokens). Multi-token rating handling (chain rule for "10") specified. Rationale: eliminates format-failure confound, matches standard Pythia evaluation protocol, preserves rank-based test parity. Asymmetry between arms acknowledged; Pilot 1B includes a Sonnet log-likelihood-scored variant as robustness check.
- **§4.5:** Cost estimate revised. Pilot 1A: ~$10-15 (was ~$150). Pilot 1B: ~$30-60 additional (was $400-600). Total worst case: ~$50.
- **§5.2:** Item 4 (Pythia vs. Opus gap) restricted to Pythia-eligible subset. Item 5 (disagreement signal) restricted to same. New item 5a added: Pile-cutoff discontinuity test (Pythia performance Aug-Dec 2020 vs. 2021-2022) to bound secondary contamination via Pile-CC/OpenWebText2.
- **§10:** Hash-lock procedure generalized to apply to each version (v1.0, v1.1, ...). OpenTimestamps stamping and public push made part of the standard procedure rather than optional. Cross-reference to §0 for revision rules.
- **§11.1:** Pilot 1A scope updated to reflect Pythia-eligible subset and log-likelihood protocol.

**Data-collection attestation.** As of 2026-05-01 the corpus has not been constructed, no API calls have been made, no model outputs have been collected, no outcome data has been queried, and no analyses have been run. The transition from v1.0 to v1.1 is fully pre-data.

**Verification.** v1.0 remains hash-locked at git tag `prereg-v1.0` (commit 613c0be), SHA-256 `dbc74374ac8b09011941cb41875cbcf2bee49f292a5a1eb507742e524e0b2b8e`, with OpenTimestamps proof in git history. v1.1 hash recorded in `HASH.md`.

**Author judgment.** This revision conforms to all five conditions in §0 (Revision policy). The factual error in §4.1 is a clear factual misstatement, not a strategic adjustment under pressure of seen data. The §4.4 design improvement removes a confound that would have made the test ambiguous; it is not motivated by reasoning about expected outcomes. The §4.5 cost correction is calibration, not design. Documented in `DECISIONS.md` D-005 (meta-arbitration on factual error handling).

**Pre-lock review.** v1.1 underwent adversarial line-by-line review by the human reviewer before hash-lock; four material weaknesses were identified and addressed pre-lock (pseudocode for log-likelihood protocol, scale-comparability acknowledgment, formal statistical specification for §5.2 #5a, Pile cutoff row in §6 table) plus two final tightening edits (D-005 inspectability claim, §5.2 #5a middle-zone behavioral consequence). Documented in `DECISIONS.md` D-006.

---

## Convention for future entries

If a subsequent pre-data revision becomes necessary, append a new `v1.x → v1.y` section here following the same structure: trigger, list of changes by section, data-collection attestation, verification pointers to prior version, and author judgment about conformance with §0. After data collection begins, no further revisions occur — design changes become deviations in `DEVIATIONS.md`.
