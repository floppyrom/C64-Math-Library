# V5 Hybrid Low-ZP source build

V5 is a **derived source build**. It deliberately does not duplicate the full V1 and V2 assembly trees.

`tools/build_hybrid.py`:

1. builds V1 from `relocatable_source/v1_balanced/math_relocatable.asm` using the selected V5 map;
2. independently rebuilds V2 from `relocatable_source/v2_pareto_fast/math_relocatable.asm` at its reference map;
3. imports only the certified low-ZP V2 kernels;
4. relocates their internal code/data references into `HYBRID_CODE`;
5. patches the existing stable V1 public wrapper slots in place, so callers keep the same 54-entry ABI and imported direct calls pay no dispatcher penalty.

The certified import set is intentionally conservative. The builder rejects a selected `HYBRID_CODE` range that overlaps the active V1 map, crosses `$D000-$DFFF`, is unaligned, or exceeds 64 KiB.

Reference `HYBRID_CODE=$A000`; alternate proof `HYBRID_CODE=$E000`.

## Multiplication refresh inheritance

V5 deliberately inherits the refreshed low-ZP multiplication family from the V1 source build rather than duplicating another canonical assembly tree. The 2026-09-20 refresh therefore gives V5 the V1-selected direct `SMUL8`, FAST17 `SMUL16`, FAST24 `UMUL24`/`SMUL24`, and mixed-call-safe FAST31/V29 `UMUL32`/`SMUL32` paths while preserving the 31-byte normal-ZP contract. Exact V5 signed executable mirrors remain published under `v5_hybrid_lowzp/resident/signed/multiply/native/`. See `docs/MULTIPLY_REFRESH_2026-09-20.md`.
