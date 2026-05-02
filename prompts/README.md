# Prompt Templates (frozen, hash-locked)

These files implement the verbatim prompt text specified in pre-registration v1.2 §4.2. Once the pre-registration is hash-locked, these files must not be modified — any change requires the pre-reg revision policy (§0).

## Files

- `system_prompt.txt` — system message used uniformly across all prompt variants. Establishes blinding context.
- `v1.txt` — naive: single-integer impact rating (Pilot 1B only)
- `v2.txt` — structured: four-dimension rating with brief justification (**Pilot 1A primary**)
- `v3.txt` — skeptical reviewer: weaknesses then rating (Pilot 1B only)
- `v4.txt` — predictive specifics: future findings prediction with confidence (Pilot 1B only)

## How prompts are assembled

For each blinded paper, the full prompt sent to the model is:

```
[system_prompt.txt content]

Title: <title>
Abstract: <abstract>

[v{1,2,3,4}.txt content]
```

For Opus generation arm: model receives the full assembled prompt and produces V2 generation per pre-reg §4.4 frontier-model arm specification.

For Pythia log-likelihood arm: prompt is constructed up to and including the dimension prefix (e.g., `"...(d) overall promise: "`), then log-likelihood per pre-reg §4.4 pseudocode.

## Hash verification

After commit, hashes can be verified:

```bash
shasum -a 256 prompts/*.txt
```

Any mismatch with the recorded hash in `REPRODUCE.md` indicates the prompt has been modified post-lock — investigate via git history and treat as deviation per pre-reg §9.
