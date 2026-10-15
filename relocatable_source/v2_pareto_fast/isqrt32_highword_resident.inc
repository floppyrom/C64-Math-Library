* = REG_GAME+$0A40
LCB40:
    jsr LC836
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
    jsr REG_GAME+$0866
    ldx MATH_IO+$10
    jsr REG_GAME+$0866
    lda ZP_MAIN+$55
    sta MATH_IO+$08
    lda ZP_MAIN+$56
    sta MATH_IO+$09
    clc
    rts

* = REG_GAME+$0AD0
LC836:
    ldx MATH_IO+$13
    ldy REG_GAME+$075C,x
LC83C:
    lda MATH_IO+$13
    cmp REG_TABLE+$3900,y
    bcc LC858
    bne LC84E
    lda MATH_IO+$12
    cmp REG_TABLE+$3800,y
    bcc LC858
LC84E:
    sty MATH_IO+$08
    lda #$00
    sta MATH_IO+$09
    clc
    rts
LC858:
    dey
    jmp LC83C
