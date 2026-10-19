# Historical V1 DIST8_FAST public-speed authentication

The operation-first MATH_DIST8_FAST implementation is the original V1
signed-8 distance approximation, source-linked as 61 bytes, zero private
zero-page bytes and two ordinary scratch bytes. It computes the unsigned
low byte of max(abs(x),abs(y)) + floor(min(abs(x),abs(y))/2),
including the -128 edge case. This migration does **not** change the
arithmetic or install a different fast/slow candidate.

Previously the source was independently linkable, but objective=speed
failed closed because no matched-input full-public cycle provenance was
recorded. The new source model assembles the original 61-byte code at
two relocations and executes 512 reproducible signed8 X/Y pairs. It
verifies exact Z8 and C, unchanged X/Y and high Z, stack depth,
immutable executable bytes and source SHA-256. Each model records
mean, p95, maximum full-public CPU-model cycles and input corpus SHA.

The existing source remains the only link:resident-approx variant.
It uses 61 code bytes, two scratch bytes, no ZP and the common 32-byte
public I/O block = 95 total RAM bytes. Insufficient RAM budgets must
fail rather than silently select an inaccurate/slower source.

The dedicated workflow also runs the original native VICE r46284
distance qualification, in addition to the two-map source model and
broader installer/publication checks. The new measurements are **not**
physical VIC-II/IRQ/PAL frame timing; genuine game latency should still
be evaluated at the busiest frame when mixed with other operations.

No V1–V5 profile, resident instruction or code/table artifact is removed.
