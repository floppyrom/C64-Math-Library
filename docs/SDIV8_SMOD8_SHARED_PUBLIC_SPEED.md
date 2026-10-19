# Authentic shared V1 signed 8-bit DIV/MOD speed provenance

The operation-first installer has always retained the original V1–V5
`MATH_SDIV8` / `MATH_SMOD8` signed 8-bit quotient/remainder producer.
Both public names point to **one** source-linked 530-byte code image.
A single private zero-page byte is required, with 0 other scratch,
and exactly 32 bytes of common public I/O. The input/output ABI is
identical for both public operations: signed low-byte N8/D8; signed
Q8/R8 and carry C (C=1 only on D=0). High N/D/Q/R bytes and stack
are preserved, as is the original source code.

Before this qualification, `objective=speed` failed closed for both
`SDIV8` and `SMOD8`, despite their already exhaustive correctness
and native qualification. It was **not** evidence that the kernels
themselves were slow. This migration installs no replacement source:
it measures the original historical V1 530-byte code directly on
512 signed N8/D8 pairs, at independent code and I/O origins, including
zero, extremes, sign combinations, and small denominators. Each
operation gets an authenticated per-operation source hash, identical
input corpus SHA, public CPU-model mean, p95, and maximum call costs.

The speed objective may then accept either or both operation names.
When linked together, they must still select **one** physical code
image, one private ZP byte, and one public I/O region rather than
duplicating the kernel. Budget restrictions must reject builds that
cannot reserve the exact 562 bytes of main RAM plus one zero-page byte.

A dedicated workflow reruns exhaustive signed8 source-model correctness,
512-pair matched public speed measurements, two-origin mixed linking,
and existing native VICE r46284 qualification of the unmodified producer.
Results are CPU-model cycles, **not** true VIC-II badline/IRQ/PAL timing.
No resident-only historical cycle table is treated as comparable to
full public-call measurements.

This is speed-provenance parity for two already historically fast
public APIs. It retains V1–V5 profiles and does not introduce slower
portable code or a new source-kernel speed claim.
