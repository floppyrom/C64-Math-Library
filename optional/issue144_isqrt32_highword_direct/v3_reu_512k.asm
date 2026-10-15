!cpu 6510
* = $0C00
LCB40:
    jsr LC841
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
    jsr $C971
    ldx $C010
    jsr $C971
    lda $57
    sta $C008
    lda $58
    sta $C009
    clc
    rts

* = $0C90
LC841:
    ldx $C013
    ldy $C867,x
LC847:
    lda $C013
    cmp $9900,y
    bcc LC863
    bne LC859
    lda $C012
    cmp $9800,y
    bcc LC863
LC859:
    sty $C008
    lda #$00
    sta $C009
    clc
    rts
LC863:
    dey
    jmp LC847
