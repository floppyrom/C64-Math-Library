# Issue #39 — V1 accumulator-resident 24÷8 DIV/MOD candidate screen

**12 October 2026. Status: candidate screening only.** This changes no shipping resident, no public API, no stable addresses, no ZP/stack allocation, no official performance catalog. Part of #39; full unsigned family remains open.

## Algorithm

Merged PR #78 reduced the full-N2/D8 restoring divider from 84 to 69 bytes with shared carry-aware subtraction. The candidate takes one further step: hold the 8-bit partial remainder in accumulator A over all 24 iterations. Use `ROL A` instead of `ROL MATH_R` and eliminate the per-iteration `LDA MATH_R` and `STA MATH_R`. The ninth bit stays in C; on success, `CMP D0` or the ninth bit enables the same `SBC D0`, then `INC Q0`. Write `MATH_R+0` **once** after the 24-bit quotient loop. Candidate code **69→61 bytes**, zero additional ZP or stack, with 23 trailing unused bytes zero-filled in the in-memory test image.

This engine is guarded by the previously proven V1 N2>0, D2=D1=0, 0<D0<256 dispatch. Other divisor classes and short/zero cases still use their existing byte-identical paths. No claims about general 24÷24 optimality or relative REU DMA timing.

## Reproducible evidence

A locally assembled isolated 24÷8 test used 3,344 identical input pairs (6,688 old/new CPU runs). Old mean **1154.797847**, new mean **929.159091** cycles on this D8-only targeted mix; **3,344 faster, 0 tied, 0 slower**. Every pair passed Q/R/carry and N/D/stack oracle checks.

The additional **independent GitHub Actions complete-resident current-main screen** runs `python3 tools/screen_issue39_v1_24by8_accumulator.py`, reconstructing PR #78 unchanged SHA-256 `28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0`, applying only the candidate `$1D00` island in memory, then executing both public entries on same-input canonical and seven supplementary workloads, a 4,080-pair D8 stress set, 2,048 high-divisor controls, and 1,024 N2-zero controls. **48,388 old/new calls passed**, exact Q/R/C, preserved high N/D sentinels and SP, **no slower cases**.

| Public-entry corpus | PR #78 old mean | 61-byte candidate mean | Faster / tied / slower |
|---|---:|---:|---|
| UDIV24 canonical 4,753 | 170.238165 | **166.190196** | 84 / 4,669 / 0 |
| UMOD24 canonical 1,553 | 246.822279 | **234.433355** | 84 / 1,469 / 0 |
| Both APIs, D8 stress 4,080 per API | 1202.660784 | **976.350000** | 4,080 / 0 / 0 |

All cycle figures are mini6502 instruction cycles including routine RTS, not native emulator timing. Note that the D8 stress corpus uses a freshly generated seed and its old mean differs slightly from PR #78's original stress corpus; each old/new comparison *within* the new test is identically paired.

**Unresolved publication gates:** native x64sc validation of source-built full residents, reference/alternate relocations, preservation of V5's imported 24-bit engine, all-profile unsigned and signed validators, historical parent proof after changing the V1 hash, public rankings, both changelogs, source mirrors, checksum/release metadata and independent post-merge `main` CI. Do **not** present this screen as an integrated release or close #39.

Sources: `tools/candidates/issue39_v1_24by8_accumulator.asm`, `tools/screen_issue39_v1_24by8_accumulator.py`, and draft PR #79.
