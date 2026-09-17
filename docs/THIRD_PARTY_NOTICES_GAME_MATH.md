# Third-Party / Algorithm Provenance — Game Math

This release contains original integration code, generated lookup tables and validation tooling together with previously selected C64 Math API kernels. This file records algorithm/provenance points relevant to the active game-math extension; it does not grant or modify rights in any independently sourced component.

## ISQRT32

The active `MATH_ISQRT32` implementation is an independently derived exact hybrid. It does **not** contain the earlier Verz/Codebase64-derived recurrence. It uses the exact identity that, for `N=(H<<16)+L` and `r=floor(sqrt(H))`, `r` is the high byte of `floor(sqrt(N))`; it then forms `H-r^2` and runs only the eight remaining restoring base-4 refinement steps.

The active contract is exact `floor(sqrt(N32))`, with the 32-bit input preserved and `C=0` on return. See `validation/review/ISQRT32_FAST_VALIDATION.json`, `validation/review/ISQRT32_FAST_PERFORMANCE_4130.json`, and `validation/review/ISQRT32_FAST_DELTA_AUDIT.json`. The delta audit confirms that unrelated resident code/data remain byte-identical to the preceding reviewed release.

## Distance and trig algorithms

`DIST8_FAST` uses the well-known `max + min/2` hypotenuse approximation. `DIST8_ACCURATE` uses coefficients 243/107 selected by an exhaustive search performed for this release. SIN/COS tables are generated directly from their mathematical definitions. The V1 compact and V2/V3 fast atan2 implementations use generated signed-log/final-angle tables and a standard log-ratio identity; V4 uses a generated exact REU plane. The active table quantization, quadrant folding and integration are generated and exhaustively validated by this repository.

General algorithm references can be useful background, but no external wiki implementation is incorporated into the active ISQRT32 kernel.
