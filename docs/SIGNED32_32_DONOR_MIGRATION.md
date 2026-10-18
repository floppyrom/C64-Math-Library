# Signed 32/32 DIV/MOD historical donor migration — research gate

The historical research started when the operation-first builder had just one
signed Q32/R32/C implementation: a **412-byte executable** constant-round
restoring divider with **9 bytes ordinary scratch, 0 ZP**. It remains
selectable for resource-constrained projects. **PR #302 subsequently merged**
a second, faster source-linked producer: the **2,880-byte/12-ZP V2 hybrid**.
The matched new-source public-call evidence is in
`docs/SIGNED32_32_V2_HYBRID_TRANSPLANT.md`; this separate resident survey
preserves the original five-profile comparison and corpus.

This is the first performance-recovery target after merging PR #298
(signed 32/16) and PR #300 (signed 24/24). Before cloning historical
arithmetic, run the exact same complete-public-call inputs against
released, initialized V1–V5 resident binaries and the compact source:

    python3 tools/research_signed32_32_parity.py --cases 192 \
      --out build/signed32_32_research.json

The research tool loads each unchanged historical PRG plus its corresponding
REU image when applicable, runs MATH_INIT, exercises **both signed 32/32
public aliases**, and separately builds the compact operation-first producer
at $8000 / IO $C000 and $7123 / IO $C040. It checks all eight result bytes,
division by zero carry, signed -2^31 / -1 wrap, preservation of both public
inputs, and stack balance. It records mean, p95, max, zero divisor,
quotient-zero, general division, input-corpus digest and original PRG hashes.

This is deliberately **donor triage, not a selectable speed model**:
physical resident code/data layouts, code placement, and possible REU
resources differ. Its measured entry-through-RTS Mini6502 cycles exclude
caller JSR, IRQ/VIC contention, REU transfer timing and hardware timing.
Never feed these cross-layout numbers directly to the speed optimizer.

## Historical candidate architecture to investigate

The V2–V4 signing path is not a second independent signed divider:
`relocatable_source/division/sdiv32_32_signflow_common.inc` normalizes
N/D (saving signs transiently on the CPU stack), invokes the **profile's
qualified unsigned 32/32 magnitude engine**, restores public operands,
corrects quotient and remainder signs and returns the full ABI. Other
profiles have different private engines. The new builder already includes
several shared unsigned 32/32 sources, including an unrestricted hybrid
with low-divisor fast paths. The signed wrapper over the existing qualified V2 unsigned hybrid has now
been transplanted and is independently selectable. This survey is retained
as reproducible historical donor evidence; **its timings are not the
source-linked V2 hybrid's measured timing**.

## Promotion requirements

1. Select the best proven donor for matched signed input mixes, not old
   headline numbers. Preserve V1–V5 and their SHA-256 reference sources.
2. Link the selected arithmetic core with an exact signed wrapper, keeping
   full public Q32/R32/C, N/D immutability, zero divisor and -2^31/-1 behavior.
3. Charge every shared source byte, table, ZP, stack, SMC/illegal opcode,
   initialization requirement and alignment against global budgets.
4. Verify the source-linked code at $8000 and $7123 using CPU model and
   native VICE r46284 for both DIV and MOD, along with interleaved calls.
5. Compare the *new linked public donor* versus portable on **identical
   operands and placements**, including per-input regressions and peak
   24-frame arithmetic cost, not merely aggregate mean.
6. Keep the 412-byte zero-ZP implementation as a legitimate compact
   alternative. No automatic `speed` promotion without above evidence.

Following PR #302, **29 APIs** have qualified multi-variant speed selection.
The other **27 single-variant operations** still need historical fast-source
audit and source-linked comparisons. Completing a
superficial timing model of one lone candidate would not establish that it
matches the fastest historical V1–V5 implementation.
