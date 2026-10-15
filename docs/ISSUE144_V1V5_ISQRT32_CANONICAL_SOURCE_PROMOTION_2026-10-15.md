# Issue #144 C — V1/V5 normal-resident ISQRT32 canonical-source promotion

**Date:** 15 October 2026. **Scope:** canonical source and actual V5 hybrid source inheritance, **not** new reference-binary publication.

This integrates the independently qualified 32-bit direct-highword root seed from research PRs [#178](https://github.com/floppyrom/C64-Math-Library/pull/178) and [#179](https://github.com/floppyrom/C64-Math-Library/pull/179). V1 installs a final-owner `!source` include at `REG_GAME+$0A40`, with the bounded helper at `REG_GAME+$0AA8`. The V5 hybrid builder derives from this same normal V1 resident source; it does **not** fork, duplicate or copy an extra private root.

## Qualified research precedent

- V1 VICE: 96 public root calls across two layouts; paired original/candidate captured status equal.
- V1 source-model: 657 unrestricted 32-bit inputs per layout (1,314 pairs); exactly 51 modeled NMOS-6510 cycles saved per ordinary public call, no slower calls.
- V5 derived source-model: 1,329 unrestricted 32-bit inputs per layout (2,658 pairs); exactly 51 modeled cycles saved per call, zero regressions, 72 `ISQRT16` interleaving smokes, original 31-byte normal ZP budget intact.
- V5 VICE: 96 paired root public calls across reference and alternate maps; output/carry captured status identical.

## New canonical integration acceptance conditions

1. The source generator must retain the unique final-owner module, and assembled source must preserve all public ABI addresses and both relocation maps.
2. Reconstruct the historical baseline by reversing **only** the signed-off root module; reject any drift. Do not compare the optimized routine against itself.
3. V5 must prove the actual generated hybrid image owns exactly the V1 resident root bytes, with no imported-core or unrelated byte changes; its full 56-entry ABI validator and mixed sequential public calls must pass.
4. Run original versus optimized with deterministic same-input model and real checksum-pinned headless x64sc on V1 and V5. No use of test-only caller RAM or normal-ZP expansion.
5. Preserve the five frozen reference PRGs, two REU images and production `PERFORMANCE.md` until an independent **binary** rebuild/release and cycle/corpus benchmark gate is passed.

## Boundaries

These checks do not certify asynchronous IRQ/NMI reentrancy, native mixed calls through all 56 imported V5 kernels with the alternate `HYBRID_CODE=$E000` region loaded, nor physical VIC/REU/DMA wall time. The existing root public state contract is unchanged; the faster algorithm is not silently declared IRQ-reentrant. OptiSearch's private source and donor snapshots remain strictly outside this public repository.

Canonical source integration is a **source milestone**. `PERFORMANCE.md` remains the frozen reference-binary measurement ledger until the separately checked binary promotion.
