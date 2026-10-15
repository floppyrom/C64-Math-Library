# Issue #144 — workstream B: signed 32/16 R-first normalization fusion

16 October 2026. **Source-only candidate; qualification distinct from shipped binary.**

## Target and independent mechanism

Current V2/V3/V4 native signed `MATH_SDIV32_16` and `MATH_SMOD32_16` share the signed magnitude producer. In the negative-numerator, positive-divisor path, the legacy code calls `U3216_ENTRY`, then calls the shared negative-remainder correction, then jumps to the negative-quotient correction. This incurs a redundant nested call/return and a `CLC` whose output is superseded by the quotient corrector's `SEC`.

The candidate keeps **the same R-first then Q correction order**, copying the already-proven two-byte remainder correction into private `D32F_R_THEN_Q` and tail-jumping to the unchanged `MULDIV16_S_NEG_Q`. This retains the exact accumulator and volatile N/Z/V/C flag outcomes rather than using the faster but observably different Q-first shared `MULDIV16_S_DIV_QR` tail. No illegal opcodes, additional ZP, data tables, caller-owned RAM, public IO change or runtime feature flags.

## Matched CPU-model results

[Reproducer](../tools/issue144_signed32_rq_tail_fusion_screen.py) uses the canonical signed source for V2, V3 and V4, reference and alternate relocated memory maps. It reverses **exactly** the installed source transformation when reconstructing the original baseline, and rejects unknown source/physical-region drift.

Across **26,352 matched public DIV/MOD comparisons** (2,196 operands × two APIs × three profiles × two maps): same Q32/R16, carry, numerator, divisor, A/X/Y, complete processor status and SP on every case.

| Domain | Paired modeled CPU cycles saved |
|---|---:|
| N32 negative, D16 positive nonzero | **11 on every call** |
| Remaining nonzero sign combinations | **0** |
| D16 = 0 | **0** |
| This sign-balanced/edge-enriched corpus, overall | **2.805100182 cycles per public call** |

Zero observed slower cases. The older experimental Q-first version saved 14 cycles on the same sign class, but changed volatile A and (rarely) V; **that variant is rejected**.

## Native VICE, source and release gates

[Independent native x64sc runner](../tools/native_issue144_signed32_rq_tail_fusion.py) passed **576 baseline/candidate signed public calls** across V2–V4, both maps and both DIV/MOD entries. Captured Q, R, preserved inputs, A/X/Y, all flags and stack were equal byte-for-byte. The native test uses a SHA256-pinned VICE installation. This establishes native output equivalence, *not* measured CPU or VIC/REU bus cycles.

A separate [V2–V5 source-build proof](../tools/issue144_signed32_rq_source_qualification.py) validates all 56 public entries and V5 hybrid inheritance on reference and alternate layouts. Keep this PR unmerged until the dedicated CI, full-library, comparable unsigned-performance, source regeneration and SHA256 publication gates all pass.

**Boundaries:** Five shipped reference PRGs, two REU images, public binary benchmarks and `PERFORMANCE.md` remain historical. This small signed win does **not** solve the main unrestricted unsigned 32/16 quotient-producer challenge, nor does it close issue #144. Physical REU/VIC DMA timing, IRQ/NMI concurrency and actual binary publication remain separate work.
