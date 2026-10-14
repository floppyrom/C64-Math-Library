; Signed SHR16 nonnegative-domain alias installer, V2/V3/V4 (research).
; REQUIRES: both signed 32-bit operands >= 0 on every call while enabled,
; MATH_INIT, independent unsigned clone $0D05..$0E49, free code RAM here.
; The signed public entry stays at $5E15; its original target is $C50C.
; On a negative operand, signed correctness is NOT guaranteed.
; Interrupts and other users must NOT execute $5E15 while enabling or
; disabling; the two JMP operands are written separately.
!cpu 6510
* = $0C00
SMUL32_SHR16_NONNEG_ENABLE:
    lda $5E15
    cmp #$4C
    bne unsupported
    lda $5E16
    cmp #$0C
    bne unsupported
    lda $5E17
    cmp #$C5
    bne unsupported
    lda #$03
    sta $5E16
    lda #$0E
    sta $5E17
    clc
    rts
unsupported:
    sec
    rts

SMUL32_SHR16_NONNEG_DISABLE:
    lda $5E15
    cmp #$4C
    bne restore_failed
    lda $5E16
    cmp #$03
    bne restore_failed
    lda $5E17
    cmp #$0E
    bne restore_failed
    lda #$0C
    sta $5E16
    lda #$C5
    sta $5E17
    clc
    rts
restore_failed:
    sec
    rts
