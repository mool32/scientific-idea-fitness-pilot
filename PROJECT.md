# Project context

## Why this pilot exists

This pilot tests one narrow empirical question that gates a much larger research direction. The narrow question: *can a language model, given only a paper's abstract and stripped technical content, predict its multi-year scientific impact substantially better than trivial bibliometric heuristics?*

If yes, an LLM-based fitness function for scientific ideas is empirically viable as one component of a next-generation epistemic infrastructure. If no, that path is closed and other approaches (formal predictive testing, replication outcomes, structured human arbitration) become the focus instead.

## The larger context

The pilot sits inside a project building infrastructure for scientific work in an AI-mediated environment. Three observations from the cultural-evolution and metascience literature shape the design (full treatment in `00_three_insights.md`):

1. **Cultural transmission is reconstructive, not replicative** (Sperber's Cultural Attractor Theory; Acerbi et al. 2021). When ideas travel, recipients reconstruct rather than copy. In an LLM-mediated environment this becomes literal — every "summary" is a reconstruction. Naive copy-count metrics misdescribe what's actually happening.

2. **Transmission-fitness systematically diverges from truth-fitness under realistic incentives** (Smaldino & McElreath 2016). Selection on "what gets published" produces, over time, *less* rigorous methodology, not more. The replication crisis is the empirical consequence. Any fitness function trained naively on published-success signal inherits this pathology.

3. **Alignment between transmission and truth is achievable through institutional features** (Hong & Henrich 2021). Pre-registration, replication, adversarial review, predictive testing on out-of-sample data — these are cost-imposing mechanisms that make incorrect ideas expensive to transmit. They are how science distinguishes itself from divination as an epistemic technology.

The infrastructure being built is intended to encode these features structurally rather than ritually. This pilot tests the most uncertain technical assumption: that LLM-as-judge has discriminative ability in the first place.

## What this pilot is NOT

- Not a benchmark of "best LLM for science." Pilot 1A uses a single frontier model + a contamination control. Comparative model rankings would be a different study.
- Not a measurement of LLM creativity, novelty, or generation capability. The judge function and the generator function are separate concerns.
- Not a claim that retrodictive prediction (predicting past papers' future impact) generalizes cleanly to prospective use (judging not-yet-published ideas). Retrodictive calibration is a necessary but insufficient validation step.
- Not pre-committing the larger infrastructure design. A negative result here closes one path; the larger project pivots to other validation approaches.

## Pre-registration

The full pre-registration is in [`02_pre_registration.md`](./02_pre_registration.md), hash-locked at SHA-256 `839a8b7f0c751fad4b27cc37d1254ba31cdf23bdc84de8662116c432f1c88c5c` (see `HASH.md`). All design decisions, success criteria, and analysis plans were committed before any data was collected. Results will be published regardless of direction.

## Author

Theodor Spiro (tspiro@vaika.org).

## Replication

Once data collection completes, full corpus + raw model outputs + analysis code will be released in this repository. Reproduction instructions in `REPRODUCE.md` (TBD).
