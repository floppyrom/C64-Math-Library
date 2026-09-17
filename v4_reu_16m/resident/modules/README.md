# Resident module sources

This directory contains the V4 REU-16M profile's independently assembled arithmetic modules and readable profile-local game-math kernels.

## ATAN2

`reu_atan2.a` publishes the exact REU-backed ATAN2 body used by `../game_math_extension.asm`, behind stable public entry `MATH_ATAN2_8=$5E2A`. V4 performs an exact 8-bit phase lookup through REU bank 8 and returns in a fixed 48 public-entry cycles with 0 normal-ZP use.

Unlike the stock-C64 kernels, this source fragment is intentionally position-neutral: the surrounding V4 game-math source assigns its implementation address, while the public ABI remains `$5E2A`. The shipped V4 REU image supplies the lookup data.

The stock compact/fast algorithms and comparative benchmark live in `../../../routines/atan2/`.
