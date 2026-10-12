# Issue #39 — V2–V5 16-bit high-divisor dispatch sweep

**12 October 2026. Research-only. No shipped binary or ABI changes.**

The source already dispatches through LDX D1 / CPX #15 / BCS.
This exhaustive **17-value candidate sweep** changes only the CPX
immediate operand at $B8EF in each in-memory resident copy and checks
UDIV16 and UMOD16 public entries for V2/V3/V4/V5 using the same input
sequence per threshold and routine. No extra RAM, ZP, stack, or wrapper.
Q/R/C, N/D preservation, stack, and UMOD16 current Q-buffer side effects
are compared to an unpatched current resident. CPU cycles include public
entry and RTS; not native VIC memory contention.

| Profile | Public entry | Tested cases | Default 15 cycles | Best correct cutoff | Mean cycles | Slower individual calls |
|---|---|---:|---:|---:|---:|---:|
| v2_pareto_fast | MATH_UDIV16 | 4201 | 272.111878 | 15 | 272.111878 | 0 |
| v2_pareto_fast | MATH_UMOD16 | 3177 | 321.475291 | 16 | 321.359144 | 7 |
| v3_reu_512k | MATH_UDIV16 | 4201 | 272.111878 | 15 | 272.111878 | 0 |
| v3_reu_512k | MATH_UMOD16 | 3177 | 321.475291 | 16 | 321.359144 | 7 |
| v4_reu_16m | MATH_UDIV16 | 4201 | 272.111878 | 15 | 272.111878 | 0 |
| v4_reu_16m | MATH_UMOD16 | 3177 | 321.475291 | 16 | 321.359144 | 7 |
| v5_hybrid_lowzp | MATH_UDIV16 | 4201 | 272.111878 | 15 | 272.111878 | 0 |
| v5_hybrid_lowzp | MATH_UMOD16 | 3177 | 321.475291 | 16 | 321.359144 | 7 |

**64 configurations fail arithmetic correctness:**
cutoffs 1, 2, 4, 8, 10, 12, 13, and 14 on each
profile/API. These are invalid optimizations, regardless of speed.

At cutoff 16, UDIV16 is **0.054035 cycles slower on average**
(9 inputs faster, 10 slower); UMOD16 is **0.116147 cycles faster**
but **7 individual inputs become slower** (11 faster). These
statistics are identical in each of the four profile images because
they share the same producer. No non-default threshold has
zero regressions across both public APIs and all four profiles.

The official corpus is supplemented by 256 samples each of
q2..9, q10..31, q32..255, 384 full random, 256 small divisors,
and 64 zero divisors per API. The extended 4,201/3,177-input
corpora must not be confused with the official ranking corpus.
Exact operand fingerprints, rejected N/D counterexamples, class means,
and complete delta/faster/slower counts are in
validation/review/ISSUE39_V2V5_U16_D1_CUTOFF_SWEEP.json.

**Decision:** retain #15 on V2–V5 as the shared default.
Do not promote #16 based solely on its tiny modulo mean gain and
do not promote any of #1–#14 because they fail correctness.
This finishes only the cutoff-constant experiment, not the full
unsigned DIV/MOD campaign; issue #39 remains open.
