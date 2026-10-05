# v2_pareto_fast — Pareto-fast stock C64

Faster stock profile; call MATH_INIT once.

## Use

- Public symbols and addresses: `resident/math_api.inc`
- Current executable image: `resident/math_v2_pareto_fast_game_math.prg`
- Fully commented active sources: `resident/`
- Example calls: `examples/`
- Profile performance: `PUBLIC_PERFORMANCE.csv` and `PUBLIC_PERFORMANCE_GAME_MATH.csv`

The common API, current validation, memory map, profile selection guide and technical assessment are in the top-level `docs/` and `validation/` directories.

SMUL32 note: the repository's `compact126` native record kernel is compatible only as an **opt-in alternate ownership mode**, because its executable-ZP requirement conflicts with this profile's resident SMUL16 kernel. The fixed public `MATH_SMUL32` therefore remains unchanged. See `../docs/SMUL32_COMPACT126.md`.

FAST31 public path: this profile now keeps five 32-bit multiply table-pointer pairs in already-owned persistent ZP holes and rebinds only one shared pair on ordinary calls. This saves **17 cycles/call** for ordinary SMUL32/UMUL32 and their SHR16 derivatives; READY timing is unchanged. The canonical SMUL32 mean is **726.605230 cycles**. The current stable API union touches 220 bytes, remaining inside V2's documented 221-byte ZP commitment. See `../docs/SMUL32_FAST31_V2.md`.

This streamlined distribution intentionally excludes superseded PRGs, generated harness builds, historical provenance and duplicated reference bundles. The full archival package retains those materials.
## Reviewed source-relocatable build

For new integrations, prefer `../relocatable_source/v2_pareto_fast/math_relocatable.asm` plus its `math_config.inc` rather than relocating the fixed resident PRG. The bundled fixed-map PRG remains the byte-exact reference output. See `../docs/SOURCE_RELOCATION.md`.

