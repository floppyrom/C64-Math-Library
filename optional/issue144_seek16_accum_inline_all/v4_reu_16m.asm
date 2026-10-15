!cpu 6510
; ---- executable island $3600 ----
* = $0D00
L3600:
    lda #$FF
    sta $9118,x
    ldy #$00
    lda $C004
    sta $9110,x
    sec
    sbc $90F8,x
    bcs L3618
    eor #$FF
    adc #$01
    dey
L3618:
    sta $62
    sty $59
    ldy #$00
    lda $C000
    sta $9100,x
    sec
    sbc $90E8,x
    sta $60
    lda $C001
    sta $9108,x
    sbc $90F0,x
    bcs L3648
    eor #$FF
    sta $61
    lda $60
    eor #$FF
    adc #$01
    sta $60
    bcc L3645
    inc $61
L3645:
    dey
    lda $61
L3648:
    sta $61
    sty $58
    bne L3664
    lda $60
    cmp $62
    bcs L3664
    ldy $62
    sta $62
    sty $60
    lda $58
    ora #$01
    sta $5C
    lda #$80
    bne L366C
L3664:
    lda $59
    ora #$01
    sta $5C
    lda #$00
L366C:
    sta $5A
    lda $61
    sta $9148,x
    lsr a
    sta $9138,x
    lda $60
    sta $9140,x
    ror a
    sta $9130,x
    lda $60
    sec
    sbc #$01
    sta $9120,x
    lda $61
    sbc #$00
    sta $9128,x
    bcc L36E5
    lda $C011
    bmi L36E8
    sta $9158,x
    lda $C010
    sta $9150,x
L369F:
    lda #$00
    sta $63
    sta $64
    sta $5B
    ldy $9158,x
    beq L36B2
L36AC:
    INLINE_L5E54:
    lda $63
    clc
    adc $62
    sta $63
    bcc INLINE_L5E5F
    inc $64
INLINE_L5E5F:
    cmp $60
    lda $64
    sbc $61
    bcc INLINE_L5E71
    sta $64
    lda $63
    sbc $60
    sta $63
    inc $5B
INLINE_L5E71:
    

    dey
    bne L36AC
L36B2:
    lda $63
    sta $9160,x
    lda $64
    sta $9170,x
    txa
    tay
    lda $9158,x
    jsr $5E72
    lda $9150,x
    beq L36E3
L36C9:
    jmp SEEK_ACCUM_ONCE
L36CC:
    lda $63
    sta $9168,x
    lda $64
    sta $9178,x
    txa
    ora #$08
    tay
    lda $9158,x
    sec
    adc #$00
    jsr $5E72
L36E3:
    clc
    rts
L36E5:
    jmp $401E
L36E8:
    lda $61
    sta $5F
    lda $62
    sta $54
    lda $60
    ldy $5F
    beq L36FF
L36F6:
    lsr $5F
    ror a
    lsr $54
    ldy $5F
    bne L36F6
L36FF:
    sta $53
    jsr $3D23
    sta $9158,x
    tya
    sta $9150,x
    jmp L369F

* = $0F60
SEEK_ACCUM_ONCE:
ONCE_L5E54:
    lda $63
    clc
    adc $62
    sta $63
    bcc ONCE_L5E5F
    inc $64
ONCE_L5E5F:
    cmp $60
    lda $64
    sbc $61
    bcc ONCE_L5E71
    sta $64
    lda $63
    sbc $60
    sta $63
    inc $5B
ONCE_L5E71:
    jmp L36CC
