; Issue144 V1/V5 all-domain 32-bit root highword seed, canonical normal-resident owner.
; Dedicated root slot REG_GAME+$0A40 and proven unused helper at REG_GAME+$0AA8.
; 51 modeled CPU cycles saved per ordinary call; no new ZP or caller-owned RAM.
; Preserves public entry, input, X/Y, carry; V5 imports this exact V1 resident.
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
