# Resident module sources

This directory contains the V2 Pareto-Fast profile's independently assembled arithmetic modules and readable profile-local game-math kernels.

## ATAN2

`pareto_atan2.a` is the V2 fast four-quadrant ATAN2 body installed at `$C543-$C57A`, behind stable public entry `MATH_ATAN2_8=$5E2A`. It uses 0 ZP and five 256-byte table pages (`$9600`, `$9700`, `$5500`, `$5F00`, `$4700`). Exhaustive validation covers all 65,536 signed-byte vectors with maximum error 1 phase unit and 46.953064 mean public-entry cycles.

The shared algorithm source and exhaustive standalone benchmark live in `../../../routines/atan2/`.
