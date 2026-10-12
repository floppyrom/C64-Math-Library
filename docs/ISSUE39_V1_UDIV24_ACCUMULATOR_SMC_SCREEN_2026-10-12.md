# Issue #39 — 68-byte writable-RAM accumulator/Self-Modifying 24÷8 screen

**12 October 2026 — SCREENING ONLY, not a released arithmetic implementation.**

## Why this variant exists

Merged PR #78 has a 69-byte exact V1 24÷8 shared-subtract loop. Research PR #79 qualified a simpler, non-self-modifying **61-byte** alternative holding the partial remainder in A instead of RAM. This optional variant keeps A-resident remainder, but takes advantage of the resident V1 code executing from **writable RAM**: it loads D0 once per call and patches the immediate operands of a `CMP #imm` and `SBC #imm` in the same 24-iteration loop. The two per-call patches replace repeated slower absolute operand fetches. The source assembles to **68 bytes**, with no additional normal ZP or stack reserve; it is still 1 byte smaller than the current released PR #78 core.

**Do not use this form from ROM, read-only banked storage or in a re-entrant/threaded situation.** The writes target instruction operands, making concurrent invocations unsafe without external exclusion. The 61-byte non-self-modifying PR #79 candidate must remain independently available; this fast RAM specialist is not a universal replacement.

## Complete V1 public-entry proof

The independent CI reproducer `tools/screen_issue39_v1_24by8_accumulator_selfmod.py` verifies the exact post-PR #78 V1 resident SHA256 `28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0`, patches **only** the 68-byte source kernel at $1D00 in memory, zeroes the remaining 16 bytes of the original 84-byte island, and runs the old/current public entries on the exact same inputs. It asserts Q/R, success/error carry, preserved N/D and high sentinels, SP, unchanged program bytes outside the island, and no per-case slowdown.

| Public-entry corpus | 69-byte PR #78 | 61-byte portable PR #79 | 68-byte RAM specialist |
|---|---:|---:|---:|
| UDIV24 canonical 4,753 | 170.238165 | 166.190196 | **165.228277** |
| UMOD24 canonical 1,553 | 246.822279 | 234.433355 | **231.489375** |
| Full-N24/D8 stress 4,080 pairs, either API | 1202.660784 | 976.350000 | **927.934314** |

Both APIs across all canonical, seven workload, 4,080 D8, wide-divisor and N2-zero controls: **48,388 complete old/new 6502 calls; zero wrong output, zero slower calls**. The D8 stress saving relative to the portable kernel is about **48.416 cycles per call**, on that specific input distribution. Profile-independent or REU-inclusive timing dominance is not claimed.

Native VICE x64sc executed separately assembled old and new kernels directly from writable RAM on 64 equal input pairs each (**128 calls**); Q/R/C and preserved N/D all matched the independent mathematical oracle. This isolated native certificate is **not full resident or native cycle timing**. The private reproducible native VICE harness/report reside alongside the Oct12 project handoffs.

## Publication decision and next steps

Preserve the 61-byte non-self-modifying and 68-byte RAM-only versions **as distinct, documented candidates**. Before selecting any as V1 shipped core: qualify integrated source and reference/alternate relocation; show V5's independently imported UDIV24/UMOD24 binaries remain unchanged; run full unsigned/signed checks, full native resident tests, official common and workload benchmarks; rewrite historical PR #78 old/new reconstructions for new V1 hashes; publish standalone mirrors, version-specific ABI constraints, both changelogs, release metadata and SHA256SUMS, and await green PR and post-merge main CI. Leave issue #39 unsigned DIV/MOD unchecked until all family audit gates complete.

Candidate: `tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm`. Reproducer: `tools/screen_issue39_v1_24by8_accumulator_selfmod.py`. PR #80.
