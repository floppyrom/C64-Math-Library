# Signed core reuse and liftable-source audit — 2026-10-08

## Scope

This pass followed the project workflow **manual architecture review -> OptiSearch -> post-OptiSearch manual review -> exhaustive timing/validation**. It was triggered by the observation that V5 `MATH_SDIV16_SHL8` was materially faster than V2-V4 even though V5 was using the relocated V2 unsigned 32/16 divider as its magnitude engine.

The audit covered the signed division paths most likely to duplicate already-qualified unsigned arithmetic:

- `MATH_SDIV16_SHL8`
- `MATH_SDIV32_16`
- `MATH_SDIV32_32`

It also reviewed the publication model for `MATH_UMULDIV16` / `MATH_SMULDIV16`, because the profile `standalone/` files were exact executable mirrors but not the clean symbolic source modules a developer would normally expect to copy into another project.

## Architectural result

### SDIV16_SHL8

V2, V3 and V4 previously bound signed magnitudes into a separate `D32F` signed 32/16 magnitude path. The new front end instead:

1. computes `|D|` directly into the selected `U3216` divisor state;
2. computes `|N << 8|` directly into the selected `U3216` numerator state;
3. enters `U3216_ENTRY`, the same magnitude engine used by the unsigned path;
4. applies quotient and remainder signs through the already-qualified MULDIV16 result tails.

V5 already used this architecture; its helper received a further safe positive-divisor classification shortcut during the post-OptiSearch manual pass. The V2-V4 shifted helper is deliberately kept smaller because expanding it would overlap the adjacent reciprocal implementation.

### SDIV32/16

V2-V4 now normalize signed `N32` and `D16` directly into the same `U3216` private state used by `MATH_UDIV32_16`. V5 uses the relocated V2 `U3216` substrate and places its thin signed front end in the retired V1 signed-prefix page, preserving the V5 **31-byte normal-ZP contract**.

The post-OptiSearch manual pass uses the Z flag preserved by `STA` to skip a redundant low-byte zero classification when a positive divisor already has a nonzero high byte. This saves about 0.45 cycles on the canonical mixed corpus without increasing the public resource contract.

### SDIV32/32

V2-V4 no longer keep a duplicate signed magnitude divider. The signed wrapper:

1. verifies nonzero divisor semantics;
2. saves only the original sign bytes on the transient CPU stack;
3. temporarily normalizes public `N32` / `D32` to positive magnitudes in place;
4. calls the profile-selected public `MATH_UDIV32_32`;
5. restores `N` and `D`;
6. fixes quotient/remainder signs.

The public unsigned divider preserves its inputs, so the temporary normalization is fully restored before return. This also means future qualified improvements to the selected unsigned 32/32 engine automatically benefit the signed wrapper.

V1 remains on its Balanced private signed 32/32 core. V5 inherits that Balanced 32/32 choice. The shared public-unsigned wrapper was not selected for those profiles because it did not improve their intended resource/performance point.

## Final measured candidate means

All figures below are real public-entry timings from the deterministic signed-division corpus. Caller JSR/input stores are excluded; the routine RTS is included.

| Routine | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| `MATH_SDIV16_SHL8` | 846.155071 | 630.032715 | 630.265213 | 628.417884 | 628.885496 |
| `MATH_SDIV32_16` | 955.051690 | 724.392148 | 724.449509 | 721.003490 | 722.170774 |
| `MATH_SDIV32_32` | 566.839288 | 420.452435 | 416.865672 | 418.153927 | 572.005880 |

For comparison, the pre-pass published means were:

| Routine | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| `MATH_SDIV16_SHL8` | 846.155071 | 715.633370 | 714.004798 | 712.609597 | 630.805016 |
| `MATH_SDIV32_16` | 955.051690 | 817.550927 | 817.533479 | 813.759215 | 958.522137 |
| `MATH_SDIV32_32` | 566.839288 | 537.452736 | 536.835972 | 537.194633 | 572.005880 |

The important point is architectural rather than profile-specific: the signed fast profiles now pay for sign/magnitude handling around the best qualified magnitude engine instead of maintaining a second full divider.

## Validation

Latest candidate proof:

- **364,533** signed division/modulo calls, zero errors;
- V1-V5 input-preservation and carry/divide-by-zero semantics retained;
- **65** published native signed source mirrors, **270** byte/source checks;
- signed layout: **279** checks / **65** signed-vs-unsigned pair comparisons;
- **11** explicitly approved shared-core pair relationships;
- reference source rebuilds pass;
- V5 reference/alternate hybrid builds pass;
- V5 remains at **31 normal ZP bytes**.

The shared-core validator is intentionally whitelist-based. Any executable overlap not declared as an audited magnitude-substrate relationship remains a failure.

## OptiSearch pass

Archive used:

- `OptiSearchV2-2026-10-06(2).zip`
- SHA-256 `f5a6a9f0e8728186f91a95c1112a70488cf943fc99b2380c52272424e44455eb`

The retained generic OptiSearch signed 32/32 frontier is not competitive with the library-specific composition: its exact point is roughly **3480 cycles / 376 code bytes / 40 ZP**, versus roughly **417-420 cycles** for the selected V2-V4 public path. The useful OptiSearch contribution here is therefore the optimization workflow and local MOS6502 rewrite catalogue, not replacement of the magnitude engine.

The current signed wrappers and fast MULDIV16 source were screened for the relevant local rules:

- zero coalescing;
- negation fusion;
- sign-branch reuse;
- branchless sign fill;
- fall-through JMP removal;
- store/reload removal.

When explicit `* =` placement directives are treated as hard control-flow barriers, **no legal local rewrite survives** in the selected signed wrappers. One apparent MULDIV16 fall-through win was rejected during the post-OptiSearch manual pass because it crossed an explicit code-island origin; the required JMP was restored.

## Post-OptiSearch manual pass

The manual re-read found one valid improvement not selected by the generic local rules: for a positive 16-bit divisor, `STA` preserves the Z flag produced by the high-byte load. A nonzero positive high byte can therefore bypass the low-byte zero test.

This is retained in the roomy V2-V5 SDIV32/16 front ends and in the V5 shifted helper. It is not retained in the V2-V4 shifted helper because the larger branch layout intrudes into the neighboring reciprocal slot and breaks `MATH_URECIP16_Q16`. The smaller helper is therefore the correct selected point there.

## Signed implementation taxonomy

The old rule “signed arithmetic must never enter corresponding unsigned executable code” was too strict. It made executable ownership a goal in itself and could force duplicate arithmetic.

The enforceable rule is now:

> The signed public API owns signed semantics, normalization and result correction. A magnitude engine may be shared only through an explicit, audited validator exception.

Signed multiplication and the smaller signed dividers remain private where that is the best implementation. Shared magnitude graphs are used only where measured and qualified.

## Liftable MULDIV16 source

Every stable API still has an exact profile-local executable mirror under `<profile>/standalone/`. Those files are audit views: they intentionally show the exact reachable shipped code and may rely on shared tables/data.

MULDIV16 now additionally has human-facing symbolic sources under `routines/muldiv16/`:

- `muldiv16_composed.inc` — portable composition using public multiply/divide primitives;
- `muldiv16_fast_v2v4.inc` — fused V2/V3/V4 producer-to-divider implementation.

The integrated profile sources include these same files, so they are no longer documentation-only copies. `routines/muldiv16/README.md` lists the private symbols required by the fused variant.

The project keeps both publication layers deliberately:

1. exact executable mirrors for auditability;
2. curated symbolic modules for practical lifting and adaptation.
