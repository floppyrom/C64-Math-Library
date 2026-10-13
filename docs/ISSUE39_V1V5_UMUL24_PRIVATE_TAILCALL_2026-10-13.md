# Issue39 — V1/V5 UMUL24 private core public tail-call

Protected release stage, 13 October 2026. Native VICE and PR/main CI pending.

The selected public FAST24 adapter now jumps into the unsigned private arithmetic rather than JSR/RTS. The final z3 product byte is stored in the producer, and both carry exits join a single public result tail. Signed FAST24 remains executable-independent.

Every one of 10,324 identical unsigned input pairs saved exactly 8 cycles: 474.042329 -> 466.042329. Both memory maps and the V5 hybrid verified; V2/V3/V4 remain binary unchanged. No new ZP, stack, table, resident space or public entry. No private OptiSearch source is published. Issue #39 stays OPEN.
