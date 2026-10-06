; Turbo16 optimized public CALL wrapper.
; Paired with turbo16_overlay.asm. The overlay remains exactly 113 bytes.
; z0 is written directly to MATH_Z by the active overlay; A/X/Y return z2/z1/z3.
;
; Direct-result STA shifts overlay operands after z0 by one byte:
; x0 remains +$16, x1 becomes +$25, y1 becomes +$35.
T16_X0    = TURBO16_ZP_BASE+$16
T16_X1    = TURBO16_ZP_BASE+$25
T16_Y1    = TURBO16_ZP_BASE+$35
T16_AX1   = TURBO16_ZP_BASE+$02

* = REG_API+$0840
T16_PUBLIC_CALL:
        lda MATH_X
        sta+1 T16_X0
        lda MATH_Y+$01
        sta+1 T16_Y1
        ldy MATH_Y
        lda MATH_X+$01
        sta+1 T16_X1
        jsr T16_AX1
        sta MATH_Z+$02
        stx MATH_Z+$01
        sty MATH_Z+$03
        clc
        rts
