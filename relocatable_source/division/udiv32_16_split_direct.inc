; Direct-public UDIV32/16 with split constrained tail and bounded byte-divisor path.
; V2/V3/V4 share the arithmetic; profile wrapper defines U3216_D8_BASE in a
; free source-owned hole.  N/D are preserved, Q32/R16 written directly.
; NMOS 6502/6510; decimal mode must be clear.
;
; The high word is divided by the existing certified UDIV16 size-fast core.
; Its residual is <D.  The remaining low 16 dividend bits are then consumed as
; two independent byte phases: each source byte becomes its quotient byte in
; place, eliminating one ZP ROL from every one of the 16 constrained steps.
; D<256 uses a compact 32/8 restoring path with an 8-bit residual, bounding the
; former narrow-divisor tail without tables or extra ZP.
U3216_N0  = ZP_MAIN+$0E
U3216_N1  = ZP_MAIN+$0F
U3216_D0  = ZP_MAIN+$10
U3216_D1  = ZP_MAIN+$11
U3216_Q2  = ZP_MAIN+$12
U3216_Q3  = ZP_MAIN+$13
U3216_R0  = ZP_MAIN+$14
U3216_R1  = ZP_MAIN+$15
U3216_LN0 = ZP_MAIN+$16
U3216_LN1 = ZP_MAIN+$17
U3216_DIV16 = REG_KERNEL+$020C

* = MATH_UDIV32_16
        lda MATH_N+0
        sta U3216_LN0
        lda MATH_N+1
        sta U3216_LN1
        lda MATH_N+2
        sta U3216_N0
        lda MATH_N+3
        sta U3216_N1
        lda MATH_D+0
        sta U3216_D0
        lda MATH_D+1
        sta U3216_D1
        jmp U3216_ENTRY

* = MATH_UMOD32_16
        jmp MATH_UDIV32_16

* = REG_KERNEL+$0E00
U3216_ENTRY:
        lda U3216_D1
        bne U3216_GENERAL
        lda U3216_D0
        bne U3216_D8_DISPATCH
        jmp U3216_ZERO
U3216_D8_DISPATCH:
        ; Preserve the exceptionally cheap N<D case for one-byte N/D.
        lda U3216_N1
        ora U3216_N0
        ora U3216_LN1
        bne U3216_D8_JUMP
        lda U3216_LN0
        cmp U3216_D0
        bcc U3216_D8_QZERO
U3216_D8_JUMP:
        jmp U3216_D8
U3216_D8_QZERO:
        lda #0
        sta MATH_Q+0
        sta MATH_Q+1
        sta MATH_Q+2
        sta MATH_Q+3
        sta MATH_R+1
        lda U3216_LN0
        sta MATH_R+0
        clc
        rts

U3216_GENERAL:
        jsr U3216_DIV16
        lda U3216_R1
U3216_B0:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE0
        cmp U3216_D1
        bcc U3216_NO0
        bne U3216_TAKE0
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO0
U3216_TAKE0:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO0
U3216_FORCE0:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO0:
U3216_B1:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE1
        cmp U3216_D1
        bcc U3216_NO1
        bne U3216_TAKE1
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO1
U3216_TAKE1:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO1
U3216_FORCE1:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO1:
U3216_B2:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE2
        cmp U3216_D1
        bcc U3216_NO2
        bne U3216_TAKE2
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO2
U3216_TAKE2:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO2
U3216_FORCE2:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO2:
U3216_B3:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE3
        cmp U3216_D1
        bcc U3216_NO3
        bne U3216_TAKE3
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO3
U3216_TAKE3:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO3
U3216_FORCE3:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO3:
U3216_B4:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE4
        cmp U3216_D1
        bcc U3216_NO4
        bne U3216_TAKE4
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO4
U3216_TAKE4:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO4
U3216_FORCE4:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO4:
U3216_B5:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE5
        cmp U3216_D1
        bcc U3216_NO5
        bne U3216_TAKE5
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO5
U3216_TAKE5:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO5
U3216_FORCE5:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO5:
U3216_B6:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE6
        cmp U3216_D1
        bcc U3216_NO6
        bne U3216_TAKE6
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO6
U3216_TAKE6:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO6
U3216_FORCE6:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO6:
U3216_B7:
        rol U3216_LN1
        rol U3216_R0
        rol
        bcs U3216_FORCE7
        cmp U3216_D1
        bcc U3216_NO7
        bne U3216_TAKE7
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO7
U3216_TAKE7:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO7
U3216_FORCE7:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO7:
        rol U3216_LN1
