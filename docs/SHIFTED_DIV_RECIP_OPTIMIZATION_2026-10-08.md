# Shifted DIV / reciprocal optimization campaign — 2026-10-08

This note records the dedicated follow-up to the signed DIV/MOD campaign under the library-wide **manual design -> OptiSearch -> post-OptiSearch synthesis** workflow. The stable 56-entry API, public input/output vectors, divide-by-zero behavior and fixed-point semantics are unchanged.

## Scope

The campaign covers:

- `MATH_UDIV16_SHL8`: unsigned `(N16 << 8) / D16`, returning Q24 and R16.
- `MATH_SDIV16_SHL8`: signed `(N16 << 8) / D16`, truncating toward zero and returning signed R16.
- `MATH_URECIP16_Q16`: `floor(65536 / D16)` in the library's Q16 reciprocal contract.
- V2/V3/V4 direct shifted-input adapters.
- V5's low-ZP hybrid direct shifted-input and reciprocal-fallback paths.

## Manual architecture pass

### Direct shifted-input binding

The previous shifted divide paths paid avoidable adapter work around an already-fast 32/16 divider. The new adapters materialize the widened numerator directly in the private divider state:

`N16 << 8 = 00:N_hi:N_lo:00`

without saving, rewriting and restoring the stable public N vector.

V2/V3/V4 enter the selected private UDIV32/16 split-tail core directly. V1 uses its existing balanced private 32/16 engine and output continuation. The signed adapters bind `|D|` once, form the shifted numerator magnitude directly, and reuse the existing signed continuation/output machinery rather than routing through a generic signed public wrapper.

### Reciprocal fallback

For `URECIP16_Q16`, the small-divisor fallback now seeds the private 32/16 state with the exact constant numerator `0x00010000` and the public divisor. This avoids constructing that numerator through the public vectors.

V3/V4 retain their already-faster REU reciprocal path, so their published reciprocal means are unchanged.

### V5 hybrid path

V5 now uses the same certified relocated V2 UDIV32/16 split-tail private entry already reused by the low-ZP MULDIV16 fusion. An early V5 candidate incorrectly targeted `$A100`; machine validation exposed that immediately. The corrected entry is `HYBRID_CODE+$0C00`.

The helper cannot share the high hybrid tail because direct UDIV16 owns `$B800-$BDC9`. The hybrid builder therefore installs the roughly 220-byte helper in a page-aligned free run of the sparse V1 table image, checking the actual generated destination before writing it. Page alignment preserves branch-page timing while keeping V5's **31-byte normal-ZP contract** unchanged.

## Real machine timing

All values below are measured through the public entry to RTS with the repository's deterministic NMOS-6502 model. The unsigned and signed shifted routines use the same structured/random corpus as the permanent family validators; reciprocal is exhaustive over all 65,536 16-bit divisors.

| Profile | UDIV16_SHL8 before | after | SDIV16_SHL8 before | after | URECIP16_Q16 before | after |
|---|---:|---:|---:|---:|---:|---:|
| V1 | 877.773617 | **770.773617** | 952.471538 | **846.155071** | 119.994705 | **108.497635** |
| V2 | 652.649695 | **552.649695** | 819.067394 | **715.633370** | 117.958527 | **94.822998** |
| V3 | 653.124974 | **553.124974** | 817.401091 | **714.004798** | 66.233795 | **66.233795** |
| V4 | 652.577740 | **552.577740** | 816.061505 | **712.609597** | 66.233795 | **66.233795** |
| V5 | 663.298759 | **553.298759** | 953.277863 | **630.805016** | 118.742294 | **95.044128** |

Final measured ranges:

| Routine | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| UDIV16_SHL8 | 182-1807 | 122-918 | 122-918 | 122-918 | 122-918 |
| SDIV16_SHL8 | 180-1893 | 62-1765 | 62-1765 | 62-1765 | 118-971 |
| URECIP16_Q16 | 41-1801 | 41-947 | 41-239 | 41-239 | 41-950 |

The largest gain is V5 `SDIV16_SHL8`: **953.277863 -> 630.805016 cycles mean**, a reduction of about **33.8%**. V2-V4 signed shifted division falls by about 103 cycles per call, while V1 falls by about 106 cycles.

## OptiSearch pass

The uploaded `OptiSearchV2-2026-10-06(2).zip` was verified at SHA-256:

`f5a6a9f0e8728186f91a95c1112a70488cf943fc99b2380c52272424e44455eb`

The relevant generic Q0 shifted-divider/reciprocal generators expose `threshold` and `suffix_start` schedule coordinates. The complete 4x4 coordinate space was swept on the same deterministic screening corpus and representative compact points were emulator-qualified.

For unsigned shifted division, the compact `threshold=0, suffix_start=0` Q0 core averaged about **10953.94 cycles / 359 bytes**. The default more-unrolled coordinate was slower (**10958.44**) and larger (**569 bytes**). For reciprocal the compact core averaged about **790.28 cycles / 359 bytes** while the default coordinate was about **796.27 / 569 bytes**. Neither is remotely competitive with the library's direct private-state architecture.

For signed shifted division, the absolute best screened generic coordinate averaged about **11152.94 cycles / 676 bytes**, only ~0.46 cycle ahead of the compact **11153.41 / 536-byte** point. That tiny schedule gain costs 140 bytes and is still an order of magnitude behind the specialized library path.

The OptiSearch result therefore confirms the architectural choice: **bind the shifted numerator directly into the already-selected fast 32/16 substrate rather than transplant a generic restoring/Q0 divider**.

## Post-OptiSearch synthesis

A final manual pass after the OptiSearch sweep found one additional adapter-level win. The unsigned adapters loaded `#0` twice while constructing `00:N_hi:N_lo:00`. Reordering the zero stores allows one accumulator zero to seed both zero bytes.

This removes **2 bytes and exactly 2 cycles per UDIV16_SHL8 call** in V1-V5, with no ABI, ZP, table or persistent-stack change. The final timing table above includes this refinement.

## Validation

The final candidate passes with zero errors on all five profiles:

- `UDIV16_SHL8`: 4,753 cases per profile.
- `SDIV16_SHL8`: 4,585 cases per profile.
- `URECIP16_Q16`: exhaustive 65,536 divisors per profile.

The permanent unsigned and signed division family validators remain the release gates, so these paths are checked together with the surrounding DIV/MOD APIs on every normal CI run. Generated residents, standalone/source views, public benchmark indexes and package checksums are regenerated before promotion.
