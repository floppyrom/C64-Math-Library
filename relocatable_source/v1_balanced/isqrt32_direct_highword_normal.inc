; Issue144: V1 and derived V5 unrestricted ISQRT32 direct high-word seed.
; Final source owner of original REG_GAME+$0A40 root entry and free +$0AA8 helper.
; Same public ABI and normal 31-byte V1/V5 ZP. Input MATH_N unchanged.
; Source-only promotion; reference PRGs, REU images and published performance remain historical.
* = REG_GAME+$0A40
LCB40:
    jsr LC8DB
    ldx MATH_IO+$08
    stx V1_SCRATCH+$04
    lda #$00
    sta V1_SCRATCH+$05
    sec
    lda MATH_IO+$12
    sbc REG_TABLE+$3800,x
    sta V1_SCRATCH+$01
    lda MATH_IO+$13
    sbc REG_TABLE+$3900,x
    sta V1_SCRATCH+$02
    lda #$00
    sta V1_SCRATCH+$03
    ldx MATH_IO+$11
    jsr REG_GAME+$0924
    ldx MATH_IO+$10
    jsr REG_GAME+$0924
    lda V1_SCRATCH+$04
    sta MATH_IO+$08
    lda V1_SCRATCH+$05
    sta MATH_IO+$09
    clc
    rts

* = REG_GAME+$0AA8
LC8DB:
    ldx MATH_IO+$13
    ldy REG_GAME+$0801,x
LC8E1:
    lda MATH_IO+$13
    cmp REG_TABLE+$3900,y
    bcc LC8FD
    bne LC8F3
    lda MATH_IO+$12
    cmp REG_TABLE+$3800,y
    bcc LC8FD
LC8F3:
    sty MATH_IO+$08
    lda #$00
    sta MATH_IO+$09
    clc
    rts
LC8FD:
    dey
    jmp LC8E1
