# Prepared-ratio V2 profile provenance correction

**Date:** 2026-09-17  
**Scope:** prepared-ratio research only. No shipped binary or stable API is changed.

A profile-provenance audit found an important distinction that the first prepared-ratio experiments did not preserve.

## What V2 actually ships

The V2 Pareto-Fast resident profile has:

```text
I_UMUL8  = $5300   pareto_umul8.a
I_UMUL16 = $5400   pareto_umul16.a
```

The installed `$5400` kernel is the size-aware **integrated 3xUMUL8** implementation. It consumes public X/Y vectors and writes public Z.

The repository also contains:

```text
v2_pareto_fast/resident/modules/record_umul16_17zp.a
```

That file is a separate record/research source with `generic` / `same_x` entry geometry. It is **not the UMUL16 implementation installed at `$5400` in the shipped V2 resident image**.

## Consequence for the first prepared-ratio benchmark

The early `generate_prepared_ratio.py` / `generate_prepared_fraction.py` experiments were written against the record-core ABI and assumed:

```text
UMUL_GENERIC = $53EC
UMUL_SAME_X  = $5400
```

They were then patched into the shipped V2 image for mini6502 timing. Because shipped `$5400` is instead `pareto_umul16`, those experiments did not execute the intended `same_x` core in that image.

Therefore the earlier prepared-ratio cycle tables based on that assumption, including the approximately:

```text
216.14-cycle APPLY
1176.83-cycle general PREP+2xAPPLY
~1059.77-cycle strict-fraction prediction
```

must be treated as **record-core counterfactual/research numbers, not V2 resident-image evidence**.

The same warning applies to safe-vs-fast state comparisons and the first fused SCALE2 work when they depend on the record-core addresses.

## What remains valid

The following findings do not depend on that profile-address mistake:

- Quake64's current `scale_nd + lerp16` arithmetic structure and its repeated ratio work.
- The semantic invariant for a correctly oriented near-plane crossing: `0 < n < d`.
- The prepared-Q16 arithmetic proof: rounded Q0.16 gives maximum integer error <=1 for signed16 applied values.
- The same <=1 maximum-error bound also holds for floor Q0.16, because the multiplier error is strictly less than one Q0.16 unit.
- The independent observation that one dynamic ratio applied to X/Y is a hard-to-fake compound workload.
- The general exact `UMULDIV16` results, which use their own validated kernels and harnesses.

## Corrected V2 research path

New work now targets the implementation that is actually shipped:

```text
generate_prepared_fraction_pareto.py
    rounded strict-fraction PREP
    APPLY built from three calls to installed V2 UMUL8 ($5300)

prepared_fraction_pareto_model.py
    instruction-level actual-core cycle model
    exhaustive calibration against published UMUL8 45.494140625 mean / 44..47 range

generate_prepared_fraction_pareto_inline.py
    PREP-patched balanced fixed-X quarter-square products
    removes dynamic UMUL8 X binding and three JSR/RTS pairs per APPLY
    nearest and floor PREP modes

benchmark_prepared_fraction_pareto.py
    resident-image gate against shipped V2 + literal Quake64 arithmetic
```

The actual-core model predicts, on the strict 5,000-edge `$C0FFEE` stress corpus:

| Candidate | PREP mean | APPLY mean | PREP + 2 APPLY | Max error |
|---|---:|---:|---:|---:|
| actual V2 Pareto, nearest | 694.284 | 373.563 | 1441.411 | <=1 |
| fixed-X inline, nearest | 718.284 | 293.239 | 1304.762 | <=1 |
| fixed-X inline, floor | 688.972 | 293.237 approx. | 1275.45 approx. | <=1 |

These are **instruction-level model results**, not yet resident-image certification. The UMUL8 submodel itself exactly reproduces the published exhaustive native timing distribution; the compound candidates still need the dedicated mini6502 harness to be run before their cycle numbers are promoted.

## Research interpretation

This correction does not weaken the architectural case for prepared ratio. It changes the implementation target.

The shipped Pareto profile does not expose a cheap persistent `same_x` UMUL16 lifecycle. Its practical path is instead to exploit the fact that the prepared Q0.16 multiplier is fixed across applications:

```text
PREP ratio
    -> patch fixed-X quarter-square sites once

APPLY value
    -> 3 inline fixed-X 8x8 products
    -> high16 only
```

That is a more profile-native optimization and avoids the fragile assumption that unrelated UMUL16 state remains bound.

Until `benchmark_prepared_fraction_pareto.py` is run successfully, the corrected model is the leading evidence and the old record-core cycle tables should not be used for release or performance claims.
