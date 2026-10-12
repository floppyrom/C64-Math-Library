# Issue #39: exhaustive V2 UMOD8 fast-path guard study

2026-10-12. No resident/code/API changes. Retain D>=24.

The 10-stage unrolled magnitude-subtraction path is valid for D>=24
because floor(255/24)=10. A lower cutoff without a new algorithm
could give a wrong remainder and was not considered.

All 65,536 N/D operands were checked for remainder, carry, all Q
bytes unchanged, inputs unchanged, high-R sentinels, and stack.
Each D>=24 pair ran both fast and fallback resident paths; 2,277
direct-cutoff reruns confirmed reconstructed CPU timing.
This is 6502 instruction timing, not a native bus contention measure.

| Fast guard | Mean cycles | Difference | Faster | Slower |
|---|---:|---:|---:|---:|
| D>=24 | 52.204453 | +0.000000 | 0 | 0 |
| D>=25 | 52.274643 | +0.070190 | 24 | 232 |
| D>=26 | 52.347595 | +0.143143 | 49 | 463 |
| D>=28 | 52.502335 | +0.297882 | 84 | 940 |
| D>=30 | 52.668961 | +0.464508 | 88 | 1448 |
| D>=31 | 52.755997 | +0.551544 | 88 | 1704 |
| D>=32 | 52.845413 | +0.640961 | 88 | 1960 |
| D>=33 | 52.937210 | +0.732758 | 88 | 2216 |
| D>=34 | 53.030777 | +0.826324 | 88 | 2472 |
| D>=36 | 53.223221 | +1.018768 | 88 | 2984 |
| D>=40 | 53.627060 | +1.422607 | 88 | 4008 |
| D>=48 | 54.489334 | +2.284882 | 88 | 6056 |
| D>=64 | 56.339035 | +4.134583 | 88 | 10152 |
| D>=80 | 58.256271 | +6.051819 | 88 | 14248 |
| D>=96 | 60.185120 | +7.980667 | 88 | 18344 |
| D>=128 | 63.945129 | +11.740677 | 88 | 26536 |
| D>=160 | 67.640198 | +15.435745 | 88 | 34728 |
| D>=192 | 71.350891 | +19.146439 | 88 | 42920 |
| D>=224 | 75.077209 | +22.872757 | 88 | 51112 |
| D>=255 | 78.701981 | +26.497528 | 88 | 59048 |

The current D>=24 boundary wins all 20 tested cutoffs:
52.204453 cycles; D>=25 averages 52.274643, D>=32 52.845413.
The best cutoff for this specific existing kernel is unchanged.
This does not establish whole-family or global UMOD8 optimality.
Full report: validation/review/ISSUE39_V2_UMOD8_GUARD_THRESHOLD_SWEEP.json.
Keep issue #39 unsigned DIV/MOD family open.
