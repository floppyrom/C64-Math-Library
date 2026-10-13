# Issue #39 — UMUL16/UMUL24 OptiSearch resource-class audit

13 October 2026. **Research-only finding; no resident or public ABI change.**

## UMUL16 — incompatible performance/resource classes

On the existing 10,169-pair deterministic reference/alternate validation corpus, the shipped full public call averages 273.9800373685 CPU-model cycles in V1/V5 and 216.9800373685 in V2/V3/V4. See `validation/multiply_refresh/UMUL16_DIRECTOUT_VALIDATION.json` and `tools/validate_umul16_directout.py`.

A private OptiSearch near-page generator was tested on the **same operand pairs**: all 10,169 products were correct, with a reported 156.3854853-cycle mean in **its own** emulator. This is **not** a paired public-entry speedup: timing models and register/memory contracts differ. The private candidate uses 95 bytes of executable ZP (`$80–$DE`), 81 executable stack-page bytes starting at `$0100`, 2,044 table bytes, self-modification and a special register ABI; its allowed opcode policy includes stable undocumented opcodes. Native VICE/public-ABI/stack-ownership proof is **not available**. The private tool and candidate are not published.

Existing published `v2_pareto_fast/resident/modules/record_umul16_17zp.a` already includes a fused quarter-square record (17 ZP, 2,044 table bytes, no stack-page execution), while the V2–V4 integrated producer `relocatable_source/multiply/umul16_directout.asm` already has direct low-result output. V1/V5's `MATH_UMUL16` already tail-jumps to its kernel. Do not double-count these prior optimizations.

## UMUL24 — compare the carry-transfer lineage

| Standalone record | Source-reported mean | ZP | Code | Tables |
| --- | ---: | ---: | ---: | ---: |
| Public FAST24 carry-transfer | 357.041715026 | 24 bytes | 307 bytes | 2,044 bytes |
| Private retained OptiSearch 24-bit record | 361.041715026 | 27 bytes | 311 bytes | 2,044 bytes |

The public source is `v1_balanced/resident/modules/record_umul24_24zp_carry.a`; qualification is `validation/records/UMUL24_FAST24.json`. The private retained frontier metadata has **different timing provenance**; the nominal four-cycle gap is not a verified matched-input/public-ABI comparison.

The published FAST24 record already keeps the top partial-product row in Y, absorbs merge carry with `INY`, directly merges column two and propagates carry into the middle-row top. V1/V5's public UMUL24 already tail-calls its private core (PR #106). V2/V3/V4 directly finish the common no-carry path (PR #105). These are **existing improvements**, not a new production proposal.

## Verdict and remaining gate

**No default promotion; issue #39 remains open.** Neither isolated candidate has demonstrated an additional composable public-ABI/resource-compatible gain. Next candidates must be evaluated as complete public calls on the same corpus, across both relocation maps, normal ZP/stack reservations, mixed signed/unsigned calls, and VICE. The existing isolated public records remain available under their own documented contracts. Private OptiSearch implementation files are never copied into the repository.
