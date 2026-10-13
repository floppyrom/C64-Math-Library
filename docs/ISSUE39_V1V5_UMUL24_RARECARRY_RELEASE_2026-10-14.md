# Issue39 — V1/V5 UMUL24 rare-carry CLC production-stage

Staged 14 October 2026; native VICE and PR/main CI still mandatory.

FAST24 now uses BCC over the rare INX/CLC overflow repair; the common tail returns without a redundant CLC. NOP padding preserves the occupied private code layout, both exits return carry clear. The published 24-bit input, output and stack contracts are unchanged.

Each of 10,324 public unsigned cases per profile saves one CPU-model cycle: 466.042329 -> 465.042329. Both relocation maps and the V5 hybrid are rebuilt; signed/mixed regressions, ZP, resident size and standalone publication are checked. V2-V4 binaries unchanged. Native cycle timing is NOT measured. OptiSearch private code excluded; issue #39 remains open.
