# Issue39 — V2-V4 UMUL24 no-carry CLC removal

Staged 13 October 2026. NOT RELEASED until native VICE/PR/main CI.

The BCS fallthrough already proves carry clear; STA/STX preserve carry so replacing redundant CLC/RTS by RTS/NOP saves two CPU cycles. Rare final carry continues through the old branch. The signed producer is unchanged.

In the paired 10,324-case public corpus, 7,789 calls save two cycles and 2,535 are unchanged, with no regressions. Official mean 419.292135 -> 417.783224 cycles.

No new ZP or table data, no new resident bytes, stable public API, V1/V5 unchanged; reference/alternate and hybrid source validated. No private OptiSearch code is published. Issue #39 remains open.
