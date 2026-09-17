# Positive-fraction prepared ratio specialization

**Status:** calibrated cycle model; not yet resident-image certification and not a stable API.

The real-game audits reveal a stronger contract than the original signed prepared-ratio prototype for the most important current use case, Quake64 near-plane interpolation.

For a valid crossing oriented from the behind endpoint to the front endpoint:

```text
n = ZCLIP - z_behind
d = z_front - z_behind

0 < n < d
```

So the prepared ratio itself is always a **positive strict fraction**. Only the X/Y component being interpolated is signed.

That lets us ask a more implementation-plan-friendly question:

> How much do we gain by exposing the actual semantic domain instead of paying for signed ratio generality that the workload does not need?

## Proposed research contract

```text
URATIO16_PREP_FRACTION
    n : uint16
    d : uint16
    requires 0 < n < d

    m = round(n * 65536 / d)

URATIO16_APPLY_S16
    y : signed16

    result = trunc_toward_zero(y * m / 65536)
```

The Q0.16 error contract remains the same as the broader prepared-ratio work: for signed16 `y`, the integer result differs from exact `trunc(y*n/d)` by at most one.

## What disappears

The existing general PREP handles:

- ratio sign calculation;
- signed absolute value for `n`;
- signed absolute value for `d`;
- divide-by-zero;
- zero numerator;
- `|n|>|d|` rejection;
- identity/negate-identity mode;
- general-mode state.

None of that is required by `0<n<d`.

The hot APPLY similarly no longer needs:

- `RATIO_MODE` dispatch;
- `RATIO_SIGN` combination;
- a stored combined output sign.

It only needs to branch on the sign of `y`, multiply `abs(y)` by the prepared positive Q0.16 magnitude, and form the signed high-half result.

## Calibrated cycle model

`prepared_fraction_model.py` contains an instruction-level model of the current V2 `record_umul16_17zp.a` `same_x` core. It includes `(zp),Y` page-cross costs and the native carry branches.

The important calibration check is that, on the exact same 5,000-pair `$C0FFEE` Quake stress corpus used by `PREPARED_RATIO_V2_5000.json`, the model reproduces the already measured general fast APPLY mean exactly:

```text
measured APPLY mean   216.1442 cycles
modeled APPLY mean    216.1442 cycles
model difference        0.0000 cycles
```

That does not turn the specialization estimate into resident-image evidence, but it gives a strong calibrated prediction before spending time integrating another assembler candidate.

### Specialized APPLY prediction

| Path | Mean cycles | Min | Max |
|---|---:|---:|---:|
| current general fast APPLY | 216.1442 | 192 | 256 |
| positive-fraction APPLY model | **182.2030** | **164** | **216** |

Predicted saving:

```text
33.9412 cycles / APPLY
15.70% below the current APPLY mean
```

The arithmetic model reports **zero errors** against the same prepared-Q16 contract.

For positive `y`, removing ratio/mode/sign bookkeeping saves about 28 wrapper cycles plus the same native multiply behavior. Negative `y` also benefits because the result can be negated directly from the native A:Y high word rather than publishing it and rereading it first.

## PREP prediction

On this corpus, the current signed/general prefix through strict-fraction initialization averages about:

```text
87.178 cycles
```

A strict positive-fraction prefix needs only operand copies, quotient-state clear and an explicit initial `CLC`:

```text
38 cycles
```

So the modeled prefix saving is:

```text
49.178 cycles
```

Applying that delta to the already measured unrolled PREP mean gives:

```text
current measured unrolled PREP   744.5384
predicted fraction PREP           695.3604
```

The 16-step fractional divide body and rounding logic are unchanged.

## Predicted X/Y pair

Combining the calibrated APPLY model with the measured PREP baseline:

```text
current general prepared pair     1176.8268 cycles
fraction-specialized prediction   1059.7664 cycles
                                  ---------
saving                              117.0604 cycles
```

That is about **9.95% below the current prepared-ratio pair**.

Against the measured Quake64 arithmetic pair on the same stress corpus:

```text
Quake64 current                    3510.2862
fraction prepared prediction       1059.7664
```

or approximately **69.81% lower**.

Again, the 1059.77 figure is a **model prediction**, not a new mini6502 resident-image measurement.

## Why this specialization is acceptable under the roadmap

This is not specialization for a benchmark-friendly constant. It expresses a real semantic invariant of interpolation:

```text
0 < t < 1
```

That domain appears in near clipping, edge interpolation and many geometry kernels. It is therefore more reusable than a Quake-specific constant trick while still avoiding generality that the operation does not need.

The result also reinforces the project rule that we should expose semantic operations rather than blindly general primitives.

## Next gate

1. Generate an actual V2 `URATIO16_PREP_FRACTION` / `URATIO16_APPLY_S16` assembly candidate.
2. Add it to `benchmark_prepared_ratio.py` and verify the model against mini6502.
3. Compare both fast-bound and safe-state policies.
4. Only then decide whether this strict-fraction family deserves promotion over the broader signed prepared-ratio API.

The broader signed PREP/APPLY remains useful research, especially for callers that genuinely need signed ratios. For the currently demonstrated hard-to-fake workload, the positive-fraction contract is the better optimization target.
