# Issue #39 — V5 narrow-divisor delegation for UDIV32/32 and UMOD32/32

**Date:** 2026-10-11. **Scope:** V5 Hybrid 31-byte normal-ZP resource class. The wider unsigned DIV/MOD campaign remains open.

## Algorithm and correctness
The already-published V1/V5 32/32 early gate identifies D=0, N<D and N=D. For the remaining N>D, D!=0 cases, the high-byte q1 filter and q2/3 guard transfer D3=0 directly to the legacy 32/32 core. A V5-only, 21-byte helper now checks D2. When D3=D2=0, D is nonzero and fits 16 bits, so the existing **V5 imported V2 UDIV32/16** engine yields the *identical* full 32-bit quotient and lower 16 remainder bits; the helper zeros the upper remainder bytes and clears carry. D2!=0 resumes the original 32/32 core. Thus the arithmetic is unchanged for every 32-bit operand pair.

The helper occupies previously zero storage at **REG_LOW+$0D00** (reference $1D00–$1D14, immediately beyond PR #58's loop unroll at $1900–$1CF7). The three-byte V5 transfer at **REG_TABLE+$0859** is redirected from REG_GAME to the helper; V1's canonical source and runtime bytes remain untouched. Source references are assembled using selected configuration addresses, so reference and alternate V5 layouts are both valid. No additional normal zero page, no public ABI/address changes, no stack-page commitment, no resident PRG length change, and no REU memory.

**Why not V1?** The same narrow-denominator dispatch was screened on V1 and yielded up to **403 cycles slower** on sampled calls under the slower V1 32/16 producer. The V1 variant was therefore rejected; V5's imported faster 32/16 architecture is decisive.

## Measured same-input public cycles
Paired 6502 executable calls, including RTS, identical operands for old and new 32/32 V5 resident programs.

| Routine | Previous V5 mean | Candidate mean | Reduction | Faster / equal / slower |
|---|---:|---:|---:|---|
| UDIV32_32 (2,729 pairs) | 358.009161 | **275.013192** | **23.2%** | 234 / 2,486 / 9 |
| UMOD32_32 (1,705 pairs) | 435.224633 | **302.353079** | **30.5%** | 234 / 1,467 / 4 |

The guard has a real workload trade-off. On an independent full-width numerator and **16-bit nonzero divisor** workload (1,024 pairs for each public API), *all calls improved*: division 1666.642→732.894 cycles; modulo 1666.648→732.835 cycles. On **17–24-bit divisors**, 1,021/1,024 division calls and 1,022/1,024 modulo calls became **10 cycles slower** because the helper rejects that class before calling the old core (about 0.65% of the baseline mean). With 25–32-bit divisors or D=0, the route is untouched and all sampled calls tie. The common-input corpus overweights structured edge operands; the headline mean is **not** a universal workload-weighted speed claim.

## Validation and provenance
- 10,706 paired public operand cases / 21,412 CPU calls, with q/r/carry/input preservation, cycle distribution and deterministic operand hashes in `validation/review/ISSUE39_V5_32_32_NARROW_DELEGATION.json`.
- V5 signed and unsigned full-profile machine-code suites: 36,273 signed and 164,410 unsigned calls passed locally; V5 hybrid mixed-call/REU/direct routine validation passed.
- Genuine native VICE x64sc old/new full-resident tests passed **80 calls per version**, 160 total, across both 32/32 APIs. The executable reports VICE 3.10 despite the saved runtime archive's 3.13.2 filename.
- Previously published PR #57 zero-high bypass proof is revalidated using its reconstructed **historical PR #58 V5 parent image**, not falsely comparing it with this new V5 dispatcher. The q1/q2/3 proof assertions now distinguish the unchanged V1 means from the new V5 means.
- Private OptiSearch is not included in the library or represented as an independently generated winning 32/32 engine; this is a manual implementation-family architecture reuse of a previously certified V2-derived engine.

## Publication gate
Source-built V5 reference and alternate hybrid binaries, all-profile correctness and paired-corpus reports, standalone mirrors, public and consolidated catalogs, performance documentation, both changelogs, release status and checksums must be regenerated and then verified by independent PR-head and post-merge `main` CI. Do not mark issue #39 complete on this change alone.
