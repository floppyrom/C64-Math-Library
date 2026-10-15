!cpu 6510
* = $0C00
LCB40:
    jsr LC8DB
    ldx $C008
    stx $C044
    lda #$00
    sta $C045
    sec
    lda $C012
    sbc $9800,x
    sta $C041
    lda $C013
    sbc $9900,x
    sta $C042
    lda #$00
    sta $C043
    ldx $C011
    jsr $CA24
    ldx $C010
    jsr $CA24
    lda $C044
    sta $C008
    lda $C045
    sta $C009
    clc
    rts

* = $0C90
LC8DB:
    ldx $C013
    ldy $C901,x
LC8E1:
    lda $C013
    cmp $9900,y
    bcc LC8FD
    bne LC8F3
    lda $C012
    cmp $9800,y
    bcc LC8FD
LC8F3:
    sty $C008
    lda #$00
    sta $C009
    clc
    rts
LC8FD:
    dey
    jmp LC8E1
