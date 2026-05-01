# Retrodictive Calibration Pilot: AI-Agent-Executable Plan

Цель пилота — измерить может ли LLM-as-judge discriminate between scientific ideas which proved valuable vs. unsuccessful, при условии что его prediction делается *как будто* до того как outcome стал known. Если discriminative ability above chance, fitness function на этой основе viable. Если at chance — нужны другие подходы.

План структурирован так чтобы AI agent (Claude with code execution, или подобный) мог выполнить его автономно с минимальным human input. Указано где human judgment essential.

## Phase 0: Setup и validation infrastructure

**Step 0.1.** Define the prediction task formally. Given a scientific idea proposed at time T, predict its impact measured at time T+ΔT, где ΔT chosen так чтобы outcome was known но не in training corpus by construction.

Choice of ΔT involves trade-off. Слишком short — outcomes still developing, signal noisy. Слишком long — corpus contamination risk. For ML papers reasonable ΔT = 3-5 years. Pre-registration: ΔT = 4 years for primary analysis, 2 years and 6 years as sensitivity checks.

**Step 0.2.** Define impact measure. Agent should NOT use raw citation count — it has known pathologies (Matthew effect, prestige bias, trendiness). Better composite: combine normalized citations within field-year, follow-up replication attempts, integration в downstream papers (whether method/result reused vs. just cited as background), inverse of retraction rate. Concrete formula to be specified в pre-registration.

**Step 0.3.** Pre-register the entire pilot. Hash-locked document specifying: corpus selection criteria, prediction prompt(s), impact measure formula, primary success criterion (e.g. AUC > 0.6 above chance baseline), sensitivity analyses, publication plan включая null result. Это non-trivial: pilot itself должен следовать тем principles которые ты предлагаешь для системы. Otherwise hypocritical.

## Phase 1: Corpus construction

**Step 1.1.** Choose source. ML papers from 2020-2022 на arXiv с full abstracts available. Restrict to specific subfields where impact measurable cleanly: NLP, computer vision, RL. Reasonable initial size: 500 papers.

**Step 1.2.** Agent task: pull abstracts and metadata via arXiv API. Filter by subfield via category labels. Sort by date.

**Step 1.3.** Stratify sample. Не random — stratified to ensure representation across impact tiers. Take papers с citations в top 10% (high impact), middle 40-60% (median), bottom 10% (low impact) according to current 2026 metrics. 100-150 papers per tier. Stratification *uses outcome data* — это known limitation, alternative is random sampling but it gives unbalanced classes which makes discriminative testing harder.

**Step 1.4.** Critical: **blind the agent to outcome data when constructing prompts.** Agent generating predictions must NOT see citation counts, follow-up papers, retraction status. Agent doing impact measurement does see them but operates on separate pipeline. Implement as separate scripts с separate data files.

**Step 1.5.** Validate corpus. Manual spot-check by human на 20 random papers — verify subfield classification correct, abstracts complete, no obviously misclassified items. Это the human checkpoint — needed because agent's classification может silently fail на edge cases.

## Phase 2: Prediction generation

**Step 2.1.** Design prediction prompt. Multiple variants для testing prompt-dependence:

— V1 (naive): «Rate the likely scientific impact of this idea on a 1-10 scale.»

— V2 (structured): «Given this abstract, estimate: (a) novelty 1-10, (b) technical soundness 1-10, (c) likely follow-up potential 1-10, (d) overall promise 1-10. Briefly justify each.»

— V3 (skeptical reviewer): «You are a skeptical reviewer assessing this paper for likely real impact. List potential weaknesses. Then rate likely impact 1-10.»

— V4 (predictive specifics): «If this idea is correct, what specific findings should appear in the next 3 years? Rate confidence in each prediction 1-10.»

**Step 2.2.** Critical contamination control. Agent must operate as if it does not know outcome. Several mechanisms:

— Use temporal cutoff models where available. Compare predictions from older models (cutoff before paper publication) vs. current models. Discrepancy signals contamination.

