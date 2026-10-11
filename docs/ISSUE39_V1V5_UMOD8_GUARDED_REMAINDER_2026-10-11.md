# Issue #39 — V1/V5 guarded remainder-only UMOD8

**Date:** 2026-10-11. **Status:** source-backed improvement proposed for V1 Balanced and V5 Hybrid, with exhaustive public ABI tests. Entire unsigned DIV/MOD campaign remains open.

## Architecture

The previous V1 and V5 UMOD8 public wrappers always copied numerator and divisor into zero-page scratch before invoking a dedicated magnitude routine. A **77-byte new remainder-only core** at `REG_LOW+$0E00` (reference $1E00–$1E4C) first tests the divisor against **32**.

For **D≥32**, the maximum possible quotient on 8-bit operands is 7. The fast path therefore performs up to seven immediate, non-shifting subtract/compare steps directly on the accumulator, stores only MATH_R, clears carry, and returns. It never touches MATH_Q or zero-page scratch and preserves MATH_N/MATH_D. For **D<32** (including D=0), a symbolic jump to `MATH_UMOD8+3` resumes the original V1 or imported V2/V5 public wrapper immediately after its first LDA MATH_N. This reuses the certified original algorithm on inputs where repeated subtraction might have unbounded tail costs. It does not call the unguarded UDIV8 quotient producer; that would clobber MATH_Q and change modulo semantics.

V5's hybrid builder retains the source-backed 77-byte V1 helper, imports the original V2 UMOD8 wrapper and its private core, verifies the old wrapper's first three bytes, then patches only its public first three bytes to JMP the new helper. V5 remains a 31-normal-ZP resource class, with no added ZP, new stack commitments, RAM-sized resident PRG growth or public ABI changes. Both profiles source-assemble at reference and alternate maps.

## Exhaustive same-input results

Each profile was tested against its **exact merged PR #62 parent** resident, recovered by clearing only the 77-byte previously empty helper island and restoring the original three public wrapper bytes, with verified SHA256 parent hashes. The new paired suite compares **65,536 input pairs per profile × two old/new implementations = 262,144 complete public 6502 calls**. It checks the full remainder, carry, both input bytes and high sentinels, unchanged four Q bytes, and untouched high R bytes. Tests are independently checked against Python division/modulo with divide-by-zero carry semantics.

| Corpus | V1 old | V1 new | V5 old | V5 new |
|---|---:|---:|---:|---:|
| Exhaustive 8×8 (65,536 pairs/profile) | 65.285156 | **53.140671** | 64.819153 | **52.835800** |
| Library common-input (2,465 identical pairs/profile) | 67.294523 | **58.439757** | 66.848276 | **58.129412** |

On the full domain V1 improves **18.60%**, V5 **18.49%**. On the common input corpus V1 improves **13.16%**, V5 **13.04%**. V1 has **57,344 faster qualified D≥32 cases**, zero equal or slower; V5 has **57,060 faster, 284 equal, zero slower** in that same class. In each profile all **8,192 low-divisor cases** fall back to the existing algorithm and incur exactly **+14 instruction cycles** due to the conservative extra dispatch. The maximum observed regression is therefore +14, not zero. This is a workload-dependent weighted win, **not a universal Pareto claim**. Physical REU/DMA latency is excluded from CPU instruction timing of V3/V4, which are unchanged.

A separate source-generating V1 UDIV8 comparison tested the shipped 12-subtraction prefix against K=4,6,8,10 under the **exact owned $4000–$4125 code budget**, 65,536 pairs each (327,680 calls). K12 remains the fastest mean within that budget: 59.571976 cycles versus 59.806564 (K10), 60.118088 (K8), 60.975052 (K6), 62.759293 (K4). This is a bounded no-cycle-gain decision, **not a claim of global UDIV8 optimality**. Larger prefix variants would overwrite separately owned code starting at $4126 and require an independent relocation/size trade-off.

## Verification, OptiSearch, release contracts

- **320 full-resident native VICE x64sc calls:** 80 cases × old/new × two public profiles; all match each other and independent remainder/carry/quotient-preservation oracle. Archived executable identifies as VICE 3.10 despite bundle naming.
- V1/V5 all-profile source and alternate relocation, standard 822,050 unsigned and 364,533 signed public calls, the 136,335 common-input corpus, and V5 mixed-call checks form the release gate.
- Historical PR #57 zero-high bypass, PR #59 V5 32/32 D16 delegation, PR #60 negative V1 24-bit selector, PR #61 24/8, and PR #62 V1 32/32 D8 documents/certificates must all reconstruct their *own historical parents* via `tools/issue39_umod8_guard_parent.py`; no stale full-resident hash is silently rebranded as old evidence.
- Previous private OptiSearch 8-bit native quotient-prefix/borrow and small-quotient screens informed the architecture triage. This is manual public-ABI remainder projection plus bounded dispatch; **no native OptiSearch-generated engine is being falsely credited**.
- Final publication updates both changelogs, generated residents/source mirrors, performance and best-profile catalogs, release metadata, package checksum seal and independent GitHub validation.

The **unsigned DIV/MOD family checkbox in issue #39 remains unchecked** pending the remaining 16/24/32-bit architecture and no-gain assessments.
