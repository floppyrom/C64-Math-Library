# Resident module sources

These are the commented arithmetic sources used to produce the binary slices linked by `../math_resident.asm`.

They are kept separate rather than textually included into one ACME source because many imported benchmark sources reuse generic local symbol names (`n0`, `d0`, `cg_code_start`, etc.). `tools/rebuild_resident.py` assembles each module independently, extracts its declared code/data regions, then links the slices into the resident image.

The comments in the imported division/UMOD/multiply sources document the algorithm-specific tricks. The new `resident_umul16.a` comments explain its four-UMUL8 construction.
