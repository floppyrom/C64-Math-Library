# Signed DIV/MOD optimization campaign — 2026-10-08

This note records the first family completed under the library-wide **manual design -> OptiSearch -> post-OptiSearch synthesis** campaign tracked by issue #39. The stable API and signed arithmetic semantics are unchanged.

## Scope

Reviewed stable signed division/remainder entries:

- `MATH_SDIV8` / `MATH_SMOD8`
- `MATH_SDIV16` / `MATH_SMOD16`
- `MATH_SDIV24` / `MATH_SMOD24`
- `MATH_SDIV32_16` / `MATH_SMOD32_16`
- `MATH_SDIV32_32` / `MATH_SMOD32_32`

`MATH_SDIV16_SHL8` is also measured because it composes through the selected signed 32/16 divider. A dedicated shifted-division/reciprocal campaign will revisit its own adapter architecture separately.

## Manual pass

### SDIV24 magnitude-deferral experiment

A V2 prototype transplanted the SDIV16 four-sign-quadrant idea into SDIV24: q=0 was tested before eagerly materializing both operand magnitudes, and the first residual was written directly to R. The candidate passed the signed corpus but reproduced the existing V2 timing exactly (**248.344384 cycles mean, 57-3339**) and was therefore rejected. The current SDIV24 architecture remains selected.

### SDIV32/16 direct public-output fusion

V2/V3/V4 previously completed the private magnitude division and then repaired/copied private quotient/remainder state into the stable ABI. The new path carries quotient sign as one-bit control state, writes the remainder directly to the public result, and uses positive/negative quotient tails in the existing adapter reservation.

This retains the same private magnitude engine, stable inputs/outputs, 12-byte transient ZP class, public addresses and divide-by-zero semantics.

| Profile | SDIV32/16 before | after | SMOD32/16 before | after | SDIV16_SHL8 before | after |
|---|---:|---:|---:|---:|---:|---:|
| V1 | 955.051690 | 955.051690 | 1061.083032 | 1061.083032 | 952.471538 | 952.471538 |
| V2 | 833.995638 | **817.550927** | 861.849097 | **848.623105** | 834.061287 | **819.067394** |
| V3 | 833.572737 | **817.533479** | 863.249097 | **850.511191** | 832.687023 | **817.401091** |
| V4 | 829.631189 | **813.759215** | 861.002888 | **848.283755** | 831.029880 | **816.061505** |
| V5 | 958.522137 | 958.522137 | 1061.475812 | 1061.475812 | 953.277863 | 953.277863 |

V1/V5 retain their low-pressure 32/16 implementation because the V2-derived transplant is not a compatible improvement under that layout/resource choice.

### SDIV32/32 preserved-input sign rediscovery

The stable ABI preserves N and D. The old native signed 32/32 wrapper nevertheless saved quotient-sign and remainder-sign flags before entering the magnitude core, then loaded those flags after return. The new wrapper removes those flag bytes and recomputes:

- quotient sign from original `sign(N) XOR sign(D)`; and
- remainder sign from original `sign(N)`.

The private magnitude engine is unchanged. V2/V3/V4 no longer need the two ZP sign-flag bytes; V1/V5 eliminate the equivalent V1 scratch flag bytes. The V1/V5 wrapper remains at `$C134`, after the longer V1 unsigned 32/32 legacy tail; V2-V4 use `$C12C`.

| Profile | SDIV32/32 before | after | SMOD32/32 before | after |
|---|---:|---:|---:|---:|
| V1 | 586.396050 | **566.839288** | 785.979061 | **766.253430** |
| V2 | 553.098146 | **537.452736** | 746.032491 | **730.251986** |
| V3 | 552.481381 | **536.835972** | 742.016606 | **726.236101** |
| V4 | 552.840042 | **537.194633** | 754.883032 | **739.102527** |
| V5 | 591.562641 | **572.005880** | 785.582671 | **765.857040** |

The 32/32 maximum also falls by 16 cycles in V2-V4 (2384 -> 2368) and by 20 cycles in V1/V5 (2474 -> 2454).

## OptiSearch pass

The uploaded OptiSearchV2 archive was verified as the same build used by the prior review (SHA-256 `f5a6a9f0e8728186f91a95c1112a70488cf943fc99b2380c52272424e44455eb`).

For signed 32/16, the retained frontier confirms the library's speed profiles should remain on the **fast decomposed-rectangular** family. A paired screening corpus found:

| OptiSearch coordinate | Mean cycles | Code | ZP | Other RAM |
|---|---:|---:|---:|---:|
| extreme | 757.835 | 2775 B | 19 B | 11642 B |
| fast | 764.344 | 2075 B | 18 B | 0 |
| q2-special | 771.765 | 1226 B | 20 B | 0 |
| direct-fast | 819.840 | 1095 B | 18 B | 0 |
| 512-class | 894.038 | 480 B | 18 B | 0 |
| practical-small | 1512.060 | 359 B | 18 B | 0 |

The extreme point is not suitable for the fixed profiles because of its 11.6 KiB additional RAM demand. The fast point confirms the existing speed-oriented magnitude family; the library's new public-output/sign-flow fusion is the useful post-OptiSearch synthesis step. The q2-special point is retained as a possible Custom Pareto trade-off for the later Pareto-family audit rather than replacing the fixed speed profiles.

For signed 32/32, OptiSearch's active generic restoring Q+R point is approximately **3480.067 cycles / 376 code / 40 ZP**, far behind the library's ~537-572-cycle native paths, so no core transplant is justified.

## Rejected output-liveness idea

OptiSearch correctly treats output liveness as an optimization dimension, including quotient-only and remainder-only division. It does **not** justify changing the stable `SMOD*` entries: the library's stable modulo aliases return the same Q+R state as their corresponding signed divider, and the validators enforce that contract.

The repository also retains an earlier signed remainder-only A/B experiment in `relocatable_source/division/remainder_fast_v2.inc`; it was correct but **29-41 cycles slower** because it duplicated signed magnitude setup. No remainder-only stable replacement is installed.

## SDIV8/16/24 disposition

- **SDIV8:** current direct native signed implementation retained. OptiSearch's attractive q-only points are not Q+R ABI-compatible; no compatible replacement demonstrated a fixed-profile win.
- **SDIV16:** current four-sign-case direct-output implementation retained. It already performs early q=0/q=1 specialization and avoids post-core sign rediscovery; no compatible OptiSearch transplant improved it.
- **SDIV24:** current selected profile-specific fast/Repose-derived implementations retained. The new magnitude-deferral transplant was correctness-clean but timing-neutral.

## Validation

The final candidate passes the deterministic signed division/modulo corpus on all five rebuilt profiles with zero errors. This covers signed division, modulo aliases, divide-by-zero, preserved inputs and `SDIV16_SHL8` composition. Signed DIV/MOD validation is promoted to the normal CI workflow so future changes cannot silently regress these paths.

The family is complete only after regenerated resident/source/standalone artifacts, benchmark indexes, signed-source mirrors, documentation, changelogs, checksums/package audit and full CI are synchronized.
