# v3_reu_512k — 512 KiB REU

Uses the matching 512 KiB game-math REU image; call MATH_INIT once.

## Use

- Public symbols and addresses: `resident/math_api.inc`
- Current executable image: `resident/math_v3_reu_512k_game_math.prg`
- Fully commented active sources: `resident/`
- Example calls: `examples/`
- Profile performance: `PUBLIC_PERFORMANCE.csv` and `PUBLIC_PERFORMANCE_GAME_MATH.csv`

REU image: `reu/c64_math_v3_512k_game_math.reu`

The common API, current validation, memory map, profile selection guide and technical assessment are in the top-level `docs/` and `validation/` directories.

This streamlined distribution intentionally excludes superseded PRGs, generated harness builds, historical provenance and duplicated reference bundles. The full archival package retains those materials.
## Reviewed source-relocatable build

For new integrations, prefer `../relocatable_source/v3_reu_512k/math_relocatable.asm` plus its `math_config.inc` rather than relocating the fixed resident PRG. The bundled fixed-map PRG remains the byte-exact reference output. See `../docs/SOURCE_RELOCATION.md`.

