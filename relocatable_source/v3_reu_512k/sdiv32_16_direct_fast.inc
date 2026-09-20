; V2/V3/V4 direct-input SDIV32/16 front-end.
; Keeps the selected fast private mixed-width magnitude engine, but removes the
; six-byte signed input shadow. Twelve transient ZP bytes remain.
D32F_N0  = ZP_MAIN+$42
D32F_N1  = ZP_MAIN+$43
D32F_D0  = ZP_MAIN+$44
D32F_D1  = ZP_MAIN+$45
D32F_Q0  = ZP_MAIN+$46
D32F_Q1  = ZP_MAIN+$47
D32F_R0  = ZP_MAIN+$48
D32F_R1  = ZP_MAIN+$49
D32F_LN0 = ZP_MAIN+$4A
D32F_LN1 = ZP_MAIN+$4B
D32F_LQ0 = ZP_MAIN+$4C
D32F_LQ1 = ZP_MAIN+$4D
D32F_DIV_U32_16 = REG_TABLE+$2E00

* = REG_LOW+$1690
D32F_PUBLIC:
        jsr D32F_DIV_S32_16
        lda D32F_LQ0
        sta MATH_Q+0
        lda D32F_LQ1
        sta MATH_Q+1
        lda D32F_Q0
        sta MATH_Q+2
        lda D32F_Q1
        sta MATH_Q+3
        lda D32F_R0
        sta MATH_R+0
        lda D32F_R1
        sta MATH_R+1
        rts
D32F_PUBLIC_END:

* = REG_TABLE+$3200
D32F_DIV_S32_16:
        lda MATH_D+1
        bmi D32F_DNEG
        bne D32F_DPOS_HI
        lda MATH_D+0
        bne D32F_DPOS_LOW
        jmp D32F_ZERO
D32F_DPOS_LOW:
        sta D32F_D0
        lda #0
        sta D32F_D1
        jmp D32F_N_FOR_DPOS
D32F_DPOS_HI:
        sta D32F_D1
        lda MATH_D+0
        sta D32F_D0
D32F_N_FOR_DPOS:
        lda MATH_N+3
        bmi D32F_NP_SETUP
D32F_PP_SETUP:
        lda MATH_N+0
        sta D32F_LN0
        lda MATH_N+1
        sta D32F_LN1
        lda MATH_N+2
        sta D32F_N0
        lda MATH_N+3
        sta D32F_N1
        jsr D32F_DIV_U32_16
        rts

D32F_NP_SETUP:
        lda #0
        sec
        sbc MATH_N+0
        sta D32F_LN0
        lda #0
        sbc MATH_N+1
        sta D32F_LN1
        lda #0
        sbc MATH_N+2
        sta D32F_N0
        lda #0
        sbc MATH_N+3
        sta D32F_N1
        jsr D32F_DIV_U32_16
        lda #0
        sec
        sbc D32F_R0
        sta D32F_R0
        lda #0
        sbc D32F_R1
        sta D32F_R1
        lda #0
        sec
        sbc D32F_LQ0
        sta D32F_LQ0
        lda #0
        sbc D32F_LQ1
        sta D32F_LQ1
        lda #0
        sbc D32F_Q0
        sta D32F_Q0
        lda #0
        sbc D32F_Q1
        sta D32F_Q1
        clc
        rts

D32F_DNEG:
        lda #0
        sec
        sbc MATH_D+0
        sta D32F_D0
        lda #0
        sbc MATH_D+1
        sta D32F_D1
        lda MATH_N+3
        bmi D32F_NN_SETUP
D32F_PN_SETUP:
        lda MATH_N+0
        sta D32F_LN0
        lda MATH_N+1
        sta D32F_LN1
        lda MATH_N+2
        sta D32F_N0
        lda MATH_N+3
        sta D32F_N1
        jsr D32F_DIV_U32_16
        lda #0
        sec
        sbc D32F_LQ0
        sta D32F_LQ0
        lda #0
        sbc D32F_LQ1
        sta D32F_LQ1
        lda #0
        sbc D32F_Q0
        sta D32F_Q0
        lda #0
        sbc D32F_Q1
        sta D32F_Q1
        clc
        rts

D32F_NN_SETUP:
        lda #0
        sec
        sbc MATH_N+0
        sta D32F_LN0
        lda #0
        sbc MATH_N+1
        sta D32F_LN1
        lda #0
        sbc MATH_N+2
        sta D32F_N0
        lda #0
        sbc MATH_N+3
        sta D32F_N1
        jsr D32F_DIV_U32_16
        lda #0
        sec
        sbc D32F_R0
        sta D32F_R0
        lda #0
        sbc D32F_R1
        sta D32F_R1
        clc
        rts

D32F_ZERO:
        lda #0
        sta D32F_D0
        sta D32F_D1
        jmp D32F_DIV_U32_16
D32F_PREFIX_END:
