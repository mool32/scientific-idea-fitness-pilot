# External-reviewer recruit message — DRAFT v2 for human reviewer to adapt

**Status:** Draft v2 for critique by Theodor Spiro before adaptation and sending. Voice should be the human reviewer's, not Claude's. This file is a starting point, not the final message.

**Revisions from v1 per human reviewer critique:**
- Opening cut: now leads with problem statement, not biographical preamble
- AI mention de-foregrounded: moved from second sentence to parenthetical mid-paragraph
- Signature includes affiliation context (independent researcher + recent preprints) so reviewer can triage credibility quickly
- Body split into two paragraphs (setup + ask) for scannability

**Constraints honored:**
- Two short paragraphs + signature (researchers triage by length and first sentence)
- Framing makes "no, you have a problem" the easy answer
- Specific time bound (30 minutes, 5-day window)
- Honest about AI collaboration (mentioned in context, not foregrounded)
- Honest about asymmetry (no quid pro quo)
- Specific entry points to reduce friction

---

## Subject line options

- "30-min ask: pre-registration discipline check on a small pilot — looking for a sharp eye"
- "Pre-registration revision pattern — independent check before we proceed?"
- "Quick adversarial-review ask: do our pre-registration revisions look sustainable?"

(Lean the first; tone signals what's wanted.)

---

## Body draft v2

Hi [Name],

I've identified what may be a structural problem in the pre-registration discipline of a small pilot I'm running, and I'd like a sharp independent eye on whether the revision pattern is sustainable. Over the last 48 hours I've revised the pre-registration twice, both pre-data, both individually defensible — but the pattern itself (three versions in two days, plus an effective expansion of the revision policy in v1.2) is exactly the cumulative-reasonable-adjustment trajectory that erodes pre-registration discipline. I caught it, paused, and committed to a moratorium plus stage-gate binding — but I'm a single reviewer of my own work (project executed with AI collaboration via Claude), which is exactly the failure mode independent review is supposed to catch.

Could I ask 30 minutes of your time to read the revision trail (`02_pre_registration.md` v1.0 → v1.1 → v1.2 plus `DECISIONS.md` entries D-005, D-007, D-008) and tell me sharply whether the v1.2 bundling of a new partial-correlation co-primary test with a framing correction was a structural problem, and whether the revision pattern overall is sustainable or already eroded? I'd rather you tell me "yes, you have a problem" within the next 5 days than discover post-execution that I should have stopped here. No quid pro quo offered — appeal to shared interest in methodology rigor. Repository: https://github.com/mool32/scientific-idea-fitness-pilot (start with `PROJECT.md`, then the revision trail).

Theodor Spiro
Independent researcher (biophysics background)
Recent preprints: functional differentiation in language models, EEG-based connectivity metrics, LLM epistemic monoculture
[your email]

---

## Notes for human reviewer adapting this draft

1. **Voice:** rewrite in your voice. The draft above is intentionally somewhat formal; if your normal voice is more direct, more casual, more academic, or more technical, adjust. Reviewers can detect AI-flat tone and it raises questions about whether the artifact is mostly AI-generated, which would itself be relevant context they'd want.

2. **Personalization:** if you have prior connection to the recipient (read their work, met them at a conference, share a collaborator), say so in one sentence at the top. "I read your paper on X and your treatment of Y is exactly the kind of skeptical eye I'm looking for" makes the cold ask warmer without compromising the framing.

3. **Don't over-promise on time:** "30 minutes" is honest if they read carefully. Don't say "5 minutes" or "quick look" — they'll either bounce off when it takes longer or do superficial review. Reviewers prefer accurate time estimates.

4. **Don't apologize for asking:** the ask is appropriate; over-apologizing signals weak case. The framing already establishes appropriate humility without grovel.

5. **One reviewer at a time, or simultaneous?** If you reach out to multiple candidates simultaneously, mention "I'm asking 2-3 people in parallel because I want one independent eye and want to respect everyone's time if someone else takes it on." If sequentially, no mention needed.

6. **What if they ask for compensation?** "This is unfunded pilot work but if a paper results I'd like to acknowledge your contribution by name in the methodology section / acknowledgments" is fair offer. Don't promise authorship.

7. **What if they engage with substance and surface concerns?** D-010+ captures their feedback. Address concerns before Phase 2 launch. If concerns require pre-reg revision, the moratorium is suspended specifically for the response and the revision is documented as "external-review-driven correction" with the reviewer's input cited.

8. **What if they say no?** Try the next candidate. If 5-day timeout reached with no engagement, document and proceed per D-009's fallback path.

9. **Affiliation line:** swap in your actual recent preprints / current work. The example line is illustrative; make it accurate to what you'd want a reviewer to look at if they wanted to assess your background.

10. **What you should NOT do:** do not send this draft verbatim. The whole point is to invite an external voice; if the message itself sounds AI-generated, the reviewer might reasonably wonder if the substance is also.
