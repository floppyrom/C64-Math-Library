# Signed/unsigned V2 biased 24-bit multiplication: one shared producer

This promotion brings the historical V2 source-linked $CA parity-biased
quarter-square algorithm into the operation-first C64 builder for **both**
UMUL24 and SMUL24, without duplicating its code, tables, ZP or creating
a new fixed V1–V5 profile. Signed multiplication is not implemented as a
second multiply core. The signed entry invokes the canonical unsigned
24×24→48 public kernel, then corrects high output bytes by subtracting
Y×2^24 when X is negative and X×2^24 when Y is negative, modulo 2^48.
Inputs X/Y remain unchanged; the full six-byte Z48 product and C=0 are
the public contract, with Z6/Z7 and operand sentinels preserved.

Both entry names are assembled from
\`tools/selective_v2_fast_umul24.py\`, itself extracting the original V2
\`v2_pareto_fast/resident/modules/pareto_umul24.a\` arithmetic rows.
The immutable four 511-element lookup planes are stored in four
page-aligned 512-byte reservations. The code island is 512 bytes, and
24 contiguous call-exclusive ZP bytes support the historical 6502 indirect
pointer layout. It needs writable code and is **non-reentrant**. The
selector charges alignment padding and 32 bytes of public I/O.

A 0-ZP / 9-byte call-scratch / 227-byte compact signed kernel remains a
genuine Pareto alternative, alongside the original 156-byte compact
unsigned kernel. No old historical profile binary is changed.

## Acceptance gates

1. A matched 512-case public signed input corpus compares both the V2 and
   compact kernels at $8000 and $7123, recording complete-call CPU-model
   mean and maximum cycles, source digests and corpus SHA256.
2. A dual-operation build chooses both variants automatically under
   \`objective=speed\`, using explicit positive call weights and the same
   2,560-byte source image and 24-ZP producer, even when called alternately.
3. The mixed 150-call, 24-frame signed/unsigned trace compares **both**
   variants on identical frame slots, inputs and code placements. It
   reports mean workload impact, peak frame and every individual-call
   or non-peak-frame regression. This is not physical PAL/IRQ/VIC timing.
4. Native VICE r46284 tests both public entries from **the same linked
   two-API PRG at two relocations**, 96 signed and 96 unsigned calls per
   placement. The CPU-model 512-case interleave validates state-sharing
   and the signed correction after any preceding unsigned call.
5. Full-library publication, SHA256 source ledger, all-56 builder safety
   and unmodified historical baseline binaries must pass.
6. Insufficient RAM/24-ZP budgets must select or permit an explicit pin
   of the independently linkable 0-ZP compacts. No compiler/project
   source scanning and no profile name are required.

Example:

    make builder-speed SPEED_CONFIG=examples/operation-first-shared24-speed.json

If signed-source timing or worst-frame proof fails, do not promote the
variant as a speed improvement, even if it passes arithmetic correctness.
