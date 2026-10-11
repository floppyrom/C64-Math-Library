# Issue #39 — V5 UMOD16 remainder-only frontend in the last 69 bytes of the page (2026-10-11)

This source-level transplant follows the separately qualified V5 UMOD24 dedicated remainder-only frontend (PR #52). The V2/V3/V4 UMOD16 implementation (`RM16U_ENTRY` in `relocatable_source/division/remainder_fast_v2.inc`) is **69 bytes**, and the previously free 256-byte final V5 `REG_LOW` page contains 179 bytes of UMOD24 code. Import the V2 frontend into the **remaining space** at reference `$2FB3–$2FF7` / alternate `$AFB3–$AFF7`, leaving eight bytes free. This is a manual re-use of an existing Repose/OptiSearch-derived architecture, **not a new optimizer-produced division engine**.

The imported branch paths and operands are source-relocated: internal `RM16U` addresses point to the new low-page region, while references to `DU16F` (`$B800–$BDC9` in the V2 donor) point to V5's relocated, already-certified 1,482-byte direct 16-bit engine at `HYBRID_CODE+$1800`. The V5 source builder checks the destination is zero and maps all reachable V2 instruction starts. The stable V5 `MATH_UMOD16` API entry changes only its private JMP target; the quotient-producing `MATH_UDIV16` and previously imported `MATH_UMOD24` remain unchanged.

## Correctness and common-input performance

Across **1,705 identical-input UMOD16 public calls** tested against the merged post-PR52 V5 image, **all** remainder, carry, N/D preservation and cycle-parity checks passed. Original V5 mean **205.028739** → candidate **198.610557** cycles (−6.418182; −3.13%). The new V5 cycles equal the V2 donor's cycles **per call** for all 1,705 operands (not only in aggregate). **1,613** calls improve; **92** are two cycles slower (maximum slowdown +2). This is an explicitly documented mean-speed Pareto gain, not universal dominance. V5 `MATH_UMOD24` mean stays **207.490663** with **identical** 1,553-case cycle vectors. V5 `UDIV16` and `UDIV24` vectors also remain identical (2,729 and 4,753 cases respectively).

The joint direct-UMOD16/24 path occupies **248 of 256 bytes in an already-existing, formerly unused memory page**. Added normal ZP: **0**; added resident PRG file bytes: **0**; added pages: **0**; existing 31-byte V5 zero-page window and all 56 public ABI addresses unchanged. The remainder-only APIs promise remainder/carry; q=0/q=1 exits need not construct quotient bytes.

Local full V5 regression: **164,410 unsigned + 36,273 signed** machine-code calls, zero failures. Full V5 hybrid integration checks pass on reference and alternate layouts, including all 56 public APIs, mixed calls, sentinel outside-ZP preservation, and exhaustive 65,536-case UMOD8 regressions. Targeted genuine VICE x64sc 3.13.2 emulator checks: 16 operands on old and new images, **32 native calls, zero mismatches**. Both source-built V5 reference and alternate binaries reproduce.

SHA-256 of candidate source-built reference V5 resident: `6aff56fc151a2bf6037323764f2317c6f3416cf8c181332a5592e31f2cf91f1d`. Alternate: `02005dbf5d14753bff8401de90036893f44aa7dd67860ee060f57da3860bd95c`. Baseline (post-UMOD24 PR52) reference: `23833dcaf92d5b69cc16e215e67a38776c6feee6523526d7e5592813ceeb7939`.

The permanent identical-input parity check is `tools/validate_v5_umod16_frontend.py`, run alongside `tools/validate_v5_umod24_frontend.py` in the public comparable-benchmark workflow.

This does **not** close the unsigned DIV/MOD campaign. Further resource-constrained V1/V5 and wider-width searches, explicit no-gain outcomes, and campaign-wide publication/green main CI remain prerequisites for checking off issue #39.
