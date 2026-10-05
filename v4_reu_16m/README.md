# v4_reu_16m — 16 MiB REU

Uses the matching 16 MiB game-math REU image; call MATH_INIT once.

## Use

- Public symbols and addresses: `resident/math_api.inc`
- Current executable image: `resident/math_v4_reu_16m_game_math.prg`
- Fully commented active sources: `resident/`
- Example calls: `examples/`
- Profile performance: `PUBLIC_PERFORMANCE.csv` and `PUBLIC_PERFORMANCE_GAME_MATH.csv`

REU image: `reu/c64_math_v4_16m_game_math.reu`

The common API, current validation, memory map, profile selection guide and technical assessment are in the top-level `docs/` and `validation/` directories.

This streamlined distribution intentionally excludes superseded PRGs, generated harness builds, historical provenance and duplicated reference bundles. The full archival package retains those materials.
## Reviewed source-relocatable build

For new integrations, prefer `../relocatable_source/v4_reu_16m/math_relocatable.asm` plus its `math_config.inc` rather than relocating the fixed resident PRG. The bundled fixed-map PRG remains the byte-exact reference output. See `../docs/SOURCE_RELOCATION.md`.

## Optional SMUL32 compact126 overlay

V4 also exposes the validated signed 32x32 compact126 record source under `optional/smul32_compact126/`. It is an **exclusive overlay**, not the fixed resident `MATH_SMUL32`: it owns 136 ZP bytes and `$0100-$017D` while installed. The ordinary profile remains unchanged and keeps the native SMUL16 executable-ZP image. See `../docs/SMUL32_COMPACT126.md` for the exact lifecycle/compatibility constraints.
