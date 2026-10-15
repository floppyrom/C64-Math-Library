# Issue #144 C — canonical V1/V5 normal-resident ISQRT32 source promotion

15 October 2026. **Canonical source integrated, reference binaries deliberately frozen.** Based on separately qualified [V1 feasibility PR #178](https://github.com/floppyrom/C64-Math-Library/pull/178) and [V5 hybrid inheritance PR #179](https://github.com/floppyrom/C64-Math-Library/pull/179).

## Source ownership and compatibility

The independent V1 highword-seeded source is installed as the **final owner** of `REG_GAME+$0A40` and its previously unused helper at `REG_GAME+$0AA8` in `relocatable_source/v1_balanced/isqrt32_direct_highword_normal.inc`. The ordinary `MATH_ISQRT32` entry at `REG_GAME_API+$30` remains a fixed trampoline. `tools/source_relocation.py` emits the include again on canonical regeneration. This unchanged V1-derived source is also selected by the actual V5 hybrid builder. No additional normal zero-page bytes or external caller-owned application RAM.

The historical source-generated root is reproduced by **removing exactly the independently known final-owner module**, not by substituting arbitrary guessed bytes. Legacy V1 feasibility and V5 research comparators remain meaningful after promotion and explicitly reject unknown source changes.

## Exact qualification

[Dedicated source + native workflow](https://github.com/floppyrom/C64-Math-Library/actions/runs/38813010679) passed on the promotion branch before publication seal. Both the reference and alternate relocatable maps passed **full 56-entry public ABI** source-built model validation for each of V1 and V5, **21,678 ordinary machine-code calls per profile/map (86,712 total)**, including the normal mixed-call contracts. Another **2,628 paired unrestricted 32-bit public root calls** (657 V1 + 657 V5 on each map) achieved **exactly 51 modeled 6510 cycles saved per call**, no slower cases. Historical V5 root16/root32 interleaving proof also remains available from PR #179.

The native gate installed SHA256-pinned headless VICE 3.10+r46274 and passed **192 actual x64sc public root executions**: 96 for V1 and 96 for V5, baseline and candidate in two relocation maps, with captured outputs/status identical. Canonical source generator regeneration preserved the V1 final-owner source file byte-for-byte.

## Exclusions and remaining work

This qualifies **canonical source**, not refreshed reference PRGs or REUs. The shipped `PERFORMANCE.md` remains a frozen-binary baseline; it must not be changed until those binary artifacts are deliberately rebuilt and benchmarked on an identical workload. Native root-only VICE checks do **not** certify full 56-entry V5 imported-native mixed-call behavior, IRQ/NMI reentrancy, concurrent READY-state users or physical VIC/REU bus-time. These remain follow-up gates, as do production-image publication and broader Issue #144 multiplication/division/SEEK optimization.
