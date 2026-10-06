; Register-return V2/V3/V4 unsigned 16x16 >> 8 fixed-point adapter.
; MATH_UMUL16 already returns product bytes 1/2/3 in X/A/Y respectively
; and returns with C=0.  Avoid reloading those bytes from public RAM.
!cpu 6510

* = REG_GAME+$03B5
UMUL16_SHR8_REG_RETURN:
        jsr MATH_UMUL16
        stx MATH_Z
        sta MATH_Z+$01
        sty MATH_Z+$02
        rts

* = MATH_UMUL16_SHR8
        jmp UMUL16_SHR8_REG_RETURN
