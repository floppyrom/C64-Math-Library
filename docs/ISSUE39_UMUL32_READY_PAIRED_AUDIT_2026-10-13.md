# Issue #39 — UMUL32 vs UMUL32_READY comparable-input audit

Source-backed benchmark clarification — 13 October 2026.

## Why

The previous published `MATH_UMUL32` timing used 2,409 input pairs, whereas `MATH_UMUL32_READY` used 1,024 different input pairs. Their means must **not** be compared as if they came from the same workloads. The READY entry has its own state contract; a speed comparison does not make it interchangeable with the ordinary entry.

## Qualified current-resident result

The new `tools/issue39_umul32_ready_same_input.py` executes the **same ordered 2,409 input pairs** through each entry on every one of the five current resident PRGs. Every public-entry execution validates the complete 64-bit product, input preservation and carry. The CPU model counts entry through RTS and excludes caller JSR and input stores.

| Public profile | UMUL32 mean | READY mean | READY savings | Pairwise distribution |
| --- | ---: | ---: | ---: | --- |
| V1 balanced | 712.235367 | 690.235367 | 22 cycles | 2,409 at -22 cycles |
| V2 Pareto fast | 690.235367 | 690.235367 | 0 | 2,409 equal |
| V3 REU 512K | 690.235367 | 690.235367 | 0 | 2,409 equal |
| V4 REU 16M | 690.235367 | 690.235367 | 0 | 2,409 equal |
| V5 hybrid low-ZP | 712.235367 | 690.235367 | 22 cycles | 2,409 at -22 cycles |

**This is a benchmarking-methodology correction, not a new speedup.** V1 and V5's ordinary entries perform pointer setup that READY can skip under its established prerequisite. V2/V3/V4's normal path already uses the ready body. Never subtract the historical 697.175781-cycle READY mean from the historical 712.235367/690.235367 UMUL32 means; they refer to different corpora.

The current source/PR-head GitHub Actions proof is at `validation/review/ISSUE39_UMUL32_READY_PAIRED_AUDIT.json`, with the exact 2,409-pair SHA-256 `a53c473ea26290c4f7623c9599eeabc9158e56065222f3f695b8fe84ee2e0496`.

## Reproduce

```sh
python3 tools/issue39_umul32_ready_same_input.py --output validation/review/ISSUE39_UMUL32_READY_PAIRED_AUDIT.json
```

Do not treat native OptiSearch-only timing records as compatible public ABI results. No resident bytes, ABI, REU layout, or normal ZP allocation changed. Continue unsigned multiply manual + OptiSearch audits; **issue #39 stays open**.
