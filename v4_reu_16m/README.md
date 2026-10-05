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

SMUL32 note: the repository's `compact126` native record kernel is compatible only as an **opt-in alternate ownership mode**, because its executable-ZP requirement conflicts with this profile's resident SMUL16 kernel. The fixed public `MATH_SMUL32` therefore remains unchanged. See `../docs/SMUL32_COMPACT126.md`.

FAST31 public path: this profile now keeps **all six** 32-bit multiply table-pointer pairs in already-owned persistent ZP holes, eliminating the ordinary mixed-call pointer repair. Signed SMUL32/SMUL32_SHR16 save **25 cycles** and unsigned UMUL32/UMUL32_SHR16 save **22 cycles**; READY timings are unchanged. The canonical SMUL32 mean is **719.090079 cycles** and the regenerated stable-API ZP union touches **201 bytes**. Turbo BEGIN/END may overlay these bytes temporarily; END restores the pre-overlay values exactly. See `../docs/SMUL32_FAST31_V2.md`.

This streamlined distribution intentionally excludes superseded PRGs, generated harness builds, historical provenance and duplicated reference bundles. The full archival package retains those materials.
## Reviewed source-relocatable build

For new integrations, prefer `../relocatable_source/v4_reu_16m/math_relocatable.asm` plus its `math_config.inc` rather than relocating the fixed resident PRG. The bundled fixed-map PRG remains the byte-exact reference output. See `../docs/SOURCE_RELOCATION.md`.

