; Stable wide-intermediate 16-bit multiply/divide primitives.
; Stable public slots (common free hole after MATH_INIT):
;   REG_API+$02E0  UMULDIV16: (u16 X * u16 Y) / u16 D -> Q32,R16
;   REG_API+$02E3  SMULDIV16: (s16 X * s16 Y) / s16 D -> Q32,R16
; ; X/Y/D are preserved by the selected multiply/divide engines.
; N is internal scratch and receives the full 32-bit product.
; Divide by zero inherits UDIV/SDIV semantics: C=1 and Q/R=0.

MATH_UMULDIV16 = REG_API+$02E0
MATH_SMULDIV16 = REG_API+$02E3

* = MATH_UMULDIV16
    jmp MULDIV16_U_COMPOSED
* = MATH_SMULDIV16
    jmp MULDIV16_S_COMPOSED

; The historical fixed-image chain helpers are not relocation-safe source
; primitives, so the V1/V5 baselines inline the symbolic four-byte handoff.
; The unsigned core begins immediately after the old +$03A0 chain block.
* = REG_API+$03C9
MULDIV16_U_COMPOSED:
    jsr MATH_UMUL16
    ldx #$03
MULDIV16_U_COPY:
    lda MATH_Z,x
    sta MATH_N,x
    dex
    bpl MULDIV16_U_COPY
    jmp MATH_UDIV32_16

; V1/V5 signed baseline. V2/V3/V4 overlay +$03E0..+$03F7 with their
; optimized signed producer handoff while preserving the public candidate.
* = REG_API+$03E0
MULDIV16_S_COMPOSED:
    jsr MATH_SMUL16
    ldx #$03
MULDIV16_S_COPY:
    lda MATH_Z,x
    sta MATH_N,x
    dex
    bpl MULDIV16_S_COPY
    jmp MATH_SDIV32_16
