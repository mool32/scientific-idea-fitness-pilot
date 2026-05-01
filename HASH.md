# Pre-Registration Hash Lock

This file records the cryptographic hash of `02_pre_registration.md` at each version of the pre-registration. The current version is the canonical `02_pre_registration.md` in the working tree. Prior versions remain in git history under their original tags. Revisions are governed by §0 (Revision policy) of the pre-registration; transitions are documented in `CHANGELOG.md`.

## Current version: v1.1

- **File:** `02_pre_registration.md`
- **SHA-256:** `382a7a46afbca1ce2095e27fa69ac26d7a537c108164a160267d411cefc4485c`
- **Hashed at (UTC):** `2026-05-01T20:43:22Z`
- **Length:** 384 lines
- **Author:** Theodor Spiro (tspiro@vaika.org)
- **Git tag:** `prereg-v1.1`

## Verification

To verify integrity at any later time:

```bash
shasum -a 256 02_pre_registration.md
# Should output: 382a7a46afbca1ce2095e27fa69ac26d7a537c108164a160267d411cefc4485c
```

If the hash differs, either (a) the working tree has been modified post-lock — investigate via git history; or (b) a new version has been issued — see CHANGELOG.md.

## OpenTimestamps proof

A blockchain-anchored timestamp proof is committed as `02_pre_registration.md.ots`. This provides independent verification of the pre-registration's existence at this hash, without trust in GitHub or any single party.

To verify:

```bash
ots verify 02_pre_registration.md.ots
```

Initial proof contains pending attestations to multiple Bitcoin calendar servers. After Bitcoin block inclusion (~1-3 hours from initial stamp), run `ots upgrade 02_pre_registration.md.ots` to download the complete blockchain proof, then commit the upgraded `.ots` file.

---

## Prior version: v1.0 (superseded 2026-05-01 by v1.1, see CHANGELOG.md)

- **File:** `02_pre_registration.md` at git tag `prereg-v1.0` (commit `613c0be`)
- **SHA-256:** `dbc74374ac8b09011941cb41875cbcf2bee49f292a5a1eb507742e524e0b2b8e`
- **Hashed at (UTC):** `2026-05-01T19:18:51Z`
- **Length:** 313 lines
- **OpenTimestamps proof:** in git history at the same commit (`02_pre_registration.md.ots` content as of `prereg-v1.0` tag)
- **Public push:** 2026-05-01T19:20:13Z UTC to `github.com/mool32/scientific-idea-fitness-pilot`

To verify v1.0 at any later time:

```bash
git show prereg-v1.0:02_pre_registration.md | shasum -a 256
# Should output: dbc74374ac8b09011941cb41875cbcf2bee49f292a5a1eb507742e524e0b2b8e
```

## Note on v1.0 hash provenance

The v1.0 hash above was finalized before the first public push to GitHub. An earlier draft hash (`839a8b7f0c751fad4b27cc37d1254ba31cdf23bdc84de8662116c432f1c88c5c`, computed 2026-05-01T18:57:12Z) reflected an incorrect author-identity field that was corrected before any external observer could timestamp it. The v1.0 hash above is the canonical pre-public-push hash. No deviation entry was required because no public commitment to the earlier hash existed at the time of correction.

## Subsequent versions

(none beyond v1.1 yet)
