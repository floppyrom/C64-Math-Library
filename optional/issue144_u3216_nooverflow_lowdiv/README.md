# Optional no-overflow 32÷16 quotient/remainder — V2/V3/V4 reference

Machine source: [optin_v2_v3_v4_reference.asm](optin_v2_v3_v4_reference.asm).

Requires original, initialized **reference-map** V2/V3/V4 C64 Math Library. Explicitly reserve **$0800–$09FE** (511 bytes, overlapping ordinary BASIC program RAM). Assemble with ACME-compatible NMOS 6510 assembler, load in that RAM, and use `JSR $0800` in place of a normal `JSR MATH_UDIV32_16` / `MATH_UMOD32_16`. Inputs and Q/R/carry follow the usual ordinary public MATH_N / MATH_D / MATH_Q / MATH_R contract.

For D in **$0100–$7FFF**, a 16-bit remainder doubling cannot carry out and the newly unrolled tail removes forced-subtract code. For D=0, 8-bit divisors and D≥$8000, the routine jumps to the **original** UDIV32/16 at $31B0 so all unsigned inputs are valid. It uses the original $420C high-word divider and resident ZP $10–$19, without extra normal ZP. **Hardcoded fixed reference addresses**: do not apply to arbitrary relocations without reassembling and recertifying.

Same-input public CPU-model qualification: 4,261 cases per API/profile, mean eligible-D saving 59.725 UDIV / 62.725 UMOD cycles, uniform fullwidth saving 24.324 / 27.324 cycles, and **−11/−8 cycle** high-D fallback regression. Independently pinned real x64sc native Q/R/C/N/D/SP proof: 288 baseline/candidate calls across all three profiles. Source byte-identical to the tested script. Native cycle timing is not measured.

**Research-only opt-in, not a default optimization or generally IRQ/NMI-reentrant routine.** The shipped PRGs, REUs, builder and PERFORMANCE are untouched. See [full proof and limitations](../../docs/ISSUE144_UDIV32_16_NOOVERFLOW_LOW_D_OPTIN_2026-10-15.md).
