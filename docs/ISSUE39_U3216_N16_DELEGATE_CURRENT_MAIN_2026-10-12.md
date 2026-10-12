# Issue #39: 32/16 N16 donor screen on exact current residents

12 October 2026. Research only: NO stable source or binary change.

A 26-byte in-memory dispatcher checks N2|N3 and calls the existing
16/16 public divider when both are zero, clearing Q2/Q3 afterwards.
Otherwise it resumes original 32/16 code. Both 32/16 public entries
and Q/R/C/N/D, high-R sentinels and stack were compared old/new.

79,130 identical input pairs and 158,260 complete 6502 public calls
across five profile residents; zero mismatches. This candidate requires
an additional nested JSR (+2 stack bytes) on the narrow path.
The $E100 prototype lies below the KERNAL ROM map on a normal C64:
native VICE, legal executable RAM placement, banking, full relocation
and interrupt behavior have NOT been qualified. CPU-cycle counts only.

| Profile | API | Official mean delta | N16 mean delta | N16 with D8 mean delta | Full-N32 mean delta |
|---|---|---:|---:|---:|---:|
| v1_balanced | MATH_UDIV32_16 | -92.993404 | -469.363281 | -542.173828 | +17.000000 |
| v1_balanced | MATH_UMOD32_16 | -159.053959 | -467.066406 | -525.654297 | +17.000000 |
| v2_pareto_fast | MATH_UDIV32_16 | +0.731037 | -366.684570 | +292.599609 | +17.000000 |
| v2_pareto_fast | MATH_UMOD32_16 | -9.039883 | -365.233398 | +291.179688 | +17.000000 |
| v3_reu_512k | MATH_UDIV32_16 | +0.731037 | -366.684570 | +292.599609 | +17.000000 |
| v3_reu_512k | MATH_UMOD32_16 | -9.039883 | -365.233398 | +291.179688 | +17.000000 |
| v4_reu_16m | MATH_UDIV32_16 | +0.731037 | -366.684570 | +292.599609 | +17.000000 |
| v4_reu_16m | MATH_UMOD32_16 | -9.039883 | -365.233398 | +291.179688 | +17.000000 |
| v5_hybrid_lowzp | MATH_UDIV32_16 | +0.731037 | -366.684570 | +292.599609 | +17.000000 |
| v5_hybrid_lowzp | MATH_UMOD32_16 | -9.039883 | -365.233398 | +291.179688 | +17.000000 |

Negative deltas are faster. On V1 the N16/D8 class wins
more than 500 cycles, but on V2–V5 the same class loses about 292.
Every uniform full-width N32 sample loses 17 cycles. The official
mixed corpus is not representative of full-width uniform usage.

Verdict: do NOT promote to a universal default. Preserve the
research assembly under tools/candidates and detailed per-class JSON.
Next try a D-high-aware filter, with a separate screen for full-width
regressions. Also compare with any independently produced OptiSearch
architecture only after compatible public ABI/resource certification.
Issue #39 stays OPEN; unsigned division/modulo family is incomplete.
