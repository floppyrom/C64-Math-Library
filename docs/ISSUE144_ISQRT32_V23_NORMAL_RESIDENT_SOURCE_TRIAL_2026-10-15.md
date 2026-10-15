# Issue #144 C: V2/V3 normal-resident ISQRT32 direct-highword source trial

15 October 2026 — **source-build integration only**, NOT a published PRG or REU binary update.

The V2/V3 ordinary `MATH_ISQRT32` root producer starts at `REG_GAME+$0A40` (reference $CB40, alternate $8A40) and has a fixed 192-byte allocation through `+$0AFF`. Independent all-input highword-seed research in PR #155 and normal-resident feasibility in PR #174 established a fully relocatable alternative inside this allocation. The optional older prototype at $0C00 was *not* suitable for normal library users because it needed caller-owned RAM; this integration uses no external RAM and no new normal ZP.

## Ownership and regeneration

Each of the two canonical monolithic source builders now appends a distinct, profile-local `isqrt32_highword_resident.inc` as **last owner** of the existing root interval. `tools/source_relocation.py` emits the includes on future provenance regeneration so the improvement is not lost. The V2 and V3 seeds use the correct per-profile table and game-code addresses, symbolic `MATH_IO`, `REG_TABLE`, `ZP_MAIN` and `REG_GAME` offsets. Unrelated resident bytes and public JMP trampoline remain byte-identical to prior source builds.

## Evidence and remaining boundaries

PR #174: **3,388 paired model comparisons** (847 radicands per profile and reference/alternate map), exactly **47 CPU-model cycles saved** each; zero slower; integer root, carry, input, X/Y, SP preserved. **192 real x64sc calls** (48 per profile/map) passed with a genuine V3 512-KiB REU.

The new canonical-source qualification reruns both layouts, ordinary public `ISQRT32` calls, interleaved independent `ISQRT16`, source/public ABI/resource gates and native x64sc. CPU-model savings exclude VIC/REU bus or DMA physical timing.

**No reference binaries or production `PERFORMANCE.md` are changed.** The full `generate_sources.py` monolith from *frozen historical PRGs* has older unrelated text drift versus today's production source. Its new final-owner-include preservation is checked separately rather than claiming global regeneration is byte-for-byte identical. IRQ/NMI-time shared-ZP safety, new default binary publication and the remaining unrestricted division/multiplication issue #144 targets remain open. No private OptiSearch source is included.