U3216_B8:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE8
        cmp U3216_D1
        bcc U3216_NO8
        bne U3216_TAKE8
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO8
U3216_TAKE8:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO8
U3216_FORCE8:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO8:
U3216_B9:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE9
        cmp U3216_D1
        bcc U3216_NO9
        bne U3216_TAKE9
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO9
U3216_TAKE9:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO9
U3216_FORCE9:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO9:
U3216_B10:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE10
        cmp U3216_D1
        bcc U3216_NO10
        bne U3216_TAKE10
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO10
U3216_TAKE10:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO10
U3216_FORCE10:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO10:
U3216_B11:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE11
        cmp U3216_D1
        bcc U3216_NO11
        bne U3216_TAKE11
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO11
U3216_TAKE11:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO11
U3216_FORCE11:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO11:
U3216_B12:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE12
        cmp U3216_D1
        bcc U3216_NO12
        bne U3216_TAKE12
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO12
U3216_TAKE12:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO12
U3216_FORCE12:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO12:
U3216_B13:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE13
        cmp U3216_D1
        bcc U3216_NO13
        bne U3216_TAKE13
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO13
U3216_TAKE13:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO13
U3216_FORCE13:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO13:
U3216_B14:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE14
        cmp U3216_D1
        bcc U3216_NO14
        bne U3216_TAKE14
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO14
U3216_TAKE14:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO14
U3216_FORCE14:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO14:
U3216_B15:
        rol U3216_LN0
        rol U3216_R0
        rol
        bcs U3216_FORCE15
        cmp U3216_D1
        bcc U3216_NO15
        bne U3216_TAKE15
        ldx U3216_R0
        cpx U3216_D0
        bcc U3216_NO15
U3216_TAKE15:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        bcs U3216_NO15
U3216_FORCE15:
        tax
        lda U3216_R0
        sbc U3216_D0
        sta U3216_R0
        txa
        sbc U3216_D1
        sec
U3216_NO15:

        rol U3216_LN0
        sta MATH_R+1
        lda U3216_LN0
        sta MATH_Q+0
        lda U3216_LN1
        sta MATH_Q+1
        lda U3216_Q2
        sta MATH_Q+2
        lda U3216_Q3
        sta MATH_Q+3
        lda U3216_R0
        sta MATH_R+0
        clc
        rts

U3216_ZERO:
        lda #0
        sta MATH_Q+0
        sta MATH_Q+1
        sta MATH_Q+2
        sta MATH_Q+3
        sta MATH_R+0
        sta MATH_R+1
        sec
        rts

* = U3216_D8_BASE
; Compact exact 32/8 path. Each byte is both source and quotient storage.
U3216_D8:
        lda #0
        ldx #8
U3216_D8_B3:
        rol U3216_N1
        rol
        bcs U3216_D8_F3
        cmp U3216_D0
        bcc U3216_D8_N3
        sbc U3216_D0
        bcs U3216_D8_N3
U3216_D8_F3:
        sbc U3216_D0
        sec
U3216_D8_N3:
        dex
        bne U3216_D8_B3
        rol U3216_N1

        ldx #8
U3216_D8_B2:
        rol U3216_N0
        rol
        bcs U3216_D8_F2
        cmp U3216_D0
        bcc U3216_D8_N2
        sbc U3216_D0
        bcs U3216_D8_N2
U3216_D8_F2:
        sbc U3216_D0
        sec
U3216_D8_N2:
        dex
        bne U3216_D8_B2
        rol U3216_N0

        ldx #8
U3216_D8_B1:
        rol U3216_LN1
        rol
        bcs U3216_D8_F1
        cmp U3216_D0
        bcc U3216_D8_N1
        sbc U3216_D0
        bcs U3216_D8_N1
U3216_D8_F1:
        sbc U3216_D0
        sec
U3216_D8_N1:
        dex
        bne U3216_D8_B1
        rol U3216_LN1

        ldx #8
U3216_D8_B0:
        rol U3216_LN0
        rol
        bcs U3216_D8_F0
        cmp U3216_D0
        bcc U3216_D8_N0
        sbc U3216_D0
        bcs U3216_D8_N0
U3216_D8_F0:
        sbc U3216_D0
        sec
U3216_D8_N0:
        dex
        bne U3216_D8_B0
        rol U3216_LN0

        sta MATH_R+0
        lda #0
        sta MATH_R+1
        lda U3216_LN0
        sta MATH_Q+0
        lda U3216_LN1
        sta MATH_Q+1
        lda U3216_N0
        sta MATH_Q+2
        lda U3216_N1
        sta MATH_Q+3
        clc
        rts
U3216_D8_END:
