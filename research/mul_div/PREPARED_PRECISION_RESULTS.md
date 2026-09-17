# Prepared ratio precision reduction

**Status:** mathematical bound + calibrated cycle model; Q14 cycle point is not yet resident-image certified.

The first prepared-ratio work used rounded Q0.16 state because it mapped naturally to the existing 16x16 high-half multiply:

```text
m16 = round((n/d) * 65536)
result = trunc(component * m16 / 65536)
```

For the actual semantic promise we adopted, however, Q16 is more precise than necessary.

## The precision law

For rounded Qp state:

```text
mp = round((n/d) * 2^p)
```

nearest rounding guarantees:

```text
|mp/2^p - n/d| <= 1 / (2 * 2^p)
```

If the signed component magnitude is bounded by `M`, then the real-valued product error is at most:

```text
M / 2^(p+1)
```

To guarantee that truncation differs from exact `trunc(component*n/d)` by at most one integer unit, it is sufficient that:

```text
M / 2^(p+1) <= 1
```

This yields:

| Component bound | Minimum sufficient rounded ratio precision |
|---:|---:|
| full signed16, `|y| <= 32768` | **Q14** |
| `|y| <= 16384` | Q13 |
| `|y| <= 8192` | Q12 |
| `|y| <= 4096` | Q11 |

So **Q14 is sufficient for the complete signed16 input range while retaining the same <=1 integer-error contract**.

The earlier Q16 design was two fractional bits more accurate than the contract required.

## Why this matters on the 6510

The PREP routine is a fractional divider. A strict interpolation ratio begins with `0<n<d`, so each fractional output bit costs another carry-pipelined divide stage.

Dropping from 16 to 14 ratio bits removes two complete stages.

The generated multiplier state can still use the existing native UMUL16 high-half path: after producing rounded Q14 state, shift the 14-bit multiplier left by two before binding it as a Q16 multiplier.

```text
m16 = m14 << 2
```

No APPLY arithmetic changes are required.

The only extra semantic case is rounding very-near-one ratios to exactly `1.0`. Q14 can produce `m14=$4000`, which cannot be represented as a 16-bit Q16 multiplier after the left shift. That case should be treated as an **identity operation**, which is still within the <=1 contract.

## Calibrated PREP model

`prepared_precision_model.py` models the actual unrolled strict-fraction instruction geometry and calibrates its Q16 result against the previously established strict-fraction Q16 PREP prediction.

On the same 5,000-edge `$C0FFEE` strict near-clip stress corpus:

| Ratio precision | Modeled PREP mean | Stress max error | Full signed16 <=1 guarantee? |
|---|---:|---:|---|
| Q16 | 695.360 cycles | 1 | yes |
| Q15 | ~669.55 cycles | 1 | yes |
| **Q14** | **~643.94 cycles** | **1** | **yes** |
| Q13 | ~618.47 cycles | 1 on this ±8192 corpus | no, only `|y|<=16384` |
| Q12 | ~592.88 cycles | 1 on this ±8192 corpus | no, only `|y|<=8192` |
| Q11 | lower again | 2 on this corpus | no |

The important point is not the stress-corpus error alone. **Q14 has a domain-wide mathematical <=1 guarantee for every signed16 component.** Q13/Q12 become valid only when the caller contract also bounds component magnitude.

## Predicted fused SCALE2 result

The strict-fraction APPLY mean is already about:

```text
182.194 cycles / signed16 component
```

Using Q14 PREP and fusing two applications into one compound call gives a calibrated prediction of approximately:

```text
Q14 PREP                        ~643.94
2 x APPLY                       ~364.39
remove PREP terminal CLC+RTS      -8.00
remove first APPLY return         ~-6.51
----------------------------------------
fused SCALE2 internal           ~993.82 cycles
one external caller JSR           +6.00
----------------------------------------
call-to-return                  ~999.82 cycles
```

So the Q14 precision law brings the compound operation to **about one thousand cycles including a single caller JSR** in the calibrated model, while keeping the full signed16 <=1 error guarantee.

Against the earlier Quake64 stress arithmetic reference of about `3510.29` cycles, that is roughly **71.7% lower** before caller marshalling differences.

This is a model prediction until the Q14 assembly candidate is run through the resident-image harness.

## API implication

This precision result makes the semantic family cleaner:

```text
full signed16 components, <=1 error
    -> Q14 prepared fraction

known |component| <= 8192, <=1 error
    -> Q12 specialization

exact result required
    -> exact MUL_DIV / exact-corrected path
```

The ratio precision should therefore be selected from the **required result error and component range**, not fixed arbitrarily at Q16.

That is consistent with the implementation plan: spend precision only where it buys visible/useful capability.

## Next gate

1. Generate an actual Q14 fused strict-fraction SCALE2 V2 kernel.
2. Run it in `mini6502` against the shipped V2 image.
3. Verify zero prepared-contract failures and max exact-ratio error <=1.
4. Compare the actual result against the ~993.82-cycle calibrated prediction.
5. Only after resident evidence, decide whether Q14 SCALE2 becomes the primary interpolation candidate.
