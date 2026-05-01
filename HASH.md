# Pre-Registration Hash Lock

This file records the cryptographic hash of `02_pre_registration.md` at the moment of pre-registration. After this point, the pre-registration is immutable. Any subsequent change requires a new versioned file (`02_pre_registration_v1.1.md` etc.) with the deviation documented in `DEVIATIONS.md`.

## Pre-registration v1.0

- **File:** `02_pre_registration.md`
- **SHA-256:** `dbc74374ac8b09011941cb41875cbcf2bee49f292a5a1eb507742e524e0b2b8e`
- **Hashed at (UTC):** `2026-05-01T19:18:51Z`
- **Length:** 313 lines
- **Author:** Theodor Spiro (tspiro@vaika.org)
- **Git tag:** `prereg-v1.0`

## Verification

To verify integrity at any later time:

```bash
shasum -a 256 02_pre_registration.md
# Should output: dbc74374ac8b09011941cb41875cbcf2bee49f292a5a1eb507742e524e0b2b8e
```

If the hash differs, the pre-registration has been modified post-lock — investigate via git history. Any legitimate revision should appear as a new file `02_pre_registration_v1.x.md` with its own hash entry below, leaving v1.0 untouched.

## OpenTimestamps proof

A blockchain-anchored timestamp proof is committed alongside the pre-registration as `02_pre_registration.md.ots`. This provides independent verification of the pre-registration's existence at this hash, without trust in GitHub or any single party.

To verify:

```bash
ots verify 02_pre_registration.md.ots
```

Initial proof contains pending attestations to multiple Bitcoin calendar servers (a/b.pool.opentimestamps.org, a.pool.eternitywall.com, ots.btc.catallaxy.com). After Bitcoin block inclusion (~1-3 hours from initial stamp), run `ots upgrade 02_pre_registration.md.ots` to download the complete blockchain proof, then commit the upgraded `.ots` file.

## Note on hash provenance

This hash was finalized before the first public push to GitHub. An earlier draft hash (`839a8b7f0c751fad4b27cc37d1254ba31cdf23bdc84de8662116c432f1c88c5c`, computed 2026-05-01T18:57:12Z) reflected an incorrect author-identity field that was corrected before any external observer could timestamp it. The corrected hash above is the canonical v1.0 hash. No deviation entry is required because no public commitment to the earlier hash existed at the time of correction.

## Subsequent versions

(none yet)
