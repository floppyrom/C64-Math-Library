**Final certification (14 October 2026):** SIN8, COS8, SINCOS8 and ATAN2_8 all passed exhaustive public CPU-model checks, 480 native VICE calls and post-merge main qualification. No public ABI/resource-compatible new speed gain was demonstrated; the existing V1 memory-saving and V2-V5 speed-first implementations are retained. Issue #39 stays open.

# Issue #39 — Trigonometric and angular routine public audit

**Research stage, not yet a final family release.** Audited MATH_SIN8, MATH_COS8, MATH_SINCOS8, MATH_ATAN2_8 on all five public profiles and both source relocations. Private OptiSearch source is not redistributed.

The new CPU-model test calls SIN8, COS8 and SINCOS8 on every 8-bit phase in both memory maps: **7,680 new public calls**. All combined outputs are exactly equal to separate SIN/COS outputs, inputs preserved, carry clear, and hardware stack stable. Source-reference and alternate maps have identical outputs and cycle vectors. The existing signed-byte ATAN2 public dispatch certificate already covers **655,360 calls** (full 65,536 signed x/y inputs per profile and map), with at most one phase unit error on V1/V2/V3/V5 and exact rounded-reference phases on V4.

| Profile | Combined SINCOS public CPU-model cycles | CPU-model cycles saved vs separate SIN and COS |
|---|---:|---:|
| V1 | 39 | 13 |
| V2 / V3 / V4 / V5 | 31 | 15 |

No change has been made to the shipped program binaries, ZP layout, tables, or stable API. V1 uses a single lookup plane plus phase rotation to conserve memory; V2–V5 use separate indexed sine/cosine planes for the faster combined path. Moving V1 to the faster two-table layout changes its code/table resource class and is **not** automatically a Pareto improvement. Standalone optimized ATAN2 variants are already in the public catalog.

Native VICE spot checks and complete independent PR/main qualification remain required before checking off the trig family in Issue #39. No hardware-native cycle timing is claimed.
