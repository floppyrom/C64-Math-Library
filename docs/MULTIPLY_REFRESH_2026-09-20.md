# Multiplication refresh — 20 September 2026

This refresh re-evaluates the complete public multiplication family across all five fixed profiles after the recent Repose/quarter-square and signed-quadrant work. The selection rule is deliberately profile-specific: a new arithmetic idea is tested everywhere, but a profile changes only when the candidate wins under that profile's ZP, RAM, stack, REU and coexistence constraints.

The public ABI is unchanged. All selected implementations remain relocatable through the normal source-build path, use no persistent hardware-stack reservation, and have been tested in mixed API workloads rather than only as isolated benchmark kernels.

## Selected implementations

| Family | V1 Balanced | V2 Pareto-Fast | V3 REU 512K | V4 REU 16M | V5 Hybrid Low-ZP |
|---|---|---|---|---|---|
| `UMUL8` | retained | retained | retained REU path | retained REU path | retained |
| `SMUL8` | direct signed QS | direct signed QS | direct signed QS | direct signed QS | direct signed QS |
| `UMUL16` | retained 17-ZP record core | retained 17-ZP record core | retained 17-ZP record core | retained 17-ZP record core | retained 17-ZP record core |
| `SMUL16` | **FAST17 low-ZP native** | retained 116-ZP practical native | retained 116-ZP practical native | retained 116-ZP practical native | **FAST17 low-ZP native** |
| `UMUL24` | **FAST24 private** | retained record kernel | retained record kernel | retained record kernel | **FAST24 private** |
| `SMUL24` | **FAST24 signed composition** | **FAST24 signed composition** | **FAST24 signed composition** | **FAST24 signed composition** | **FAST24 signed composition** |
| `UMUL32` | **FAST31/V29 q0** | **FAST31/V29 q0** | **FAST31/V29 q0** | **FAST31/V29 q0** | **FAST31/V29 q0** |
| `SMUL32` | **FAST31/V29 signed** | **FAST31/V29 signed** | **FAST31/V29 signed** | **FAST31/V29 signed** | **FAST31/V29 signed** |

`READY` and fixed-shift entries follow the selected producer for their profile. In particular, `MATH_UMUL32_READY`, `MATH_SMUL32_READY`, `MATH_UMUL32_SHR16`, `MATH_SMUL32_SHR16` and `MATH_SMUL16_SHR8` were revalidated after the producer changes.

## Headline measurements

The consolidated table is authoritative for per-profile resource accounting and provenance. Key refreshed public measurements are:

| Entry | Profile(s) | Mean cycles | Range | Cases |
|---|---|---:|---:|---:|
| `MATH_SMUL8` | all five | **67.992188** | 66–70 | 65,536 exhaustive/profile |
| `MATH_SMUL16` | V1 | **293.298407** | 260–327 | 4,457 |
| `MATH_SMUL16` | V5 | **292.974871** | 260–325 | 4,457 |
| `MATH_SMUL16` | V2 | 252.324882 | 230–293 | 4,457 |
| `MATH_SMUL16` | V3 | 252.623962 | 230–293 | 4,457 |
| `MATH_SMUL16` | V4 | 252.662553 | 230–293 | 4,457 |
| `MATH_UMUL24` | V1/V5 | **489.988792** | 462–542 | 2,409 |
| `MATH_SMUL24` | V1 | **531.496472** | 474–591 | 2,409 |
| `MATH_SMUL24` | V2/V3/V4 | **487.181818 / 486.816106 / 487.220008** | 430–550 overall | 2,409 each |
| `MATH_UMUL32` | all five | **712.235367** | 652–831 | 2,409 |
| `MATH_UMUL32_READY` | all five | **697.175781** | 642–784 | 1,024 |
| `MATH_SMUL32` | V1/V2/V3/V4/V5 | **744.569946 / 743.605230 / 744.033209 / 744.090079 / 743.913242** | 660–873 | 2,409 each |
| `MATH_SMUL16_SHR8` | V1/V5 | **333.867232** | 301–366 | 4,361 |
| `MATH_SMUL16_SHR8` | V2/V3/V4 | **293.411374** | 271–334 | 4,361 each |
| `MATH_UMUL32_SHR16` | all five | **779.876404** | 717–896 | 4,361 |
| `MATH_SMUL32_SHR16` | all five | **812.998853** | 725–938 | 4,361 |

See `docs/CONSOLIDATED_ROUTINE_TABLE.csv` and `docs/CONSOLIDATED_ROUTINE_TABLE.md` for the complete 245-row measurement/resource table.

## Why UMUL8 and UMUL16 did not change

The new knowledge was applied to the unsigned routines as well; retention is an explicit selection result rather than an omission.

The fastest standalone `UMUL8` research point reaches about 41.99 cycles by spending executable/persistent ZP and a 2,044-byte table set. That is attractive as a standalone specialty kernel, but it does not improve the fixed profiles cleanly: V1/V5 must preserve the 31-byte profile contract, V3/V4 already have their REU path, and adopting the high-resource point in V2 changes the resource contract and coexistence geometry. The existing public `UMUL8` paths are therefore retained.

