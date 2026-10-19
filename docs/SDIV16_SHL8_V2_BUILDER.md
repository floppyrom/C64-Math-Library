# Historical V2 shared-core signed shifted16 public speed candidate

Status: **research until exact-head CI and native VICE pass**. This file does
not claim that the five historical profiles can be retired.

The operation-first `MATH_SDIV16_SHL8` API is exact signed fixed-point
`(N16 << 8) / D16`, truncating toward zero. It writes low 24 quotient
bits and low 16 remainder bits, with remainder sign equal to the numerator.
Q3 and R2..3 are not outputs and must be untouched. D=0 yields zero
Q24/R16 and C=1; other inputs clear C. Both public inputs and stack depth
must survive. Signed overflow (-32768<<8)/-1 wraps modulo 24 bits.

## Independent choices

| Source | Reserved executable | ZP | RAM scratch | Native assumptions |
|---|---:|---:|---:|---|
| `link:portable-zerozp` | 237 B | 0 | 3 B | NMOS 6510, CLD |
| `link:v2-signed-shifted-public` | 2,624 B | 12 | 0 B | NMOS LAX/ANC, CLD |

The signed option source-links the canonical V2 Pareto-Fast 32/16 split-tail
producer without modifying its bytes or fixed arithmetic strategy, then
appends a compact sign/magnitude adapter at a separate public entry.

The adapter stages `abs(N16) << 8` directly as the 32-bit donor's
`n1:n0:ln1:ln0` numerator; the low byte and high byte are zero, while
middle bytes contain the magnitude. `abs(D16)` is copied to `d1:d0`.
After calling the V2 magnitude kernel, Q24 is negated if N and D have
opposite signs and R16 is negated if N was negative. The full public
input window remains untouched; zero divisor is handled early. The fixed
12-byte private ZP and 2,624-byte image reservations are explicit.

This is a **Pareto alternative**, not a replacement for portable code:
for projects with 0 available ZP or tight RAM, only the small portable
implementation fits and must remain available. Speed mode must choose
the V2 candidate only if a matched complete-call benchmark proves its
advantage under the selected memory budget.

## Acceptance before release

1. Build with each source under two independent RAM layouts and compare
   the *same 384 signed N/D input pairs*, including D=0, signed extremes,
   -32768/-1 overflow and preserved public sentinels.
2. Compare mean, p95 and sampled maximum CPU-model cycles. Every candidate
   must use the **same public-call ABI**. Resident-only V2 timing does not
   qualify an alternative.
3. Run a 150-call 24-math-frame replay including the busiest frame and
   each per-frame regression. This does not simulate PAL VIC badlines,
   raster IRQ interference, SID updates or REU service.
4. Verify resource-budget rejection of an explicitly pinned candidate
   and automatic portable fallback under insufficient RAM/ZP.
5. Execute 96 public API calls on each of two relocated images in pinned
   native VICE r46284, with independent Q24/R16/C oracle and input checks.
6. Reconcile all package source SHA256 entries, publication audit totals,
   full operation-first builder and five-profile legacy certifications.

The long-term goal is to recognize when unsigned shifted16 and signed
shifted16 can share *one* physical V2 32/16 producer rather than duplicating
the same 2.3 KiB donor in a mixed build. Independent correctness and
full-public-cycle qualification of the signed adapter comes first.
