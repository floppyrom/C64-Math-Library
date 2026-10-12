# Issue #39: V1 24/8 shared-subtraction inner-loop screen

**12 October 2026 — candidate screen, NOT an integrated code release.** The unsigned DIV/MOD family and Issue #39 remain open.

The shipped V1 24-bit quotient/remainder core has a guarded exact 24/8 division path. Its 84-byte executable island at `$1D00` shifts the 24-bit numerator through Q, tracks an 8-bit partial remainder, and routes the overflow-bit and ordinary subtraction into two near-duplicate blocks. The ordinary-success block also pays an unconditional `JMP` before the loop's `DEX/BNE`.

The experimental version moves `LDA MATH_R` before the `BCS` (which preserves C), tests `CMP MATH_D` only when overflow did not occur, and shares one `SBC/STA/INC` sequence on both subtraction paths. C is guaranteed set on entry to the shared SBC by either the ninth remainder bit or the successful CMP. This yields **69 executable bytes, saving 15**, with the same 24-bit Q and 8-bit remainder semantics, **no extra normal ZP, no stack use and no changed public API**.

Source: `tools/candidates/issue39_v1_24by8_shared_subtraction.asm`. Permanent screen: `tools/screen_issue39_v1_24by8_shared_subtraction.py`. The latter verifies the exact current V1 resident hash and the entire original 84-byte island, constructs an **in-memory only** replacement with the 15 trailing bytes cleared, initializes two real V1 residents and compares the **original public MATH_UDIV24 and MATH_UMOD24 entries** across the exact official identical-input corpora, seven independently seeded narrow-width workloads, 4,080 additional full-width 24/8 pairs, wide divisors and 16-bit numerator controls. It checks complete Q/R/C equivalence (also for modulo), the arithmetic oracle, N/D and their high sentinel bytes, balanced stack, exact file size and no other resident changes. **Any one slower call is a screen failure.** This is deliberately stronger than ranking an isolated loop alone.

The preliminary isolated-engine screen (not the resident gate) on 3,034 24/8 operands reported **1177.725 → 1157.281** cycles, with 2,806 faster, 228 tied, **0 slower**, maximum 72 cycles saved. These numbers do not include the V1 public dispatch and must not be advertised as published library performance.

If the actual public-entry screen passes, the next step is a **separate integrated-release PR**: change the canonical V1 symbolic source and generated resident/standalone mirrors, run full all-profile release builders and relocation + mixed-call checks, native VICE, rebenchmark all profile tables, update both changelogs, seal the package/checksums, and verify post-merge main CI. V5 inherits a V2-derived 24-bit path and must remain byte-for-byte unchanged. No stable ABI changes are permitted.

**Do not check off the overall unsigned DIV/MOD family as complete on the strength of this one screen.**
