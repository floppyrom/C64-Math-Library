# Issue #144 B — full-public-call UDIV32/16 shared subtraction research

Date: 15 October 2026. **Source-built research only; no production release.**

## Motivation and technique

The V2, V3 and V4 unsigned 32/16 producer first divides the upper dividend word using the resident 16/16 engine, then processes the remaining 16 dividend bits. Its unrolled continuation repeats the same two-byte subtract sequence in ordinary compare-accepted and 17th-bit-overflow-forced paths. Both arrive at subtraction with carry set. This independent source-level experiment shares the subtract body and sets carry after it, reducing duplicated arithmetic.

Exact, reproducible source-transplant driver: `tools/issue144_u3216_fullcall_source_transplant_screen.py`. It temporarily changes `relocatable_source/division/udiv32_16_split_direct.inc` **in the test checkout**, runs source generation and assembles full public residents on **V2/V3/V4** for **reference and alternate maps**, then compares ordinary public `MATH_UDIV32_16` and `MATH_UMOD32_16` calls with the immutable installed PRGs. It always restores the common include after running. **No donor or OptiSearch private implementation is copied.**

## Complete-public-API CPU-model results

Dedicated CI source+public model gate: [Actions run #38724485006](https://github.com/floppyrom/C64-Math-Library/actions/runs/38724485006), **PASS**. Fixed corpus SHA-256 `873a7f093e844d9ea9493cad2f6ae95a8d48707915174d39bcb70db0dac6ae4b`.

Each of **three profiles × two RAM maps × two public APIs** completes the same **1,280 paired tests**, or **15,360 public-call pairs / 30,720 model calls**, with exact Q32, R16, C, N/D and SP for unsigned full-width operands, small divisors, D=0, boundary and random inputs. For every profile/map/API:
- **512 uniform N32/D16** pairs: **6.591796875 fewer CPU-model cycles/call**.
- All 1,280 mixed cases: **4.7578125 fewer CPU-model cycles/call**.
- **878 faster, 389 equal, 13 one-cycle slower**, best savings 18 cycles; no claim of zero worst-case regression.
- Original common source text 13,036 characters, experimentally rewritten source text 10,704 characters. These are **source text lengths**, not code/PRG sizes. The separate 7,554-case isolated-tail screen lives in merged PR #161.

There is **no ≥5% full-width throughput improvement**. Relative to a ~652-cycle public baseline, saving 6.59 cycles is only ~1%.

## Real native x64sc correctness

Dedicated [Actions run #38725574165](https://github.com/floppyrom/C64-Math-Library/actions/runs/38725574165), **PASS**. `tools/issue144_u3216_fullcall_native.py` uses pinned headless x64sc r46274 and loads real reference resident images with native 6510 test harnesses. For **both public APIs on V2, V3 and V4**, 24 baseline and 24 candidate calls per group were compared: **288 native calls in total**. Q32/R16, carry, original N/D, and stack balance agree with the unsigned independent mathematical oracle and stock binaries. Native VICE only establishes correctness. **No VIC/CPU physical cycle measurements** and no REU DMA/bus timing are claimed.

## Decision and resource boundaries

**Do not silently replace the regular resident code or update PERFORMANCE.md.** Source-built optional candidate only: V1 low-ZP, V5 normal hybrid, complete package integration, reference PRG/REU hashes, mixed IRQ/NMI usage, full resource ownership and more adversarial benchmark populations would need separate certification for a production promotion. The 13 one-cycle regressions and marginal ~1% uniform gain fail our >5% architecture triage heuristic. Main issue #144 B stays **open** for a genuinely faster unrestricted arithmetic producer rather than a guard or alias optimization.

Research CI reproducibility is public. Private OptiSearch code and donor materials are not present. Both ordinary public routines and their historical production benchmark rows remain unchanged.