— Strip identifiers: author names, institution affiliations, exact dates, venue. Test how predictions change with vs. without identifiers — measures prestige bias contamination.

— Run blind: agent gets only abstract text + technical content, no metadata.

**Step 2.3.** Generate predictions. For each paper × prompt variant × model combination, get prediction. Realistic scope: 500 papers × 4 prompts × 3 models = 6000 predictions. Cost estimate: maybe $200-500 в API calls at current rates.

**Step 2.4.** Generate ensemble predictions where models disagree. If different models или different prompts give discrepant predictions for same paper, note disagreement magnitude — это само по себе fitness signal worth testing.

## Phase 3: Outcome measurement

**Step 3.1.** Independent pipeline. Different agent или different session, queries citation databases (Semantic Scholar API, OpenAlex), pulls 2026 metrics for each paper.

**Step 3.2.** Compute composite impact score per pre-registered formula. Normalize within subfield-year to control for citation rate differences. Output: single score per paper.

**Step 3.3.** Dichotomize for primary analysis (high vs. low impact, top 30% vs. bottom 30%). Continuous score retained for secondary analyses.

## Phase 4: Statistical analysis

**Step 4.1.** Primary test: AUC for predicting binary high/low impact from prediction score. Baseline: 0.5 (chance). Pre-registered success criterion: 0.6 (modest discriminative ability) for go/no-go. 0.7+ would be strong evidence fitness function viable. Below 0.55 effectively null.

**Step 4.2.** Secondary analyses pre-specified:

— Variation by prompt: which prompts produce best discrimination?

— Variation by model: do larger models discriminate better? Do older-cutoff models contaminate less?

— Variation by subfield: does method work for some areas but not others?

— Calibration: are 8/10 predictions actually more impactful than 5/10? (calibration curves, Brier score)

— Ensemble disagreement signal: does inter-model disagreement correlate with idea novelty/risk independently от mean prediction?

**Step 4.3.** Honest discussion of limitations. Stratified sampling means absolute rates not interpretable to randomly-selected papers. Citation-based impact has known biases. Contamination cannot be fully ruled out for famous papers. Ensemble of caveats.

## Phase 5: Reporting

**Step 5.1.** Write up regardless of result. Pre-registered to publish even if null. Это часть demonstrating the methodology.

**Step 5.2.** Publish corpus, predictions, code as artifact. Other researchers can replicate or extend.

**Step 5.3.** If result positive (AUC > 0.6 на primary), use as foundation for next phase: building actual fitness function with these calibrations as ground truth signal. If null, document limitations and pivot — alternative pilots to consider включают NAS-bench style evaluation в narrow domains, or human-LLM agreement studies on idea-quality judgments.

## Realistic timeline и cost для AI-agent execution

Phase 0 (setup, pre-registration): 1-2 days human + agent collaboration. Pre-registration document needs human review.

Phase 1 (corpus): agent autonomous, 1 day. Human spot-check 1 hour.

Phase 2 (predictions): agent autonomous, 2-3 days running time. Human reviews prompt designs before launch.

Phase 3 (outcomes): agent autonomous, 1 day.

Phase 4 (analysis): agent autonomous for primary, human review for interpretation. 2-3 days.

Phase 5 (write-up): mostly human. 1 week.

Total realistic: 2-3 weeks elapsed time, with maybe 30-40 hours of active human time on top of agent's autonomous work. API cost $200-500. Reasonable for individual researcher.

## Что критически нужно decision-wise before launch

Two pre-registration items requiring human judgment:

**(a)** Final composite impact formula. Skeleton дан выше; precise weights нужно зафиксировать. Recommendation: 50% normalized citation, 25% follow-up replication mentions, 15% method/result reuse в downstream, 10% inverse retraction. Sensitivity analysis с different weights.

**(b)** Primary subfield choice. NLP gives largest sample but most contamination (transformer papers everywhere). Computer vision balanced. RL smaller but cleaner. Recommendation: do all three, treat NLP as primary but check all three for robustness.
