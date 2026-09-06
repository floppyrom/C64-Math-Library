# v2_pareto_fast — Pareto-fast stock C64

Faster stock profile; call MATH_INIT once.

## Use

- Public symbols and addresses: `resident/math_api.inc`
- Current executable image: `resident/math_v2_pareto_fast_game_math.prg`
- Fully commented active sources: `resident/`
- Example calls: `examples/`
- Profile performance: `PUBLIC_PERFORMANCE.csv` and `PUBLIC_PERFORMANCE_GAME_MATH.csv`

The common API, current validation, memory map, profile selection guide and technical assessment are in the top-level `docs/` and `validation/` directories.

This streamlined distribution intentionally excludes superseded PRGs, generated harness builds, historical provenance and duplicated reference bundles. The full archival package retains those materials.
## Reviewed source-relocatable build

For new integrations, prefer `../relocatable_source/v2_pareto_fast/math_relocatable.asm` plus its `math_config.inc` rather than relocating the fixed resident PRG. The bundled fixed-map PRG remains the byte-exact reference output. See `../docs/SOURCE_RELOCATION.md`.

