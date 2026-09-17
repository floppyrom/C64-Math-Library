# Resident module sources

These are the commented arithmetic sources used to produce the binary slices linked by `../math_resident.asm`, plus directly browsable profile-local source for game-math kernels that are integrated into the resident image.

They are kept separate rather than textually included into one ACME source because many imported benchmark sources reuse generic local symbol names (`n0`, `d0`, `cg_code_start`, etc.). `tools/rebuild_resident.py` assembles the arithmetic modules independently, extracts their declared code/data regions, then links the slices into the resident image.

The comments in the imported division/UMOD/multiply sources document the algorithm-specific tricks. `resident_umul16.a` documents its four-UMUL8 construction.

## ATAN2

`resident_atan2.a` is the exact readable V1 compact ATAN2 body installed at `$C459-$C496`, behind stable public entry `MATH_ATAN2_8=$5E2A`. It uses 0 ZP and the resident `$9600/$9700` table pages. The shared algorithm source and exhaustive benchmark live in `../../../routines/atan2/`.
