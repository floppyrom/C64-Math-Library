# Issue #144 P4 — nine expensive kernels on identical frozen/current-source operands

16 October 2026. **Source-candidate benchmark, not a default binary release.**

The benchmark `tools/issue144_nine_kernel_candidate_benchmark.py` builds five fresh source PRGs and their applicable REU images for each of the reference and alternate relocations, checks the original five PRG/two REU SHA-256 seals, initializes through the correctly relocated `MATH_INIT`, and executes the **same exact input vectors** through the old frozen public entry and corresponding new source-built public entry. The arithmetic output, quotient/remainder/carry, public inputs, and SEEK16 positions and five subsequent `STEP` frames are independently checked. The benchmark records cycles from entry to RTS, not the caller's JSR, and excludes VIC/raster stalls, actual REU DMA latency, and IRQ/NMI nesting. Both relocation maps are measured independently; alternate `MATH_IO`, symbol-array addresses and relocated routine pointers are respected.

Dedicated [workflow run #38878974907](https://github.com/floppyrom/C64-Math-Library/actions/runs/38878974907) **PASS** for both maps (45 rows per map, 15,900 calls/map; 31,800 total), providing original downloadable CSV/JSON before permanent source records are generated. The full test contains **zero input-level CPU-model regressions** in this corpus. This is not an exhaustive optimality claim or a new default Pareto profile.

| Profile | ISQRT32 mean saved | SEEK16_INIT mean saved | UDIV32_16/UMOD32_16 mean saved | SMOD32_16 mean saved |
|---|---:|---:|---:|---:|
| V1 | 51 | 1.913043 | 0 | 0 |
| V2 | 47 | 14.028986 | 3.743284 | 6.707463 |
| V3 | 47 | 12.434783 | 3.743284 | 6.707463 |
| V4 | 135.205479 | 12.434783 | 3.743284 | 6.707463 |
| V5 | 51 | 1.913043 | 3.743284 | 4.770149 |

On this same corpus the current-source `SMUL32`, `UMUL32`, `SMUL32_SHR16` and `UMUL32_SHR16` have **zero cycle improvement relative to the frozen binary** on all five profiles. No claim is made that they cannot be optimized; they are still priority A. Similarly, the relatively small quotient improvements do not satisfy priority B's material unrestricted 32/16 producer goal.

Benchmark populations are per API: `ISQRT32` 438 radicands, `SEEK16_INIT` 69 movement/speed cases (all with STEP trace checks), ordinary 32×32 multiplication 417 operand pairs per API, and unsigned/signed 32/16 division/modulo 335 pairs per API, including D=0, byte divisors, high divisors, all signs and extrema. All five public profiles have the same input population per entry, enabling credible matched-input source-vs-frozen comparisons rather than mixing legacy `PERFORMANCE.md` denominators.

The source benchmark is separate from the versioned immutable artifact built by PR #194. The five historical PRGs, two historical REU files and published legacy `PERFORMANCE.md` remain unchanged. A public tagged production default, physical PAL/NTSC and VIC/REU/DMA elapsed-time analysis, IRQ/NMI scratch reentrancy, and larger unrestricted A/B/C algorithm wins all remain open. Do not close issue #144 solely on this benchmark.
