; V1 balanced direct fixed-point divide adapters.
; Reuses the selected private unsigned/signed 32/16 engines without rewriting
; the stable public N/D vectors.

V1FX_UN0  = ZP_MAIN+$0E
V1FX_UN1  = ZP_MAIN+$0F
V1FX_UD0  = ZP_MAIN+$10
V1FX_UD1  = ZP_MAIN+$11
V1FX_ULN0 = ZP_MAIN+$16
V1FX_ULN1 = ZP_MAIN+$17
V1FX_UCORE = REG_KERNEL+$0500
V1FX_UOUT  = REG_API+$01D1

* = REG_GAME+$049E
V1FX_U_SHL8:
        lda #0
        sta V1FX_ULN0
        lda MATH_N+0
        sta V1FX_ULN1
        lda MATH_N+1
        sta V1FX_UN0
        lda #0
        sta V1FX_UN1
        lda MATH_D+0
        sta V1FX_UD0
        lda MATH_D+1
        sta V1FX_UD1
        jsr V1FX_UCORE
        jmp V1FX_UOUT

V1FX_S_SHL8:
        lda MATH_D+1
        bmi V1FX_S_DNEG
        sta V1D32_D1
        lda MATH_D+0
        sta V1D32_D0
        ora V1D32_D1
        beq V1FX_S_ZERO
        jmp V1FX_S_NBIND
V1FX_S_DNEG:
        lda #0
        sec
        sbc MATH_D+0
        sta V1D32_D0
        lda #0
        sbc MATH_D+1
        sta V1D32_D1

V1FX_S_NBIND:
        lda #0
        sta V1D32_LN0
        sta V1D32_N1
        lda MATH_N+1
        bmi V1FX_S_NNEG

        lda MATH_N+0
        sta V1D32_LN1
        lda MATH_N+1
        sta V1D32_N0
        lda MATH_D+1
        bmi V1FX_S_PN
        jsr V1D32_PP_DIV
        jmp V1D32_OUTPUT
V1FX_S_PN:
        jsr V1D32_PN_DIV
        jmp V1D32_OUTPUT

V1FX_S_NNEG:
        lda #0
        sec
        sbc MATH_N+0
        sta V1D32_LN1
        lda #0
        sbc MATH_N+1
        sta V1D32_N0
        lda MATH_D+1
        bmi V1FX_S_NN
        jsr V1D32_NP_DIV
        jmp V1D32_OUTPUT
V1FX_S_NN:
        jsr V1D32_NN_DIV
        jmp V1D32_OUTPUT

V1FX_S_ZERO:
        jsr V1D32_ZERO
        jmp V1D32_OUTPUT

* = MATH_UDIV16_SHL8
        jmp V1FX_U_SHL8
* = MATH_SDIV16_SHL8
        jmp V1FX_S_SHL8


; URECIP16_Q16 small-divisor fallback.  The quotient ladder branches here
; for D<$1001.  floor(65536/D) is exactly 0x00010000 / D, so seed the same
; private 32/16 engine directly without rewriting N or D.
* = REG_GAME+$0680
V1FX_RECIP_FALLBACK:
        lda #0
        sta V1FX_ULN0
        sta V1FX_ULN1
        sta V1FX_UN1
        lda #1
        sta V1FX_UN0
        lda MATH_D+0
        sta V1FX_UD0
        lda MATH_D+1
        sta V1FX_UD1
        jsr V1FX_UCORE
        jmp V1FX_UOUT
