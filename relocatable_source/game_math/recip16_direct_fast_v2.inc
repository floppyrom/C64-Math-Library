; V2 reciprocal small-divisor fallback.
; The existing q=1..15 ladder branches to REG_GAME+$0603 for D<$1001.
; Seed 0x00010000 directly into the selected UDIV32/16 private state.

* = REG_GAME+$0603
FXRECIP_V2_FALLBACK:
        lda #0
        sta U3216_LN0
        sta U3216_LN1
        sta U3216_N1
        lda #1
        sta U3216_N0
        lda MATH_D+0
        sta U3216_D0
        lda MATH_D+1
        sta U3216_D1
        jmp U3216_ENTRY
