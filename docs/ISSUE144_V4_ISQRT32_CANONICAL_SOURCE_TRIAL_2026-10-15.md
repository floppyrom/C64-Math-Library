# Issue #144: V4 ISQRT32 fast-four canonical source integration trial

15 October 2026. This branch stages the independently qualified V4 four-fast-step refinement as canonical **source input only**. The five committed resident reference PRGs, two REU images and production `PERFORMANCE.md` are not modified.

The 4 MiB REU prefix lookup supplies a mathematically exact partial root/residual after the high 20 bits. The first four subsequent radix-4 refinement steps need only 16-bit residual/trial math; the final two retain 17-bit arithmetic. The source retains the original $91 DMA command, public MATH_ISQRT32 address, ZP ownership and existing REU payload.

**Independent PR #167 evidence:** 8,619 same-input unrestricted radicands, correct roots for all; baseline 918.542406 vs candidate 807.352361 modeled public-call cycles, improvement 111.190045 cycles (~12.1%) on average, minimum 93 saved, zero slower. Native x64sc with actual 16 MiB REU established correct results in 24 baseline + 24 candidate calls but **did not measure physical bus-time cycles**. The optimized source changes the *incidental overflow V flag* in 195/8,619 modeled calls; V is not documented as an output of this API. Other tested public status, registers, input preservation and scratch agree.

**Fresh source test:** `tools/issue144_v4_isqrt_fast4_source_native_qualify.py` restores the pinned `optional/issue144_v4_reu_isqrt_fast4/prepromotion_v4_isqrt32_reu_prefix.asm` only in an isolated temporary test checkout, assembles the prepromotion baseline and the canonical candidate in both reference/alternate layouts, checks independent input/output model pairs, and runs native VICE if `VICE_WRAPPER` is available. Full library/public ABI and package gates run on the PR. A passing source-only integration is not a binary production release.

Unrestricted producer work, native physical VIC/REU DMA timing, IRQ-time reentrancy and all other Issue #144 targets remain open. No private OptiSearch source is published.
