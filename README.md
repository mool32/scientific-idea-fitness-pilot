# Epistemic Fitness Pilot

Проект по построению fitness function для научных идей в эпоху AI-mediated research.

## Структура

- `PROJECT.md` — context, motivation, what this pilot is and isn't (start here if new)
- `00_three_insights.md` — теоретическая рамка: CAT, Smaldino-McElreath, Hong-Henrich
- `01_retrodictive_calibration_pilot.md` — операциональный план пилотного эксперимента
- `02_pre_registration.md` — **hash-locked pre-registration v1.0** (immutable)
- `HASH.md` — SHA-256 lock record
- `DECISIONS.md` — append-only arbitration trace
- `DEVIATIONS.md` — (created if/when any deviation from pre-reg occurs)
- `corpus/` — (TODO) данные корпуса
- `predictions/` — (TODO) outputs модели
- `outcomes/` — (TODO) impact metrics
- `analysis/` — (TODO) статистика и графики

## Status

- [x] Концептуальная рамка зафиксирована
- [x] План пилота зафиксирован
- [x] Pre-registration v1.0 hash-locked (2026-05-01)
- [ ] Git tag `prereg-v1.0` (manual step — see `HASH.md`)
- [ ] Pre-2020 contamination control: confirm Pythia 6.9B availability + inference setup
- [ ] **Pilot 1A:** NLP corpus construction
- [ ] **Pilot 1A:** Opus + Pythia inferences (V2 only)
- [ ] **Pilot 1A:** outcome measurement + primary statistic
- [ ] **Gate decision** (proceed to 1B, or stop and write up)
- [ ] **Pilot 1B** (contingent): expanded subfields/prompts/models
- [ ] Write-up

## Decisions locked in pre-registration v1.0

1. **Primary metric:** Spearman ρ between LLM score and composite Impact, anchored against citation-velocity baseline (ρ_LLM − ρ_baseline ≥ 0.05, 95% CI excludes zero). AUC top-30/bottom-30 retained as secondary for interpretability.
2. **Composite impact formula (flipped, truth-tracking-weighted):** 25% citations / 35% method-reuse / 25% replication mentions / 15% inverse retraction. Original transmission-weighted formula (50/25/15/10) retained as sensitivity test.
3. **Subfield strategy:** NLP only in Pilot 1A (gate decision). CV + RL in Pilot 1B if 1A passes.
4. **Models:** Pilot 1A = Opus 4.7 + Pythia 6.9B (contamination control). Pilot 1B adds Sonnet 4.6 + GPT-2 1.5B (floor reference).
5. **Stage gate:** binary, pre-committed. If 1A primary criterion not met, project stops and is written up as standalone null result. No "let's try one more thing" path.
6. **Normalization:** citation percentile rank within (subfield × publication-year) cell.
7. **Replication-mention heuristic:** regex Track A, validated against manual Track B on 50-paper subsample with κ ≥ 0.6 threshold.
8. **Method-reuse classification:** Semantic Scholar citation intents, scite.ai fallback if coverage < 70%.

## Resource estimate

- **Pilot 1A only:** ~1,000 inferences, ~$150, ~1 week wall-clock
- **Pilot 1A + 1B:** ~17,000 inferences, ~$550-750, ~3 weeks wall-clock
