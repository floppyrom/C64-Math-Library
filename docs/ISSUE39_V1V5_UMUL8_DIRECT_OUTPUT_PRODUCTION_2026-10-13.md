# Issue39 V1/V5 UMUL8 direct-output production stage

13 October 2026. Production integration completed and merged as [PR #109](https://github.com/floppyrom/C64-Math-Library/pull/109), main commit `f754cc87d0ba3518377a4e2d19a9e8fc6ac0d75a`. All PR checks and all three post-merge main checks passed; issue #39 remains open for the unsigned and signed multiplication audits.

The low product byte goes directly to public MATH_Z in the quarter-square core, eliminating an intermediate ZP store and public reload. The final public tail is CLC/RTS. Exact 11-byte delta in each resident. No ZP, resident length, table, stack or stable ABI growth.

Identical complete 65,536-pair public-input model: 90.490234375 to 84.490234375 cycles on V1 and V5 (six cycles saved on every input). The historical published V1 average 90.494644 came from a different harness and must not be used for paired subtraction. Both source maps checked, complete 56-entry V1 relocation screen passed, and current-main x64sc replay had 256 old/new public calls with all guaranteed invariants identical; native cycle timing was not measured. V2, V3 and V4 residents are unchanged. No private OptiSearch material is published.

## Final post-merge checks

- [Full-library validation](https://github.com/floppyrom/C64-Math-Library/actions/runs/38463930923) — success.
- [Comparable unsigned-performance](https://github.com/floppyrom/C64-Math-Library/actions/runs/38463930890) — success.
- [Turbo32 integration](https://github.com/floppyrom/C64-Math-Library/actions/runs/38463930880) — success.

The separate research include remains unselected, because equivalent optimized code is integrated into the canonical production generator. The six-cycle gain is a CPU-model public-entry same-input measurement, **not** a native-VICE cycle measurement. The 256 native VICE calls validate public invariants only.
