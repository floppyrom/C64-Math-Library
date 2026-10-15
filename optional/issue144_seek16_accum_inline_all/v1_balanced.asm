!cpu 6510
; ---- executable island $3723 ----
* = $0D00
L3723:
    lda #$FF
    sta $19B8,x
    ldy #$00
    lda $C004
    sta $19B0,x
    sec
    sbc $1998,x
    bcs L373B
    eor #$FF
    adc #$01
    dey
L373B:
    sta $C04F
    sty $C046
    ldy #$00
    lda $C000
    sta $19A0,x
    sec
    sbc $1988,x
    sta $C04D
    lda $C001
    sta $19A8,x
    sbc $1990,x
    bcs L3773
    eor #$FF
    sta $C04E
    lda $C04D
    eor #$FF
    adc #$01
    sta $C04D
    bcc L376F
    inc $C04E
L376F:
    dey
    lda $C04E
L3773:
    sta $C04E
    sty $C045
    bne L3798
    lda $C04D
    cmp $C04F
    bcs L3798
    ldy $C04F
    sta $C04F
    sty $C04D
    lda $C045
    ora #$01
    sta $C049
    lda #$80
    bne L37A2
L3798:
    lda $C046
    ora #$01
    sta $C049
    lda #$00
L37A2:
    sta $C047
    lda $C04E
    sta $19E8,x
    lsr a
    sta $19D8,x
    lda $C04D
    sta $19E0,x
    ror a
    sta $19D0,x
    lda $C04D
    sec
    sbc #$01
    sta $19C0,x
    lda $C04E
    sbc #$00
    sta $19C8,x
    bcs seek_skip_empty
    jmp L3827
seek_skip_empty:
    lda $C011
    bpl seek_skip_euclid
    jmp L382A
seek_skip_euclid:
    sta $19F8,x
    lda $C010
    sta $19F0,x
L37DA:
    lda #$00
    sta $C050
    sta $C051
    sta $C048
    ldy $19F8,x
    beq L37F0
L37EA:
    INLINE_L38CE:
    lda $C050
    clc
    adc $C04F
    sta $C050
    bcc INLINE_L38DD
    inc $C051
INLINE_L38DD:
    cmp $C04D
    lda $C051
    sbc $C04E
    bcc INLINE_L38F7
    sta $C051
    lda $C050
    sbc $C04D
    sta $C050
    inc $C048
INLINE_L38F7:
    

    dey
    bne L37EA
L37F0:
    lda $C050
    sta $1A00,x
    lda $C051
    sta $1A10,x
    txa
    tay
    lda $19F8,x
    jsr $38F8
    lda $19F0,x
    beq L3825
L3809:
    jmp SEEK_ACCUM_ONCE
L380C:
    lda $C050
    sta $1A08,x
    lda $C051
    sta $1A18,x
    txa
    ora #$08
    tay
    lda $19F8,x
    sec
    adc #$00
    jsr $38F8
L3825:
    clc
    rts
L3827:
    jmp $361E
L382A:
    lda $C04E
    sta $C04C
    lda $C04F
    sta $C041
    lda $C04D
    ldy $C04C
    beq L384A
L383E:
    lsr $C04C
    ror a
    lsr $C041
    ldy $C04C
    bne L383E
L384A:
    sta $C040
    jsr $3977
    sta $19F8,x
    tya
    sta $19F0,x
    jmp L37DA

* = $0F60
SEEK_ACCUM_ONCE:
ONCE_L38CE:
    lda $C050
    clc
    adc $C04F
    sta $C050
    bcc ONCE_L38DD
    inc $C051
ONCE_L38DD:
    cmp $C04D
    lda $C051
    sbc $C04E
    bcc ONCE_L38F7
    sta $C051
    lda $C050
    sbc $C04D
    sta $C050
    inc $C048
ONCE_L38F7:
    jmp L380C
