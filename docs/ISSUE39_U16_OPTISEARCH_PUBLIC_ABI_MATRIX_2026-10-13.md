# Issue 39 — V1–V5 OptiSearch 16-bit source/public-ABI replay

13 October 2026 — published donor audit; NO default resident promotion.

This replays two existing public Repose/OptiSearch NMOS 6510 sources:
a 323-byte, 2-ZP full quotient/remainder UDIV16 producer and a
976-byte, zero-ZP UMOD16 direct-chain specialist with 2 ordinary
scratch-RAM bytes and an extra nested JSR return-address frame.
Both were source-reassembled to two caller-owned code-RAM maps and
compared against the EXACT reference SHA256-pinned current V1–V5
public entry images. No private generator/source is distributed.

**86,652 identical-input paired calls = 173,304 full 6502 CPU executions**
across official common inputs plus 128 inputs in each of eight
additional independent workload classes: uniform, D8, tiny D4,
q=0, q=1, q=2..7, power of two, divisor zero.
No arithmetic, carry, preserved N/D, output high-sentinel, stack,
or caller memory sentinel mismatches; all input and cycle vectors
are SHA256-identified. Instruction cycles do not include REU/VIC
physical bus contention; no new native VICE run is claimed.

The V1 UMOD16 public entry is a quotient-producing alias to UDIV16.
The remainder-only direct-chain donor is consequently explicitly
**incompatible with V1 UMOD16** and deliberately not tested as a
valid V1 replacement. V2–V5 remainder-only outputs can have
different Q side effects, which are counted rather than silently
equated to a promised quotient-producing contract.

| Resident profile | Source donor | Public API | Official delta cycles | Faster / slower cases | Uniform delta | D8 delta | Q-side differences |
|---|---|---|---:|---:|---:|---:|---:|
| v1_balanced | biased_2zp | UDIV16 | -2.222 | 2475 / 218 | -2.852 | +5.648 | 0 |
| v1_balanced | biased_2zp | UMOD16 | -1.836 | 1511 / 182 | -2.672 | +5.484 | 0 |
| v2_pareto_fast | biased_2zp | UDIV16 | -7.893 | 2306 / 423 | +7.820 | -66.969 | 0 |
| v2_pareto_fast | biased_2zp | UMOD16 | -11.309 | 400 / 1305 | +24.555 | -75.219 | 1038 |
| v2_pareto_fast | direct_mod_0zp | UMOD16 | +11.267 | 22 / 1682 | +22.836 | +1.070 | 667 |
| v3_reu_512k | biased_2zp | UDIV16 | -7.893 | 2306 / 423 | +7.820 | -66.969 | 0 |
| v3_reu_512k | biased_2zp | UMOD16 | -11.309 | 400 / 1305 | +24.555 | -75.219 | 1038 |
| v3_reu_512k | direct_mod_0zp | UMOD16 | +11.267 | 22 / 1682 | +22.836 | +1.070 | 667 |
| v4_reu_16m | biased_2zp | UDIV16 | -7.893 | 2306 / 423 | +7.820 | -66.969 | 0 |
| v4_reu_16m | biased_2zp | UMOD16 | -11.309 | 400 / 1305 | +24.555 | -75.219 | 1038 |
| v4_reu_16m | direct_mod_0zp | UMOD16 | +11.267 | 22 / 1682 | +22.836 | +1.070 | 667 |
| v5_hybrid_lowzp | biased_2zp | UDIV16 | -7.893 | 2306 / 423 | +7.820 | -66.969 | 0 |
| v5_hybrid_lowzp | biased_2zp | UMOD16 | -11.309 | 400 / 1305 | +24.555 | -75.219 | 1038 |
| v5_hybrid_lowzp | direct_mod_0zp | UMOD16 | +11.267 | 22 / 1682 | +22.836 | +1.070 | 667 |

Delta is donor-minus-resident, where **negative is faster**.
The 2-ZP full quotient donor wins some official input-weighted
means, particularly with small divisors, but V2–V5 explicitly
lose on uniform-random 16-bit inputs. The zero-ZP modulo donor
does not improve the official current-resident mean; its distinct
resource envelope remains useful for individually lifted code.
This does NOT disqualify the transplant of individual borrow/branch
strategies into the already optimized resident kernels.

**Resource decision:** code is at caller-owned RAM, not owned
resident code islands; the biased donor requires 2 additional ZP
bytes, and the direct modulo donor uses 976 code/data bytes,
2 scratch RAM bytes and extra nested JSR stack depth.
Neither is a resource-neutral common default in the five profiles.
Do not replace stable V1/V2/V3/V4/V5 resident defaults, alter any
public ABI or claim full-profile optimality from this test.

Reproducer: tools/screen_issue39_u16_optisearch_public_abi.py
Exact evidence: validation/review/ISSUE39_U16_OPTISEARCH_PUBLIC_ABI_MATRIX.json
Existing public donor source remains accessible under
routines/standalone_lab/portable/. OptiSearch provenance: Repose.
The private OptiSearch workspace stays private.

Issue 39 remains OPEN. This is a U16 donor-class no-default
decision, not the entire unsigned DIV/MOD architecture audit.
