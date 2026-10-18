# V2 signed 32/32 source-linked magnitude transplant (research)

This implements a source-linked signed 32/32 Q32/R32/C producer around the
existing independently qualified unrestricted unsigned V2 hybrid, rather than
copying a resident binary image. Both SDIV32_32 and SMOD32_32 share one
physical executable producer. The ordinary 412-byte/0-ZP/9-RAM portable
restoring routine is **preserved** as the compact alternative.

The composed donor occupies a **2,880-byte executable slot**, reserves
**12 call-exclusive ZP bytes**, does not require new initialization or
tables and is not reentrant. The signed wrapper occupies up to the final
384 bytes and normalizes public operands temporarily, calls the existing
unrestricted unsigned producer, restores the inputs, corrects quotient and
remainder signs and returns carry=0. Zero divisors tail-call the known
unsigned public zero guard (C=1, Q=R=0). The -2^31/-1 special case uses
32-bit wrap semantics.

Original V2/V3/V4 resident Q32/R32 routines were measured on a common 192
input-pair research corpus at ~514 cycles, whereas the current portable
builder averaged ~3,300. **This hybrid composition is a NEW implementation**,
not automatically equal in speed to those resident binaries; do not use
the historical measurements as its speed model.

The first gate checks the exact public ABI, resource sharing, two relocations,
zero divisor, signed extremes, N/D immutability, code immutability, compact
fallback, and pinned native VICE r46284 calls. A further same-corpus
CPU-model performance and busy-frame comparison is required before
automatic \`speed\` selection is allowed. This candidate remains experimental
until complete full-library qualification succeeds.

Neither original V1–V5 sources nor historical performance baselines change.
