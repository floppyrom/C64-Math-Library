; Selected signed 16x16 >> 8 adapter; inherits profile-selected MATH_SMUL16.
!cpu 6510
* = REG_GAME+$0E80
SMUL16_SHR8_selected:
        jsr MATH_SMUL16
        ; V2-V4 return A=byte1, X=byte2; byte3 is already public Z3.
        sta MATH_IO+$08
        stx MATH_IO+$09
        lda MATH_IO+$0B
        sta MATH_IO+$0A
        rts
* = MATH_SMUL16_SHR8
        jmp SMUL16_SHR8_selected
