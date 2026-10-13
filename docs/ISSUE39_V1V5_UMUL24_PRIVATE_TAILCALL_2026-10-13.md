# Issue39 — V1/V5 UMUL24 private core public tail-call

Merged in PR #106 on 13 October 2026 (335185f3ad0233763d4aafdad91301f6261604b3). Native VICE PASS: 384 real full-resident old/new calls. All postmerge main workflows green: Validate library #38410138207, Comparable unsigned #38410137785, Turbo32 #38410137989.

The selected public FAST24 adapter now jumps into the unsigned private arithmetic rather than JSR/RTS. The final z3 product byte is stored in the producer, and both carry exits join a single public result tail. Signed FAST24 remains executable-independent.

Every one of 10,324 identical unsigned input pairs saved exactly 8 cycles: 474.042329 -> 466.042329. Both memory maps and the V5 hybrid verified; V2/V3/V4 remain binary unchanged. No new ZP, stack, table, resident space or public entry. No private OptiSearch source is published. Issue #39 stays OPEN.

Native VICE validates both unsigned and signed public entries on two resident profiles, original and candidate, with exact products, input preservation, carry and sentinel parity. It does not measure cycles. See validation/review/ISSUE39_V1V5_UMUL24_TAILCALL_NATIVE_2026-10-13.json.
