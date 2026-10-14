# Issue39 normalization logarithmic-branch production staging

The released candidate removes one redundant conditional branch at each of eight logarithmic ratio dispatch sites in V1/V2/V5. Both states of each original branch pair are equivalent to the new BEQ; no output state, carry, scratch or public input changes.

Exhaustive model: 1073960 signed public calls on both reference and alternate maps. Native x64sc: 320 old/new calls, exact public outputs/flags/input preservation. Code shrinks by 16 bytes per stock implementation without enlarging resident images; both REU profiles remain unchanged.

Reproduced 136,335 unsigned DIV/MOD common-corpus and 30,720 UDIV32/16 workload machine calls with identical numeric metrics; provenance SHA renewed only after rebenchmark. Historical whole-PRG auditors can reconstruct the old exact SHA-pinned resident from `validation/review/ISSUE39_NORMALIZE_LOG_BRANCH_PROVENANCE_2026-10-14.json`.

**Not complete:** independent PR/main CI and migration of archived parent-only arithmetic proof adapters. Do not merge until green. Distance/normalization and Issue39 remain open.
