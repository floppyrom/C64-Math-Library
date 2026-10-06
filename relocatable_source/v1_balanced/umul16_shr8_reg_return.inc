; Register-return V1/V5 unsigned 16x16 >> 8 fixed-point adapter.
; The low-ZP UMUL16 path repairs pointer highs before return, which clobbers A
; but preserves X=product byte1, Y=product byte3, public Z2=product byte2 and C=0.
!cpu 6510

* = REG_GAME+$041E
UMUL16_SHR8_LOWZP_REG_RETURN:
        jsr MATH_UMUL16
        stx MATH_Z
        lda MATH_Z+$02
        sta MATH_Z+$01
        sty MATH_Z+$02
        rts

* = MATH_UMUL16_SHR8
        jmp UMUL16_SHR8_LOWZP_REG_RETURN
