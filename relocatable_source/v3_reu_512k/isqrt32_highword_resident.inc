* = REG_GAME+$0A40
LCB40:
    jsr LC841
    ldx MATH_IO+$08
    stx ZP_MAIN+$55
    lda #$00
    sta ZP_MAIN+$56
    sec
    lda MATH_IO+$12
    sbc REG_TABLE+$3800,x
    sta ZP_MAIN+$52
    lda MATH_IO+$13
    sbc REG_TABLE+$3900,x
    sta ZP_MAIN+$53
    lda #$00
    sta ZP_MAIN+$54
    ldx MATH_IO+$11
    jsr REG_GAME+$0871
    ldx MATH_IO+$10
    jsr REG_GAME+$0871
    lda ZP_MAIN+$55
    sta MATH_IO+$08
    lda ZP_MAIN+$56
    sta MATH_IO+$09
    clc
    rts

* = REG_GAME+$0AD0
LC841:
    ldx MATH_IO+$13
    ldy REG_GAME+$0767,x
LC847:
    lda MATH_IO+$13
    cmp REG_TABLE+$3900,y
    bcc LC863
    bne LC859
    lda MATH_IO+$12
    cmp REG_TABLE+$3800,y
    bcc LC863
LC859:
    sty MATH_IO+$08
    lda #$00
    sta MATH_IO+$09
    clc
    rts
LC863:
    dey
    jmp LC847
