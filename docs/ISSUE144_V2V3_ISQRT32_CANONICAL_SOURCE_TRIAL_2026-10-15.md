# Issue #144 C — V2/V3 normal-resident ISQRT32 source integration

**15 October 2026. Source integration only; not a new released PRG or REU payload.**

This trial changes the V2 and V3 canonical source-built `MATH_ISQRT32` implementations to avoid saving/restoring the low half of the radicand while obtaining its highword square-root seed. Each profile's new relocatable final-owner include fits the existing 192-byte `REG_GAME+$0A40` to `REG_GAME+$0AFF` resident slot. Normal zero-page budget, caller RAM, public entry, output, carry, input preservation and V3 REU image are unchanged.

**Evidence.** The separately merged source research [PR #174](https://github.com/floppyrom/C64-Math-Library/pull/174) demonstrated 47 saved 6510 CPU-model cycles on every one of 3,388 source-built, paired all-domain public calls across V2/V3 and both memory maps; no regressions. Another 192 real x64sc public calls passed with identical result/status bytes, including V3 and its 512-KiB REU. The canonical-source staging workflow independently passed regeneration-owner verification, paired public model, real VICE, and 56-entry public-ABI validation on V2/V3 reference and alternate maps. These measurements **do not** include physical VIC/REU DMA timing.

**Whole-file regeneration limitation.** The old `tools/generate_sources.py` regenerates a monolithic file from immutable historic PRGs. It also rewrites **unrelated** source components promoted in earlier optimization campaigns. The trial's special gate therefore checks that `tools/source_relocation.py` regenerates the new final-owner include statement inside a disposable project-local path, without rewriting optimized production sources. Full byte-for-byte monolith regeneration idempotence remains **unresolved**, and should be separately corrected before a production binary refresh.

Frozen five reference resident PRGs, two REU images, production `PERFORMANCE.md`, READY contracts and builder selection are not modified. Whole-library postmerge qualification, physical timing, IRQ/NMI overlapping callers and unrestricted DIV/MUL optimization remain Issue #144 tasks. No OptiSearch private source is published.
