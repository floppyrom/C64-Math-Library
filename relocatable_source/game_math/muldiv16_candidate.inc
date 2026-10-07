; Candidate wide-intermediate 16-bit multiply/divide primitives.
; Intended future public slots (common free hole after MATH_INIT):
;   REG_API+$02E0  UMULDIV16: (u16 X * u16 Y) / u16 D -> Q32,R16
;   REG_API+$02E3  SMULDIV16: (s16 X * s16 Y) / s16 D -> Q32,R16
; These are intentionally not yet listed in PUBLIC_API_COMPLETE.csv.
; X/Y/D are preserved by the selected multiply/divide engines.
; N is internal scratch and receives the full 32-bit product.
; Divide by zero inherits UDIV/SDIV semantics: C=1 and Q/R=0.

MATH_UMULDIV16_CANDIDATE = REG_API+$02E0
MATH_SMULDIV16_CANDIDATE = REG_API+$02E3

; Existing cross-profile composition helpers in the historical API support
; area. These remain non-stable implementation details.
MULDIV16_Z32_TO_N32 = REG_API+$0250
* = MATH_UMULDIV16_CANDIDATE
    jmp MULDIV16_U_COMPOSED
* = MATH_SMULDIV16_CANDIDATE
    jmp MULDIV16_S_COMPOSED

; Relocation-safe V1/V5 unsigned baseline. The older helper at +$0300 is
; retained for provenance but is not source-relocation-safe on every map.
* = REG_API+$03D0
MULDIV16_U_COMPOSED:
    jsr MATH_UMUL16
    jsr MULDIV16_Z32_TO_N32
    jmp MATH_UDIV32_16

; V1/V5 signed baseline. V2/V3/V4 overlay this address with the optimized
; signed producer handoff while preserving the same candidate entry.
* = REG_API+$03E0
MULDIV16_S_COMPOSED:
    jsr MATH_SMUL16
    jsr MULDIV16_Z32_TO_N32
    jmp MATH_SDIV32_16
