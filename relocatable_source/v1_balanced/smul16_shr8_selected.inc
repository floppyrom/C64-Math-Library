; Selected signed 16x16 >> 8 adapter; inherits profile-selected MATH_SMUL16.
!cpu 6510
* = REG_GAME+$0E80
SMUL16_SHR8_selected:
        jsr MATH_SMUL16
        ; V1/V5 return X=byte1, Y=byte3; byte2 is already public Z2.
        stx MATH_IO+$08
        lda MATH_IO+$0A
        sta MATH_IO+$09
        sty MATH_IO+$0A
        rts
* = MATH_SMUL16_SHR8
        jmp SMUL16_SHR8_selected
