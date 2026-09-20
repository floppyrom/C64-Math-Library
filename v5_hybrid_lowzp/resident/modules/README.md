# Resident module sources

This directory publishes readable profile-local source for V5 Hybrid Low-ZP kernels that are composed from the certified V1/V2 source profiles by `tools/build_hybrid.py`.

## ATAN2

`hybrid_atan2.a` is the exact readable V5 sum-fast ATAN2 body installed at `$C814-$C86C`, behind stable public entry `MATH_ATAN2_8=$5E2A`. The builder imports the V2 kernel and maps LOGX/LOGY/QPOS/QNEG to V1-free pages `$6D00/$6E00/$6F00/$7000`. It measures 44.962814 mean public-entry cycles (29–47) with exhaustive result/cycle parity to V2.

The canonical algorithm and exhaustive benchmark live in `../../../routines/atan2/`.

