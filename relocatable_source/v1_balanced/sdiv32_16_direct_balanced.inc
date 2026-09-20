; V1 Balanced direct-input SDIV32/16 front-end.
; Keeps the selected 480-byte private mixed-width magnitude engine, but removes
; the six-byte signed input shadow. Signed inputs are read directly from the
; public vectors. Twelve transient ZP bytes hold only magnitude/q/r state.
V1D32_N0  = ZP_MAIN+$12
V1D32_N1  = ZP_MAIN+$13
V1D32_D0  = ZP_MAIN+$14
V1D32_D1  = ZP_MAIN+$15
V1D32_Q0  = ZP_MAIN+$16
V1D32_Q1  = ZP_MAIN+$17
V1D32_R0  = ZP_MAIN+$18
V1D32_R1  = ZP_MAIN+$19
V1D32_LN0 = ZP_MAIN+$1A
V1D32_LN1 = ZP_MAIN+$1B
V1D32_LQ0 = ZP_MAIN+$1C
V1D32_LQ1 = ZP_MAIN+$1D
V1D32_DIV_U32_16 = REG_KERNEL+$1B00

; Keep the stable public JMP at MATH_SDIV32_16 pointing here.
* = REG_LOW+$1590
V1D32_PUBLIC:
        jsr V1D32_DIV_S32_16
        lda V1D32_LQ0
        sta MATH_Q+0
        lda V1D32_LQ1
        sta MATH_Q+1
        lda V1D32_Q0
        sta MATH_Q+2
        lda V1D32_Q1
        sta MATH_Q+3
        lda V1D32_R0
        sta MATH_R+0
        lda V1D32_R1
        sta MATH_R+1
        rts
V1D32_PUBLIC_END:

* = REG_KERNEL+$1C00
V1D32_DIV_S32_16:
        ; Classify divisor sign directly from the stable public input.
        lda MATH_D+1
        bmi V1D32_DNEG
        bne V1D32_DPOS_HI
        lda MATH_D+0
        bne V1D32_DPOS_LOW
        jmp V1D32_ZERO
V1D32_DPOS_LOW:
        sta V1D32_D0
        lda #0
        sta V1D32_D1
        jmp V1D32_N_FOR_DPOS
V1D32_DPOS_HI:
        sta V1D32_D1
        lda MATH_D+0
        sta V1D32_D0
V1D32_N_FOR_DPOS:
        lda MATH_N+3
        bmi V1D32_NP_SETUP
        ; PP: positive numerator / positive divisor.
V1D32_PP_SETUP:
        lda MATH_N+0
        sta V1D32_LN0
        lda MATH_N+1
        sta V1D32_LN1
        lda MATH_N+2
        sta V1D32_N0
        lda MATH_N+3
        sta V1D32_N1
        jsr V1D32_DIV_U32_16
        rts

V1D32_NP_SETUP:
        ; NP: negative numerator / positive divisor. q and r are negative.
        lda #0
        sec
        sbc MATH_N+0
        sta V1D32_LN0
        lda #0
        sbc MATH_N+1
        sta V1D32_LN1
        lda #0
        sbc MATH_N+2
        sta V1D32_N0
        lda #0
        sbc MATH_N+3
        sta V1D32_N1
        jsr V1D32_DIV_U32_16
        lda #0
        sec
        sbc V1D32_R0
        sta V1D32_R0
        lda #0
        sbc V1D32_R1
        sta V1D32_R1
        lda #0
        sec
        sbc V1D32_LQ0
        sta V1D32_LQ0
        lda #0
        sbc V1D32_LQ1
        sta V1D32_LQ1
        lda #0
        sbc V1D32_Q0
        sta V1D32_Q0
        lda #0
        sbc V1D32_Q1
        sta V1D32_Q1
        clc
        rts

V1D32_DNEG:
        ; |d|. A negative int16 divisor is necessarily nonzero.
        lda #0
        sec
        sbc MATH_D+0
        sta V1D32_D0
        lda #0
        sbc MATH_D+1
        sta V1D32_D1
        lda MATH_N+3
        bmi V1D32_NN_SETUP
        ; PN: positive numerator / negative divisor => negative quotient only.
V1D32_PN_SETUP:
        lda MATH_N+0
        sta V1D32_LN0
        lda MATH_N+1
        sta V1D32_LN1
        lda MATH_N+2
        sta V1D32_N0
        lda MATH_N+3
        sta V1D32_N1
        jsr V1D32_DIV_U32_16
        lda #0
        sec
        sbc V1D32_LQ0
        sta V1D32_LQ0
        lda #0
        sbc V1D32_LQ1
        sta V1D32_LQ1
        lda #0
        sbc V1D32_Q0
        sta V1D32_Q0
        lda #0
        sbc V1D32_Q1
        sta V1D32_Q1
        clc
        rts

V1D32_NN_SETUP:
        ; NN: quotient positive, remainder negative.
        lda #0
        sec
        sbc MATH_N+0
        sta V1D32_LN0
        lda #0
        sbc MATH_N+1
        sta V1D32_LN1
        lda #0
        sbc MATH_N+2
        sta V1D32_N0
        lda #0
        sbc MATH_N+3
        sta V1D32_N1
        jsr V1D32_DIV_U32_16
        lda #0
        sec
        sbc V1D32_R0
        sta V1D32_R0
        lda #0
        sbc V1D32_R1
        sta V1D32_R1
        clc
        rts

V1D32_ZERO:
        lda #0
        sta V1D32_D0
        sta V1D32_D1
        jmp V1D32_DIV_U32_16
V1D32_PREFIX_END:
