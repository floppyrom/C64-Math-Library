# 2026-09-07 addendum — Custom Pareto Builder

The repository now includes a build-time stock-C64 Pareto selector. It accepts a total ZP budget, optional exact extra-RAM budget, initialization policy and optional routine weights, and generates the fastest certified compatible V1/V2 combination that fits while retaining the same 45-entry API. Default equal-weight breakpoints are 31/36/60/147/176/221 ZP bytes. See `PARETO_BUILDER.md` and `../validation/pareto/`.

# V5 Hybrid Low-ZP addendum

The current repository extends the original V1–V4 release with **V5 Hybrid Low-ZP**. V5 retains V1's 31-byte normal ZP contract while importing a certified subset of faster V2 division/modulo/COS/SINCOS paths. It preserves the same 45-entry API and has separate reference/alternate, cycle-parity, ZP-confinement, cold-load, deterministic-build and configuration validation under `validation/hybrid/`. See `HYBRID_PROFILE.md`.

The V1–V4 results below remain the historical basis for those four profiles.

# Release Notes — 2026-09-06 Reviewed Source Edition

**Documented LEAN FINAL:** the complete manual now includes a plain-English Turbo16/Turbo32 explanation. Generated `build_source/` outputs and superseded slow-ISQRT32 candidate evidence are intentionally omitted from the distribution and recreated on demand; no active code/ABI/REU data changed.

This reviewed edition supersedes the earlier same-day binary-relocation Git package. It preserves the 45-entry stable API and corrected game-math baseline while making relocation an assembly-time source configuration, retaining the fast independent ISQRT32, and extending V3/V4 with six build-time-relocatable Turbo16/Turbo32 lifecycle entries. Reference resident PRGs and REU images remain byte-identical.

See `../CHANGELOG.md`, `SOURCE_RELOCATION.md`, and `../validation/REVIEWED_RELEASE_VALIDATION.md`.

---

# Release Notes — 2026-09-06 FINAL Game Math Edition

This release supersedes `c64_math_api_v1-v4_native_signed_complete_FINAL_2026-09-05`. It contains all signed and unsigned routines from that collection plus 19 new stable game/fixed-point entries. It also fixes the V2–V4 native SMUL16 initialization/package defect discovered during extension validation.

Headline additions: exact 32/32 signed/unsigned divmod; Q-style multiply/divide shifts; exact Q16 reciprocal; SIN/COS/SINCOS; signed-byte ATAN2; exact 16/32-bit integer square roots; fast and higher-accuracy distance approximations.

All four profiles pass the final machine validation and byte-level integration audit.


## Fast ISQRT32 follow-up

The reviewed source release now replaces the initial clean-but-slower 16-step ISQRT32 with an independently derived hybrid that seeds the exact high root byte through ISQRT16 and performs only eight remaining base-4 steps. The public ABI is unchanged. On the unchanged 4,130-case comparison corpus, means improve to 1378.900969 / 1198.619613 / 1197.859322 / 1046.622518 cycles for V1–V4. V4 uses 512 additional resident table bytes at `$9800-$99FF` for the fastest residual initialization.
