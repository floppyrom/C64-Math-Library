; Direct-output Turbo16 public CALL wrapper.
; The 122-byte overlay writes the complete 32-bit product directly to MATH_Z.
; The wrapper only binds x/y SMC operands and tail-jumps into the active ZP code.
T16_ENTRY = TURBO16_ZP_BASE+$02
T16_X0    = TURBO16_ZP_BASE+$16
T16_X1    = TURBO16_ZP_BASE+$25
T16_Y1    = TURBO16_ZP_BASE+$35

* = REG_API+$0840
T16_PUBLIC_CALL:
        ldx MATH_Y+$01
        lda MATH_X
        sta+1 T16_X0
        lda MATH_X+$01
        sta+1 T16_X1
        stx+1 T16_Y1
        ldy MATH_Y
        jmp T16_ENTRY
