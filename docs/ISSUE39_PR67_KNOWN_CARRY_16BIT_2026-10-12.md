# Issue39 — PR67 carry-proven internal 16-bit branch pruning

**Date:** 2026-10-12. **Status:** V2–V5 exact-source release staging, V1 untouched. The unsigned DIV/MOD campaign remains OPEN.

The private unsigned and signed 16-bit quotient chains contained three
dead carry-conditional branch plus absolute JMP pairs each. Two unsigned pairs
follow `ANC #0` (which forces C=0); the third follows `ANC #0; STA`.
The signed core similarly has two `ANC #0` cases, plus one `SEC; BCC`
which can never branch. Each five-byte sequence becomes `JMP target; NOP; NOP`,
retaining all original instruction locations and removing two executed
cycles wherever the old dead conditional branch was entered.

This is a **zero-resident-growth, zero-normal-ZP-growth, zero-ABI-change**
micro-optimization, NOT an algorithmic replacement or a universal massive gain.
V2 source sites: signed $7C8A/$7CA5/$7CC0; unsigned $B884/$B8A0/$B8E4.
V3/V4 signed sites: $7D6B/$7D86/$7DA1, with unsigned at $B884/$B8A0/$B8E4.
V5 imports V2's code and has signed sites $B25F/$B27A/$B295.

## Same-input unsigned comparison (complete resident public CPU calls)
| Operation | Old V2 cycles | New V2 cycles | Mean saving |
|---|---:|---:|---:|
| UDIV16 | 161.761451 | 161.758520 | 0.002931 |
| UMOD16 | 198.610557 | 198.601173 | 0.009384 |

Identical-input test contains 2,729 UDIV16 cases and 1,705 UMOD16 cases
per profile. Large-quotient fallback remains exactly unchanged. The profile-
seeded correctness suite and signed paired-screen have separate published
mean values and should never be compared without a matching corpus.

## Validation
- V2 OptiSearch Reduced6502 patched-old/new full resident comparisons:
  2,057 unsigned pairs for each of UDIV16 and UMOD16; 2,521 signed
  SMOD16 pairs; correct Q/R/C/input for every relevant public contract.
  Early sample savings UDIV/UMOD16 35 cases × 2 cycles; signed SMOD16
  138 cases × 2 cycles and 36 cases × 4 cycles. This sample is *not* the
  official 2,729/1,705 corpus.
- Native x64sc **VICE binary reports 3.10**, not 3.13.2:
  256 inputs × four APIs × two images × four changed profiles
  = **8,192** full-resident old/new public calls, all outputs equal and
  independently checked against unsigned/signed quotient/remainder/carry.
  Harness explicitly uses `SEI; CLD; LDA #$34; STA $01` to bank out BASIC
  ROM before entering resident $B800 code, and invokes `MATH_INIT`.
  These native tests do **not** exercise REU DMA.
- Reference and alternate source assembly for V2/V3/V4 succeeded.
  Each new reference resident differs in precisely six expected five-byte
  branch rewrite slots, with no other bytes changed.
- V5 hybrid donor rebuild also differs at exactly those six spots.
  Five-profile candidate public ABI screen runs 2,729 UDIV16 and 1,705
  UMOD16 identical pairs, plus 1,200 signed pairs per API/profile.
- Signed 5,477-case × 2 APIs × five profiles paired result saved under
  `validation/review/ISSUE39_PR67_SIGNED16_SAME_INPUT_AUDIT.json` and `benchmarks/ISSUE39_PR67_SIGNED16_SAME_INPUT_AUDIT.csv`; PR66's original frozen
  signed research artifacts are preserved unchanged.
- Complete unsigned seeded regression suite: 822,050
  public CPU calls; common unsigned corpus: 136,335 calls.
  Profile-seeded signed regression also passed; all five resident PRGs
  deterministic against their source-built reference candidate.

**V1 was not modified. No step in the Issue39 unsigned DIV/MOD campaign has
been marked complete.** Next target is deeper in-core short-quotient algorithm
refinement: the present gain is useful but intentionally tiny.
