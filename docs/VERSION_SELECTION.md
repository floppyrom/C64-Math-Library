# Version selection — 2026-09-06

| Profile | Best use | Key game-math trade-off |
|---|---|---|
| V1 Balanced | stock C64, tight ZP | full extension with **0 new ZP**; slower resident paths |
| V2 Pareto-Fast | fastest practical no-REU build | 24-byte game ZP plus large native SMUL16 ZP commitment |
| V3 REU 512K | standard 512 KiB REU | exact REU reciprocal tail; Turbo ownership discipline |
| V4 REU 16M | VICE / modern 16 MiB REU | exact reciprocal, atan2 and ISQRT16 lookup acceleration |

Choose V2 without REU, V3 with a 512 KiB REU, V4 when 16 MiB compatibility is acceptable, and V1 when ZP integration cost dominates. V2–V4 require `MATH_INIT`; V3/V4 require the matching game-math REU image.
