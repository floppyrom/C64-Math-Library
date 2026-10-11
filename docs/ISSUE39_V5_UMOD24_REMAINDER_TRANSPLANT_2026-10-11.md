# Issue #39 — V5 UMOD24 remainder-only transplant (2026-10-11)

## Result and provenance

V5's legacy UMOD24 API was a direct alias to its imported V2 24-bit quotient-producing core. V2/V3/V4 already have a faster **dedicated remainder-only frontend**, whose q=0 and q=1 exits avoid constructing quotient bytes. That existing *V2 source* is now independently imported into V5 rather than trying to generate another arithmetic engine. It is a **manual architecture/lifetime transplant on an already-qualified Repose/OptiSearch-derived core**, not proof that OptiSearch independently found a superior native V5 implementation. The private OptiSearch archive is not published.

V2 source `relocatable_source/division/remainder_fast_v2.inc` assembles its 179-byte `RM24U_ENTRY` at `REG_LOW+$0F00` (reference `$1F00–$1FB2`). The V5 source builder relocates it into the unused final page of V5 `REG_LOW+$1F00` (reference `$2F00–$2FB2`; alternate `$AF00–$AFB2`). The V5 public `MATH_UMOD24` retains its stable address and points to this new private frontend. Its absolute targets are relocated to the existing, source-built V2 24-bit kernel; relative branches retain their byte phase for identical branch-cycle behavior. Destination bytes are checked zero before copying; the relocation map includes the newly imported instruction-start set. V5 `UDIV24` remains unchanged.

**Resources:** +179 occupied code bytes in already-existing, previously empty resident address space; +0 resident PRG file bytes; +0 normal-ZP bytes; +0 tables/REU. Normal V5 31-byte zero-page contract unchanged. The modulo ABI guarantees remainder/carry and preserved N/D; quotient bytes on a dedicated remainder-only exit are not part of its contract.

## Paired same-input execution, current PR #51 base → candidate

The deterministic *identical-input* corpus includes 1,553 independent 24-bit modulo calls. It uses exactly the same inputs for V2 and V5, and the 24-bit result, carry and preserved operands agree for all cases.

| Metric | V5 old alias | V5 new frontend | V2 reference |
|---|---:|---:|---:|
| Mean instruction cycles | 214.991629 | **207.490663** | 207.490663 |
| Minimum | 56 | 42 | 42 |
| Maximum | 1412 | 1419 | 1419 |
| Calls faster than old | — | 914 | — |
| Calls slower than old | — | 375 | — |
| Largest regression | — | +7 cycles | — |

V5's new cycle count equals V2's **on each of all 1,553 calls**, not only on average. Mean improvement is **7.500966 cycles/call (3.49%)**. This is an explicitly documented trade-off: the specialized q=0/1 exits are cheaper, but some hard-divisor paths add a seven-cycle dispatch cost.

Across **9,716 paired public-entry calls** testing UMOD24, UDIV24, UMOD16 and UMOD32/16, zero errors or input-preservation changes; the latter three retain their original cycle vectors. A real VICE x64sc 3.13.2 targeted native check tested 16 operands before and after (32 calls), including equality, divide by zero and high-quotient cases: no arithmetic/carry differences.

Further source- and full-suite qualification: V5 reference and alternate native builder builds pass. V5 `validate_unsigned_division`: **164,410 calls, 0 errors**; V5 `validate_signed_division`: **36,273 calls, 0 errors**. Independent V1–V4 alternate source maps: 56 API entries / 21,678 calls **per profile**, zero errors. Full all-profile signed/unsigned and the **136,335-call** common benchmark are required again for release publication. Dedicated permanent `tools/validate_v5_umod24_frontend.py` asserts exact per-call V2/V5 output/cycle parity so future donor updates cannot silently erode it.

Canonical source-built V5 resident SHA-256: `23833dcaf92d5b69cc16e215e67a38776c6feee6523526d7e5592813ceeb7939`. Original merged V5 resident SHA-256: `d3b654f56f7ddfe26ce7130d5e925fdde85e41875e7da4bcd5aafe62440483a7`.

**Campaign status:** The remaining unsigned DIV/MOD architecture/resource screens (particularly UMOD16 zero-ZP, V1/5 32-bit formats, remaining 8/16 and hard-tail paths) need separate manual/OptiSearch passes and explicit no-gain decisions before issue #39's full unsigned family can be checked off. No V2/V3/V4 arithmetic code or public ABI changes here.
