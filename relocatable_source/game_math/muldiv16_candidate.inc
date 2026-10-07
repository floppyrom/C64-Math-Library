; Candidate wide-intermediate 16-bit multiply/divide primitives.
; Intended future public slots:
;   REG_GAME_API+$0054  UMULDIV16: (u16 X * u16 Y) / u16 D -> Q32,R16
;   REG_GAME_API+$0057  SMULDIV16: (s16 X * s16 Y) / s16 D -> Q32,R16
; These are intentionally not yet listed in PUBLIC_API_COMPLETE.csv.
; X/Y/D are preserved by the selected multiply/divide engines.
; N is internal scratch and receives the full 32-bit product.
; Divide by zero inherits UDIV/SDIV semantics: C=1 and Q/R=0.

MATH_UMULDIV16_CANDIDATE = REG_GAME_API+$0054
MATH_SMULDIV16_CANDIDATE = REG_GAME_API+$0057

; Re-state the historical Z32->N32 convenience helper symbolically so the
; candidate remains fully relocatable on the alternate source map.
* = REG_API+$0250
MULDIV16_Z32_TO_N32:
    ldx #$03
MULDIV16_COPY_ZN:
    lda MATH_Z,x
    sta MATH_N,x
    dex
    bpl MULDIV16_COPY_ZN
    rts

; Public candidate slots are ordinary three-byte JMP entries.
* = MATH_UMULDIV16_CANDIDATE
    jmp MULDIV16_U_CORE
* = MATH_SMULDIV16_CANDIDATE
    jmp MULDIV16_S_CORE

; $03E0-$03FF is the free tail immediately before the V1/V5 seek island.
; Two nine-byte composition cores fit without changing any existing region.
* = REG_API+$03E0
MULDIV16_U_CORE:
    jsr MATH_UMUL16
    jsr MULDIV16_Z32_TO_N32
    jmp MATH_UDIV32_16

MULDIV16_S_CORE:
    jsr MATH_SMUL16
    jsr MULDIV16_Z32_TO_N32
    jmp MATH_SDIV32_16
