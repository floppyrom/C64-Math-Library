# Issue39 — V2–V4 UMUL24 redundant no-carry CLC removal

Staged 13 October 2026. Native VICE passed: 576 real full resident old/new calls; PR/main CI pending.

The BCS fall-through already has carry clear; STA/STX preserve it. The terminal CLC/RTS becomes RTS/NOP at the same two addresses, saving two cycles without moving later labels or altering signed code.

In the paired 10,324-case public corpus, 7,789 calls save two cycles and 2,535 are unchanged, with no regressions. Official mean 419.292135 -> 417.783224 cycles.

No new ZP or table data, no new resident bytes, stable public API, V1/V5 unchanged; reference/alternate and hybrid source validated. No private OptiSearch code is published. Issue #39 remains open.

Native VICE validates both unsigned and signed public entries on three resident profiles, original and candidate, with exact products, input preservation, carry and sentinel parity. It does not measure cycles. See validation/review/ISSUE39_V2V4_UMUL24_NOCARRY_CLC_NATIVE_2026-10-13.json.
