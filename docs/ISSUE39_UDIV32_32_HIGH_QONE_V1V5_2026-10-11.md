# Issue #39 — V1/V5 bounded high-byte q=1 shortcut for UDIV32/32 and UMOD32/32 (2026-10-11)

## Diagnosis

The common-input benchmark removes the profile-specific RNG confounder. Before this patch, V1 and V5 had **470.755955 cycles** average for `MATH_UDIV32_32` and **523.279765** for `MATH_UMOD32_32`; the V2–V4 live-high kernels were faster at **242.548553** and **295.997654**, respectively. V1/V5's existing early gate already handles divisor zero, quotient zero and equality, but **N>D and quotient exactly one** still enter their expensive legacy long division loop. Importing the V2 core wholesale would change code and temporary-ZP/resource-class ownership, rather than preserve the 31-byte V5 normal-ZP limit.

## High-byte proof and selected architecture

Let `N` and `D` be unsigned 32-bit inputs. The existing source gate dispatches to the new private helper only after establishing `N>D` and `D!=0`. Then:
- If `D3>=128`, `D>=2^31`, so `2D>=2^32>N`; hence the quotient is exactly one.
- Otherwise, if `0<D3<128` and `N3<2*D3`, then `N<2*D3*2^24<=2D`, so the quotient is exactly one.
- All remaining inputs rejoin the **unchanged** legacy core, including all `D3=0` high-quotient stress cases and the conservative equal-high-byte boundary.

For proven q=1, a four-byte SEC/SBC chain writes `R=N-D`, writes `Q=1`, clears carry, and returns. The public operands are never mutated. The helper occupies **73 newly executable bytes** in a previously unused `REG_TABLE+$0810` island (reference `$6810–$6858`), relocated symbolically to the alternate memory map. Public entry addresses, 31-byte V5 normal-ZP contract, zero-page ownership, resident PRG span, and V2/V3/V4 arithmetic remain unchanged. Existing signed 32-bit DIV/MOD wrappers are exercised by the full signed suite.

The V5 hybrid builder source-guards the inherited helper signature and existing prechecked nonzero call site; it does not apply the previous legacy zero-gate patch a second time. This is **manual range-analysis synthesis**, not a new native OptiSearch/Repose candidate. Private OptiSearch remains unpublished.

## Actual 6502 matched-input measurements

| API (both V1 and V5) | Previous mean | New mean | Improvement | Matched calls per profile |
|---|---:|---:|---:|---:|
| `MATH_UDIV32_32` | 470.755955 | **370.572004** | **21.28%** | 2,729 |
| `MATH_UMOD32_32` | 523.279765 | **444.652199** | **15.03%** | 1,705 |

Total **8,868 paired old/new public calls** across V1/V5: zero arithmetic/carry/input errors. For each profile, UDIV32_32 has 545 faster and 735 slower cases; UMOD32_32 has 270 faster and 502 slower cases. Some nonqualifying N>D calls incur **up to 22 extra cycles** from the range gate. Largest observed win is **597 cycles** in one call. An explicit average-latency/Pareto tradeoff: not every input is faster. On the common input corpus V1/V5 still lag V2–V4, and results must not be described as universal workload dominance or physically timed REU cycles.

The local source-prototype also passed:
- **164,410 V1 unsigned**, **164,410 V5 unsigned** public machine-code family calls.
- **97,329 V1 signed**, **36,273 V5 signed** public machine-code family calls, including inherited signed 32/32 wrappers.
- **22,170** V1–V5 matched-input 32/32-family calls (`2,729+1,705` across 5 profiles), preserving the previous V2/V3/V4 means.

Release publication must rebuild and verify all reference and alternate source configurations, all five-profile **822,050 unsigned** and **364,533 signed** family calls, all **136,335 common-input** calls, standalone sources, public rankings, package audits, and both changelogs, then achieve independent green CI. This technical document is not a claim of issue #39 entire unsigned-family completion.

**Next work:** further V1/V5 narrow-divisor/high-quotient rescue architectures (including possible reuse of existing V5 32/16 engine) and explicit no-gain decisions for 8-, 16-, 24-, 32/16- and 32/32-width resource classes before marking unsigned DIV/MOD complete.
