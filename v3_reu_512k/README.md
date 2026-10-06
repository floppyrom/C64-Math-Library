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

SMUL32 note: the repository's `compact126` native record kernel remains an **opt-in alternate ownership mode**, because its executable-ZP requirement conflicts with this profile's resident SMUL16 kernel. It does not replace the stable public entry. The public `MATH_SMUL32` is independently accelerated by the FAST31 persistent-pointer integration, which keeps the per-routine footprint at 31 ZP bytes and zero persistent stack-page bytes. An exclusive Turbo-style source alias is available under [`optional/smul32_compact126/`](optional/smul32_compact126/); a production lifecycle must preserve/restore its documented ZP, page-$01, and ordinary-RAM ranges. See `../docs/SMUL32_FAST31_V2.md` and `../docs/SMUL32_COMPACT126.md`.

FAST31 public path: this profile now keeps **all six** 32-bit multiply table-pointer pairs in already-owned persistent ZP holes, eliminating the ordinary mixed-call pointer repair. Signed SMUL32/SMUL32_SHR16 save **28 cycles** and unsigned UMUL32/UMUL32_SHR16 save **22 cycles**; READY timings are unchanged. The canonical SMUL32 mean is **716.033209 cycles** and the regenerated stable-API ZP union touches **202 bytes**. Turbo BEGIN/END may overlay these bytes temporarily; END restores the pre-overlay values exactly. See `../docs/SMUL32_FAST31_V2.md`.

This streamlined distribution intentionally excludes superseded PRGs, generated harness builds, historical provenance and duplicated reference bundles. The full archival package retains those materials.
## Reviewed source-relocatable build

For new integrations, prefer `../relocatable_source/v3_reu_512k/math_relocatable.asm` plus its `math_config.inc` rather than relocating the fixed resident PRG. The bundled fixed-map PRG remains the byte-exact reference output. See `../docs/SOURCE_RELOCATION.md`.

