# MULDIV16: full-width 16-bit multiply/divide

`MATH_UMULDIV16` and `MATH_SMULDIV16` are stable fused scale/ratio primitives.
They compute the **full 32-bit product first** and divide that product by a
16-bit divisor. This avoids the overflow error of truncating a 16x16 product
back to 16 bits before division.

## ABI

| Entry | Inputs | Outputs | Status |
|---|---|---|---|
| `MATH_UMULDIV16` | unsigned `X16`, `Y16`, `D16` | `Q32`, `R16` | `C=0` success; `C=1` on `D=0` |
| `MATH_SMULDIV16` | signed `X16`, `Y16`, `D16` | signed `Q32`, signed `R16` | `C=0` success; `C=1` on `D=0` |

Reference addresses are `$32E0` and `$32E3`. Relocatable callers should
use the generated `math_api.inc`, not hard-code these addresses.

For a nonzero divisor:

```text
UMULDIV16: Q,R = divmod(X*Y, D)

SMULDIV16:
  P = signed(X) * signed(Y)
  Q = trunc(P / signed(D))       ; toward zero
  R = P - Q*signed(D)
```

The signed remainder therefore follows the sign of the full product when
nonzero. `X`, `Y`, and `D` are preserved. `N` and `Z` are internal
scratch for this fused operation. On divisor zero, both calls return `C=1`
with `Q=0` and `R=0`.

## Why it is useful

A common fixed-point/game calculation is `(value * scale) / denominator`.
Doing the multiply at 16-bit precision can overflow even when the final
quotient fits comfortably. MULDIV16 preserves all 32 product bits, so it is
appropriate for scaling coordinates, interpolation ratios, unit conversions,
projection factors, timers, and other rational transforms.

## Implementations and performance

The canonical 9,001-case corpus includes signed/unsigned edge values,
divide-by-zero, exact divisibility, quotient boundaries, and deterministic
random triples. Reference and alternate-map cycle vectors are identical.

| Profile | UMULDIV16 mean | min-max | SMULDIV16 mean | min-max |
|---|---:|---:|---:|---:|
| V1 Balanced | 1289.022331 | 513-2300 | 1378.300411 | 490-2271 |
| V2 Pareto-Fast | **801.646373** | 301-1923 | **889.395956** | 83-1893 |
| V3 REU 512K | **801.646373** | 301-1923 | **889.395956** | 83-1893 |
| V4 REU 16M | **801.646373** | 301-1923 | **889.395956** | 83-1893 |
| V5 Hybrid Low-ZP | **834.646373** | **334-1956** | **916.200755** | **83-1920** |

V1 keeps the compact compositional implementation: full public multiply,
four-byte product handoff, then the selected mixed-width divider.

V2-V4 use two OptiSearch-derived fusion ideas:

1. **Producer-consumer state fusion.** The unsigned quarter-square producer's
   returned product bytes are written directly into the private UDIV32/16
   state, bypassing public product materialization and divider marshalling.
2. **Signed-quadrant fusion.** Signed X/Y/D are normalized once, an unsigned
   magnitude multiply/divide is performed, then quotient and remainder signs
   are applied once. This avoids doing signed-product correction and then
   reconstructing a magnitude again inside signed division.

On the paired V2-V4 signed corpus, the fused signed path improves the composed
baseline from **1133.038773 to 889.395956 cycles mean**, with maximum latency
**2162 to 1893**, **zero slower cases**, and per-call savings of **64 to 988
cycles**.

V5 now applies the same producer-consumer principle under its stricter **31-byte
normal-ZP contract**, without importing the high-ZP V2 multiplier. The hybrid
builder reuses the qualified V1 **17-ZP UMUL16 record producer**, binds its
quarter-square pointers in the overlapping low-ZP window, and feeds the returned
`z0/X/A/Y` product bytes directly into the relocated private V2 UDIV32/16
state. The signed path normalizes X/Y once, performs one unsigned magnitude
multiply/divide, then fixes quotient and remainder signs. Divisor magnitude is
bound only after multiplication because the divider's D slots overlap the
producer pointer image.

Against the previous V5 composition, unsigned mean latency improves
**956.646373 -> 834.646373 cycles** (456-2078 -> 334-1956), while signed
improves **1378.300411 -> 916.200755 cycles** (490-2271 -> 83-1920). The
reference and alternate maps have identical cycle vectors. The remaining V5
gap to V2-V4 is primarily the cost of re-binding the overlapping low-ZP
quarter-square pointers on each call; retaining those bindings across arbitrary
public calls would violate V5's shared-scratch assumptions.

The fused routines add no persistent stack reservation and reuse the existing
profile multiplication/division scratch classes. The V2-V4 signed fusion lives
in a certified previously unused `REG_LOW+$0BCD` island; the unsigned direct
handoff replaces the now-dead composed handoff at `REG_API+$03C9`.

## Validation

`tools/validate_muldiv16.py` executes 9,001 unsigned and 9,001 signed cases
for every fixed profile on both reference and alternate maps, checks exact
quotient/remainder/Carry semantics, verifies X/Y/D preservation, and requires
cycle-vector identity across relocation maps. The common source validator also
executes both calls as part of the stable 56-entry API suite.
