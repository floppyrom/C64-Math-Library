# Historical SEEK8 DDA four-entry public speed qualification

This work authenticates the original generated 651-byte RAM-operand SEEK8
routine, rather than replacing it with a slower or less capable mover.

The four operation-first exports `MATH_SEEK8_INIT`, `MATH_SEEK8_STEP`,
`MATH_SEEK8_STEP_INT`, and `MATH_SEEK8_STEP1` retain their distinct
public entry addresses but share one physical 651-byte executable, one
160-byte persistent eight-slot state block, 19 bytes of initializer
scratch and **zero** zero-page bytes. The stock implementation requires no
REU, writable code, source profile image or global initialization.

Each entry receives 256 identical deterministic cases at both source
relocations, including stationary targets, short and long moves, all
eight slots, fractional and integral speeds. The original generated
source is reassembled by its existing bound-symbol relocator. Initialization
is called to establish a real durable slot before measuring STEP calls;
its cost is charged **only to the INIT API**, not hidden in every STEP.
For speed builds, project callers supply realistic relative frequencies
for whichever of the four APIs they select. The builder measures the
source's complete public call costs and retains a single kernel even when
all four exports are requested.

Preservation checks cover I/O operands, speed fields, sprite slot X,
caller stack, INIT arrival carry, source immutability and public
persistence. Existing long-running eight-sprite source regression and
native VICE r46284 tests remain mandatory. Source-model means and
synthetic workloads are **not** physical VIC-II, raster interrupt,
badline or PAL frame timing.

Unlike the alternative-kernel migrations, this closes an installer
**speed-provenance gap** for an already available historical source.
It does not claim new executable acceleration, shared resources beyond
the source's existing physical owner, or completion of profile parity
for the 1541/1571/1581 drive-target variants.
