# External-reviewer recruit message — DRAFT for human reviewer to adapt

**Status:** Draft for critique by Theodor Spiro before adaptation and sending. Voice should be the human reviewer's, not Claude's. This file is a starting point, not the final message.

**Constraints honored:**
- Single paragraph + link + signature (researchers are busy; long emails get deferred)
- Framing makes "no, you have a problem" the easy answer, not "approve our work"
- Specific time bound (30 minutes reading, 5-day window)
- Honest about AI collaboration (relevant context for metascience reviewer; hiding it would be its own integrity issue)
- Honest about asymmetry (no quid pro quo; appeals to shared interest in methodology rigor)

---

## Subject line options

- "30-min ask: pre-registration discipline check on a small pilot — looking for a sharp eye"
- "Pre-registration revision pattern — independent check before we proceed?"
- "Quick adversarial-review ask: do our pre-registration revisions look sustainable?"

(I lean the first; tone signals what's wanted.)

---

## Body draft

Hi [Name],

I'm a solo independent researcher (biophysics background) running a small pre-registered pilot on whether LLMs can predict scientific impact of papers from abstracts. I've been collaborating with Claude on the design and execution. Over the last 48 hours I've revised the pre-registration twice, both pre-data, both individually defensible — but the pattern itself (three versions in two days, plus an effective expansion of the revision policy in v1.2) is exactly the kind of cumulative-reasonable-adjustment trajectory that erodes pre-registration discipline. I caught the pattern, paused, and wrote a meta-entry committing to a moratorium and a stage-gate binding — but I'm a single reviewer of my own work, and that's exactly the failure mode the larger project says external review exists to catch. Could I ask 30 minutes of your time to read the revision trail (`02_pre_registration.md` v1.0 → v1.1 → v1.2 plus `DECISIONS.md` entries D-005, D-007, D-008) and tell me sharply whether the v1.2 bundling of a new partial-correlation co-primary test together with the framing correction was a structural problem, and whether the revision pattern overall is sustainable or already eroded? I'd rather you tell me "yes, you have a problem" within the next 5 days than discover post-execution that I should have stopped here. No quid pro quo offered — just an appeal to shared interest in methodology rigor. Repository: https://github.com/mool32/scientific-idea-fitness-pilot (start with PROJECT.md for context, then the revision trail).

Theodor Spiro
[your contact]

---

## Notes for human reviewer adapting this draft

1. **Voice:** rewrite in your voice. The draft above is intentionally somewhat formal; if your normal voice is more direct, more casual, more academic, or more technical, adjust. Reviewers can detect AI-flat tone and it raises questions about whether the artifact is mostly AI-generated, which would itself be relevant context they'd want.

2. **Personalization:** if you have prior connection to the recipient (read their work, met them at a conference, share a collaborator), say so in one sentence at the top. "I read your paper on X and your treatment of Y is exactly the kind of skeptical eye I'm looking for" makes the cold ask warmer without compromising the framing.

3. **Don't over-promise on time:** "30 minutes" is honest if they read carefully. Don't say "5 minutes" or "quick look" — they'll either bounce off when it takes longer or do superficial review. Reviewers prefer accurate time estimates.

4. **Don't apologize for asking:** the ask is appropriate; over-apologizing signals weak case. The framing "I'd rather you tell me 'you have a problem' than discover it post-execution" already establishes appropriate humility without grovel.

5. **One reviewer at a time, or simultaneous?** If you reach out to multiple candidates simultaneously, mention "I'm asking 2-3 people in parallel because I want one independent eye and want to respect everyone's time if someone else takes it on" — transparent about the ask not being unique to them. If sequentially, no mention needed.

6. **What if they ask for compensation?** Most metascience people will treat this as collegial. If asked, "this is unfunded pilot work but if a paper results I'd like to acknowledge your contribution by name in the methodology section / acknowledgments" is fair offer. Don't promise authorship — that's not standard for this kind of one-shot review.

7. **What if they say yes but want to negotiate scope?** "30 minutes on revision-pattern sustainability" is the minimum-viable ask. If they want to do deeper review, accept enthusiastically but treat their broader feedback as bonus, not requirement. Don't expand the ask just because they're willing.

8. **What if they engage with substance and surface concerns?** D-010 captures their feedback. Address concerns before Phase 2 launch. If concerns require pre-reg revision, the moratorium is suspended specifically for the response and the revision is documented as "external-review-driven correction" with the reviewer's input cited.

9. **What if they say no?** Try the next candidate. If 5-day timeout reached with no engagement, document and proceed per D-009's fallback path.

10. **What you should NOT do:** do not send this draft verbatim. The whole point is to invite an external voice; if the message itself sounds AI-generated, the reviewer might reasonably wonder if the substance is also.
