; Turbo32 resident binder/summation and stable public CALL wrapper.
; Paired with turbo32_overlay.asm. The overlay remains exactly 135 bytes.
; Y is read directly from MATH_Y; product bytes 0-3 and 7 land directly in
; MATH_Z; bytes 4-6 return in Y/X/A and are stored by the wrapper.
;
; Operand offsets are validated against turbo32_overlay.asm by
; tools/validate_turbo32_runtime.py.
T32_X0  = TURBO32_ZP_BASE+$43
T32_NL0 = TURBO32_ZP_BASE+$46
T32_SH0 = TURBO32_ZP_BASE+$4C
T32_NH0 = TURBO32_ZP_BASE+$4F
T32_X1  = TURBO32_ZP_BASE+$52
T32_NL1 = TURBO32_ZP_BASE+$57
T32_SH1 = TURBO32_ZP_BASE+$5C
T32_NH1 = TURBO32_ZP_BASE+$5F
T32_X2  = TURBO32_ZP_BASE+$62
T32_NL2 = TURBO32_ZP_BASE+$67
T32_SH2 = TURBO32_ZP_BASE+$6C
T32_NH2 = TURBO32_ZP_BASE+$6F
T32_X3  = TURBO32_ZP_BASE+$72
T32_NL3 = TURBO32_ZP_BASE+$77
T32_SH3 = TURBO32_ZP_BASE+$7C
T32_NH3 = TURBO32_ZP_BASE+$7F
T32_ENTRY = TURBO32_ZP_BASE+$42

T32_Z01 = TURBO32_ZP_BASE+$04
T32_Z11 = TURBO32_ZP_BASE+$05
T32_Z21 = TURBO32_ZP_BASE+$06
T32_Z31 = TURBO32_ZP_BASE+$07
T32_Z02 = TURBO32_ZP_BASE+$08
T32_Z12 = TURBO32_ZP_BASE+$09
T32_Z22 = TURBO32_ZP_BASE+$0A
T32_Z32 = TURBO32_ZP_BASE+$0B
T32_Z03 = TURBO32_ZP_BASE+$0C
T32_Z13 = TURBO32_ZP_BASE+$0D
T32_Z23 = TURBO32_ZP_BASE+$0E
T32_Z33 = TURBO32_ZP_BASE+$0F
T32_Z14 = MATH_Z+$05
T32_Z24 = MATH_Z+$06
T32_Z34 = MATH_Z+$07

T32_SUM_AFTER_A = REG_LOW+$0135
T32_SUM_X_CLC   = REG_LOW+$0149

* = REG_LOW
T32_PREP:
        lda+1 T32_X0
T32_PREP_LOADED:
        sta+1 T32_SH0
        eor #$FF
        sta+1 T32_NL0
        sta+1 T32_NH0
        lda+1 T32_X1
        sta+1 T32_SH1
        eor #$FF
        sta+1 T32_NL1
        sta+1 T32_NH1
        lda+1 T32_X2
        sta+1 T32_SH2
        eor #$FF
        sta+1 T32_NL2
        sta+1 T32_NH2
        lda+1 T32_X3
        sta+1 T32_SH3
        eor #$FF
        sta+1 T32_NL3
        sta+1 T32_NH3
        ldx #$04
        sec
        jmp T32_ENTRY

T32_OVERFLOW_A:
        inc+1 T32_Z32
        bne T32_OVERFLOW_A_DONE
        inc+1 T32_Z33
        bne T32_OVERFLOW_A_DONE
        inc T32_Z34
T32_OVERFLOW_A_DONE:
        clc
        jmp T32_SUM_AFTER_A

T32_OVERFLOW_B:
        inc+1 T32_Z33
        bne T32_OVERFLOW_B_DONE
        inc T32_Z34
T32_OVERFLOW_B_DONE:
        jmp T32_SUM_X_CLC

* = REG_LOW+$0100
T32_SUMMATION:
        tay
        clc
        lda+1 T32_Z01
        adc MATH_Z+$01
        sta MATH_Z+$01
        lda MATH_Z+$02
        adc+1 T32_Z11
        bcc T32_SUM_NO_X1
        inx
        clc
T32_SUM_NO_X1:
        adc+1 T32_Z02
        sta MATH_Z+$02
        lda+1 T32_Z03
        adc+1 T32_Z12
        bcc T32_SUM_NO_Y1
        iny
        cpx #$01
        adc MATH_Z+$03
        bcc T32_SUM_AFTER_A
        clc
        iny
        bne T32_SUM_AFTER_A
        jmp T32_OVERFLOW_A
T32_SUM_NO_Y1:
        adc MATH_Z+$03
        bcc T32_SUM_NO_Y2
        iny
T32_SUM_NO_Y2:
        cpx #$01
T32_SUM_AFTER_A:
        adc+1 T32_Z21
        sta MATH_Z+$03
        tya
        ldx T32_Z14
        adc+1 T32_Z13
        bcs T32_SUM_CARRY_X0
        adc+1 T32_Z31
        bcc T32_SUM_X_OK
        inx
        beq T32_SUM_OVERFLOW_B
T32_SUM_X_CLC:
        clc
T32_SUM_X_OK:
        adc+1 T32_Z22
        tay
        txa
        adc+1 T32_Z32
        bcs T32_SUM_CARRY_X1
        adc+1 T32_Z23
        tax
        lda T32_Z24
        adc+1 T32_Z33
        bcs T32_SUM_INC_TOP
        rts
T32_SUM_CARRY_TOP_A:
        adc #$00
T32_SUM_INC_TOP:
        inc T32_Z34
        rts
T32_SUM_CARRY_X1:
        clc
        adc+1 T32_Z23
        tax
        lda T32_Z24
        adc+1 T32_Z33
        bcs T32_SUM_CARRY_TOP_A
        adc #$01
        bcs T32_SUM_INC_TOP
        rts
T32_SUM_CARRY_X0:
        inx
        clc
        adc+1 T32_Z31
        bcc T32_SUM_X_OK
        inx
        bne T32_SUM_X_CLC
T32_SUM_OVERFLOW_B:
        jmp T32_OVERFLOW_B

* = REG_API+$0900
T32_PUBLIC_CALL:
        lda MATH_X+$01
        sta+1 T32_X1
        lda MATH_X+$02
        sta+1 T32_X2
        lda MATH_X+$03
        sta+1 T32_X3
        ldy MATH_Y+$03
        lda MATH_X
        sta+1 T32_X0
        jsr T32_PREP_LOADED
        sta MATH_Z+$06
        stx MATH_Z+$05
        sty MATH_Z+$04
        clc
        rts
