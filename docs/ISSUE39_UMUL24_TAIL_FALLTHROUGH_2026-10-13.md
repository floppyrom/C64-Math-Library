# Issue39 — V2–V4 UMUL24 no-carry direct result tail

Merged in PR #105 on 13 October 2026 (d1688725c8f9e7f35e6de4d36815d2a6d0265b40). Native VICE PASS: 576 real full-resident old/new calls. All postmerge main workflows green: Validate library #38402703856, Comparable unsigned #38402703783, Turbo32 #38402703796.

The common result-completion path writes product bytes four and five directly instead of jumping to the existing public tail. Rare final carry continues through the old branch. The signed producer is unchanged.

In the paired 10,324-case public corpus, 7,789 calls save three cycles and 2,535 are unchanged, with no regressions. Official mean 421.555502 -> 419.292135 cycles.

No new ZP or table data, no new resident bytes, stable public API, V1/V5 unchanged; reference/alternate and hybrid source validated. No private OptiSearch code is published. Issue #39 remains open.

Native VICE validates both unsigned and signed public entries on three resident profiles, original and candidate, with exact products, input preservation, carry and sentinel parity. It does not measure cycles. See validation/review/ISSUE39_UMUL24_TAIL_NATIVE_2026-10-13.json.
