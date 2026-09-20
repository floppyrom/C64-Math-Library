# Division family refresh — 2026-09-20

## Scope

This refresh re-evaluates the complete unsigned/signed division family across all five fixed profiles after Repose supplied a new UDIV24 family. The production rule is the same as for the multiplication refresh: a new idea is tested against every profile, but only the fastest compatible derivative is selected under that profile’s ZP/RAM/REU contract. Public ABI addresses and semantics remain unchanged.

The affected family includes `UDIV8/16/24/32_16/32_32`, `SDIV8/16/24/32_16/32_32`, the corresponding `UMOD`/`SMOD` aliases, `UDIV16_SHL8` / `SDIV16_SHL8`, and `URECIP16_Q16`.

## Repose UDIV24 result

The strongest supplied standalone source, `udiv24-q0counter-t13-k13.a`, uses 15 ZP bytes and a selective q0-counter/deferred-zero structure. Its standalone reference result is **105.516635 core cycles** with approximately 1.1 KiB of code. The library ports the idea into profile-local public-ABI cores rather than copying one fixed-address binary into every profile.

For V2/V3/V4 the resulting module is `udiv24_direct_repose.inc`; V1 uses the low-pressure `udiv24_direct_repose_balanced.inc`; V5 repacks the selected V2-style core through the hybrid builder. The signed 24-bit paths use private signed-owned magnitude engines, so `SDIV24` never executes the public unsigned divider.

## Final profile selection

| Family | V1 | V2 | V3 | V4 | V5 |
|---|---|---|---|---|---|
| UDIV8 | direct CPU | direct CPU | **REU retained** | **REU retained** | direct CPU |
| UMOD8 | prior compatible path retained | prior compatible path retained | **REU remainder retained** | **REU remainder retained** | compatible V2/V5 path retained |
| UDIV16 | balanced direct-public | fast direct-public | fast direct-public | fast direct-public | fast core repacked |
| UDIV24 | Repose-derived balanced | **Repose q0-counter** | **Repose q0-counter** | **Repose q0-counter** | Repose core repacked |
| UDIV32/16 | retained where faster | retained/relocated selected core | retained selected core | retained selected core | V2 selected core import |
| UDIV32/32 | early q=0 gate | early q=0 gate | early q=0 gate | early q=0 gate | early q=0 gate |
| SDIV8 | direct-output native signed | same | same | same | same |
| SDIV16 | balanced direct-output | fast direct-output | fast direct-output | fast direct-output | fast core repacked under 31-ZP contract |
| SDIV24 | balanced direct-output | fast direct-output | Repose-derived private magnitude core | same | fast core repacked under 31-ZP contract |
| SDIV32/16 | direct-output native signed | fast direct-output | fast direct-output | fast direct-output | refreshed low-ZP native signed |
| SDIV32/32 | redundant-zero test removed | same | same | same | same |

V3/V4 deliberately **do not** take the new CPU UDIV8 core: their REU quotient/remainder planes remain faster for the fixed REU profiles. This is a profile-selection result, not an incomplete port.

## Final resident measurements

The table below uses the final resident validators. The corpora are identical within each validator family and are intended as current-release measurements; cross-release claims use the separate same-corpus audit described below.

| Entry | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| `MATH_UDIV8` | 59.572 | 59.383 | 70.863 | 70.863 | 59.383 |
| `MATH_UDIV16` | 132.726 | 127.774 | 125.424 | 125.626 | 126.386 |
| `MATH_UDIV24` | 194.156 | 183.661 | 191.745 | 187.307 | 187.122 |
| `MATH_UDIV32_16` | 870.340 | 753.995 | 755.944 | 757.480 | 756.639 |
| `MATH_UDIV32_32` | 428.554 | 401.556 | 395.885 | 404.409 | 421.077 |
| `MATH_SDIV8` | 88.373 | 88.373 | 88.373 | 89.010 | 90.272 |
| `MATH_SDIV16` | 187.131 | 169.428 | 171.806 | 169.754 | 171.905 |
| `MATH_SDIV24` | 313.583 | 248.344 | 236.810 | 237.569 | 253.487 |
| `MATH_SDIV32_16` | 955.052 | 833.996 | 833.573 | 829.631 | 958.522 |
| `MATH_SDIV32_32` | 586.396 | 553.098 | 552.481 | 552.840 | 591.563 |

Unsigned validation covers **822,050 machine calls** across the five profiles; signed division/modulo validation covers **364,533 machine calls**. Both report zero arithmetic errors.

## Same-corpus release gate

To prevent misleading comparisons caused by changing benchmark distributions, the pre-refresh and final residents were also run side-by-side on one fixed deterministic corpus. That evidence is stored in `validation/division_refresh/DIVISION_FAMILY_SAME_CORPUS.json`.

- **V1:** 19 of 23 measured public division-family paths improve and 4 are cycle-identical; **0 regressions**.
- **V2:** 19 of 23 measured public division-family paths improve and 4 are cycle-identical; **0 regressions**.
- **V3:** 17 of 23 measured public division-family paths improve and 6 are cycle-identical; **0 regressions**.
- **V4:** 17 of 23 measured public division-family paths improve and 6 are cycle-identical; **0 regressions**.
- **V5:** 19 of 23 measured public division-family paths improve and 4 are cycle-identical; **0 regressions**.

The same-corpus gate is the selection authority when old and new consolidated-table rows use different validation corpora.

## Source exposure

The selected unsigned/direct modules are published as profile-local canonical includes under `relocatable_source/<profile>/`. Exact signed executable mirrors are published under each profile’s `resident/signed/division/native/` directory. V3/V4 additionally expose `reu_div8_public_stubs.inc`, which keeps their REU UDIV8/UMOD8 paths relocation-safe on both maps. V5 is generated from the V1/V2 canonical sources and its current source-build manifest records the exact imported/repacked components.

Key selected modules include:

- `udiv8_direct_public.inc` / `reu_div8_public_stubs.inc`
- `umod8_relocatable_public.inc`
- `udiv16_direct_balanced.inc` / `udiv16_direct_fast.inc`
- `udiv24_direct_repose_balanced.inc` / `udiv24_direct_repose.inc`
- `sdiv8_direct_public.inc`
- `sdiv16_directout_balanced.inc` / `sdiv16_directout_fast.inc`
- `sdiv24_directout_balanced.inc` / `sdiv24_directout_fast.inc` / `sdiv24_directout_repose.inc`
- `sdiv32_16_direct_balanced.inc` / `sdiv32_16_direct_fast.inc`
- `udiv32_32_early_gate.inc`
- `sdiv32_32_skip_redundant_zero.inc`

## Validation and release gates

- V1–V4 reference and alternate source builds: 46/46 stable entries, 4,589 calls per profile/map.
- V5 reference/alternate hybrid builds: 46/46 stable entries, 4,589 calls per map.
- Published signed sources: 65 routines / 270 checks PASS.
- Signed executable ownership: 279 checks / 65 zero-overlap comparisons PASS.
- Custom Pareto: 12 reference/alternate builds, 55,068 common-API calls; direct V2 parity 75,644 cases; exhaustive UMOD8; deterministic and stress gates PASS.
- Deterministic source rebuild: PASS on all reference/alternate fixed-profile maps.
- Package audit: PASS.
- Release audit: **PASS_WITH_ACME_NOT_RUN**, 205 checks.

The final release does not claim a fresh external ACME/Perfect6502 certification run for the new division refresh. The supplied Repose standalone result is retained as research provenance; all integrated public figures above come from the library’s final resident validation stack.
