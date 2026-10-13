# Issue #39 — UMUL32 READY pointer lifetime under mixed public calls

13 October 2026. Bounded public-resident CPU-model screen of **V1 balanced and V5 hybrid low-ZP**, with no resident, source, ABI or ZP allocation changes.

## Why this matters

The two ordinary `MATH_UMUL32` entry points refresh six quarter-square zero-page pointer high bytes. The `MATH_UMUL32_READY` entry omits this restoration and is 22 cycles faster on the **same 2,409 input pairs** in the published paired audit, but its readiness contract is not unconditional. V2–V4 use a different persistent pointer-high layout; these two low-ZP profiles cannot assume that property.

## Reproducible mixed-call result

`tools/issue39_umul32_ready_lifetime_audit.py` exercises **14 existing public operations × four input states = 56 independent interleaving states/profile**. For every state it starts from `MATH_INIT`, establishes valid UMUL32 pointers with the ordinary call, invokes the other routine, then independently replays **26 identical 32×32 operand pairs** against ordinary and READY public entry points. Every ordinary call checks the exact 64-bit product, carry clear, and input preservation.

| Measure, per low-ZP profile | V1 | V5 |
| --- | ---: | ---: |
| Interleaving states | 56 | 56 |
| States where pointer highs changed | 12 | 12 |
| Ordinary `UMUL32` calls correct | 1,456 / 1,456 | 1,456 / 1,456 |
| Unqualified `UMUL32_READY` calls incorrect | 312 / 1,456 | 312 / 1,456 |
| Other screened READY calls correct | 1,144 / 1,456 | 1,144 / 1,456 |

The three invalidating operations in this bounded screen are **`MATH_UMUL24`, `MATH_SMUL16` and `MATH_SMUL24`**. Each changed the shared pointer high bytes **$09, $0B and $0D** for all four tested input states. In each case READY failed for all 26 subsequent inputs; a minimal witness is `x=0, y=0`: the normal entry returned zero, while the unqualified READY entry returned a nonzero product. This is **expected behavior outside READY's prerequisite**, not a defect in that API.

The complete 85,001-byte CI artifact `issue39-umul32-ready-lifetime.json` is available from workflow run `38477039930`, SHA-256 `e1a61c031b2a15e66d7983c38e3d8fdd2ce2d7d8a622098c37094a889c504cee`. It includes every tested state, pointer before/after and first witness. These are CPU-model calls, **not native VICE timing**. The public source and binaries were not modified.

## Conclusion and next architecture gate

**Do not replace the V1/V5 ordinary public entry with a jump to READY.** This direct bypass saves 22 cycles only when its pointer state survives; it breaks ordinary-public-call semantics after valid mixed routine usage. Eliminating restoration requires a different provably persistent pointer layout or invalidation/recovery mechanism, charged for normal ZP, size, ABI, and mixed calls, including both relocation maps and native VICE. V2–V4 have already solved this through their separate resource map.

The private OptiSearch standalone UMUL32 tail-flag-flow optimizations are not automatically portable to this shared public kernel. This is an evidence-based rejection of one tempting candidate, **not a full no-gain verdict for the 32-bit family**. Issue #39's unsigned multiply task remains open.
