# Issue39 V1/V5 UMUL8 direct-output production stage

13 October 2026. Source and deployable PRGs staged on the PR branch. Pending full PR and post-merge main CI. Issue #39 remains open.

The low product byte goes directly to public MATH_Z in the quarter-square core, eliminating an intermediate ZP store and public reload. The final public tail is CLC/RTS. Exact 11-byte delta in each resident. No ZP, resident length, table, stack or stable ABI growth.

Identical complete 65,536-pair public-input model: 90.490234375 to 84.490234375 cycles on V1 and V5 (six cycles saved on every input). The historical published V1 average 90.494644 came from a different harness and must not be used for paired subtraction. Both source maps checked, complete 56-entry V1 relocation screen passed, and current-main x64sc replay had 256 old/new public calls with all guaranteed invariants identical; native cycle timing was not measured. V2, V3 and V4 residents are unchanged. No private OptiSearch material is published.
