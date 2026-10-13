; Issue #39 V1 32/16 zero-divisor cold-path source integration TRIAL.
; Every address is relative to configured REG_KERNEL / REG_LOW and every
; arithmetic operand goes through ZP_MAIN. Keep this include after the
; 32/16 dual-loop unroll so the redirect and return are source-owned here.
; This is a TRIAL and must not be merged as a default until certified.
; V1 code $4500 has JSR div_u16 at REG_KERNEL+$0500.
; The existing BCC/zero-cleanup/block is overlaid by BCS and fallthrough.

* = REG_KERNEL+$04F0
OOL_DIVZERO_COLD:
    lda #$00
    sta ZP_MAIN+$18
    sta ZP_MAIN+$19
    rts

* = REG_KERNEL+$0503
    bcs OOL_DIVZERO_COLD   ; C=1 from 16/16 producer iff D16=0

* = REG_KERNEL+$0505
OOL_L450C:
    lda ZP_MAIN+$16
    sta ZP_MAIN+$18
    lda ZP_MAIN+$17
    sta ZP_MAIN+$19
    lda ZP_MAIN+$15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs OOL_L4537
    cmp ZP_MAIN+$11
    bcc OOL_L4542
    bne OOL_L452B
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc OOL_L4542
OOL_L452B:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs OOL_L4542
OOL_L4537:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
OOL_L4542:
    ldx #$0F
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs OOL_L4565
    cmp ZP_MAIN+$11
    bcc OOL_L4570
    bne OOL_L4559
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc OOL_L4570
OOL_L4559:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs OOL_L4570
OOL_L4565:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
OOL_L4570:
    jmp D3216_LOW_ROUNDS
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    sta ZP_MAIN+$15
    clc
    rts

; Clear seven trailing bytes of original continuation after relocating -7.
* = REG_KERNEL+$0574
    !byte $00, $00, $00, $00, $00, $00, $00

; Existing 15-round inline unroll returns here, not to old $4573.
* = REG_LOW+$0B6A
    jmp REG_KERNEL+$056C
