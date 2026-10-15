!cpu 6510
; ---- executable island $18E2 ----
* = $0D00
L18E2:
    lda #$FF
    sta $9118,x
    ldy #$00
    lda $C004
    sta $9110,x
    sec
    sbc $90F8,x
    bcs L18FA
    eor #$FF
    adc #$01
    dey
L18FA:
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
    bcs L192A
    eor #$FF
    sta $61
    lda $60
    eor #$FF
    adc #$01
    sta $60
    bcc L1927
    inc $61
L1927:
    dey
    lda $61
L192A:
    sta $61
    sty $58
    bne L1946
    lda $60
    cmp $62
    bcs L1946
    ldy $62
    sta $62
    sty $60
    lda $58
    ora #$01
    sta $5C
    lda #$80
    bne L194E
L1946:
    lda $59
    ora #$01
    sta $5C
    lda #$00
L194E:
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
    bcc L19C7
    lda $C011
    bmi L19CA
    sta $9158,x
    lda $C010
    sta $9150,x
L1981:
    lda #$00
    sta $63
    sta $64
    sta $5B
    ldy $9158,x
    beq L1994
L198E:
    INLINE_L3EE3:
    lda $63
    clc
    adc $62
    sta $63
    bcc INLINE_L3EEE
    inc $64
INLINE_L3EEE:
    cmp $60
    lda $64
    sbc $61
    bcc INLINE_L3F00
    sta $64
    lda $63
    sbc $60
    sta $63
    inc $5B
INLINE_L3F00:
    

    dey
    bne L198E
L1994:
    lda $63
    sta $9160,x
    lda $64
    sta $9170,x
    txa
    tay
    lda $9158,x
    jsr $3F01
    lda $9150,x
    beq L19C5
L19AB:
    jmp SEEK_ACCUM_ONCE
L19AE:
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
    jsr $3F01
L19C5:
    clc
    rts
L19C7:
    jmp $5E72
L19CA:
    lda $61
    sta $5F
    lda $62
    sta $54
    lda $60
    ldy $5F
    beq L19E1
L19D8:
    lsr $5F
    ror a
    lsr $54
    ldy $5F
    bne L19D8
L19E1:
    sta $53
    jsr $3D23
    sta $9158,x
    tya
    sta $9150,x
    jmp L1981

* = $0F60
SEEK_ACCUM_ONCE:
ONCE_L3EE3:
    lda $63
    clc
    adc $62
    sta $63
    bcc ONCE_L3EEE
    inc $64
ONCE_L3EEE:
    cmp $60
    lda $64
    sbc $61
    bcc ONCE_L3F00
    sta $64
    lda $63
    sbc $60
    sta $63
    inc $5B
ONCE_L3F00:
    jmp L19AE
