# Issue #39 — 32/16 divisor-aware narrow-numerator donor screen

12 October 2026. **Research-only, no binary or API change.**

Following the 26-byte N16-only donor A/B (PR87), this screen adds
a high-divisor filter to its source: delegate N<65536 to the
resident 16/16 routine only when the divisor high byte D1 reaches
a chosen minimum threshold (1, 4, 16, 64). This avoids invoking
the inferior 16/16 producer on V2–V5 for D<256, while retaining
the established 32/16 path for other operands and D=0.

The research helper is 33 bytes and uses a nested JSR (+2 stack
bytes). It resides at $E100 in a **flat CPU model**, under KERNAL
ROM in an unmodified C64 memory configuration. This is NOT a
native VICE-certified loadable implementation, and remains unsafe
to transplant without actual writable RAM placement and source
relocation testing.

Exact released V1–V5 resident SHA-256 checks; both UDIV32/16 and
UMOD32/16 public-entry calls and Q32/R/C/N/D, sentinel and stack
preservation. **79,130 common old/new input pairs** tested across
all profiles, four live candidate thresholds and originals:
**395,650 fully executed 6502 public calls**, zero ABI errors.
Instruction CPU timing excludes REU/VIC contention.

| Profile | Public entry | D1 minimum | Official mean delta cycles | N16-target delta | N16/D8 delta | N32 uniform delta |
|---|---|---:|---:|---:|---:|---:|
| v1_balanced | MATH_UDIV32_16 | 1 | -12.742763 | -459.192383 | +25.000000 | +17.000000 |
| v1_balanced | MATH_UDIV32_16 | 4 | -3.508611 | -459.759766 | +25.000000 | +17.000000 |
| v1_balanced | MATH_UDIV32_16 | 16 | -3.508611 | -451.024414 | +25.000000 | +17.000000 |
| v1_balanced | MATH_UDIV32_16 | 64 | -3.508611 | -365.703125 | +25.000000 | +17.000000 |
| v1_balanced | MATH_UMOD32_16 | 1 | -30.605865 | -456.587891 | +25.000000 | +17.000000 |
| v1_balanced | MATH_UMOD32_16 | 4 | -15.825806 | -457.028320 | +25.000000 | +17.000000 |
| v1_balanced | MATH_UMOD32_16 | 16 | -15.825806 | -449.284180 | +25.000000 | +17.000000 |
| v1_balanced | MATH_UMOD32_16 | 64 | -15.825806 | -373.869141 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UDIV32_16 | 1 | -6.174789 | -359.720703 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UDIV32_16 | 4 | +1.087944 | -361.040039 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UDIV32_16 | 16 | +1.087944 | -350.584961 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UDIV32_16 | 64 | +1.087944 | -282.153320 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UMOD32_16 | 1 | -20.093255 | -358.595703 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UMOD32_16 | 4 | -8.468622 | -358.763672 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UMOD32_16 | 16 | -8.468622 | -348.391602 | +25.000000 | +17.000000 |
| v2_pareto_fast | MATH_UMOD32_16 | 64 | -8.468622 | -288.411133 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UDIV32_16 | 1 | -6.174789 | -359.720703 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UDIV32_16 | 4 | +1.087944 | -361.040039 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UDIV32_16 | 16 | +1.087944 | -350.584961 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UDIV32_16 | 64 | +1.087944 | -282.153320 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UMOD32_16 | 1 | -20.093255 | -358.595703 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UMOD32_16 | 4 | -8.468622 | -358.763672 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UMOD32_16 | 16 | -8.468622 | -348.391602 | +25.000000 | +17.000000 |
| v3_reu_512k | MATH_UMOD32_16 | 64 | -8.468622 | -288.411133 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UDIV32_16 | 1 | -6.174789 | -359.720703 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UDIV32_16 | 4 | +1.087944 | -361.040039 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UDIV32_16 | 16 | +1.087944 | -350.584961 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UDIV32_16 | 64 | +1.087944 | -282.153320 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UMOD32_16 | 1 | -20.093255 | -358.595703 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UMOD32_16 | 4 | -8.468622 | -358.763672 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UMOD32_16 | 16 | -8.468622 | -348.391602 | +25.000000 | +17.000000 |
| v4_reu_16m | MATH_UMOD32_16 | 64 | -8.468622 | -288.411133 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UDIV32_16 | 1 | -6.174789 | -359.720703 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UDIV32_16 | 4 | +1.087944 | -361.040039 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UDIV32_16 | 16 | +1.087944 | -350.584961 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UDIV32_16 | 64 | +1.087944 | -282.153320 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UMOD32_16 | 1 | -20.093255 | -358.595703 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UMOD32_16 | 4 | -8.468622 | -358.763672 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UMOD32_16 | 16 | -8.468622 | -348.391602 | +25.000000 | +17.000000 |
| v5_hybrid_lowzp | MATH_UMOD32_16 | 64 | -8.468622 | -288.411133 | +25.000000 | +17.000000 |

These are **paired workload differences**, not a universal speed
ranking. All four candidate gates still add 17 cycles to every
full-width numerator on the tested uniform class. Selection based
only on the official weighted corpus is not an unconditional
improvement and would disadvantage different game/demo workloads.

The source code and detailed JSON preserve every faster/slower
count, maximum regression, per-class deltas, exact input hashes
and five resident hashes.

**Disposition:** retain released 32/16 cores as defaults. Publish
this 33-byte source as a reproducible, library-dependent candidate
for future opt-in/narrow-input specialization and potential
source-owned-RAM native qualification. It is not standalone and
must not be installed at $E100 without accounting for ROM banking.
This does not finish the issue #39 unsigned DIV/MOD family campaign.