`UMUL16` was already upgraded to the record-derived 17-ZP resident core in the September 14 work. Faster high-ZP standalone points exist, but they collide with the resource role of V1/V5 and with V2–V4's persistent 116-ZP native `SMUL16` region. The current 17-ZP public `UMUL16` is retained in all five profiles.

## SMUL16: one algorithm does not fit every profile

The FAST17 signed composition is a large win for the low-ZP profiles and now uses a private copy of the qualified 17-ZP magnitude core. It therefore remains a true native signed executable path: signed and unsigned executable graphs are disjoint, although immutable quarter-square tables are shared.

The same FAST17 idea was ported and benchmarked in V2/V3/V4. It was slower there than the existing 116-ZP practical native signed kernel, so those three profiles deliberately retain that implementation. This is the intended profile-selection model: share optimization knowledge, not necessarily identical machine code.

## SMUL24: Repose four-quadrant composition

The refreshed signed 24-bit path uses four-quadrant dispatch:

- positive/positive enters the unsigned producer directly;
- one-negative quadrants use one upper-half two's-complement correction;
- negative/negative negates both operands and fuses the X transformation into the binding phase before entering the installed-X magnitude producer.

The selected C64ML form uses the 24-ZP carry-optimized magnitude geometry. It is selected in every profile. V1/V5 also adopt the corresponding private unsigned FAST24 producer; V2/V3/V4 retain their existing record `UMUL24` because the replacement candidate was slightly slower on the controlled comparison corpus.

## 32-bit: FAST31/V29 for signed and unsigned

The 32-bit refresh factors the V29 quarter-square work into private unsigned q0 and signed quadrant producers. Both share immutable table data and profile scratch, but the published signed/unsigned executable graphs remain disjoint.

An important difference from the earlier isolated V29 experiment is **mixed-call safety**. The shipped public `SMUL32` and `UMUL32` entries restore the pointer-high state they require because other API calls are allowed to reuse those ZP bytes. `READY` entries may skip that binder under their documented initialized/bound-state contract. For that reason the final public `SMUL32` means are around 743–745 cycles rather than the earlier isolated V2 figure near 715.6 cycles. The latter remains useful research evidence, but is not the mixed-API-safe public timing selected here.

V3/V4 required an additional layout correction: the private unsigned q0 core was first placed where the REU Turbo entry points live. It is now relocated into the superseded resident UMUL32 region (`$5800`/`$5900` islands for V2–V4), preserving the V3/V4 Turbo API. The Turbo relocation suite passes after this change.

## Source exposure

The selected refresh kernels are independent canonical include files rather than hidden monolithic generated code. They live under each fixed profile's `relocatable_source/<profile>/` directory, for example:

- `smul8_direct_signed.inc`
- `smul16_fast17_composed.inc` where selected
- `smul16_shr8_selected.inc`
- `smul24_fast24_composed.inc`
- `umul24_fast24_shared.inc` where selected
- `smul32_fast31_v29.inc`
- `umul32_v29_shared.inc`

`tools/source_relocation.py` explicitly preserves these independent modules when canonical relocatable sources are regenerated. Exact initialized executable mirrors for all signed entries continue to be published under each profile's `resident/signed/multiply/native/` tree and are verified byte-for-byte against the resident image.

V5 is generated from the V1 low-ZP/hybrid architecture, so its selected low-ZP arithmetic is inherited through the hybrid build while its signed native mirrors are still published under `v5_hybrid_lowzp/resident/signed/multiply/native/`.

## Validation

The final refresh passed the repository's integration checks rather than only standalone arithmetic tests:

- V1–V4 reference and alternate relocatable source builds: **46/46 API entries, 4,589 calls per map**;
- signed multiplication regression: **264,999 calls**, zero arithmetic errors;
- refresh-sensitive unified benchmark: **415,078 calls**;
- V3/V4 Turbo relocation: **17,196 Turbo16/Turbo32 calls**, confirming no UMUL32/Turbo collision;
- signed executable ownership: **279 layout checks and 65 signed/unsigned zero-overlap comparisons**;
- published signed native source validation: **65 routines / 270 checks**;
- deterministic V1–V4 source rebuild: **8 checks**;
- deterministic hybrid rebuild: **2 maps**;
- release audit: **205 checks**, passing with the repository's pre-existing ACME-not-run qualification.

Evidence is under `validation/multiply_refresh/`, `validation/review/`, `validation/turbo_relocation/`, `validation/source_relocation/` and `validation/hybrid/`.

## Standing integration rule

A multiplication record or practical improvement is now treated as a library-wide candidate. It should be tested against every fixed profile, selected only where it wins under that profile's resource contract, exposed as reusable source, propagated to READY/fixed-shift derivatives, and reflected in the consolidated measurements. A faster standalone benchmark is not by itself sufficient reason to replace a resident profile implementation.
