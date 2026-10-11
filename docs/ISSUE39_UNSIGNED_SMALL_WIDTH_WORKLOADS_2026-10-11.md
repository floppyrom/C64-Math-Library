# Issue #39 — unsigned 8/16/24: seven-workload and OptiSearch architecture screen

**Date:** 2026-10-11. **Status:** measured audit, NOT a global no-gain/optimality certificate. The overall unsigned DIV/MOD campaign remains open.

## Architecture and resource classes

- **8-bit:** V1/V2/V5 use small quotient-prefix chains with a restoring tail, while V3/V4 have a REU-assisted quotient/remainder path. The REU cycle figures below omit bus/DMA latency. V1 has a separate source-relocatable UMOD8 magnitude core; a quotient-producing alias is not automatically a better modulo engine.
- **16-bit:** V1 shares its quotient-producing direct-subtract/align engine with UMOD16, optimized for its limited normal ZP. V2/V3/V4/V5 use the faster imported V2 engine with remainder-only modulo adapters. V1 is measurably faster on some small-divisor and divisor-zero classes.
- **24-bit:** V1 uses the Repose counter/tail and its conditional narrow-divisor escape through V1 32/16. V2–V5 use the faster V2-derived core, with separate remainder-only modulo front ends. The large V1 small-divisor gap merits an explicit further pass.

## New reproducible 53,760-call audit

The permanent public validator tools/audit_issue39_unsigned_small_workloads.py checks **UDIV8, UMOD8, UDIV16, UMOD16, UDIV24 and UMOD24** across seven separately seeded classes, 256 input pairs each on every profile: uniform, divisors 1–255, quotient zero, quotient one, quotient 2–7, powers of two, and divisor zero. That is **42 strata × five profiles × 256 = 53,760 public 6502 calls**. Each call checks quotient where demanded, remainder, carry and input preservation. The published JSON and CSV record input/cycle/resident SHA-256, per-class mean/p95 and extrema. This adds to, rather than replaces, the 136,335-call common corpus and 822,050-call unsigned correctness suite.

Selected independent 256-case means (6502 instruction cycles):

| Public operation / input class | V1 | V2/V5 | V3/V4 |
|---|---:|---:|---:|
| UDIV8 uniform | 64.531 | 64.078 | 53.758 |
| UDIV8 quotient 0 | 35.000 | 35.000 | 38.000 |
| UMOD8 power-of-two divisors | 99.539 | 98.504 | 50.000 |
| UDIV16 small divisors | 913.398 | 992.430 | 992.430 |
| UMOD16 quotient 0 | 41.164 | 32.152 | 32.152 |
| UDIV24 small divisors | 1732.379 | 899.328 | 899.328 |
| UMOD24 quotient 1 | 93.070 | 74.273 | 74.273 |
| UMOD24 divisor 0 | 69.992 | 75.008 | 75.008 |

No profile universally dominates all workloads. In particular, these REU timings are not physical bus-time or DMA wall-clock comparisons.

## Rejected V1 24-bit fast-path expansion

The shipped V1 narrow-divisor escape requires D2=D1=0 and N2>=D0 before delegating to its 32/16 engine. An experimental two-byte branch removal at $7FA8–$7FA9 lets every D2=D1=0, N2>0 case delegate, including those currently rejected by the N2/D0 comparison. Arithmetic remains correct on measured calls but performance does not uniformly improve:

- On 4,753 canonical UDIV24 operands, 177.742→177.458 average cycles: **6 faster, 78 slower** (the rest equal).
- On 256 independent small-divisor pairs, 1732.379→1614.000: **126 faster and 127 slower**, up to +230 cycles.
- On a dedicated 1,757-case narrow corner screen, UDIV24 **1498.930→1585.365**, with 417 faster and 1,338 slower; worst regression **+422 cycles**. UMOD24 similarly regresses from 1499.634→1585.795, with 421 faster and 1,335 slower; worst +422.

The permanent negative validator tools/audit_issue39_v1_24narrow_rejection.py uses a separate deterministic seed and asserts the critical failure properties (>400-cycle tail and a majority slowed in the targeted corner class). The earlier exploratory numerical values and permanent corpus should not be conflated. **Reject the expansion; retain the current bounded guard.**

## Genuine private OptiSearch candidate triage

Using the private OptiSearchV2 executable generator, stable NMOS illegal-opcode policy, and 101 deterministic operands per width, the following independently generated **native** arithmetic strategies qualified for correct output. Mean native cycles:

| OptiSearch strategy | UDIV8 | UDIV16 | UDIV24 |
|---|---:|---:|---:|
| restoring unsigned | 503.634 | 1469.733 | 2887.525 |
| q0 counter | 268.871 | 699.495 | 1266.366 |
| small-quotient ladder, threshold 4 | 125.158 | 441.624 | 682.257 |
| leading q0/in-place borrow, threshold 4 | Unsupported | 409.980 | 626.970 |
| in-place borrow ladder, threshold 8 | Unsupported | 290.990 | 561.832 |

These are **not public-ABI comparisons**: native register/memory carriers, initial setup, carry, code placement, ZP and mixed-call obligations differ from the C64 library. No source code or private generated artifacts from OptiSearch are published. This screen is not a global no-gain certificate. The library already uses several related borrow-retention, q0 and early-quotient mechanisms.

## Campaign disposition

The six small-width operations now have another independent workload-conditioned baseline, executable ABI checks, a documented failed V1 architecture expansion, and a real but non-equivalent native OptiSearch screen. Further profile-specific candidate work, particularly V1 24-bit small divisors, and final 32-bit audits remain necessary. **Leave the issue #39 unsigned DIV/MOD checklist unchecked.** Shipped source, ABI, resident binaries, normal ZP, REU behavior and memory maps are untouched by this publication.
