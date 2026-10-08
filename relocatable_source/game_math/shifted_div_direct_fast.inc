; Direct fixed-point divide adapters for V2/V3/V4.
; Feed (N16 << 8) directly into the selected private 32/16 state rather than
; saving/re-writing/restoring the stable public N vector.

* = REG_GAME+$0435
FXDIV_U_SHL8:
        lda #0
        sta U3216_LN0
        lda MATH_N+0
        sta U3216_LN1
        lda MATH_N+1
        sta U3216_N0
        lda #0
        sta U3216_N1
        lda MATH_D+0
        sta U3216_D0
        lda MATH_D+1
        sta U3216_D1
        jmp U3216_ENTRY

FXDIV_S_SHL8:
        ; Bind |D| once and reject zero without touching N/D.
        lda MATH_D+1
        bmi FXDIV_S_DNEG
        sta D32F_D1
        lda MATH_D+0
        sta D32F_D0
        ora D32F_D1
        beq FXDIV_S_ZERO
        jmp FXDIV_S_NSET
FXDIV_S_DNEG:
        lda #0
        sec
        sbc MATH_D+0
        sta D32F_D0
        lda #0
        sbc MATH_D+1
        sta D32F_D1

FXDIV_S_NSET:
        lda #0
        sta D32F_LN0
        sta D32F_N1
        lda MATH_N+1
        bmi FXDIV_S_NNEG

        ; positive N: |N<<8| = 00:N1:N0:00
        lda MATH_N+0
        sta D32F_LN1
        lda MATH_N+1
        sta D32F_N0
        jsr D32F_DIV_U32_16
        ldx #0
        lda MATH_D+1
        bpl FXDIV_S_RPOS
        inx
FXDIV_S_RPOS:
        jmp D32F_RPOS_OUT

FXDIV_S_NNEG:
        ; negative N: form abs(N16) directly in the shifted magnitude slots.
        lda #0
        sec
        sbc MATH_N+0
        sta D32F_LN1
        lda #0
        sbc MATH_N+1
        sta D32F_N0
        jsr D32F_DIV_U32_16
        ldx #1
        lda MATH_D+1
        bpl FXDIV_S_RNEG
        dex
FXDIV_S_RNEG:
        jmp D32F_RNEG_OUT

FXDIV_S_ZERO:
        jmp D32F_ZERO

!if * > REG_GAME+$04BB { !error "shifted DIV direct adapters overflow reciprocal boundary" }

* = MATH_UDIV16_SHL8
        jmp FXDIV_U_SHL8
* = MATH_SDIV16_SHL8
        jmp FXDIV_S_SHL8
