; Optimized Turbo16 public CALL wrapper.
; The 113-byte overlay is unchanged byte-for-byte. Keep x1 live in A after
; patching its SMC operand so the umult_ax1 entry no longer reloads MATH_X+1.
T16_ENTRY = TURBO16_ZP_BASE+$02
T16_X0    = TURBO16_ZP_BASE+$16
T16_X1    = TURBO16_ZP_BASE+$24
T16_Y1    = TURBO16_ZP_BASE+$34
T16_Z0    = TURBO16_ZP_BASE+$70

* = REG_API+$0840
T16_PUBLIC_CALL:
        ldx MATH_Y+$01
        lda MATH_X
        sta+1 T16_X0
        lda MATH_X+$01
        sta+1 T16_X1
        stx+1 T16_Y1
        ldy MATH_Y
        jsr T16_ENTRY
        sta MATH_Z+$02
        stx MATH_Z+$01
        sty MATH_Z+$03
        lda+1 T16_Z0
        sta MATH_Z
        clc
        rts
