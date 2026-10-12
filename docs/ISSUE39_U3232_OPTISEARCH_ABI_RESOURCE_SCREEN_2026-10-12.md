# Issue 39 — OptiSearch 32/32 donor replay against current V1–V5

12 October 2026. Research-only public ABI qualification; no production promotion.

This reruns the THREE already-published Repose/OptiSearch standalone
unsigned 32-bit donor sources from routines/standalone_lab/portable
without copying new private OptiSearch material. Two caller-owned
RAM placements are reassembled, and identical input pairs are used
against the exact current SHA-pinned full V1–V5 public 32/32 entries.
Unlike a native standalone leaderboard, this includes full public
entry costs, dividend/divisor preservation, Q/R/carry, mixed calls
and stack/sentinel checks. REU images are loaded in the CPU model.

131,330 matched input pairs / 262,660 complete CPU executions,
zero mathematical or promised public-ABI mismatches. The operations
include the official common corpus and eight separate distributions:
uniform-full32, D8, D16, D24, quotient 0, quotient 1, high quotient
and divisor zero. Modulo Q side effects are recorded separately
rather than being assumed part of remainder-only contracts.

| Profile | Source donor | API | Official delta cycles | Official slower calls | Uniform delta | D8 delta |
|---|---|---|---:|---:|---:|---:|
| v1_balanced | aligned_0zp | UDIV32_32 | +72.186 | 502 | -39.359 | +2244.078 |
| v1_balanced | aligned_0zp | UMOD32_32 | +138.667 | 412 | -38.344 | +2265.625 |
| v1_balanced | zptail_4zp | UDIV32_32 | +44.873 | 479 | -44.828 | +1899.656 |
| v1_balanced | zptail_4zp | UMOD32_32 | +99.778 | 400 | -47.781 | +1919.828 |
| v1_balanced | mod_aligned_0zp | UMOD32_32 | +77.261 | 377 | -52.406 | +1647.375 |
| v2_pareto_fast | aligned_0zp | UDIV32_32 | +165.463 | 712 | +0.344 | +3015.047 |
| v2_pareto_fast | aligned_0zp | UMOD32_32 | +258.724 | 1113 | +2.469 | +3010.359 |
| v2_pareto_fast | zptail_4zp | UDIV32_32 | +138.150 | 215 | -5.125 | +2670.625 |
| v2_pareto_fast | zptail_4zp | UMOD32_32 | +219.835 | 974 | -6.969 | +2664.562 |
| v2_pareto_fast | mod_aligned_0zp | UMOD32_32 | +197.318 | 968 | -11.594 | +2392.109 |
| v3_reu_512k | aligned_0zp | UDIV32_32 | +165.463 | 712 | +0.344 | +3015.047 |
| v3_reu_512k | aligned_0zp | UMOD32_32 | +258.724 | 1113 | +2.469 | +3010.359 |
| v3_reu_512k | zptail_4zp | UDIV32_32 | +138.150 | 215 | -5.125 | +2670.625 |
| v3_reu_512k | zptail_4zp | UMOD32_32 | +219.835 | 974 | -6.969 | +2664.562 |
| v3_reu_512k | mod_aligned_0zp | UMOD32_32 | +197.318 | 968 | -11.594 | +2392.109 |
| v4_reu_16m | aligned_0zp | UDIV32_32 | +165.463 | 712 | +0.344 | +3015.047 |
| v4_reu_16m | aligned_0zp | UMOD32_32 | +258.724 | 1113 | +2.469 | +3010.359 |
| v4_reu_16m | zptail_4zp | UDIV32_32 | +138.150 | 215 | -5.125 | +2670.625 |
| v4_reu_16m | zptail_4zp | UMOD32_32 | +219.835 | 974 | -6.969 | +2664.562 |
| v4_reu_16m | mod_aligned_0zp | UMOD32_32 | +197.318 | 968 | -11.594 | +2392.109 |
| v5_hybrid_lowzp | aligned_0zp | UDIV32_32 | +132.999 | 545 | -39.359 | +2992.047 |
| v5_hybrid_lowzp | aligned_0zp | UMOD32_32 | +238.761 | 304 | -33.625 | +2999.359 |
| v5_hybrid_lowzp | zptail_4zp | UDIV32_32 | +105.685 | 527 | -44.828 | +2647.625 |
| v5_hybrid_lowzp | zptail_4zp | UMOD32_32 | +199.872 | 287 | -43.062 | +2653.562 |
| v5_hybrid_lowzp | mod_aligned_0zp | UMOD32_32 | +177.355 | 1177 | -47.688 | +2381.109 |

Delta is DONOR MINUS RESIDENT; positive is worse. Mean results are
workload-specific and do not imply universal speed dominance.
Every donor/profile/API has slower official cases. Zero-ZP donors
require four scratch RAM bytes in addition to 496–576 code bytes.
The 544-byte zptail needs four caller-owned additional ZP bytes.
The remainder donor carries a nested JSR return-address cost.
All require caller-owned executable RAM and unproven integration
space in the fixed-profile resident builds. None is demonstrated
to Pareto-dominate the current resident under all contracts.

Neither public API, resident program, REU image, code origin nor
shipped profile ZP budget was changed. The private OptiSearch search
workspace remains private; Repose is credited for existing sources.
Instruction-cycle timing excludes physical VIC and REU bus delay.
No new native VICE execution or timing is claimed.

Reproducer: tools/screen_issue39_u3232_optisearch_current_abi.py
Evidence: validation/review/ISSUE39_U3232_OPTISEARCH_CURRENT_ABI.json

Disposition: reject direct default transplants of these three donors.
This establishes a source-backed audit of this donor class, not
mathematical global optimality or completion of the unsigned family.
Keep issue 39 OPEN; remaining variant/profile audits continue.
