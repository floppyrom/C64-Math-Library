# Resident module sources

This directory contains the V2 Pareto-Fast profile's independently assembled arithmetic modules and readable profile-local game-math kernels.

## ATAN2

`pareto_atan2.a` is the exact readable V2 sum-fast ATAN2 body installed at `$C782-$C7DA`, behind stable public entry `MATH_ATAN2_8=$5E2A`. It uses 0 ZP and four table pages: LOGX `$9600`, LOGY `$9700`, QPOS `$6E00`, and QNEG `$6F00`. Exhaustive validation measures 44.962814 mean public-entry cycles (29–47) with maximum error 1 phase unit.

The canonical algorithm and exhaustive benchmark live in `../../../routines/atan2/`.

