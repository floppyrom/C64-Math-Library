!cpu 6510
* = $0C00
LCB40:
    jsr LC836
    ldx $C008
    stx $57
    lda #$00
    sta $58
    sec
    lda $C012
    sbc $9800,x
    sta $54
    lda $C013
    sbc $9900,x
    sta $55
    lda #$00
    sta $56
    ldx $C011
    jsr $C966
    ldx $C010
    jsr $C966
    lda $57
    sta $C008
    lda $58
    sta $C009
    clc
    rts

* = $0C90
LC836:
    ldx $C013
    ldy $C85C,x
LC83C:
    lda $C013
    cmp $9900,y
    bcc LC858
    bne LC84E
    lda $C012
    cmp $9800,y
    bcc LC858
LC84E:
    sty $C008
    lda #$00
    sta $C009
    clc
    rts
LC858:
    dey
    jmp LC83C
