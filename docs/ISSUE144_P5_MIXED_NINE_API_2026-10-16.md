# Issue #144 P5 — mixed ordinary-call lifetime qualification

This reproducible test exercises all nine expensive public kernels in changing
interleaved orders using one persistent CPU instance per source/frozen binary,
not a fresh emulator for each call. It covers five profiles and both memory
relocation maps. Each map executes 96 rounds of nine calls per profile
(4,320 calls/map; 8,640 total). Source PRGs and REUs are rebuilt; historical
binary SHA-256 identities are preserved.

The test checks mathematical outputs, quotient/remainder/carry, preserved
caller input, stack balance after every call, decimal mode, movement INIT and
five subsequent STEP results. Deterministic seed and paired outputs make
failures reproducible. The two map jobs upload separate JSON proofs.

**Qualification scope:** sequential shared-state lifetime only. It is a
6510 CPU-model check, not a real VICE x64sc execution and not an IRQ/NMI
preemption, real raster-phase, physical 1541/REU bus or DMA timing proof.
The library's existing native VICE workflows are distinct. No safety
claim is made for calls interrupted halfway through shared scratch use.

This does not change historical PRGs, REUs, production PERFORMANCE.md,
private OptiSearch or any normal resident code. The broader issue remains
open for unrestricted multiply/divide gains, interrupt-resource analysis,
physical board qualification and versioned default release.
