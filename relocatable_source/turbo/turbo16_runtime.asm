; Optimized Turbo16 public CALL wrapper.
; Paired with turbo16_overlay.asm. The overlay remains exactly 113 bytes.
; x1 is kept live in A for the umult_ax1 entry and the overlay writes Z0
; directly to MATH_Z, eliminating the old reload/result-copy overhead.
;
; Offsets reflect the canonical 113-byte overlay after the direct Z0 store.
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
        jsr T16_ENTRY
        sta MATH_Z+$02
        stx MATH_Z+$01
        sty MATH_Z+$03
        clc
        rts
