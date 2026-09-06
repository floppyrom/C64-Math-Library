# License and provenance notes — V4 16 MiB REU

This reviewed source distribution contains the active profile sources, generated tables/REU image, examples, documentation and validation evidence. Historical reference bundles are intentionally not duplicated in this streamlined package.

Previously selected low-level kernels retain their existing provenance/licensing status; this integration does not purport to relicense third-party code. The active `MATH_ISQRT32` kernel is the new independent ISQRT16-seeded hybrid implementation documented in `../docs/THIRD_PARTY_NOTICES_GAME_MATH.md`.

The source-relocation layer and generated configuration/build tooling are included for auditability. Assembly-time address/bank changes are validated by the alternate-map regression.
