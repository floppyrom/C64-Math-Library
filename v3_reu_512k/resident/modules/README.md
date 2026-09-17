# Resident module sources

This directory contains the V3 REU-512K profile's independently assembled arithmetic modules and readable profile-local game-math kernels.

## ATAN2

`pareto_atan2.a` is the V3 fast stock-CPU ATAN2 body installed at `$C543-$C57A`, behind stable public entry `MATH_ATAN2_8=$5E2A`. It is the same certified four-quadrant implementation used by V2: 0 ZP, 1280 bytes of tables, 46.953064 mean public-entry cycles, and maximum error 1 phase unit over all 65,536 signed-byte vectors.

The shared algorithm source and exhaustive standalone benchmark live in `../../../routines/atan2/`.
