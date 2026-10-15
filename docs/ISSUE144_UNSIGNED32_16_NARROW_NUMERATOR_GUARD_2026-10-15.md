# Issue144 B: 22-byte guarded 32÷16 unsigned full-output Pareto option

**Correct on the entire unsigned 32-bit numerator / 16-bit divisor domain.**
**Not a default performance optimization.** This opt-in dispatches to
existing MATH_UDIV16 when the upper numerator word is zero, clearing
both upper quotient bytes first. Otherwise it dispatches to the
original MATH_UDIV32_16. In either case output is the same full Q32,
R16, C including the original D16=0 divide-by-zero contract.
The ordinary public MATH_UMOD32_16 alias returns a quotient too:
this fast path preserves that full output, **not** remainder-only.

## Same-input public-call CPU-model savings in cycles

Positive values mean faster. Negative values mean SLOWER.
Uniform means pseudorandom full-width N32; small10/50/100pct
means a controlled fraction of numerators have zero upper word.
All workloads also include explicitly seeded D=0 cases.

| Profile | Comparable API | Uniform | Small 10% | Small 50% | Small 100% | Quotient 0/1 |
|---|---|---:|---:|---:|---:|---:|
| v1_balanced | UDIV32_16 | -14.00 | 29.18 | 212.59 | 446.15 | 481.43 |
| v1_balanced | UMOD32_16 | -11.00 | 32.18 | 215.59 | 449.15 | 484.43 |
| v2_pareto_fast | UDIV32_16 | -14.00 | 20.71 | 165.47 | 348.82 | 367.26 |
| v2_pareto_fast | UMOD32_16 | -11.00 | 23.71 | 168.47 | 351.82 | 370.26 |
| v3_reu_512k | UDIV32_16 | -14.00 | 20.71 | 165.47 | 348.82 | 367.26 |
| v3_reu_512k | UMOD32_16 | -11.00 | 23.71 | 168.47 | 351.82 | 370.26 |
| v4_reu_16m | UDIV32_16 | -14.00 | 20.71 | 165.47 | 348.82 | 367.26 |
| v4_reu_16m | UMOD32_16 | -11.00 | 23.71 | 168.47 | 351.82 | 370.26 |
| v5_hybrid_lowzp | UDIV32_16 | -14.00 | 20.71 | 165.47 | 348.82 | 367.26 |
| v5_hybrid_lowzp | UMOD32_16 | -11.00 | 23.71 | 168.47 | 351.82 | 370.26 |

Each workload has 256 fixed-seed identical operand pairs/profile/API,
**12,800 paired comparisons / 25,600 baseline+candidate CPU calls**.
Each pair passes complete Q32, R16, carry, unchanged input N/D,
decimal flag cleared and balanced stack. Both signed-looking top-bit
and divisor-zero inputs are included. No new normal zero page.
Native real x64sc: **480 baseline+guard calls across V1–V5**
pass exact Q/R/C, inputs and stack, including D=0 and full N32.
Native CPU cycles are **not** measured.

### Performance threshold and calling contract

For fully uniform full-width numerators, the 22-byte guard
costs **14 extra CPU-model cycles/call** compared with public UDIV32_16,
or 11 extra versus UMOD32_16. It must NOT be installed as the default.
It becomes useful for workloads with enough known-narrow N32:
10% narrow in the measured 256-case mixtures saved ~21–29 cycles/call
for UDIV and ~24–32 for UMOD, while always-narrow saved
~349–446 (UDIV) and ~352–449 (UMOD). These are workload-specific.
The routine is a direct callable $0C80 source example. The application
must verify $0C80..$0C95 is actually free; the library does not reserve it.
The caller can JSR the optional address, or select this source in a
custom builder and measure its actual application-specific input mix.

**A, X, Y and N/Z/V are volatile under the documented public ABI.**
They can differ between the original full-width producer and UDIV16.
A program relying on exact X/Y or N/Z/V values (despite the documented
volatile contract) must NOT substitute this path. The CPU proof
counts these differences transparently. Carry, Q/R, inputs and stack
are exact. Do not use reentrantly or with overlapping IRQ/NMI math:
the helper reuses normal resident ZP, self-modifying state and tables.
Call MATH_INIT as required by the resident profile. No new REU data.

Source: optional/issue144_u32_16_narrow_guard/guard.asm
Same-input reproducible benchmark: tools/issue144_u32div_smallnumerator_screen.py
Native VICE harness: tools/native_issue144_u32_16_narrow_guard.py
CPU proof: validation/review/ISSUE144_U32DIV32_16_NARROW_N_RESEARCH.json
Native proof: validation/review/ISSUE144_U32DIV32_16_NARROW_GUARD_NATIVE_VICE.json
Normal five resident PRGs, REUs, public symbol addresses, normal
zero-page usage and regular PERFORMANCE leaderboard remain unchanged.
No private OptiSearch generator source included.
