# Resident module sources

This directory contains the V3 REU-512K profile's independently assembled arithmetic modules and readable profile-local game-math kernels.

## ATAN2

`pareto_atan2.a` is the exact readable V3 sum-fast stock-CPU ATAN2 body installed at `$C78D-$C7E5`, behind stable public entry `MATH_ATAN2_8=$5E2A`. It uses the same 0-ZP four-page implementation as V2 and measures 44.962814 mean public-entry cycles (29–47), with maximum error 1 phase unit over all 65,536 vectors.

The canonical algorithm and exhaustive benchmark live in `../../../routines/atan2/`.

