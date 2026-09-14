; GENERATED CANONICAL SOURCE. Builds the stable 45-entry API from symbolic assembly source.
; The fixed FINAL PRG is provenance/reference only. This file is the relocatable build input.
; Compatible with the included source assembler; syntax is intentionally ACME-style.
!cpu 6510
!source "math_config.inc"

; Public API symbols
MATH_UMUL8 = REG_API
MATH_UMUL16 = REG_API+$0020
MATH_UMUL24 = REG_API+$0060
MATH_UMUL32 = REG_API+$00B0
MATH_UMUL32_READY = REG_API+$00C0
MATH_SMUL8 = REG_API+$0B80
MATH_SMUL16 = REG_API+$0BB0
MATH_SMUL24 = REG_API+$0BF0
MATH_SMUL32 = REG_API+$0C40
MATH_SMUL32_READY = REG_API+$0FE0
MATH_UDIV8 = REG_API+$0120
MATH_UDIV16 = REG_API+$0140
MATH_UDIV24 = REG_API+$0170
MATH_UDIV32_16 = REG_API+$01B0
MATH_UMOD8 = REG_API+$0200
MATH_UMOD16 = REG_API+$0220
MATH_UMOD24 = REG_API+$0223
MATH_UMOD32_16 = REG_API+$0226
MATH_SDIV8 = REG_API+$0CA0
MATH_SDIV16 = REG_API+$0D20
MATH_SDIV24 = REG_API+$0DE0
MATH_SDIV32_16 = REG_API+$0EE0
MATH_SMOD8 = REG_API+$0FD4
MATH_SMOD16 = REG_API+$0FD7
MATH_SMOD24 = REG_API+$0FDA
MATH_SMOD32_16 = REG_API+$0FDD
MATH_UDIV32_32 = REG_GAME_API
MATH_UMOD32_32 = REG_GAME_API+$0003
MATH_SDIV32_32 = REG_GAME_API+$0006
MATH_SMOD32_32 = REG_GAME_API+$0009
MATH_UMUL16_SHR8 = REG_GAME_API+$000C
MATH_SMUL16_SHR8 = REG_GAME_API+$000F
MATH_UMUL32_SHR16 = REG_GAME_API+$0012
MATH_SMUL32_SHR16 = REG_GAME_API+$0015
MATH_UDIV16_SHL8 = REG_GAME_API+$0018
MATH_SDIV16_SHL8 = REG_GAME_API+$001B
MATH_URECIP16_Q16 = REG_GAME_API+$001E
MATH_SIN8 = REG_GAME_API+$0021
MATH_COS8 = REG_GAME_API+$0024
MATH_SINCOS8 = REG_GAME_API+$0027
MATH_ATAN2_8 = REG_GAME_API+$002A
MATH_ISQRT16 = REG_GAME_API+$002D
MATH_ISQRT32 = REG_GAME_API+$0030
MATH_DIST8_FAST = REG_GAME_API+$0033
MATH_DIST8_ACCURATE = REG_GAME_API+$0036
MATH_INIT = REG_API+$0280
MATH_X = MATH_IO
MATH_Y = MATH_IO+$04
MATH_Z = MATH_IO+$08
MATH_N = MATH_IO+$10
MATH_D = MATH_IO+$14
MATH_Q = MATH_IO+$18
MATH_R = MATH_IO+$1C


; Source interval $2000-$2FFF
* = REG_LOW+$1000
    lda #>REG_TABLE+$2000
    sta ZP_MAIN+$0F
    lda #>REG_TABLE+$2200
    sta ZP_MAIN+$11
    ldx MATH_IO
    ldy MATH_IO+$04
    jsr REG_LOW+$1600
    sta MATH_IO+$09
    lda ZP_MAIN+$12
    sta MATH_IO+$08
    lda MATH_IO
    bpl L2028
    sec
    lda MATH_IO+$09
    sbc MATH_IO+$04
    sta MATH_IO+$09
L2028:
    lda MATH_IO+$04
    bpl L2037
    sec
    lda MATH_IO+$09
    sbc MATH_IO
    sta MATH_IO+$09
L2037:
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00
    lda #>REG_TABLE+$2000
    sta ZP_MAIN+$0F
    lda #>REG_TABLE+$2200
    sta ZP_MAIN+$11
    lda #$00
    sta MATH_IO+$08
    sta MATH_IO+$09
    sta MATH_IO+$0A
    sta MATH_IO+$0B
    ldx MATH_IO
    ldy MATH_IO+$04
    jsr REG_LOW+$1600
    sta MATH_IO+$09
    lda ZP_MAIN+$12
    sta MATH_IO+$08
    ldx MATH_IO
    ldy MATH_IO+$05
    jsr REG_LOW+$1600
    sta ZP_MAIN+$16
    lda ZP_MAIN+$12
    clc
    adc MATH_IO+$09
    sta MATH_IO+$09
    lda ZP_MAIN+$16
    adc MATH_IO+$0A
    sta MATH_IO+$0A
    bcc L2148
    inc MATH_IO+$0B
L2148:
    ldx MATH_IO+$01
    ldy MATH_IO+$04
    jsr REG_LOW+$1600
    sta ZP_MAIN+$16
    lda ZP_MAIN+$12
    clc
    adc MATH_IO+$09
    sta MATH_IO+$09
    lda ZP_MAIN+$16
    adc MATH_IO+$0A
    sta MATH_IO+$0A
    bcc L2169
    inc MATH_IO+$0B
L2169:
    ldx MATH_IO+$01
    ldy MATH_IO+$05
    jsr REG_LOW+$1600
    sta ZP_MAIN+$16
    lda ZP_MAIN+$12
    clc
    adc MATH_IO+$0A
    sta MATH_IO+$0A
    lda ZP_MAIN+$16
    adc MATH_IO+$0B
    sta MATH_IO+$0B
    lda MATH_IO+$01
    bpl L219D
    sec
    lda MATH_IO+$0A
    sbc MATH_IO+$04
    sta MATH_IO+$0A
    lda MATH_IO+$0B
    sbc MATH_IO+$05
    sta MATH_IO+$0B
L219D:
    lda MATH_IO+$05
    bpl L21B5
    sec
    lda MATH_IO+$0A
    sbc MATH_IO
    sta MATH_IO+$0A
    lda MATH_IO+$0B
    sbc MATH_IO+$01
    sta MATH_IO+$0B
L21B5:
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO
    sta ZP_MAIN+$0E
    lda MATH_IO+$01
    sta ZP_MAIN+$0F
    lda MATH_IO+$02
    sta ZP_MAIN+$10
    lda MATH_IO+$04
    sta ZP_MAIN+$17
    lda MATH_IO+$05
    sta ZP_MAIN+$18
    lda MATH_IO+$06
    sta ZP_MAIN+$19
    jsr REG_LOW+$1700
    sta MATH_IO+$0D
    lda ZP_MAIN+$0E
    sta MATH_IO+$08
    lda ZP_MAIN+$0F
    sta MATH_IO+$09
    lda ZP_MAIN+$10
    sta MATH_IO+$0A
    lda ZP_MAIN+$11
    sta MATH_IO+$0B
    lda ZP_MAIN+$12
    sta MATH_IO+$0C
    lda MATH_IO+$02
    bpl L225E
    sec
    lda MATH_IO+$0B
    sbc MATH_IO+$04
    sta MATH_IO+$0B
    lda MATH_IO+$0C
    sbc MATH_IO+$05
    sta MATH_IO+$0C
    lda MATH_IO+$0D
    sbc MATH_IO+$06
    sta MATH_IO+$0D
L225E:
    lda MATH_IO+$06
    bpl L227F
    sec
    lda MATH_IO+$0B
    sbc MATH_IO
    sta MATH_IO+$0B
    lda MATH_IO+$0C
    sbc MATH_IO+$01
    sta MATH_IO+$0C
    lda MATH_IO+$0D
    sbc MATH_IO+$02
    sta MATH_IO+$0D
L227F:
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda #>REG_TABLE+$3000
    sta ZP_MAIN+$01
    sta ZP_MAIN+$05
    sta ZP_MAIN+$09
    lda #>REG_TABLE+$2E00
    sta ZP_MAIN+$03
    sta ZP_MAIN+$07
    sta ZP_MAIN+$0B
    lda MATH_IO+$01
    sta ZP_MAIN+$02
    lda MATH_IO+$02
    sta ZP_MAIN+$06
    lda MATH_IO+$03
    sta ZP_MAIN+$0A
    lda MATH_IO+$04
    sta ZP_MAIN+$0C
    lda MATH_IO+$05
    sta ZP_MAIN+$0D
    lda MATH_IO+$06
    sta ZP_MAIN+$0E
    ldy MATH_IO+$07
    lda MATH_IO
    jsr REG_LOW+$1800
    sta MATH_IO+$0E
    stx MATH_IO+$0C
    sty MATH_IO+$0D
    lda ZP_MAIN+$0C
    sta MATH_IO+$08
    lda ZP_MAIN+$0D
    sta MATH_IO+$09
    lda ZP_MAIN+$0E
    sta MATH_IO+$0A
    lda ZP_MAIN+$0F
    sta MATH_IO+$0B
    lda ZP_MAIN+$1A
    sta MATH_IO+$0F
    lda MATH_IO+$03
    bpl L2383
    sec
    lda MATH_IO+$0C
    sbc MATH_IO+$04
    sta MATH_IO+$0C
    lda MATH_IO+$0D
    sbc MATH_IO+$05
    sta MATH_IO+$0D
    lda MATH_IO+$0E
    sbc MATH_IO+$06
    sta MATH_IO+$0E
    lda MATH_IO+$0F
    sbc MATH_IO+$07
    sta MATH_IO+$0F
L2383:
    lda MATH_IO+$07
    bpl L23AD
    sec
    lda MATH_IO+$0C
    sbc MATH_IO
    sta MATH_IO+$0C
    lda MATH_IO+$0D
    sbc MATH_IO+$01
    sta MATH_IO+$0D
    lda MATH_IO+$0E
    sbc MATH_IO+$02
    sta MATH_IO+$0E
    lda MATH_IO+$0F
    sbc MATH_IO+$03
    sta MATH_IO+$0F
L23AD:
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0C
    lda MATH_IO+$14
    sta ZP_MAIN+$0D
    jsr REG_KERNEL+$1006
    lda ZP_MAIN+$0F
    sta MATH_IO+$18
    lda ZP_MAIN+$10
    sta MATH_IO+$1C
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0C
    lda MATH_IO+$11
    sta ZP_MAIN+$0D
    lda MATH_IO+$14
    sta ZP_MAIN+$0E
    lda MATH_IO+$15
    sta ZP_MAIN+$0F
    jsr REG_KERNEL+$1200
    lda ZP_MAIN+$14
    sta MATH_IO+$18
    lda ZP_MAIN+$15
    sta MATH_IO+$19
    lda ZP_MAIN+$16
    sta MATH_IO+$1C
    lda ZP_MAIN+$17
    sta MATH_IO+$1D
    rts
    !byte $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0C
    lda MATH_IO+$11
    sta ZP_MAIN+$0D
    lda MATH_IO+$12
    sta ZP_MAIN+$0E
    lda MATH_IO+$14
    sta ZP_MAIN+$0F
    lda MATH_IO+$15
    sta ZP_MAIN+$10
    lda MATH_IO+$16
    sta ZP_MAIN+$11
    jsr REG_KERNEL+$1600
    lda ZP_MAIN+$18
    sta MATH_IO+$18
    lda ZP_MAIN+$19
    sta MATH_IO+$19
    lda ZP_MAIN+$1A
    sta MATH_IO+$1A
    lda ZP_MAIN+$1B
    sta MATH_IO+$1C
    lda ZP_MAIN+$1C
    sta MATH_IO+$1D
    lda ZP_MAIN+$1D
    sta MATH_IO+$1E
    rts
    lda MATH_IO+$10
    sta ZP_MAIN+$0C
    lda MATH_IO+$11
    sta ZP_MAIN+$0D
    lda MATH_IO+$12
    sta ZP_MAIN+$0E
    lda MATH_IO+$13
    sta ZP_MAIN+$0F
    lda MATH_IO+$14
    sta ZP_MAIN+$10
    lda MATH_IO+$15
    sta ZP_MAIN+$11
    jsr REG_KERNEL+$1C00
    lda ZP_MAIN+$1C
    sta MATH_IO+$18
    lda ZP_MAIN+$1D
    sta MATH_IO+$19
    lda ZP_MAIN+$16
    sta MATH_IO+$1A
    lda ZP_MAIN+$17
    sta MATH_IO+$1B
    lda ZP_MAIN+$18
    sta MATH_IO+$1C
    lda ZP_MAIN+$19
    sta MATH_IO+$1D
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    sec
    stx ZP_MAIN+$0E
    stx ZP_MAIN+$10
    tya
    sbc ZP_MAIN+$0E
    bcs L260E
    sbc #$00
    eor #$FF
L260E:
    tax
    lda (ZP_MAIN+$0E),y
    sbc REG_TABLE+$2000,x
    sta ZP_MAIN+$12
    lda (ZP_MAIN+$10),y
    sbc REG_TABLE+$2200,x
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00
    lda ZP_MAIN+$0E
    sta REG_LOW+$1748
    sta REG_LOW+$1750
    eor #$FF
    sta REG_LOW+$174B
    sta REG_LOW+$1753
    lda ZP_MAIN+$0F
    sta REG_LOW+$1756
    sta REG_LOW+$1760
    sta REG_LOW+$1786
    eor #$FF
    sta REG_LOW+$175B
    sta REG_LOW+$1763
    sta REG_LOW+$177F
    sta REG_LOW+$1789
    lda ZP_MAIN+$10
    sta REG_LOW+$1766
    sta REG_LOW+$1770
    sta REG_LOW+$178C
    sta REG_LOW+$1799
    eor #$FF
    sta REG_LOW+$176B
    sta REG_LOW+$1773
    sta REG_LOW+$1792
    sec
    ldx #$02
L2745:
    ldy ZP_MAIN+$17,x
    lda REG_TABLE+$2400,y
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$0E,x
    lda REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    adc REG_TABLE+$2400,y
    bcs L277D
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$11,x
    lda REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    adc REG_TABLE+$2400,y
    bcs L2790
L276A:
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$14,x
    lda REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    sta ZP_MAIN+$17,x
    dex
    bpl L2745
    jmp REG_LOW+$179E
L277D:
    clc
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$11,x
    lda #$01
    adc REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    adc REG_TABLE+$2400,y
    bcc L276A
L2790:
    clc
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$14,x
    lda #$01
    adc REG_TABLE+$2600,y
    jmp REG_LOW+$1772
    clc
    lda ZP_MAIN+$11
    adc ZP_MAIN+$0F
    sta ZP_MAIN+$0F
    lda ZP_MAIN+$14
    adc ZP_MAIN+$12
    sta REG_LOW+$17B7
    lda ZP_MAIN+$17
    adc ZP_MAIN+$15
    tay
    bcc L27B6
    clc
    inc ZP_MAIN+$18
L27B6:
    lda #$00
    adc ZP_MAIN+$10
    sta ZP_MAIN+$10
    tya
    adc ZP_MAIN+$13
    sta ZP_MAIN+$11
    lda ZP_MAIN+$18
    adc ZP_MAIN+$16
    sta ZP_MAIN+$12
    lda ZP_MAIN+$19
    adc #$00
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00
    sta REG_LOW+$185D
    sta REG_LOW+$1865
    eor #$FF
    sta REG_LOW+$1860
    sta REG_LOW+$1868
    lda ZP_MAIN+$02
    sta REG_LOW+$186B
    eor #$FF
    sta ZP_MAIN
    sta REG_LOW+$1876
    lda ZP_MAIN+$06
    sta REG_LOW+$1879
    eor #$FF
    sta ZP_MAIN+$04
    sta REG_LOW+$1884
    lda ZP_MAIN+$0A
    sta REG_LOW+$1887
    eor #$FF
    sta ZP_MAIN+$08
    sta REG_LOW+$1892
    ldx #$03
    sec
    bcs L285C
L2837:
    clc
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda #$01
    adc (ZP_MAIN+$02),y
    bcc L2875
L2842:
    clc
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda #$01
    adc (ZP_MAIN+$06),y
    bcc L2883
L284D:
    clc
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda #$01
    adc (ZP_MAIN+$0A),y
    bcc L2891
L2858:
    sta ZP_MAIN+$18,x
    ldy ZP_MAIN+$0C,x
L285C:
    lda REG_TABLE+$2C00,y
    adc REG_TABLE+$3000,y
    sta ZP_MAIN+$0C,x
    lda REG_TABLE+$2E00,y
    adc REG_TABLE+$3200,y
    adc REG_TABLE+$2C00,y
    bcs L2837
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda (ZP_MAIN+$02),y
L2875:
    adc REG_TABLE+$3200,y
    adc REG_TABLE+$2C00,y
    bcs L2842
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda (ZP_MAIN+$06),y
L2883:
    adc REG_TABLE+$3200,y
    adc REG_TABLE+$2C00,y
    bcs L284D
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda (ZP_MAIN+$0A),y
L2891:
    adc REG_TABLE+$3200,y
    dex
    bpl L2858
    tax
    ldy ZP_MAIN+$18
    clc
    lda ZP_MAIN+$1B
    adc ZP_MAIN+$0D
    sta ZP_MAIN+$0D
    lda ZP_MAIN+$1C
    adc ZP_MAIN+$0E
    bcc L28AC
    inc ZP_MAIN+$0F
    beq L28EB
    clc
L28AC:
    adc ZP_MAIN+$10
    sta ZP_MAIN+$0E
    lda ZP_MAIN+$11
    adc ZP_MAIN+$14
    bcc L28B8
    inx
    clc
L28B8:
    adc ZP_MAIN+$0F
    bcc L28C0
    inx
    beq L28FD
    clc
L28C0:
    adc ZP_MAIN+$1D
    sta ZP_MAIN+$0F
    txa
    adc ZP_MAIN+$15
    bcc L28CB
    iny
    clc
L28CB:
    adc ZP_MAIN+$1E
    bcc L28D3
    iny
    beq L290B
    clc
L28D3:
    adc ZP_MAIN+$12
    tax
    tya
    adc ZP_MAIN+$13
    bcc L28DE
    inc ZP_MAIN+$19
    clc
L28DE:
    adc ZP_MAIN+$16
    tay
    lda ZP_MAIN+$17
    adc ZP_MAIN+$19
    bcs L28E8
    rts
L28E8:
    inc ZP_MAIN+$1A
    rts
L28EB:
    inc ZP_MAIN+$1E
    bne L28F9
    inc ZP_MAIN+$13
    bne L28F9
    inc ZP_MAIN+$17
    bne L28F9
    inc ZP_MAIN+$1A
L28F9:
    clc
    jmp REG_LOW+$18AC
L28FD:
    inc ZP_MAIN+$13
    bne L2907
    inc ZP_MAIN+$17
    bne L2907
    inc ZP_MAIN+$1A
L2907:
    clc
    jmp REG_LOW+$18C0
L290B:
    inc ZP_MAIN+$17
    bne L2911
    inc ZP_MAIN+$1A
L2911:
    clc
    jmp REG_LOW+$18D3
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    sec
    rts
    lda V1_SCRATCH+$04
    ora V1_SCRATCH+$05
    ora V1_SCRATCH+$06
    ora V1_SCRATCH+$07
    bne L2A2E
    jsr REG_LOW+$1A00
    rts
L2A2E:
    lda V1_SCRATCH+$07
    beq L2A36
    jmp REG_LOW+$1B01
L2A36:
    lda V1_SCRATCH+$06
    beq L2A3E
    jmp REG_LOW+$1BFD
L2A3E:
    lda V1_SCRATCH+$05
    beq L2A46
    jmp REG_LOW+$1A99
L2A46:
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda V1_SCRATCH+$01
    sta MATH_IO+$19
    lda V1_SCRATCH+$02
    sta MATH_IO+$1A
    lda V1_SCRATCH+$03
    sta MATH_IO+$1B
    lda #$00
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$20
L2A6E:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1B
    rol MATH_IO+$1C
    bcs L2A87
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc L2A94
L2A87:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    inc MATH_IO+$18
L2A94:
    dex
    bne L2A6E
    clc
    rts
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda V1_SCRATCH+$01
    sta MATH_IO+$19
    lda V1_SCRATCH+$02
    sta MATH_IO+$1A
    lda #$00
    sta MATH_IO+$1B
    lda V1_SCRATCH+$03
    sta MATH_IO+$1C
    lda #$00
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$18
L2AC3:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    bcs L2AE6
    lda MATH_IO+$1D
    cmp V1_SCRATCH+$05
    bcc L2AFC
    bne L2AE6
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc L2AFC
L2AE6:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc V1_SCRATCH+$05
    sta MATH_IO+$1D
    inc MATH_IO+$18
L2AFC:
    dex
    bne L2AC3
    clc
    rts
    lda V1_SCRATCH+$03
    cmp V1_SCRATCH+$07
    bcc L2B47
    bne L2B6F
    lda V1_SCRATCH+$02
    cmp V1_SCRATCH+$06
    bcc L2B47
    bne L2B6F
    lda V1_SCRATCH+$01
    cmp V1_SCRATCH+$05
    bcc L2B47
    bne L2B6F
    lda V1_SCRATCH
    cmp V1_SCRATCH+$04
    bcc L2B47
    bne L2B6F
    lda #$01
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    clc
    rts
L2B47:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH
    sta MATH_IO+$1C
    lda V1_SCRATCH+$01
    sta MATH_IO+$1D
    lda V1_SCRATCH+$02
    sta MATH_IO+$1E
    lda V1_SCRATCH+$03
    sta MATH_IO+$1F
    clc
    rts
L2B6F:
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH+$01
    sta MATH_IO+$1C
    lda V1_SCRATCH+$02
    sta MATH_IO+$1D
    lda V1_SCRATCH+$03
    sta MATH_IO+$1E
    lda #$00
    sta MATH_IO+$1F
    ldx #$08
L2B99:
    asl MATH_IO+$18
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs L2BD0
    lda MATH_IO+$1F
    cmp V1_SCRATCH+$07
    bcc L2BF8
    bne L2BD0
    lda MATH_IO+$1E
    cmp V1_SCRATCH+$06
    bcc L2BF8
    bne L2BD0
    lda MATH_IO+$1D
    cmp V1_SCRATCH+$05
    bcc L2BF8
    bne L2BD0
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc L2BF8
L2BD0:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc V1_SCRATCH+$05
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc V1_SCRATCH+$06
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc V1_SCRATCH+$07
    sta MATH_IO+$1F
    inc MATH_IO+$18
L2BF8:
    dex
    bne L2B99
    clc
    rts
    lda V1_SCRATCH+$03
    cmp V1_SCRATCH+$07
    bcc L2C43
    bne L2C6B
    lda V1_SCRATCH+$02
    cmp V1_SCRATCH+$06
    bcc L2C43
    bne L2C6B
    lda V1_SCRATCH+$01
    cmp V1_SCRATCH+$05
    bcc L2C43
    bne L2C6B
    lda V1_SCRATCH
    cmp V1_SCRATCH+$04
    bcc L2C43
    bne L2C6B
    lda #$01
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    clc
    rts
L2C43:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH
    sta MATH_IO+$1C
    lda V1_SCRATCH+$01
    sta MATH_IO+$1D
    lda V1_SCRATCH+$02
    sta MATH_IO+$1E
    lda V1_SCRATCH+$03
    sta MATH_IO+$1F
    clc
    rts
L2C6B:
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda V1_SCRATCH+$01
    sta MATH_IO+$19
    lda #$00
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH+$02
    sta MATH_IO+$1C
    lda V1_SCRATCH+$03
    sta MATH_IO+$1D
    lda #$00
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$10
L2C95:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs L2CCF
    lda MATH_IO+$1F
    cmp V1_SCRATCH+$07
    bcc L2CF7
    bne L2CCF
    lda MATH_IO+$1E
    cmp V1_SCRATCH+$06
    bcc L2CF7
    bne L2CCF
    lda MATH_IO+$1D
    cmp V1_SCRATCH+$05
    bcc L2CF7
    bne L2CCF
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc L2CF7
L2CCF:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc V1_SCRATCH+$05
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc V1_SCRATCH+$06
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc V1_SCRATCH+$07
    sta MATH_IO+$1F
    inc MATH_IO+$18
L2CF7:
    dex
    bne L2C95
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00

; Source interval $3000-$3FFF
* = REG_API
    lda #>REG_TABLE+$2000
    sta ZP_MAIN+$0F
    lda #>REG_TABLE+$2200
    sta ZP_MAIN+$11
    ldx MATH_IO
    ldy MATH_IO+$04
    jsr REG_KERNEL+$0700
    sta MATH_IO+$09
    lda ZP_MAIN+$12
    sta MATH_IO+$08
    clc
    rts
    !byte $00, $00, $00, $00, $00
    jmp REG_KERNEL+$0800
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO
    sta ZP_MAIN+$0E
    lda MATH_IO+$01
    sta ZP_MAIN+$0F
    lda MATH_IO+$02
    sta ZP_MAIN+$10
    lda MATH_IO+$04
    sta ZP_MAIN+$17
    lda MATH_IO+$05
    sta ZP_MAIN+$18
    lda MATH_IO+$06
    sta ZP_MAIN+$19
    jsr REG_KERNEL+$0A00
    sta MATH_IO+$0D
    lda ZP_MAIN+$0E
    sta MATH_IO+$08
    lda ZP_MAIN+$0F
    sta MATH_IO+$09
    lda ZP_MAIN+$10
    sta MATH_IO+$0A
    lda ZP_MAIN+$11
    sta MATH_IO+$0B
    lda ZP_MAIN+$12
    sta MATH_IO+$0C
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00
    lda #>REG_TABLE+$3000
    sta ZP_MAIN+$01
    sta ZP_MAIN+$05
    sta ZP_MAIN+$09
    lda #>REG_TABLE+$2E00
    sta ZP_MAIN+$03
    sta ZP_MAIN+$07
    sta ZP_MAIN+$0B
    lda MATH_IO+$01
    sta ZP_MAIN+$02
    lda MATH_IO+$02
    sta ZP_MAIN+$06
    lda MATH_IO+$03
    sta ZP_MAIN+$0A
    lda MATH_IO+$04
    sta ZP_MAIN+$0C
    lda MATH_IO+$05
    sta ZP_MAIN+$0D
    lda MATH_IO+$06
    sta ZP_MAIN+$0E
    ldy MATH_IO+$07
    lda MATH_IO
    jsr REG_KERNEL+$0C00
    sta MATH_IO+$0E
    stx MATH_IO+$0C
    sty MATH_IO+$0D
    lda ZP_MAIN+$0C
    sta MATH_IO+$08
    lda ZP_MAIN+$0D
    sta MATH_IO+$09
    lda ZP_MAIN+$0E
    sta MATH_IO+$0A
    lda ZP_MAIN+$0F
    sta MATH_IO+$0B
    lda ZP_MAIN+$1A
    sta MATH_IO+$0F
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0E
    lda MATH_IO+$14
    sta ZP_MAIN+$0F
    jsr REG_KERNEL+$0006
    lda ZP_MAIN+$10
    sta MATH_IO+$18
    lda ZP_MAIN+$11
    sta MATH_IO+$1C
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0E
    lda MATH_IO+$11
    sta ZP_MAIN+$0F
    lda MATH_IO+$14
    sta ZP_MAIN+$10
    lda MATH_IO+$15
    sta ZP_MAIN+$11
    jsr REG_KERNEL+$0200
    lda ZP_MAIN+$12
    sta MATH_IO+$18
    lda ZP_MAIN+$13
    sta MATH_IO+$19
    lda ZP_MAIN+$14
    sta MATH_IO+$1C
    lda ZP_MAIN+$15
    sta MATH_IO+$1D
    rts
    !byte $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0E
    lda MATH_IO+$11
    sta ZP_MAIN+$0F
    lda MATH_IO+$12
    sta ZP_MAIN+$10
    lda MATH_IO+$14
    sta ZP_MAIN+$11
    lda MATH_IO+$15
    sta ZP_MAIN+$12
    lda MATH_IO+$16
    sta ZP_MAIN+$13
    jsr REG_KERNEL+$0300
    lda ZP_MAIN+$14
    sta MATH_IO+$18
    lda ZP_MAIN+$15
    sta MATH_IO+$19
    lda ZP_MAIN+$16
    sta MATH_IO+$1A
    lda ZP_MAIN+$17
    sta MATH_IO+$1C
    lda ZP_MAIN+$18
    sta MATH_IO+$1D
    lda ZP_MAIN+$19
    sta MATH_IO+$1E
    rts
    lda MATH_IO+$10
    sta ZP_MAIN+$16
    lda MATH_IO+$11
    sta ZP_MAIN+$17
    lda MATH_IO+$12
    sta ZP_MAIN+$0E
    lda MATH_IO+$13
    sta ZP_MAIN+$0F
    lda MATH_IO+$14
    sta ZP_MAIN+$10
    lda MATH_IO+$15
    sta ZP_MAIN+$11
    jsr REG_KERNEL+$0500
    lda ZP_MAIN+$18
    sta MATH_IO+$18
    lda ZP_MAIN+$19
    sta MATH_IO+$19
    lda ZP_MAIN+$12
    sta MATH_IO+$1A
    lda ZP_MAIN+$13
    sta MATH_IO+$1B
    lda ZP_MAIN+$14
    sta MATH_IO+$1C
    lda ZP_MAIN+$15
    sta MATH_IO+$1D
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0E
    lda MATH_IO+$14
    sta ZP_MAIN+$0F
    jsr REG_KERNEL+$0612
    sta MATH_IO+$1C
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_API+$0140
    jmp REG_API+$0170
    jmp REG_API+$01B0
    !byte $00, $00, $00, $00, $00, $00, $00, $AD, $08, $C0, $8D, $10, $C0, $AD, $09, $C0
    !byte $8D, $11, $C0, $A9, $00, $8D, $12, $C0, $8D, $13, $C0, $60, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $A2, $03, $BD, $08, $C0, $9D, $10, $C0, $CA
    !byte $10, $F7, $60, $00, $00, $00, $00, $A2, $03, $BD, $18, $C0, $9D, $00, $C0, $CA
    !byte $10, $F7, $60, $00, $00, $00, $00, $AD, $1C, $C0, $8D, $00, $C0, $AD, $1D, $C0
    !byte $8D, $01, $C0, $60, $00, $00, $00
    lda #>REG_TABLE+$3000
    sta ZP_MAIN+$01
    sta ZP_MAIN+$05
    sta ZP_MAIN+$09
    lda #>REG_TABLE+$2E00
    sta ZP_MAIN+$03
    sta ZP_MAIN+$07
    sta ZP_MAIN+$0B
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $20, $20
    !byte $30, $20, $50, $32, $4C, $B0, $31, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $20, $40
    !byte $31, $B0, $1B, $AD, $18, $C0, $8D, $00, $C0, $AD, $19, $C0, $8D, $01, $C0, $AD
    !byte $14, $C0, $8D, $04, $C0, $AD, $15, $C0, $8D, $05, $C0, $20, $20, $30, $60, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $20, $70
    !byte $31, $B0, $27, $AD, $18, $C0, $8D, $00, $C0, $AD, $19, $C0, $8D, $01, $C0, $AD
    !byte $1A, $C0, $8D, $02, $C0, $AD, $14, $C0, $8D, $04, $C0, $AD, $15, $C0, $8D, $05
    !byte $C0, $AD, $16, $C0, $8D, $06, $C0, $20, $60, $30, $60, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $20, $B0
    !byte $31, $B0, $2F, $AD, $18, $C0, $8D, $00, $C0, $AD, $19, $C0, $8D, $01, $C0, $AD
    !byte $1A, $C0, $8D, $02, $C0, $AD, $1B, $C0, $8D, $03, $C0, $AD, $14, $C0, $8D, $04
    !byte $C0, $AD, $15, $C0, $8D, $05, $C0, $A9, $00, $8D, $06, $C0, $8D, $07, $C0, $20
    !byte $B0, $30, $60, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1000
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1100
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1200
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1300
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1500
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1520
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1550
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_LOW+$1590
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00
    jmp REG_API+$0CA0
    jmp REG_API+$0D20
    jmp REG_API+$0DE0
    jmp REG_API+$0EE0
    jmp REG_LOW+$1310
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

; Source interval $4000-$5DFF
* = REG_KERNEL
L4000:
    sta ZP_MAIN+$10
    sta ZP_MAIN+$11
    sec
    rts
    lda ZP_MAIN+$0F
    beq L4000
    lda ZP_MAIN+$0E
    cmp ZP_MAIN+$0F
    bcs L4017
    sta ZP_MAIN+$11
    lda #$00
    sta ZP_MAIN+$10
    rts
L4017:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4024
    sta ZP_MAIN+$11
    lda #$01
    sta ZP_MAIN+$10
    rts
L4024:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4031
    sta ZP_MAIN+$11
    lda #$02
    sta ZP_MAIN+$10
    rts
L4031:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L403E
    sta ZP_MAIN+$11
    lda #$03
    sta ZP_MAIN+$10
    rts
L403E:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L404B
    sta ZP_MAIN+$11
    lda #$04
    sta ZP_MAIN+$10
    rts
L404B:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4058
    sta ZP_MAIN+$11
    lda #$05
    sta ZP_MAIN+$10
    rts
L4058:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4065
    sta ZP_MAIN+$11
    lda #$06
    sta ZP_MAIN+$10
    rts
L4065:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4072
    sta ZP_MAIN+$11
    lda #$07
    sta ZP_MAIN+$10
    rts
L4072:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L407F
    sta ZP_MAIN+$11
    lda #$08
    sta ZP_MAIN+$10
    rts
L407F:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L408C
    sta ZP_MAIN+$11
    lda #$09
    sta ZP_MAIN+$10
    rts
L408C:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4099
    sta ZP_MAIN+$11
    lda #$0A
    sta ZP_MAIN+$10
    rts
L4099:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L40A6
    sta ZP_MAIN+$11
    lda #$0B
    sta ZP_MAIN+$10
    rts
L40A6:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L40B3
    sta ZP_MAIN+$11
    lda #$0C
    sta ZP_MAIN+$10
    rts
L40B3:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L40C0
    sta ZP_MAIN+$11
    lda #$0D
    sta ZP_MAIN+$10
    rts
L40C0:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L40CD
    sta ZP_MAIN+$11
    lda #$0E
    sta ZP_MAIN+$10
    rts
L40CD:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L40DA
    sta ZP_MAIN+$11
    lda #$0F
    sta ZP_MAIN+$10
    rts
L40DA:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L40E7
    sta ZP_MAIN+$11
    lda #$10
    sta ZP_MAIN+$10
    rts
L40E7:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L40F4
    sta ZP_MAIN+$11
    lda #$11
    sta ZP_MAIN+$10
    rts
L40F4:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4101
    sta ZP_MAIN+$11
    lda #$12
    sta ZP_MAIN+$10
    rts
L4101:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L410E
    sta ZP_MAIN+$11
    lda #$13
    sta ZP_MAIN+$10
    rts
L410E:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L411B
    sta ZP_MAIN+$11
    lda #$14
    sta ZP_MAIN+$10
    rts
L411B:
    sta ZP_MAIN+$11
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$12
    ldx #$00
    stx ZP_MAIN+$10
L4125:
    lda ZP_MAIN+$12
    asl
    bcs L4130
    cmp ZP_MAIN+$11
    bcc L4149
    beq L4149
L4130:
    lda ZP_MAIN+$11
L4132:
    cmp ZP_MAIN+$12
    bcc L4138
    sbc ZP_MAIN+$12
L4138:
    rol ZP_MAIN+$10
    lsr ZP_MAIN+$12
    dex
    bpl L4132
    sta ZP_MAIN+$11
    lda ZP_MAIN+$10
    clc
    adc #$14
    sta ZP_MAIN+$10
    rts
L4149:
    sta ZP_MAIN+$12
    inx
    bne L4125
    brk
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00
    !byte $A7, ZP_MAIN+$0F    ; LAX zp
    cmp ZP_MAIN+$11
    bcs L4213
L4206:
    lda #$00
    sta ZP_MAIN+$12
    sta ZP_MAIN+$13
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$14
    stx ZP_MAIN+$15
    rts
L4213:
    bne L423F
    lda ZP_MAIN+$0E
    sbc ZP_MAIN+$10
    bcc L4206
    sta ZP_MAIN+$14
    txa
    bne L4234
    lda ZP_MAIN+$10
    beq L422A
    stx ZP_MAIN+$15
    ldx #$FC
    bcs L4286
L422A:
    stx ZP_MAIN+$12
    stx ZP_MAIN+$13
    stx ZP_MAIN+$14
    stx ZP_MAIN+$15
    sec
    rts
L4234:
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$15
    sta ZP_MAIN+$13
    lda #$01
    sta ZP_MAIN+$12
    rts
L423F:
    lda ZP_MAIN+$0E
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L4256
    bne L426C
    tax
    lda ZP_MAIN+$14
    cmp ZP_MAIN+$10
    bcs L426B
    txa
L4256:
    sta ZP_MAIN+$15
    lda #$00
    sta ZP_MAIN+$13
    lda #$01
    sta ZP_MAIN+$12
    rts
L4261:
    txa
    adc #$05
    sta ZP_MAIN+$12
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$13
    rts
L426B:
    txa
L426C:
    ldx ZP_MAIN+$11
    bne L4274
    ldx ZP_MAIN+$10
    beq L422A
L4274:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$15
    cmp ZP_MAIN+$11
    bcc L42F6
    ldx #$FD
L4286:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc L4261
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inx
    bmi L4286
    cmp ZP_MAIN+$11
    bcc L4261
    bne L42A4
    lda ZP_MAIN+$14
    cmp ZP_MAIN+$10
    bcc L4261
L42A4:
    lda ZP_MAIN+$10
    sta ZP_MAIN+$16
    lda ZP_MAIN+$11
    sta ZP_MAIN+$17
    stx ZP_MAIN+$12
    stx ZP_MAIN+$13
    ldy ZP_MAIN+$15
L42B2:
    asl ZP_MAIN+$16
    rol ZP_MAIN+$17
    cpy ZP_MAIN+$17
    bcc L42CA
    bne L42C2
    lda ZP_MAIN+$14
    cmp ZP_MAIN+$16
    bcc L42CA
L42C2:
    inx
    bit ZP_MAIN+$17
    bpl L42B2
    inx
    bpl L42CF
L42CA:
    lsr ZP_MAIN+$17
    inx
L42CD:
    ror ZP_MAIN+$16
L42CF:
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$16
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$17
    bcc L42DF
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
L42DF:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$13
    dex
    beq L42EA
    lsr ZP_MAIN+$17
    bpl L42CD
L42EA:
    lda #$05
    adc ZP_MAIN+$12
    sta ZP_MAIN+$12
    bcc L42F5
    inc ZP_MAIN+$13
    clc
L42F5:
    rts
L42F6:
    lda #$02
    sta ZP_MAIN+$12
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$13
    rts
    !byte $00
    lda ZP_MAIN+$11
    ora ZP_MAIN+$12
    ora ZP_MAIN+$13
    bne L4311
    ldx #$05
L430A:
    sta ZP_MAIN+$14,x
    dex
    bpl L430A
    sec
    rts
L4311:
    !byte $A7, ZP_MAIN+$10    ; LAX zp
    cmp ZP_MAIN+$13
    bcc L4327
    bne L433A
    lda ZP_MAIN+$0F
    cmp ZP_MAIN+$12
    bcc L4327
    bne L433A
    lda ZP_MAIN+$0E
    cmp ZP_MAIN+$11
    bcs L433A
L4327:
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    sta ZP_MAIN+$16
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$17
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$18
    stx ZP_MAIN+$19
    rts
L433A:
    lda ZP_MAIN+$0E
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$0F
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    txa
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    ldx #$00
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4364
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    tay
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$15
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    bcs L436D
L4364:
    lda #$01
L4366:
    sta ZP_MAIN+$14
    stx ZP_MAIN+$15
    stx ZP_MAIN+$16
    rts
L436D:
    sta ZP_MAIN+$19
    sty ZP_MAIN+$17
    lda ZP_MAIN+$15
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcs L437F
    lda #$02
    bne L4366
L437F:
    lda ZP_MAIN+$11
    sta ZP_MAIN+$1A
    lda ZP_MAIN+$12
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$13
    sta ZP_MAIN+$1C
    stx ZP_MAIN+$14
    stx ZP_MAIN+$15
    stx ZP_MAIN+$16
L4391:
    asl ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    rol ZP_MAIN+$1C
    bcs L43B2
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$1C
    bcc L43B2
    bne L43AF
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1B
    bcc L43B2
    bne L43AF
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$1A
    bcc L43B2
L43AF:
    inx
    bne L4391
L43B2:
    ror ZP_MAIN+$1C
    ror ZP_MAIN+$1B
    ror ZP_MAIN+$1A
L43B8:
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$1C
    bcc L43E0
    bne L43CE
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1B
    bcc L43E0
    bne L43CE
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$1A
    bcc L43E0
L43CE:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$1A
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$1B
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$1C
    sta ZP_MAIN+$19
L43E0:
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    rol ZP_MAIN+$16
    lsr ZP_MAIN+$1C
    ror ZP_MAIN+$1B
    ror ZP_MAIN+$1A
    dex
    bpl L43B8
    lda ZP_MAIN+$14
    clc
    adc #$02
    sta ZP_MAIN+$14
    bcc L43FF
    inc ZP_MAIN+$15
    bne L43FE
    inc ZP_MAIN+$16
L43FE:
    clc
L43FF:
    rts
    !byte $A7, ZP_MAIN+$0F    ; LAX zp
    cmp ZP_MAIN+$11
    bcc L446F
    lda ZP_MAIN+$11
    beq L4435
    cmp #$05
    bcc L4442
    lda ZP_MAIN+$0E
    sbc ZP_MAIN+$10
    tay
    txa
    sbc ZP_MAIN+$11
    bcc L446F
    ldx #$00
L441A:
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inx
    cmp ZP_MAIN+$11
    bcc L442E
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcs L441A
L442E:
    stx ZP_MAIN+$12
    lda #$00
    sta ZP_MAIN+$13
    rts
L4435:
    lda ZP_MAIN+$10
    bne L4442
    ldx #$03
L443B:
    sta ZP_MAIN+$12,x
    dex
    bpl L443B
    sec
    rts
L4442:
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$12
    stx ZP_MAIN+$13
    lda #$00
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    ldx #$10
L4450:
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc L446A
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
L446A:
    dex
    bne L4450
    clc
    rts
L446F:
    stx ZP_MAIN+$15
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$14
    lda #$00
    sta ZP_MAIN+$12
    sta ZP_MAIN+$13
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00
    jsr REG_KERNEL+$0400
    bcc L450C
    lda #$00
    sta ZP_MAIN+$18
    sta ZP_MAIN+$19
    rts
L450C:
    lda ZP_MAIN+$16
    sta ZP_MAIN+$18
    lda ZP_MAIN+$17
    sta ZP_MAIN+$19
    lda ZP_MAIN+$15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4537
    cmp ZP_MAIN+$11
    bcc L4542
    bne L452B
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc L4542
L452B:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs L4542
L4537:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
L4542:
    ldx #$0F
L4544:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4565
    cmp ZP_MAIN+$11
    bcc L4570
    bne L4559
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc L4570
L4559:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs L4570
L4565:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
L4570:
    dex
    bne L4544
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    sta ZP_MAIN+$15
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00
L4600:
    cpx #$01
    bcc L460E
    beq L460A
    and #$01
    clc
    rts
L460A:
    lda #$00
    clc
    rts
L460E:
    lda #$00
    sec
    rts
    lda ZP_MAIN+$0E
    ldx ZP_MAIN+$0F
    cpx #$03
    bcc L4600
    cmp ZP_MAIN+$0F
    bcs L461F
    rts
L461F:
    sbc ZP_MAIN+$0F
    cmp ZP_MAIN+$0F
    bcs L4626
    rts
L4626:
    sbc ZP_MAIN+$0F
    sbc ZP_MAIN+$0F
    bcc L463E
    sbc ZP_MAIN+$0F
    bcc L463E
    stx REG_KERNEL+$0637
    stx REG_KERNEL+$063B
L4636:
    sbc #$00
    bcs L4636
    adc #$00
    clc
    rts
L463E:
    adc ZP_MAIN+$0F
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    sec
    stx ZP_MAIN+$0E
    stx ZP_MAIN+$10
    tya
    sbc ZP_MAIN+$0E
    bcs L470E
    sbc #$00
    eor #$FF
L470E:
    tax
    lda (ZP_MAIN+$0E),y
    sbc REG_TABLE+$2000,x
    sta ZP_MAIN+$12
    lda (ZP_MAIN+$10),y
    sbc REG_TABLE+$2200,x
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00
    lda #>REG_TABLE+$2000
    sta ZP_MAIN+$0F
    lda #>REG_TABLE+$2200
    sta ZP_MAIN+$11
    lda #$00
    sta MATH_IO+$08
    sta MATH_IO+$09
    sta MATH_IO+$0A
    sta MATH_IO+$0B
    ldx MATH_IO
    ldy MATH_IO+$04
    jsr REG_KERNEL+$0700
    sta MATH_IO+$09
    lda ZP_MAIN+$12
    sta MATH_IO+$08
    ldx MATH_IO
    ldy MATH_IO+$05
    jsr REG_KERNEL+$0700
    sta ZP_MAIN+$16
    lda ZP_MAIN+$12
    clc
    adc MATH_IO+$09
    sta MATH_IO+$09
    lda ZP_MAIN+$16
    adc MATH_IO+$0A
    sta MATH_IO+$0A
    bcc L4848
    inc MATH_IO+$0B
L4848:
    ldx MATH_IO+$01
    ldy MATH_IO+$04
    jsr REG_KERNEL+$0700
    sta ZP_MAIN+$16
    lda ZP_MAIN+$12
    clc
    adc MATH_IO+$09
    sta MATH_IO+$09
    lda ZP_MAIN+$16
    adc MATH_IO+$0A
    sta MATH_IO+$0A
    bcc L4869
    inc MATH_IO+$0B
L4869:
    ldx MATH_IO+$01
    ldy MATH_IO+$05
    jsr REG_KERNEL+$0700
    sta ZP_MAIN+$16
    lda ZP_MAIN+$12
    clc
    adc MATH_IO+$0A
    sta MATH_IO+$0A
    lda ZP_MAIN+$16
    adc MATH_IO+$0B
    sta MATH_IO+$0B
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda ZP_MAIN+$0E
    sta REG_KERNEL+$0A48
    sta REG_KERNEL+$0A50
    eor #$FF
    sta REG_KERNEL+$0A4B
    sta REG_KERNEL+$0A53
    lda ZP_MAIN+$0F
    sta REG_KERNEL+$0A56
    sta REG_KERNEL+$0A60
    sta REG_KERNEL+$0A86
    eor #$FF
    sta REG_KERNEL+$0A5B
    sta REG_KERNEL+$0A63
    sta REG_KERNEL+$0A7F
    sta REG_KERNEL+$0A89
    lda ZP_MAIN+$10
    sta REG_KERNEL+$0A66
    sta REG_KERNEL+$0A70
    sta REG_KERNEL+$0A8C
    sta REG_KERNEL+$0A99
    eor #$FF
    sta REG_KERNEL+$0A6B
    sta REG_KERNEL+$0A73
    sta REG_KERNEL+$0A92
    sec
    ldx #$02
L4A45:
    ldy ZP_MAIN+$17,x
    lda REG_TABLE+$2400,y
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$0E,x
    lda REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    adc REG_TABLE+$2400,y
    bcs L4A7D
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$11,x
    lda REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    adc REG_TABLE+$2400,y
    bcs L4A90
L4A6A:
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$14,x
    lda REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    sta ZP_MAIN+$17,x
    dex
    bpl L4A45
    jmp REG_KERNEL+$0A9E
L4A7D:
    clc
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$11,x
    lda #$01
    adc REG_TABLE+$2600,y
    adc REG_TABLE+$2A00,y
    adc REG_TABLE+$2400,y
    bcc L4A6A
L4A90:
    clc
    adc REG_TABLE+$2800,y
    sta ZP_MAIN+$14,x
    lda #$01
    adc REG_TABLE+$2600,y
    jmp REG_KERNEL+$0A72
    clc
    lda ZP_MAIN+$11
    adc ZP_MAIN+$0F
    sta ZP_MAIN+$0F
    lda ZP_MAIN+$14
    adc ZP_MAIN+$12
    sta REG_KERNEL+$0AB7
    lda ZP_MAIN+$17
    adc ZP_MAIN+$15
    tay
    bcc L4AB6
    clc
    inc ZP_MAIN+$18
L4AB6:
    lda #$00
    adc ZP_MAIN+$10
    sta ZP_MAIN+$10
    tya
    adc ZP_MAIN+$13
    sta ZP_MAIN+$11
    lda ZP_MAIN+$18
    adc ZP_MAIN+$16
    sta ZP_MAIN+$12
    lda ZP_MAIN+$19
    adc #$00
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00
    sta REG_KERNEL+$0C5D
    sta REG_KERNEL+$0C65
    eor #$FF
    sta REG_KERNEL+$0C60
    sta REG_KERNEL+$0C68
    lda ZP_MAIN+$02
    sta REG_KERNEL+$0C6B
    eor #$FF
    sta ZP_MAIN
    sta REG_KERNEL+$0C76
    lda ZP_MAIN+$06
    sta REG_KERNEL+$0C79
    eor #$FF
    sta ZP_MAIN+$04
    sta REG_KERNEL+$0C84
    lda ZP_MAIN+$0A
    sta REG_KERNEL+$0C87
    eor #$FF
    sta ZP_MAIN+$08
    sta REG_KERNEL+$0C92
    ldx #$03
    sec
    bcs L4C5C
L4C37:
    clc
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda #$01
    adc (ZP_MAIN+$02),y
    bcc L4C75
L4C42:
    clc
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda #$01
    adc (ZP_MAIN+$06),y
    bcc L4C83
L4C4D:
    clc
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda #$01
    adc (ZP_MAIN+$0A),y
    bcc L4C91
L4C58:
    sta ZP_MAIN+$18,x
    ldy ZP_MAIN+$0C,x
L4C5C:
    lda REG_TABLE+$2C00,y
    adc REG_TABLE+$3000,y
    sta ZP_MAIN+$0C,x
    lda REG_TABLE+$2E00,y
    adc REG_TABLE+$3200,y
    adc REG_TABLE+$2C00,y
    bcs L4C37
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda (ZP_MAIN+$02),y
L4C75:
    adc REG_TABLE+$3200,y
    adc REG_TABLE+$2C00,y
    bcs L4C42
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda (ZP_MAIN+$06),y
L4C83:
    adc REG_TABLE+$3200,y
    adc REG_TABLE+$2C00,y
    bcs L4C4D
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda (ZP_MAIN+$0A),y
L4C91:
    adc REG_TABLE+$3200,y
    dex
    bpl L4C58
    tax
    ldy ZP_MAIN+$18
    clc
    lda ZP_MAIN+$1B
    adc ZP_MAIN+$0D
    sta ZP_MAIN+$0D
    lda ZP_MAIN+$1C
    adc ZP_MAIN+$0E
    bcc L4CAC
    inc ZP_MAIN+$0F
    beq L4CEB
    clc
L4CAC:
    adc ZP_MAIN+$10
    sta ZP_MAIN+$0E
    lda ZP_MAIN+$11
    adc ZP_MAIN+$14
    bcc L4CB8
    inx
    clc
L4CB8:
    adc ZP_MAIN+$0F
    bcc L4CC0
    inx
    beq L4CFD
    clc
L4CC0:
    adc ZP_MAIN+$1D
    sta ZP_MAIN+$0F
    txa
    adc ZP_MAIN+$15
    bcc L4CCB
    iny
    clc
L4CCB:
    adc ZP_MAIN+$1E
    bcc L4CD3
    iny
    beq L4D0B
    clc
L4CD3:
    adc ZP_MAIN+$12
    tax
    tya
    adc ZP_MAIN+$13
    bcc L4CDE
    inc ZP_MAIN+$19
    clc
L4CDE:
    adc ZP_MAIN+$16
    tay
    lda ZP_MAIN+$17
    adc ZP_MAIN+$19
    bcs L4CE8
    rts
L4CE8:
    inc ZP_MAIN+$1A
    rts
L4CEB:
    inc ZP_MAIN+$1E
    bne L4CF9
    inc ZP_MAIN+$13
    bne L4CF9
    inc ZP_MAIN+$17
    bne L4CF9
    inc ZP_MAIN+$1A
L4CF9:
    clc
    jmp REG_KERNEL+$0CAC
L4CFD:
    inc ZP_MAIN+$13
    bne L4D07
    inc ZP_MAIN+$17
    bne L4D07
    inc ZP_MAIN+$1A
L4D07:
    clc
    jmp REG_KERNEL+$0CC0
L4D0B:
    inc ZP_MAIN+$17
    bne L4D11
    inc ZP_MAIN+$1A
L4D11:
    clc
    jmp REG_KERNEL+$0CD3
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
L5000:
    sta ZP_MAIN+$0F
    sta ZP_MAIN+$10
    sec
    rts
    lda ZP_MAIN+$0D
    beq L5000
    bpl L5011
    eor #$FF
    clc
    adc #$01
L5011:
    sta ZP_MAIN+$0E
    lda ZP_MAIN+$0C
    bpl L501C
    eor #$FF
    clc
    adc #$01
L501C:
    cmp ZP_MAIN+$0E
    bcs L5033
    sta ZP_MAIN+$10
    lda #$00
    sta ZP_MAIN+$0F
    bit ZP_MAIN+$0C
    bmi L502C
    clc
    rts
L502C:
    sec
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$10
    clc
    rts
L5033:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5062
    sta ZP_MAIN+$10
    lda #$01
    sta ZP_MAIN+$0F
    bit ZP_MAIN+$0C
    bmi L504F
    bit ZP_MAIN+$0D
    bmi L5049
    clc
    rts
L5049:
    lda #$FF
    sta ZP_MAIN+$0F
    clc
    rts
L504F:
    lda #$00
    sec
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$10
    bit ZP_MAIN+$0D
    bpl L505C
    clc
    rts
L505C:
    lda #$FF
    sta ZP_MAIN+$0F
    clc
    rts
L5062:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5071
    sta ZP_MAIN+$10
    lda #$02
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5071:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5080
    sta ZP_MAIN+$10
    lda #$03
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5080:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L508F
    sta ZP_MAIN+$10
    lda #$04
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L508F:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L509E
    sta ZP_MAIN+$10
    lda #$05
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L509E:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L50AD
    sta ZP_MAIN+$10
    lda #$06
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L50AD:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L50BC
    sta ZP_MAIN+$10
    lda #$07
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L50BC:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L50CB
    sta ZP_MAIN+$10
    lda #$08
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L50CB:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L50DA
    sta ZP_MAIN+$10
    lda #$09
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L50DA:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L50E9
    sta ZP_MAIN+$10
    lda #$0A
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L50E9:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L50F8
    sta ZP_MAIN+$10
    lda #$0B
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L50F8:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5107
    sta ZP_MAIN+$10
    lda #$0C
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5107:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5116
    sta ZP_MAIN+$10
    lda #$0D
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5116:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5125
    sta ZP_MAIN+$10
    lda #$0E
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5125:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5134
    sta ZP_MAIN+$10
    lda #$0F
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5134:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5143
    sta ZP_MAIN+$10
    lda #$10
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5143:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5152
    sta ZP_MAIN+$10
    lda #$11
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5152:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5161
    sta ZP_MAIN+$10
    lda #$12
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5161:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L5170
    sta ZP_MAIN+$10
    lda #$13
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L5170:
    sbc ZP_MAIN+$0E
    cmp ZP_MAIN+$0E
    bcs L517F
    sta ZP_MAIN+$10
    lda #$14
    sta ZP_MAIN+$0F
    jmp REG_KERNEL+$11A8
L517F:
    sta ZP_MAIN+$10
    ldx #$00
    stx ZP_MAIN+$0F
L5185:
    lda ZP_MAIN+$0E
    asl
    bcs L5190
    cmp ZP_MAIN+$10
    bcc L51C5
    beq L51C5
L5190:
    lda ZP_MAIN+$10
L5192:
    cmp ZP_MAIN+$0E
    bcc L5198
    sbc ZP_MAIN+$0E
L5198:
    rol ZP_MAIN+$0F
    lsr ZP_MAIN+$0E
    dex
    bpl L5192
    sta ZP_MAIN+$10
    lda ZP_MAIN+$0F
    clc
    adc #$14
    sta ZP_MAIN+$0F
    lda ZP_MAIN+$0C
    bmi L51B1
    eor ZP_MAIN+$0D
    bmi L51BC
    rts
L51B1:
    lda #$00
    sec
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$10
    lda ZP_MAIN+$0D
    bmi L51C3
L51BC:
    lda #$00
    sec
    sbc ZP_MAIN+$0F
    sta ZP_MAIN+$0F
L51C3:
    clc
    rts
L51C5:
    sta ZP_MAIN+$0E
    inx
    bne L5185
    brk
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00
    !byte $A7, ZP_MAIN+$0F    ; LAX zp
    beq L520F
    bmi L521D
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$12
    stx ZP_MAIN+$13
    jmp REG_KERNEL+$122A
L520F:
    lda ZP_MAIN+$0E
    bne L5216
    jmp REG_KERNEL+$12AF
L5216:
    sta ZP_MAIN+$12
    stx ZP_MAIN+$13
    jmp REG_KERNEL+$122A
L521D:
    lda #$00
    sec
    sbc ZP_MAIN+$0E
    sta ZP_MAIN+$12
    lda #$00
    sbc ZP_MAIN+$0F
    sta ZP_MAIN+$13
    !byte $A7, ZP_MAIN+$0D    ; LAX zp
    bmi L5237
    lda ZP_MAIN+$0C
    sta ZP_MAIN+$10
    stx ZP_MAIN+$11
    jmp REG_KERNEL+$1244
L5237:
    lda #$00
    sec
    sbc ZP_MAIN+$0C
    sta ZP_MAIN+$10
    lda #$00
    sbc ZP_MAIN+$0D
    sta ZP_MAIN+$11
    !byte $A7, ZP_MAIN+$11    ; LAX zp
    cmp ZP_MAIN+$13
    bcc L5271
    bne L5252
    lda ZP_MAIN+$10
    cmp ZP_MAIN+$12
    bcc L5271
L5252:
    lda ZP_MAIN+$10
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$16
    txa
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$17
    cmp ZP_MAIN+$13
    bcc L5281
    bne L5269
    lda ZP_MAIN+$16
    cmp ZP_MAIN+$12
    bcc L5281
L5269:
    lda ZP_MAIN+$17
    jsr REG_KERNEL+$146C
    jmp REG_KERNEL+$1289
L5271:
    lda #$00
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    lda ZP_MAIN+$0C
    sta ZP_MAIN+$16
    lda ZP_MAIN+$0D
    sta ZP_MAIN+$17
    clc
    rts
L5281:
    lda #$01
    sta ZP_MAIN+$14
    lda #$00
    sta ZP_MAIN+$15
    lda ZP_MAIN+$0D
    bpl L529A
    lda #$00
    sec
    sbc ZP_MAIN+$16
    sta ZP_MAIN+$16
    lda #$00
    sbc ZP_MAIN+$17
    sta ZP_MAIN+$17
L529A:
    lda ZP_MAIN+$0D
    eor ZP_MAIN+$0F
    bpl L52AD
    lda #$00
    sec
    sbc ZP_MAIN+$14
    sta ZP_MAIN+$14
    lda #$00
    sbc ZP_MAIN+$15
    sta ZP_MAIN+$15
L52AD:
    clc
    rts
    lda #$00
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    sta ZP_MAIN+$16
    sta ZP_MAIN+$17
    sec
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $A7, $13, $C5, $15, $B0, $0D, $A9, $00, $85, $16, $85
    !byte $17, $A5, $12, $85, $18, $86, $19, $60, $D0, $2A, $A5, $12, $E5, $14, $90, $EB
    !byte $85, $18, $8A, $D0, $14, $A5, $14, $F0, $06, $86, $19, $A2, $FC, $B0, $5C
L542A:
    stx ZP_MAIN+$14
    stx ZP_MAIN+$15
    stx ZP_MAIN+$16
    stx ZP_MAIN+$17
    sec
    rts
    !byte $0B, $00, $85, $19, $85, $17, $A9, $01, $85, $16, $60, $A5, $12, $E5, $14, $85
    !byte $18, $8A, $E5, $15, $C5, $15, $90, $0A, $D0, $1E, $AA, $A5, $18, $C5, $14, $B0
    !byte $16, $8A, $85, $19, $A9, $00, $85, $17, $A9, $01, $85, $16, $60
L5461:
    txa
    adc #$05
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$15
    rts
    !byte $8A
    ldx ZP_MAIN+$13
    bne L5474
    ldx ZP_MAIN+$12
    beq L542A
L5474:
    tay
    lda ZP_MAIN+$16
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$16
    tya
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$17
    cmp ZP_MAIN+$13
    bcc L54F6
    ldx #$FD
L5486:
    lda ZP_MAIN+$16
    sbc ZP_MAIN+$12
    tay
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$13
    bcc L5461
    sta ZP_MAIN+$17
    sty ZP_MAIN+$16
    inx
    bmi L5486
    cmp ZP_MAIN+$13
    bcc L5461
    bne L54A4
    lda ZP_MAIN+$16
    cmp ZP_MAIN+$12
    bcc L5461
L54A4:
    lda ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$13
    sta ZP_MAIN+$19
    stx ZP_MAIN+$14
    stx ZP_MAIN+$15
    ldy ZP_MAIN+$17
L54B2:
    asl ZP_MAIN+$18
    rol ZP_MAIN+$19
    cpy ZP_MAIN+$19
    bcc L54CA
    bne L54C2
    lda ZP_MAIN+$16
    cmp ZP_MAIN+$18
    bcc L54CA
L54C2:
    inx
    bit ZP_MAIN+$19
    bpl L54B2
    inx
    bpl L54CF
L54CA:
    lsr ZP_MAIN+$19
    inx
L54CD:
    ror ZP_MAIN+$18
L54CF:
    sec
    lda ZP_MAIN+$16
    sbc ZP_MAIN+$18
    tay
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$19
    bcc L54DF
    sta ZP_MAIN+$17
    sty ZP_MAIN+$16
L54DF:
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    dex
    beq L54EA
    lsr ZP_MAIN+$19
    bpl L54CD
L54EA:
    lda #$05
    adc ZP_MAIN+$14
    sta ZP_MAIN+$14
    bcc L54F5
    inc ZP_MAIN+$15
    clc
L54F5:
    rts
L54F6:
    lda #$02
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$15
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00
    lda ZP_MAIN+$0F
    ora ZP_MAIN+$10
    ora ZP_MAIN+$11
    bne L5618
    lda #$00
    sta ZP_MAIN+$18
    sta ZP_MAIN+$19
    sta ZP_MAIN+$1A
    sta ZP_MAIN+$1B
    sta ZP_MAIN+$1C
    sta ZP_MAIN+$1D
    sec
    rts
L5618:
    lda ZP_MAIN+$11
    bmi L562A
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$15
    lda ZP_MAIN+$10
    sta ZP_MAIN+$16
    lda ZP_MAIN+$11
    sta ZP_MAIN+$17
    bpl L563D
L562A:
    lda #$00
    sec
    sbc ZP_MAIN+$0F
    sta ZP_MAIN+$15
    lda #$00
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$16
    lda #$00
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
L563D:
    lda ZP_MAIN+$0E
    bmi L564F
    lda ZP_MAIN+$0C
    sta ZP_MAIN+$12
    lda ZP_MAIN+$0D
    sta ZP_MAIN+$13
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$14
    bpl L5662
L564F:
    lda #$00
    sec
    sbc ZP_MAIN+$0C
    sta ZP_MAIN+$12
    lda #$00
    sbc ZP_MAIN+$0D
    sta ZP_MAIN+$13
    lda #$00
    sbc ZP_MAIN+$0E
    sta ZP_MAIN+$14
L5662:
    lda ZP_MAIN+$14
    cmp ZP_MAIN+$17
    bcc L56CD
    bne L5678
    lda ZP_MAIN+$13
    cmp ZP_MAIN+$16
    bcc L56CD
    bne L5678
    lda ZP_MAIN+$12
    cmp ZP_MAIN+$15
    bcc L56CD
L5678:
    lda ZP_MAIN+$17
    beq L5698
    sec
    lda ZP_MAIN+$12
    sbc ZP_MAIN+$15
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$13
    sbc ZP_MAIN+$16
    sta ZP_MAIN+$1C
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$17
    sta ZP_MAIN+$1D
    ldx #$01
    sec
    jsr REG_KERNEL+$1813
    jmp REG_KERNEL+$169B
L5698:
    jsr REG_KERNEL+$1800
    lda ZP_MAIN+$0E
    bpl L56B2
    lda #$00
    sec
    sbc ZP_MAIN+$1B
    sta ZP_MAIN+$1B
    lda #$00
    sbc ZP_MAIN+$1C
    sta ZP_MAIN+$1C
    lda #$00
    sbc ZP_MAIN+$1D
    sta ZP_MAIN+$1D
L56B2:
    lda ZP_MAIN+$0E
    eor ZP_MAIN+$11
    bpl L56CB
    lda #$00
    sec
    sbc ZP_MAIN+$18
    sta ZP_MAIN+$18
    lda #$00
    sbc ZP_MAIN+$19
    sta ZP_MAIN+$19
    lda #$00
    sbc ZP_MAIN+$1A
    sta ZP_MAIN+$1A
L56CB:
    clc
    rts
L56CD:
    lda #$00
    sta ZP_MAIN+$18
    sta ZP_MAIN+$19
    sta ZP_MAIN+$1A
    lda ZP_MAIN+$0C
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$0D
    sta ZP_MAIN+$1C
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$1D
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda ZP_MAIN+$17
    beq L5838
    lda ZP_MAIN+$12
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$13
    sta ZP_MAIN+$1C
    lda ZP_MAIN+$14
    sta ZP_MAIN+$1D
    ldx #$00
    sec
L5813:
    lda ZP_MAIN+$1B
    sbc ZP_MAIN+$15
    tay
    lda ZP_MAIN+$1C
    sbc ZP_MAIN+$16
    sta ZP_MAIN+$19
    lda ZP_MAIN+$1D
    sbc ZP_MAIN+$17
    bcc L582F
    sta ZP_MAIN+$1D
    sty ZP_MAIN+$1B
    lda ZP_MAIN+$19
    sta ZP_MAIN+$1C
    inx
    bne L5813
L582F:
    stx ZP_MAIN+$18
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$19
    sta ZP_MAIN+$1A
    rts
L5838:
    lda ZP_MAIN+$15
    ora ZP_MAIN+$16
    beq L5889
    lda ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$13
    sta ZP_MAIN+$19
    lda ZP_MAIN+$14
    sta ZP_MAIN+$1A
    lda #$00
    sta ZP_MAIN+$1B
    sta ZP_MAIN+$1C
    sta ZP_MAIN+$1D
    ldx #$18
L5854:
    asl ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    rol ZP_MAIN+$1C
    bcs L5877
    sec
    lda ZP_MAIN+$1B
    sbc ZP_MAIN+$15
    tay
    lda ZP_MAIN+$1C
    sbc ZP_MAIN+$16
    bcc L5873
    sta ZP_MAIN+$1C
    sty ZP_MAIN+$1B
    inc ZP_MAIN+$18
    clc
L5873:
    dex
    bne L5854
    rts
L5877:
    sec
    lda ZP_MAIN+$1B
    sbc ZP_MAIN+$15
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$1C
    sbc ZP_MAIN+$16
    sta ZP_MAIN+$1C
    inc ZP_MAIN+$18
    clc
    bcc L5873
L5889:
    ldx #$05
L588B:
    sta ZP_MAIN+$18,x
    dex
    bpl L588B
    sec
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $A7, ZP_MAIN+$13    ; LAX zp
    cmp ZP_MAIN+$15
    bcc L5A6F
    lda ZP_MAIN+$15
    beq L5A35
    cmp #$05
    bcc L5A42
    lda ZP_MAIN+$12
    sbc ZP_MAIN+$14
    tay
    txa
    sbc ZP_MAIN+$15
    bcc L5A6F
    ldx #$00
L5A1A:
    sta ZP_MAIN+$19
    sty ZP_MAIN+$18
    inx
    cmp ZP_MAIN+$15
    bcc L5A2E
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$14
    tay
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$15
    bcs L5A1A
L5A2E:
    stx ZP_MAIN+$16
    lda #$00
    sta ZP_MAIN+$17
    rts
L5A35:
    lda ZP_MAIN+$14
    bne L5A42
    ldx #$03
L5A3B:
    sta ZP_MAIN+$16,x
    dex
    bpl L5A3B
    sec
    rts
L5A42:
    lda ZP_MAIN+$12
    sta ZP_MAIN+$16
    stx ZP_MAIN+$17
    lda #$00
    sta ZP_MAIN+$18
    sta ZP_MAIN+$19
    ldx #$10
L5A50:
    asl ZP_MAIN+$16
    rol ZP_MAIN+$17
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    sec
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$14
    tay
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$15
    bcc L5A6A
    sta ZP_MAIN+$19
    sty ZP_MAIN+$18
    inc ZP_MAIN+$16
L5A6A:
    dex
    bne L5A50
    clc
    rts
L5A6F:
    stx ZP_MAIN+$19
    lda ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda #$00
    sta ZP_MAIN+$16
    sta ZP_MAIN+$17
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00
    jsr REG_KERNEL+$1A00
    bcc L5B0C
    lda #$00
    sta ZP_MAIN+$1C
    sta ZP_MAIN+$1D
    rts
L5B0C:
    lda ZP_MAIN+$1A
    sta ZP_MAIN+$1C
    lda ZP_MAIN+$1B
    sta ZP_MAIN+$1D
    lda ZP_MAIN+$19
    rol ZP_MAIN+$1C
    rol ZP_MAIN+$1D
    rol ZP_MAIN+$18
    rol
    bcs L5B37
    cmp ZP_MAIN+$15
    bcc L5B42
    bne L5B2B
    ldy ZP_MAIN+$18
    cpy ZP_MAIN+$14
    bcc L5B42
L5B2B:
    tay
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$14
    sta ZP_MAIN+$18
    tya
    sbc ZP_MAIN+$15
    bcs L5B42
L5B37:
    tay
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$14
    sta ZP_MAIN+$18
    tya
    sbc ZP_MAIN+$15
    sec
L5B42:
    ldx #$0F
L5B44:
    rol ZP_MAIN+$1C
    rol ZP_MAIN+$1D
    rol ZP_MAIN+$18
    rol
    bcs L5B65
    cmp ZP_MAIN+$15
    bcc L5B70
    bne L5B59
    ldy ZP_MAIN+$18
    cpy ZP_MAIN+$14
    bcc L5B70
L5B59:
    tay
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$14
    sta ZP_MAIN+$18
    tya
    sbc ZP_MAIN+$15
    bcs L5B70
L5B65:
    tay
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$14
    sta ZP_MAIN+$18
    tya
    sbc ZP_MAIN+$15
    sec
L5B70:
    dex
    bne L5B44
    rol ZP_MAIN+$1C
    rol ZP_MAIN+$1D
    sta ZP_MAIN+$19
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00
    lda ZP_MAIN+$11
    bmi L5C78
    bne L5C16
    lda ZP_MAIN+$10
    bne L5C0D
    jmp REG_KERNEL+$1CE2
L5C0D:
    sta ZP_MAIN+$14
    lda #$00
    sta ZP_MAIN+$15
    jmp REG_KERNEL+$1C1C
L5C16:
    sta ZP_MAIN+$15
    lda ZP_MAIN+$10
    sta ZP_MAIN+$14
    lda ZP_MAIN+$0F
    bmi L5C34
    lda ZP_MAIN+$0C
    sta ZP_MAIN+$1A
    lda ZP_MAIN+$0D
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$12
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$13
    jsr REG_KERNEL+$1B00
    rts
L5C34:
    lda #$00
    sec
    sbc ZP_MAIN+$0C
    sta ZP_MAIN+$1A
    lda #$00
    sbc ZP_MAIN+$0D
    sta ZP_MAIN+$1B
    lda #$00
    sbc ZP_MAIN+$0E
    sta ZP_MAIN+$12
    lda #$00
    sbc ZP_MAIN+$0F
    sta ZP_MAIN+$13
    jsr REG_KERNEL+$1B00
    lda #$00
    sec
    sbc ZP_MAIN+$18
    sta ZP_MAIN+$18
    lda #$00
    sbc ZP_MAIN+$19
    sta ZP_MAIN+$19
    lda #$00
    sec
    sbc ZP_MAIN+$1C
    sta ZP_MAIN+$1C
    lda #$00
    sbc ZP_MAIN+$1D
    sta ZP_MAIN+$1D
    lda #$00
    sbc ZP_MAIN+$16
    sta ZP_MAIN+$16
    lda #$00
    sbc ZP_MAIN+$17
    sta ZP_MAIN+$17
    clc
    rts
L5C78:
    lda #$00
    sec
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    lda #$00
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$15
    lda ZP_MAIN+$0F
    bmi L5CB7
    lda ZP_MAIN+$0C
    sta ZP_MAIN+$1A
    lda ZP_MAIN+$0D
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$12
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$13
    jsr REG_KERNEL+$1B00
    lda #$00
    sec
    sbc ZP_MAIN+$1C
    sta ZP_MAIN+$1C
    lda #$00
    sbc ZP_MAIN+$1D
    sta ZP_MAIN+$1D
    lda #$00
    sbc ZP_MAIN+$16
    sta ZP_MAIN+$16
    lda #$00
    sbc ZP_MAIN+$17
    sta ZP_MAIN+$17
    clc
    rts
L5CB7:
    lda #$00
    sec
    sbc ZP_MAIN+$0C
    sta ZP_MAIN+$1A
    lda #$00
    sbc ZP_MAIN+$0D
    sta ZP_MAIN+$1B
    lda #$00
    sbc ZP_MAIN+$0E
    sta ZP_MAIN+$12
    lda #$00
    sbc ZP_MAIN+$0F
    sta ZP_MAIN+$13
    jsr REG_KERNEL+$1B00
    lda #$00
    sec
    sbc ZP_MAIN+$18
    sta ZP_MAIN+$18
    lda #$00
    sbc ZP_MAIN+$19
    sta ZP_MAIN+$19
    clc
    rts
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    jmp REG_KERNEL+$1B00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00

; Source interval $5E00-$5E38
* = REG_GAME_API
    jmp REG_GAME
    jmp REG_GAME
    jmp REG_GAME+$0034
    jmp REG_GAME+$0034
    jmp REG_GAME+$041E
    jmp REG_GAME+$0435
    jmp REG_GAME+$044C
    jmp REG_GAME+$0475
    jmp REG_GAME+$049E
    jmp REG_GAME+$04E8
    jmp REG_GAME+$0538
    jmp REG_GAME+$06E4
    jmp REG_GAME+$06EF
    jmp REG_GAME+$06FE
    jmp REG_GAME+$0714
    jmp REG_GAME+$07DB
    jmp REG_GAME+$0A40
    jmp REG_GAME+$09FC
    jmp REG_GAME+$0A0C

; Source interval $5E39-$5FFF
* = REG_KERNEL+$1E39
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00

; Source interval $6000-$9BFF
* = REG_TABLE
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $01, $02, $04, $06, $09, $0C, $10, $14, $19, $1E, $24, $2A, $31, $38
    !byte $40, $48, $51, $5A, $64, $6E, $79, $84, $90, $9C, $A9, $B6, $C4, $D2, $E1, $F0
    !byte $00, $10, $21, $32, $44, $56, $69, $7C, $90, $A4, $B9, $CE, $E4, $FA, $11, $28
    !byte $40, $58, $71, $8A, $A4, $BE, $D9, $F4, $10, $2C, $49, $66, $84, $A2, $C1, $E0
    !byte $00, $20, $41, $62, $84, $A6, $C9, $EC, $10, $34, $59, $7E, $A4, $CA, $F1, $18
    !byte $40, $68, $91, $BA, $E4, $0E, $39, $64, $90, $BC, $E9, $16, $44, $72, $A1, $D0
    !byte $00, $30, $61, $92, $C4, $F6, $29, $5C, $90, $C4, $F9, $2E, $64, $9A, $D1, $08
    !byte $40, $78, $B1, $EA, $24, $5E, $99, $D4, $10, $4C, $89, $C6, $04, $42, $81, $C0
    !byte $00, $40, $81, $C2, $04, $46, $89, $CC, $10, $54, $99, $DE, $24, $6A, $B1, $F8
    !byte $40, $88, $D1, $1A, $64, $AE, $F9, $44, $90, $DC, $29, $76, $C4, $12, $61, $B0
    !byte $00, $50, $A1, $F2, $44, $96, $E9, $3C, $90, $E4, $39, $8E, $E4, $3A, $91, $E8
    !byte $40, $98, $F1, $4A, $A4, $FE, $59, $B4, $10, $6C, $C9, $26, $84, $E2, $41, $A0
    !byte $00, $60, $C1, $22, $84, $E6, $49, $AC, $10, $74, $D9, $3E, $A4, $0A, $71, $D8
    !byte $40, $A8, $11, $7A, $E4, $4E, $B9, $24, $90, $FC, $69, $D6, $44, $B2, $21, $90
    !byte $00, $70, $E1, $52, $C4, $36, $A9, $1C, $90, $04, $79, $EE, $64, $DA, $51, $C8
    !byte $40, $B8, $31, $AA, $24, $9E, $19, $94, $10, $8C, $09, $86, $04, $82, $01, $80
    !byte $00, $80, $01, $82, $04, $86, $09, $8C, $10, $94, $19, $9E, $24, $AA, $31, $B8
    !byte $40, $C8, $51, $DA, $64, $EE, $79, $04, $90, $1C, $A9, $36, $C4, $52, $E1, $70
    !byte $00, $90, $21, $B2, $44, $D6, $69, $FC, $90, $24, $B9, $4E, $E4, $7A, $11, $A8
    !byte $40, $D8, $71, $0A, $A4, $3E, $D9, $74, $10, $AC, $49, $E6, $84, $22, $C1, $60
    !byte $00, $A0, $41, $E2, $84, $26, $C9, $6C, $10, $B4, $59, $FE, $A4, $4A, $F1, $98
    !byte $40, $E8, $91, $3A, $E4, $8E, $39, $E4, $90, $3C, $E9, $96, $44, $F2, $A1, $50
    !byte $00, $B0, $61, $12, $C4, $76, $29, $DC, $90, $44, $F9, $AE, $64, $1A, $D1, $88
    !byte $40, $F8, $B1, $6A, $24, $DE, $99, $54, $10, $CC, $89, $46, $04, $C2, $81, $40
    !byte $00, $C0, $81, $42, $04, $C6, $89, $4C, $10, $D4, $99, $5E, $24, $EA, $B1, $78
    !byte $40, $08, $D1, $9A, $64, $2E, $F9, $C4, $90, $5C, $29, $F6, $C4, $92, $61, $30
    !byte $00, $D0, $A1, $72, $44, $16, $E9, $BC, $90, $64, $39, $0E, $E4, $BA, $91, $68
    !byte $40, $18, $F1, $CA, $A4, $7E, $59, $34, $10, $EC, $C9, $A6, $84, $62, $41, $20
    !byte $00, $E0, $C1, $A2, $84, $66, $49, $2C, $10, $F4, $D9, $BE, $A4, $8A, $71, $58
    !byte $40, $28, $11, $FA, $E4, $CE, $B9, $A4, $90, $7C, $69, $56, $44, $32, $21, $10
    !byte $00, $F0, $E1, $D2, $C4, $B6, $A9, $9C, $90, $84, $79, $6E, $64, $5A, $51, $48
    !byte $40, $38, $31, $2A, $24, $1E, $19, $14, $10, $0C, $09, $06, $04, $02, $01, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $02, $02
    !byte $02, $02, $02, $02, $02, $02, $02, $02, $03, $03, $03, $03, $03, $03, $03, $03
    !byte $04, $04, $04, $04, $04, $04, $04, $04, $05, $05, $05, $05, $05, $05, $05, $06
    !byte $06, $06, $06, $06, $06, $07, $07, $07, $07, $07, $07, $08, $08, $08, $08, $08
    !byte $09, $09, $09, $09, $09, $09, $0A, $0A, $0A, $0A, $0A, $0B, $0B, $0B, $0B, $0C
    !byte $0C, $0C, $0C, $0C, $0D, $0D, $0D, $0D, $0E, $0E, $0E, $0E, $0F, $0F, $0F, $0F
    !byte $10, $10, $10, $10, $11, $11, $11, $11, $12, $12, $12, $12, $13, $13, $13, $13
    !byte $14, $14, $14, $15, $15, $15, $15, $16, $16, $16, $17, $17, $17, $18, $18, $18
    !byte $19, $19, $19, $19, $1A, $1A, $1A, $1B, $1B, $1B, $1C, $1C, $1C, $1D, $1D, $1D
    !byte $1E, $1E, $1E, $1F, $1F, $1F, $20, $20, $21, $21, $21, $22, $22, $22, $23, $23
    !byte $24, $24, $24, $25, $25, $25, $26, $26, $27, $27, $27, $28, $28, $29, $29, $29
    !byte $2A, $2A, $2B, $2B, $2B, $2C, $2C, $2D, $2D, $2D, $2E, $2E, $2F, $2F, $30, $30
    !byte $31, $31, $31, $32, $32, $33, $33, $34, $34, $35, $35, $35, $36, $36, $37, $37
    !byte $38, $38, $39, $39, $3A, $3A, $3B, $3B, $3C, $3C, $3D, $3D, $3E, $3E, $3F, $3F
    !byte $40, $40, $41, $41, $42, $42, $43, $43, $44, $44, $45, $45, $46, $46, $47, $47
    !byte $48, $48, $49, $49, $4A, $4A, $4B, $4C, $4C, $4D, $4D, $4E, $4E, $4F, $4F, $50
    !byte $51, $51, $52, $52, $53, $53, $54, $54, $55, $56, $56, $57, $57, $58, $59, $59
    !byte $5A, $5A, $5B, $5C, $5C, $5D, $5D, $5E, $5F, $5F, $60, $60, $61, $62, $62, $63
    !byte $64, $64, $65, $65, $66, $67, $67, $68, $69, $69, $6A, $6A, $6B, $6C, $6C, $6D
    !byte $6E, $6E, $6F, $70, $70, $71, $72, $72, $73, $74, $74, $75, $76, $76, $77, $78
    !byte $79, $79, $7A, $7B, $7B, $7C, $7D, $7D, $7E, $7F, $7F, $80, $81, $82, $82, $83
    !byte $84, $84, $85, $86, $87, $87, $88, $89, $8A, $8A, $8B, $8C, $8D, $8D, $8E, $8F
    !byte $90, $90, $91, $92, $93, $93, $94, $95, $96, $96, $97, $98, $99, $99, $9A, $9B
    !byte $9C, $9D, $9D, $9E, $9F, $A0, $A0, $A1, $A2, $A3, $A4, $A4, $A5, $A6, $A7, $A8
    !byte $A9, $A9, $AA, $AB, $AC, $AD, $AD, $AE, $AF, $B0, $B1, $B2, $B2, $B3, $B4, $B5
    !byte $B6, $B7, $B7, $B8, $B9, $BA, $BB, $BC, $BD, $BD, $BE, $BF, $C0, $C1, $C2, $C3
    !byte $C4, $C4, $C5, $C6, $C7, $C8, $C9, $CA, $CB, $CB, $CC, $CD, $CE, $CF, $D0, $D1
    !byte $D2, $D3, $D4, $D4, $D5, $D6, $D7, $D8, $D9, $DA, $DB, $DC, $DD, $DE, $DF, $E0
    !byte $E1, $E1, $E2, $E3, $E4, $E5, $E6, $E7, $E8, $E9, $EA, $EB, $EC, $ED, $EE, $EF
    !byte $F0, $F1, $F2, $F3, $F4, $F5, $F6, $F7, $F8, $F9, $FA, $FB, $FC, $FD, $FE, $00
    !byte $00, $CA, $01, $CC, $04, $D0, $09, $D6, $10, $DE, $19, $E8, $24, $F4, $31, $02
    !byte $40, $12, $51, $24, $64, $38, $79, $4E, $90, $66, $A9, $80, $C4, $9C, $E1, $BA
    !byte $00, $DA, $21, $FC, $44, $20, $69, $46, $90, $6E, $B9, $98, $E4, $C4, $11, $F2
    !byte $40, $22, $71, $54, $A4, $88, $D9, $BE, $10, $F6, $49, $30, $84, $6C, $C1, $AA
    !byte $00, $EA, $41, $2C, $84, $70, $C9, $B6, $10, $FE, $59, $48, $A4, $94, $F1, $E2
    !byte $40, $32, $91, $84, $E4, $D8, $39, $2E, $90, $86, $E9, $E0, $44, $3C, $A1, $9A
    !byte $00, $FA, $61, $5C, $C4, $C0, $29, $26, $90, $8E, $F9, $F8, $64, $64, $D1, $D2
    !byte $40, $42, $B1, $B4, $24, $28, $99, $9E, $10, $16, $89, $90, $04, $0C, $81, $8A
    !byte $00, $0A, $81, $8C, $04, $10, $89, $96, $10, $1E, $99, $A8, $24, $34, $B1, $C2
    !byte $40, $52, $D1, $E4, $64, $78, $F9, $0E, $90, $A6, $29, $40, $C4, $DC, $61, $7A
    !byte $00, $1A, $A1, $BC, $44, $60, $E9, $06, $90, $AE, $39, $58, $E4, $04, $91, $B2
    !byte $40, $62, $F1, $14, $A4, $C8, $59, $7E, $10, $36, $C9, $F0, $84, $AC, $41, $6A
    !byte $00, $2A, $C1, $EC, $84, $B0, $49, $76, $10, $3E, $D9, $08, $A4, $D4, $71, $A2
    !byte $40, $72, $11, $44, $E4, $18, $B9, $EE, $90, $C6, $69, $A0, $44, $7C, $21, $5A
    !byte $00, $3A, $E1, $1C, $C4, $00, $A9, $E6, $90, $CE, $79, $B8, $64, $A4, $51, $92
    !byte $40, $82, $31, $74, $24, $68, $19, $5E, $10, $56, $09, $50, $04, $4C, $01, $4A
    !byte $00, $4A, $01, $4C, $04, $50, $09, $56, $10, $5E, $19, $68, $24, $74, $31, $82
    !byte $40, $92, $51, $A4, $64, $B8, $79, $CE, $90, $E6, $A9, $00, $C4, $1C, $E1, $3A
    !byte $00, $5A, $21, $7C, $44, $A0, $69, $C6, $90, $EE, $B9, $18, $E4, $44, $11, $72
    !byte $40, $A2, $71, $D4, $A4, $08, $D9, $3E, $10, $76, $49, $B0, $84, $EC, $C1, $2A
    !byte $00, $6A, $41, $AC, $84, $F0, $C9, $36, $10, $7E, $59, $C8, $A4, $14, $F1, $62
    !byte $40, $B2, $91, $04, $E4, $58, $39, $AE, $90, $06, $E9, $60, $44, $BC, $A1, $1A
    !byte $00, $7A, $61, $DC, $C4, $40, $29, $A6, $90, $0E, $F9, $78, $64, $E4, $D1, $52
    !byte $40, $C2, $B1, $34, $24, $A8, $99, $1E, $10, $96, $89, $10, $04, $8C, $81, $0A
    !byte $00, $8A, $81, $0C, $04, $90, $89, $16, $10, $9E, $99, $28, $24, $B4, $B1, $42
    !byte $40, $D2, $D1, $64, $64, $F8, $F9, $8E, $90, $26, $29, $C0, $C4, $5C, $61, $FA
    !byte $00, $9A, $A1, $3C, $44, $E0, $E9, $86, $90, $2E, $39, $D8, $E4, $84, $91, $32
    !byte $40, $E2, $F1, $94, $A4, $48, $59, $FE, $10, $B6, $C9, $70, $84, $2C, $41, $EA
    !byte $00, $AA, $C1, $6C, $84, $30, $49, $F6, $10, $BE, $D9, $88, $A4, $54, $71, $22
    !byte $40, $F2, $11, $C4, $E4, $98, $B9, $6E, $90, $46, $69, $20, $44, $FC, $21, $DA
    !byte $00, $BA, $E1, $9C, $C4, $80, $A9, $66, $90, $4E, $79, $38, $64, $24, $51, $12
    !byte $40, $02, $31, $F4, $24, $E8, $19, $DE, $10, $D6, $09, $D0, $04, $CC, $01, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $01
    !byte $00, $01, $00, $01, $00, $01, $00, $01, $00, $01, $00, $01, $00, $01, $00, $01
    !byte $01, $01, $01, $01, $01, $02, $01, $02, $01, $02, $01, $02, $01, $02, $02, $02
    !byte $02, $03, $02, $03, $02, $03, $02, $03, $03, $03, $03, $04, $03, $04, $03, $04
    !byte $04, $04, $04, $05, $04, $05, $04, $05, $05, $05, $05, $06, $05, $06, $05, $06
    !byte $06, $07, $06, $07, $06, $07, $07, $08, $07, $08, $07, $08, $08, $09, $08, $09
    !byte $09, $09, $09, $0A, $09, $0A, $0A, $0B, $0A, $0B, $0A, $0B, $0B, $0C, $0B, $0C
    !byte $0C, $0D, $0C, $0D, $0D, $0E, $0D, $0E, $0E, $0F, $0E, $0F, $0F, $10, $0F, $10
    !byte $10, $11, $10, $11, $11, $12, $11, $12, $12, $13, $12, $13, $13, $14, $13, $14
    !byte $14, $15, $14, $15, $15, $16, $15, $17, $16, $17, $17, $18, $17, $18, $18, $19
    !byte $19, $1A, $19, $1A, $1A, $1B, $1A, $1C, $1B, $1C, $1C, $1D, $1C, $1E, $1D, $1E
    !byte $1E, $1F, $1E, $20, $1F, $20, $20, $21, $21, $22, $21, $22, $22, $23, $23, $24
    !byte $24, $25, $24, $25, $25, $26, $26, $27, $27, $28, $27, $29, $28, $29, $29, $2A
    !byte $2A, $2B, $2B, $2C, $2B, $2D, $2C, $2D, $2D, $2E, $2E, $2F, $2F, $30, $30, $31
    !byte $31, $32, $31, $33, $32, $34, $33, $34, $34, $35, $35, $36, $36, $37, $37, $38
    !byte $38, $39, $39, $3A, $3A, $3B, $3B, $3C, $3C, $3D, $3D, $3E, $3E, $3F, $3F, $40
    !byte $40, $41, $41, $42, $42, $43, $43, $44, $44, $45, $45, $46, $46, $47, $47, $48
    !byte $48, $49, $49, $4A, $4A, $4B, $4B, $4C, $4C, $4D, $4D, $4F, $4E, $50, $4F, $51
    !byte $51, $52, $52, $53, $53, $54, $54, $55, $55, $56, $56, $58, $57, $59, $59, $5A
    !byte $5A, $5B, $5B, $5C, $5C, $5E, $5D, $5F, $5F, $60, $60, $61, $61, $62, $62, $64
    !byte $64, $65, $65, $66, $66, $67, $67, $69, $69, $6A, $6A, $6B, $6B, $6D, $6C, $6E
    !byte $6E, $6F, $6F, $71, $70, $72, $72, $73, $73, $75, $74, $76, $76, $77, $77, $79
    !byte $79, $7A, $7A, $7B, $7B, $7D, $7D, $7E, $7E, $80, $7F, $81, $81, $82, $82, $84
    !byte $84, $85, $85, $87, $87, $88, $88, $8A, $8A, $8B, $8B, $8D, $8D, $8E, $8E, $90
    !byte $90, $91, $91, $93, $93, $94, $94, $96, $96, $97, $97, $99, $99, $9A, $9A, $9C
    !byte $9C, $9D, $9D, $9F, $9F, $A0, $A0, $A2, $A2, $A4, $A4, $A5, $A5, $A7, $A7, $A8
    !byte $A9, $AA, $AA, $AC, $AC, $AD, $AD, $AF, $AF, $B1, $B1, $B2, $B2, $B4, $B4, $B6
    !byte $B6, $B7, $B7, $B9, $B9, $BB, $BB, $BC, $BD, $BE, $BE, $C0, $C0, $C2, $C2, $C3
    !byte $C4, $C5, $C5, $C7, $C7, $C9, $C9, $CA, $CB, $CC, $CC, $CE, $CE, $D0, $D0, $D2
    !byte $D2, $D3, $D4, $D5, $D5, $D7, $D7, $D9, $D9, $DB, $DB, $DD, $DD, $DE, $DF, $E0
    !byte $E1, $E2, $E2, $E4, $E4, $E6, $E6, $E8, $E8, $EA, $EA, $EC, $EC, $EE, $EE, $F0
    !byte $F0, $F2, $F2, $F3, $F4, $F5, $F6, $F7, $F8, $F9, $FA, $FB, $FC, $FD, $FE, $00
    !byte $B5, $FE, $B3, $FB, $AF, $F6, $A9, $EF, $A1, $E6, $97, $DB, $8B, $CE, $7D, $BF
    !byte $6D, $AE, $5B, $9B, $47, $86, $31, $6F, $19, $56, $FF, $3B, $E3, $1E, $C5, $FF
    !byte $A5, $DE, $83, $BB, $5F, $96, $39, $6F, $11, $46, $E7, $1B, $BB, $EE, $8D, $BF
    !byte $5D, $8E, $2B, $5B, $F7, $26, $C1, $EF, $89, $B6, $4F, $7B, $13, $3E, $D5, $FF
    !byte $95, $BE, $53, $7B, $0F, $36, $C9, $EF, $81, $A6, $37, $5B, $EB, $0E, $9D, $BF
    !byte $4D, $6E, $FB, $1B, $A7, $C6, $51, $6F, $F9, $16, $9F, $BB, $43, $5E, $E5, $FF
    !byte $85, $9E, $23, $3B, $BF, $D6, $59, $6F, $F1, $06, $87, $9B, $1B, $2E, $AD, $BF
    !byte $3D, $4E, $CB, $DB, $57, $66, $E1, $EF, $69, $76, $EF, $FB, $73, $7E, $F5, $FF
    !byte $75, $7E, $F3, $FB, $6F, $76, $E9, $EF, $61, $66, $D7, $DB, $4B, $4E, $BD, $BF
    !byte $2D, $2E, $9B, $9B, $07, $06, $71, $6F, $D9, $D6, $3F, $3B, $A3, $9E, $05, $FF
    !byte $65, $5E, $C3, $BB, $1F, $16, $79, $6F, $D1, $C6, $27, $1B, $7B, $6E, $CD, $BF
    !byte $1D, $0E, $6B, $5B, $B7, $A6, $01, $EF, $49, $36, $8F, $7B, $D3, $BE, $15, $FF
    !byte $55, $3E, $93, $7B, $CF, $B6, $09, $EF, $41, $26, $77, $5B, $AB, $8E, $DD, $BF
    !byte $0D, $EE, $3B, $1B, $67, $46, $91, $6F, $B9, $96, $DF, $BB, $03, $DE, $25, $FF
    !byte $45, $1E, $63, $3B, $7F, $56, $99, $6F, $B1, $86, $C7, $9B, $DB, $AE, $ED, $BF
    !byte $FD, $CE, $0B, $DB, $17, $E6, $21, $EF, $29, $F6, $2F, $FB, $33, $FE, $35, $FF
    !byte $35, $FE, $33, $FB, $2F, $F6, $29, $EF, $21, $E6, $17, $DB, $0B, $CE, $FD, $BF
    !byte $ED, $AE, $DB, $9B, $C7, $86, $B1, $6F, $99, $56, $7F, $3B, $63, $1E, $45, $FF
    !byte $25, $DE, $03, $BB, $DF, $96, $B9, $6F, $91, $46, $67, $1B, $3B, $EE, $0D, $BF
    !byte $DD, $8E, $AB, $5B, $77, $26, $41, $EF, $09, $B6, $CF, $7B, $93, $3E, $55, $FF
    !byte $15, $BE, $D3, $7B, $8F, $36, $49, $EF, $01, $A6, $B7, $5B, $6B, $0E, $1D, $BF
    !byte $CD, $6E, $7B, $1B, $27, $C6, $D1, $6F, $79, $16, $1F, $BB, $C3, $5E, $65, $FF
    !byte $05, $9E, $A3, $3B, $3F, $D6, $D9, $6F, $71, $06, $07, $9B, $9B, $2E, $2D, $BF
    !byte $BD, $4E, $4B, $DB, $D7, $66, $61, $EF, $E9, $76, $6F, $FB, $F3, $7E, $75, $FF
    !byte $F5, $7E, $73, $FB, $EF, $76, $69, $EF, $E1, $66, $57, $DB, $CB, $4E, $3D, $BF
    !byte $AD, $2E, $1B, $9B, $87, $06, $F1, $6F, $59, $D6, $BF, $3B, $23, $9E, $85, $FF
    !byte $E5, $5E, $43, $BB, $9F, $16, $F9, $6F, $51, $C6, $A7, $1B, $FB, $6E, $4D, $BF
    !byte $9D, $0E, $EB, $5B, $37, $A6, $81, $EF, $C9, $36, $0F, $7B, $53, $BE, $95, $FF
    !byte $D5, $3E, $13, $7B, $4F, $B6, $89, $EF, $C1, $26, $F7, $5B, $2B, $8E, $5D, $BF
    !byte $8D, $EE, $BB, $1B, $E7, $46, $11, $6F, $39, $96, $5F, $BB, $83, $DE, $A5, $FF
    !byte $C5, $1E, $E3, $3B, $FF, $56, $19, $6F, $31, $86, $47, $9B, $5B, $AE, $6D, $BF
    !byte $7D, $CE, $8B, $DB, $97, $E6, $A1, $EF, $A9, $F6, $AF, $FB, $B3, $FE, $B5, $00
    !byte $BF, $C0, $C0, $C1, $C1, $C2, $C2, $C3, $C3, $C4, $C4, $C5, $C5, $C6, $C6, $C7
    !byte $C7, $C8, $C8, $C9, $C9, $CA, $CA, $CB, $CB, $CC, $CB, $CD, $CC, $CE, $CD, $CE
    !byte $CE, $CF, $CF, $D0, $D0, $D1, $D1, $D2, $D2, $D3, $D2, $D4, $D3, $D4, $D4, $D5
    !byte $D5, $D6, $D6, $D7, $D6, $D8, $D7, $D8, $D8, $D9, $D9, $DA, $DA, $DB, $DA, $DB
    !byte $DB, $DC, $DC, $DD, $DD, $DE, $DD, $DE, $DE, $DF, $DF, $E0, $DF, $E1, $E0, $E1
    !byte $E1, $E2, $E1, $E3, $E2, $E3, $E3, $E4, $E3, $E5, $E4, $E5, $E5, $E6, $E5, $E6
    !byte $E6, $E7, $E7, $E8, $E7, $E8, $E8, $E9, $E8, $EA, $E9, $EA, $EA, $EB, $EA, $EB
    !byte $EB, $EC, $EB, $EC, $EC, $ED, $EC, $ED, $ED, $EE, $ED, $EE, $EE, $EF, $EE, $EF
    !byte $EF, $F0, $EF, $F0, $F0, $F1, $F0, $F1, $F1, $F2, $F1, $F2, $F2, $F3, $F2, $F3
    !byte $F3, $F4, $F3, $F4, $F4, $F5, $F4, $F5, $F4, $F5, $F5, $F6, $F5, $F6, $F6, $F6
    !byte $F6, $F7, $F6, $F7, $F7, $F8, $F7, $F8, $F7, $F8, $F8, $F9, $F8, $F9, $F8, $F9
    !byte $F9, $FA, $F9, $FA, $F9, $FA, $FA, $FA, $FA, $FB, $FA, $FB, $FA, $FB, $FB, $FB
    !byte $FB, $FC, $FB, $FC, $FB, $FC, $FC, $FC, $FC, $FD, $FC, $FD, $FC, $FD, $FC, $FD
    !byte $FD, $FD, $FD, $FE, $FD, $FE, $FD, $FE, $FD, $FE, $FD, $FE, $FE, $FE, $FE, $FE
    !byte $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF
    !byte $FE, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FE, $FF
    !byte $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FF, $FE, $FE
    !byte $FE, $FE, $FE, $FE, $FD, $FE, $FD, $FE, $FD, $FE, $FD, $FE, $FD, $FD, $FD, $FD
    !byte $FC, $FD, $FC, $FD, $FC, $FD, $FC, $FC, $FC, $FC, $FB, $FC, $FB, $FC, $FB, $FB
    !byte $FB, $FB, $FA, $FB, $FA, $FB, $FA, $FA, $FA, $FA, $F9, $FA, $F9, $FA, $F9, $F9
    !byte $F8, $F9, $F8, $F9, $F8, $F8, $F7, $F8, $F7, $F8, $F7, $F7, $F6, $F7, $F6, $F6
    !byte $F6, $F6, $F5, $F6, $F5, $F5, $F4, $F5, $F4, $F5, $F4, $F4, $F3, $F4, $F3, $F3
    !byte $F2, $F3, $F2, $F2, $F1, $F2, $F1, $F1, $F0, $F1, $F0, $F0, $EF, $F0, $EF, $EF
    !byte $EE, $EF, $EE, $EE, $ED, $EE, $ED, $ED, $EC, $ED, $EC, $EC, $EB, $EC, $EB, $EB
    !byte $EA, $EB, $EA, $EA, $E9, $EA, $E8, $E9, $E8, $E8, $E7, $E8, $E7, $E7, $E6, $E6
    !byte $E5, $E6, $E5, $E5, $E4, $E5, $E3, $E4, $E3, $E3, $E2, $E3, $E1, $E2, $E1, $E1
    !byte $E0, $E1, $DF, $E0, $DF, $DF, $DE, $DE, $DD, $DE, $DD, $DD, $DC, $DC, $DB, $DB
    !byte $DA, $DB, $DA, $DA, $D9, $D9, $D8, $D8, $D7, $D8, $D6, $D7, $D6, $D6, $D5, $D5
    !byte $D4, $D4, $D3, $D4, $D2, $D3, $D2, $D2, $D1, $D1, $D0, $D0, $CF, $CF, $CE, $CE
    !byte $CD, $CE, $CC, $CD, $CB, $CC, $CB, $CB, $CA, $CA, $C9, $C9, $C8, $C8, $C7, $C7
    !byte $C6, $C6, $C5, $C5, $C4, $C4, $C3, $C3, $C2, $C2, $C1, $C1, $C0, $C0, $BF, $00
    !byte $00, $32, $01, $34, $04, $38, $09, $3E, $10, $46, $19, $50, $24, $5C, $31, $6A
    !byte $40, $7A, $51, $8C, $64, $A0, $79, $B6, $90, $CE, $A9, $E8, $C4, $04, $E1, $22
    !byte $00, $42, $21, $64, $44, $88, $69, $AE, $90, $D6, $B9, $00, $E4, $2C, $11, $5A
    !byte $40, $8A, $71, $BC, $A4, $F0, $D9, $26, $10, $5E, $49, $98, $84, $D4, $C1, $12
    !byte $00, $52, $41, $94, $84, $D8, $C9, $1E, $10, $66, $59, $B0, $A4, $FC, $F1, $4A
    !byte $40, $9A, $91, $EC, $E4, $40, $39, $96, $90, $EE, $E9, $48, $44, $A4, $A1, $02
    !byte $00, $62, $61, $C4, $C4, $28, $29, $8E, $90, $F6, $F9, $60, $64, $CC, $D1, $3A
    !byte $40, $AA, $B1, $1C, $24, $90, $99, $06, $10, $7E, $89, $F8, $04, $74, $81, $F2
    !byte $00, $72, $81, $F4, $04, $78, $89, $FE, $10, $86, $99, $10, $24, $9C, $B1, $2A
    !byte $40, $BA, $D1, $4C, $64, $E0, $F9, $76, $90, $0E, $29, $A8, $C4, $44, $61, $E2
    !byte $00, $82, $A1, $24, $44, $C8, $E9, $6E, $90, $16, $39, $C0, $E4, $6C, $91, $1A
    !byte $40, $CA, $F1, $7C, $A4, $30, $59, $E6, $10, $9E, $C9, $58, $84, $14, $41, $D2
    !byte $00, $92, $C1, $54, $84, $18, $49, $DE, $10, $A6, $D9, $70, $A4, $3C, $71, $0A
    !byte $40, $DA, $11, $AC, $E4, $80, $B9, $56, $90, $2E, $69, $08, $44, $E4, $21, $C2
    !byte $00, $A2, $E1, $84, $C4, $68, $A9, $4E, $90, $36, $79, $20, $64, $0C, $51, $FA
    !byte $40, $EA, $31, $DC, $24, $D0, $19, $C6, $10, $BE, $09, $B8, $04, $B4, $01, $B2
    !byte $00, $B2, $01, $B4, $04, $B8, $09, $BE, $10, $C6, $19, $D0, $24, $DC, $31, $EA
    !byte $40, $FA, $51, $0C, $64, $20, $79, $36, $90, $4E, $A9, $68, $C4, $84, $E1, $A2
    !byte $00, $C2, $21, $E4, $44, $08, $69, $2E, $90, $56, $B9, $80, $E4, $AC, $11, $DA
    !byte $40, $0A, $71, $3C, $A4, $70, $D9, $A6, $10, $DE, $49, $18, $84, $54, $C1, $92
    !byte $00, $D2, $41, $14, $84, $58, $C9, $9E, $10, $E6, $59, $30, $A4, $7C, $F1, $CA
    !byte $40, $1A, $91, $6C, $E4, $C0, $39, $16, $90, $6E, $E9, $C8, $44, $24, $A1, $82
    !byte $00, $E2, $61, $44, $C4, $A8, $29, $0E, $90, $76, $F9, $E0, $64, $4C, $D1, $BA
    !byte $40, $2A, $B1, $9C, $24, $10, $99, $86, $10, $FE, $89, $78, $04, $F4, $81, $72
    !byte $00, $F2, $81, $74, $04, $F8, $89, $7E, $10, $06, $99, $90, $24, $1C, $B1, $AA
    !byte $40, $3A, $D1, $CC, $64, $60, $F9, $F6, $90, $8E, $29, $28, $C4, $C4, $61, $62
    !byte $00, $02, $A1, $A4, $44, $48, $E9, $EE, $90, $96, $39, $40, $E4, $EC, $91, $9A
    !byte $40, $4A, $F1, $FC, $A4, $B0, $59, $66, $10, $1E, $C9, $D8, $84, $94, $41, $52
    !byte $00, $12, $C1, $D4, $84, $98, $49, $5E, $10, $26, $D9, $F0, $A4, $BC, $71, $8A
    !byte $40, $5A, $11, $2C, $E4, $00, $B9, $D6, $90, $AE, $69, $88, $44, $64, $21, $42
    !byte $00, $22, $E1, $04, $C4, $E8, $A9, $CE, $90, $B6, $79, $A0, $64, $8C, $51, $7A
    !byte $40, $6A, $31, $5C, $24, $50, $19, $46, $10, $3E, $09, $38, $04, $34, $01, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $01, $00, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $02, $01, $02, $02, $02
    !byte $02, $02, $02, $02, $02, $02, $02, $03, $03, $03, $03, $03, $03, $03, $03, $04
    !byte $04, $04, $04, $04, $04, $04, $04, $05, $05, $05, $05, $05, $05, $05, $05, $06
    !byte $06, $06, $06, $06, $06, $07, $07, $07, $07, $07, $07, $08, $08, $08, $08, $09
    !byte $09, $09, $09, $09, $09, $0A, $0A, $0A, $0A, $0A, $0A, $0B, $0B, $0B, $0B, $0C
    !byte $0C, $0C, $0C, $0D, $0D, $0D, $0D, $0E, $0E, $0E, $0E, $0E, $0F, $0F, $0F, $0F
    !byte $10, $10, $10, $10, $11, $11, $11, $11, $12, $12, $12, $13, $13, $13, $13, $14
    !byte $14, $14, $14, $15, $15, $15, $15, $16, $16, $17, $17, $17, $17, $18, $18, $18
    !byte $19, $19, $19, $1A, $1A, $1A, $1A, $1B, $1B, $1C, $1C, $1C, $1C, $1D, $1D, $1E
    !byte $1E, $1E, $1E, $1F, $1F, $20, $20, $20, $21, $21, $21, $22, $22, $23, $23, $23
    !byte $24, $24, $24, $25, $25, $26, $26, $26, $27, $27, $27, $28, $28, $29, $29, $2A
    !byte $2A, $2A, $2B, $2B, $2B, $2C, $2C, $2D, $2D, $2E, $2E, $2F, $2F, $2F, $30, $30
    !byte $31, $31, $31, $32, $32, $33, $33, $34, $34, $35, $35, $36, $36, $37, $37, $37
    !byte $38, $38, $39, $39, $3A, $3A, $3B, $3B, $3C, $3C, $3D, $3D, $3E, $3E, $3F, $3F
    !byte $40, $40, $41, $41, $42, $42, $43, $43, $44, $44, $45, $45, $46, $46, $47, $47
    !byte $48, $48, $49, $4A, $4A, $4B, $4B, $4C, $4C, $4D, $4D, $4E, $4E, $4F, $4F, $50
    !byte $51, $51, $52, $52, $53, $54, $54, $55, $55, $56, $56, $57, $57, $58, $59, $59
    !byte $5A, $5B, $5B, $5C, $5C, $5D, $5D, $5E, $5F, $5F, $60, $61, $61, $62, $62, $63
    !byte $64, $64, $65, $66, $66, $67, $67, $68, $69, $69, $6A, $6B, $6B, $6C, $6C, $6D
    !byte $6E, $6F, $6F, $70, $70, $71, $72, $73, $73, $74, $74, $75, $76, $77, $77, $78
    !byte $79, $79, $7A, $7B, $7B, $7C, $7D, $7E, $7E, $7F, $7F, $80, $81, $82, $82, $83
    !byte $84, $85, $85, $86, $87, $88, $88, $89, $8A, $8A, $8B, $8C, $8D, $8D, $8E, $8F
    !byte $90, $90, $91, $92, $93, $93, $94, $95, $96, $97, $97, $98, $99, $9A, $9A, $9B
    !byte $9C, $9D, $9D, $9E, $9F, $A0, $A0, $A1, $A2, $A3, $A4, $A5, $A5, $A6, $A7, $A8
    !byte $A9, $AA, $AA, $AB, $AC, $AD, $AD, $AE, $AF, $B0, $B1, $B2, $B2, $B3, $B4, $B5
    !byte $B6, $B7, $B7, $B8, $B9, $BA, $BB, $BC, $BD, $BE, $BE, $BF, $C0, $C1, $C2, $C3
    !byte $C4, $C5, $C5, $C6, $C7, $C8, $C9, $CA, $CB, $CC, $CC, $CD, $CE, $CF, $D0, $D1
    !byte $D2, $D3, $D4, $D5, $D5, $D7, $D7, $D8, $D9, $DA, $DB, $DC, $DD, $DE, $DF, $E0
    !byte $E1, $E2, $E2, $E4, $E4, $E5, $E6, $E7, $E8, $E9, $EA, $EB, $EC, $ED, $EE, $EF
    !byte $F0, $F1, $F2, $F3, $F4, $F5, $F6, $F7, $F8, $F9, $FA, $FB, $FC, $FD, $FE, $00
    !byte $4D, $FE, $4B, $FB, $47, $F6, $41, $EF, $39, $E6, $2F, $DB, $23, $CE, $15, $BF
    !byte $05, $AE, $F3, $9B, $DF, $86, $C9, $6F, $B1, $56, $97, $3B, $7B, $1E, $5D, $FF
    !byte $3D, $DE, $1B, $BB, $F7, $96, $D1, $6F, $A9, $46, $7F, $1B, $53, $EE, $25, $BF
    !byte $F5, $8E, $C3, $5B, $8F, $26, $59, $EF, $21, $B6, $E7, $7B, $AB, $3E, $6D, $FF
    !byte $2D, $BE, $EB, $7B, $A7, $36, $61, $EF, $19, $A6, $CF, $5B, $83, $0E, $35, $BF
    !byte $E5, $6E, $93, $1B, $3F, $C6, $E9, $6F, $91, $16, $37, $BB, $DB, $5E, $7D, $FF
    !byte $1D, $9E, $BB, $3B, $57, $D6, $F1, $6F, $89, $06, $1F, $9B, $B3, $2E, $45, $BF
    !byte $D5, $4E, $63, $DB, $EF, $66, $79, $EF, $01, $76, $87, $FB, $0B, $7E, $8D, $FF
    !byte $0D, $7E, $8B, $FB, $07, $76, $81, $EF, $F9, $66, $6F, $DB, $E3, $4E, $55, $BF
    !byte $C5, $2E, $33, $9B, $9F, $06, $09, $6F, $71, $D6, $D7, $3B, $3B, $9E, $9D, $FF
    !byte $FD, $5E, $5B, $BB, $B7, $16, $11, $6F, $69, $C6, $BF, $1B, $13, $6E, $65, $BF
    !byte $B5, $0E, $03, $5B, $4F, $A6, $99, $EF, $E1, $36, $27, $7B, $6B, $BE, $AD, $FF
    !byte $ED, $3E, $2B, $7B, $67, $B6, $A1, $EF, $D9, $26, $0F, $5B, $43, $8E, $75, $BF
    !byte $A5, $EE, $D3, $1B, $FF, $46, $29, $6F, $51, $96, $77, $BB, $9B, $DE, $BD, $FF
    !byte $DD, $1E, $FB, $3B, $17, $56, $31, $6F, $49, $86, $5F, $9B, $73, $AE, $85, $BF
    !byte $95, $CE, $A3, $DB, $AF, $E6, $B9, $EF, $C1, $F6, $C7, $FB, $CB, $FE, $CD, $FF
    !byte $CD, $FE, $CB, $FB, $C7, $F6, $C1, $EF, $B9, $E6, $AF, $DB, $A3, $CE, $95, $BF
    !byte $85, $AE, $73, $9B, $5F, $86, $49, $6F, $31, $56, $17, $3B, $FB, $1E, $DD, $FF
    !byte $BD, $DE, $9B, $BB, $77, $96, $51, $6F, $29, $46, $FF, $1B, $D3, $EE, $A5, $BF
    !byte $75, $8E, $43, $5B, $0F, $26, $D9, $EF, $A1, $B6, $67, $7B, $2B, $3E, $ED, $FF
    !byte $AD, $BE, $6B, $7B, $27, $36, $E1, $EF, $99, $A6, $4F, $5B, $03, $0E, $B5, $BF
    !byte $65, $6E, $13, $1B, $BF, $C6, $69, $6F, $11, $16, $B7, $BB, $5B, $5E, $FD, $FF
    !byte $9D, $9E, $3B, $3B, $D7, $D6, $71, $6F, $09, $06, $9F, $9B, $33, $2E, $C5, $BF
    !byte $55, $4E, $E3, $DB, $6F, $66, $F9, $EF, $81, $76, $07, $FB, $8B, $7E, $0D, $FF
    !byte $8D, $7E, $0B, $FB, $87, $76, $01, $EF, $79, $66, $EF, $DB, $63, $4E, $D5, $BF
    !byte $45, $2E, $B3, $9B, $1F, $06, $89, $6F, $F1, $D6, $57, $3B, $BB, $9E, $1D, $FF
    !byte $7D, $5E, $DB, $BB, $37, $16, $91, $6F, $E9, $C6, $3F, $1B, $93, $6E, $E5, $BF
    !byte $35, $0E, $83, $5B, $CF, $A6, $19, $EF, $61, $36, $A7, $7B, $EB, $BE, $2D, $FF
    !byte $6D, $3E, $AB, $7B, $E7, $B6, $21, $EF, $59, $26, $8F, $5B, $C3, $8E, $F5, $BF
    !byte $25, $EE, $53, $1B, $7F, $46, $A9, $6F, $D1, $96, $F7, $BB, $1B, $DE, $3D, $FF
    !byte $5D, $1E, $7B, $3B, $97, $56, $B1, $6F, $C9, $86, $DF, $9B, $F3, $AE, $05, $BF
    !byte $15, $CE, $23, $DB, $2F, $E6, $39, $EF, $41, $F6, $47, $FB, $4B, $FE, $4D, $00
    !byte $C0, $C0, $C1, $C1, $C2, $C2, $C3, $C3, $C4, $C4, $C5, $C5, $C6, $C6, $C7, $C7
    !byte $C8, $C8, $C8, $C9, $C9, $CA, $CA, $CB, $CB, $CC, $CC, $CD, $CD, $CE, $CE, $CE
    !byte $CF, $CF, $D0, $D0, $D0, $D1, $D1, $D2, $D2, $D3, $D3, $D4, $D4, $D4, $D5, $D5
    !byte $D5, $D6, $D6, $D7, $D7, $D8, $D8, $D8, $D9, $D9, $D9, $DA, $DA, $DB, $DB, $DB
    !byte $DC, $DC, $DC, $DD, $DD, $DE, $DE, $DE, $DF, $DF, $DF, $E0, $E0, $E1, $E1, $E1
    !byte $E1, $E2, $E2, $E3, $E3, $E3, $E3, $E4, $E4, $E5, $E5, $E5, $E5, $E6, $E6, $E6
    !byte $E7, $E7, $E7, $E8, $E8, $E8, $E8, $E9, $E9, $EA, $EA, $EA, $EA, $EB, $EB, $EB
    !byte $EB, $EC, $EC, $EC, $EC, $ED, $ED, $ED, $EE, $EE, $EE, $EE, $EF, $EF, $EF, $EF
    !byte $F0, $F0, $F0, $F0, $F1, $F1, $F1, $F1, $F1, $F2, $F2, $F2, $F2, $F3, $F3, $F3
    !byte $F3, $F4, $F4, $F4, $F4, $F5, $F5, $F5, $F5, $F5, $F5, $F6, $F6, $F6, $F6, $F6
    !byte $F6, $F7, $F7, $F7, $F7, $F8, $F8, $F8, $F8, $F8, $F8, $F9, $F9, $F9, $F9, $F9
    !byte $F9, $FA, $FA, $FA, $FA, $FA, $FA, $FA, $FA, $FB, $FB, $FB, $FB, $FB, $FB, $FB
    !byte $FB, $FC, $FC, $FC, $FC, $FC, $FC, $FC, $FC, $FD, $FD, $FD, $FD, $FD, $FD, $FD
    !byte $FD, $FD, $FD, $FE, $FD, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE
    !byte $FE, $FF, $FE, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FE, $FF, $FE, $FE
    !byte $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FD, $FE, $FD, $FD, $FD, $FD
    !byte $FD, $FD, $FD, $FD, $FD, $FD, $FC, $FC, $FC, $FC, $FC, $FC, $FC, $FC, $FB, $FB
    !byte $FB, $FB, $FB, $FB, $FB, $FB, $FA, $FA, $FA, $FA, $FA, $FA, $FA, $FA, $F9, $F9
    !byte $F9, $F9, $F9, $F9, $F8, $F8, $F8, $F8, $F8, $F8, $F7, $F7, $F7, $F7, $F6, $F6
    !byte $F6, $F6, $F6, $F6, $F5, $F5, $F5, $F5, $F5, $F5, $F4, $F4, $F4, $F4, $F3, $F3
    !byte $F3, $F3, $F2, $F2, $F2, $F2, $F1, $F1, $F1, $F1, $F1, $F0, $F0, $F0, $F0, $EF
    !byte $EF, $EF, $EF, $EE, $EE, $EE, $EE, $ED, $ED, $ED, $EC, $EC, $EC, $EC, $EB, $EB
    !byte $EB, $EB, $EA, $EA, $EA, $EA, $E9, $E9, $E8, $E8, $E8, $E8, $E7, $E7, $E7, $E6
    !byte $E6, $E6, $E5, $E5, $E5, $E5, $E4, $E4, $E3, $E3, $E3, $E3, $E2, $E2, $E1, $E1
    !byte $E1, $E1, $E0, $E0, $DF, $DF, $DF, $DE, $DE, $DE, $DD, $DD, $DC, $DC, $DC, $DB
    !byte $DB, $DB, $DA, $DA, $D9, $D9, $D9, $D8, $D8, $D8, $D7, $D7, $D6, $D6, $D5, $D5
    !byte $D5, $D4, $D4, $D4, $D3, $D3, $D2, $D2, $D1, $D1, $D0, $D0, $D0, $CF, $CF, $CE
    !byte $CE, $CE, $CD, $CD, $CC, $CC, $CB, $CB, $CA, $CA, $C9, $C9, $C8, $C8, $C8, $C7
    !byte $C7, $C6, $C6, $C5, $C5, $C4, $C4, $C3, $C3, $C2, $C2, $C1, $C1, $C0, $C0, $00
    !byte $00, $03, $06, $09, $0C, $10, $13, $16, $19, $1C, $1F, $22, $25, $28, $2B, $2E
    !byte $31, $33, $36, $39, $3C, $3F, $41, $44, $47, $49, $4C, $4E, $51, $53, $55, $58
    !byte $5A, $5C, $5E, $60, $62, $64, $66, $68, $6A, $6B, $6D, $6F, $70, $71, $73, $74
    !byte $75, $76, $78, $79, $7A, $7A, $7B, $7C, $7D, $7D, $7E, $7E, $7E, $7F, $7F, $7F
    !byte $7F, $7F, $7F, $7F, $7E, $7E, $7E, $7D, $7D, $7C, $7B, $7A, $7A, $79, $78, $76
    !byte $75, $74, $73, $71, $70, $6F, $6D, $6B, $6A, $68, $66, $64, $62, $60, $5E, $5C
    !byte $5A, $58, $55, $53, $51, $4E, $4C, $49, $47, $44, $41, $3F, $3C, $39, $36, $33
    !byte $31, $2E, $2B, $28, $25, $22, $1F, $1C, $19, $16, $13, $10, $0C, $09, $06, $03
    !byte $00, $FD, $FA, $F7, $F4, $F0, $ED, $EA, $E7, $E4, $E1, $DE, $DB, $D8, $D5, $D2
    !byte $CF, $CD, $CA, $C7, $C4, $C1, $BF, $BC, $B9, $B7, $B4, $B2, $AF, $AD, $AB, $A8
    !byte $A6, $A4, $A2, $A0, $9E, $9C, $9A, $98, $96, $95, $93, $91, $90, $8F, $8D, $8C
    !byte $8B, $8A, $88, $87, $86, $86, $85, $84, $83, $83, $82, $82, $82, $81, $81, $81
    !byte $81, $81, $81, $81, $82, $82, $82, $83, $83, $84, $85, $86, $86, $87, $88, $8A
    !byte $8B, $8C, $8D, $8F, $90, $91, $93, $95, $96, $98, $9A, $9C, $9E, $A0, $A2, $A4
    !byte $A6, $A8, $AB, $AD, $AF, $B2, $B4, $B7, $B9, $BC, $BF, $C1, $C4, $C7, $CA, $CD
    !byte $CF, $D2, $D5, $D8, $DB, $DE, $E1, $E4, $E7, $EA, $ED, $F0, $F4, $F7, $FA, $FD
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $20, $32, $40, $4A, $52, $59, $60, $65, $6A, $6E, $72, $76, $79, $7D
    !byte $80, $82, $85, $87, $8A, $8C, $8E, $90, $92, $94, $96, $98, $99, $9B, $9D, $9E
    !byte $A0, $A1, $A2, $A4, $A5, $A6, $A7, $A9, $AA, $AB, $AC, $AD, $AE, $AF, $B0, $B1
    !byte $B2, $B3, $B4, $B5, $B6, $B7, $B8, $B9, $B9, $BA, $BB, $BC, $BD, $BD, $BE, $BF
    !byte $C0, $C0, $C1, $C2, $C2, $C3, $C4, $C4, $C5, $C6, $C6, $C7, $C7, $C8, $C9, $C9
    !byte $CA, $CA, $CB, $CC, $CC, $CD, $CD, $CE, $CE, $CF, $CF, $D0, $D0, $D1, $D1, $D2
    !byte $D2, $D3, $D3, $D4, $D4, $D5, $D5, $D5, $D6, $D6, $D7, $D7, $D8, $D8, $D9, $D9
    !byte $D9, $DA, $DA, $DB, $DB, $DB, $DC, $DC, $DD, $DD, $DD, $DE, $DE, $DE, $DF, $DF
    !byte $E0, $E0, $E0, $E1, $E1, $E1, $E2, $E2, $E2, $E3, $E3, $E3, $E4, $E4, $E4, $E5
    !byte $E5, $E5, $E6, $E6, $E6, $E7, $E7, $E7, $E7, $E8, $E8, $E8, $E9, $E9, $E9, $EA
    !byte $EA, $EA, $EA, $EB, $EB, $EB, $EC, $EC, $EC, $EC, $ED, $ED, $ED, $ED, $EE, $EE
    !byte $EE, $EE, $EF, $EF, $EF, $EF, $F0, $F0, $F0, $F1, $F1, $F1, $F1, $F1, $F2, $F2
    !byte $F2, $F2, $F3, $F3, $F3, $F3, $F4, $F4, $F4, $F4, $F5, $F5, $F5, $F5, $F5, $F6
    !byte $F6, $F6, $F6, $F7, $F7, $F7, $F7, $F7, $F8, $F8, $F8, $F8, $F9, $F9, $F9, $F9
    !byte $F9, $FA, $FA, $FA, $FA, $FA, $FB, $FB, $FB, $FB, $FB, $FC, $FC, $FC, $FC, $FC
    !byte $FD, $FD, $FD, $FD, $FD, $FD, $FE, $FE, $FE, $FE, $FE, $FF, $FF, $FF, $FF, $FF
    !byte $20, $20, $1F, $1F, $1E, $1E, $1D, $1D, $1C, $1C, $1C, $1B, $1B, $1A, $1A, $19
    !byte $19, $19, $18, $18, $17, $17, $17, $16, $16, $15, $15, $15, $14, $14, $14, $13
    !byte $13, $13, $12, $12, $12, $11, $11, $11, $10, $10, $10, $0F, $0F, $0F, $0E, $0E
    !byte $0E, $0E, $0D, $0D, $0D, $0D, $0C, $0C, $0C, $0C, $0B, $0B, $0B, $0B, $0A, $0A
    !byte $0A, $0A, $0A, $09, $09, $09, $09, $09, $08, $08, $08, $08, $08, $08, $07, $07
    !byte $07, $07, $07, $07, $07, $06, $06, $06, $06, $06, $06, $06, $06, $05, $05, $05
    !byte $05, $05, $05, $05, $05, $05, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04
    !byte $04, $04, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03
    !byte $03, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02
    !byte $02, $02, $02, $02, $02, $02, $02, $02, $02, $01, $01, $01, $01, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $01, $04, $09, $10, $19, $24, $31, $40, $51, $64, $79, $90, $A9, $C4, $E1
    !byte $00, $21, $44, $69, $90, $B9, $E4, $11, $40, $71, $A4, $D9, $10, $49, $84, $C1
    !byte $00, $41, $84, $C9, $10, $59, $A4, $F1, $40, $91, $E4, $39, $90, $E9, $44, $A1
    !byte $00, $61, $C4, $29, $90, $F9, $64, $D1, $40, $B1, $24, $99, $10, $89, $04, $81
    !byte $00, $81, $04, $89, $10, $99, $24, $B1, $40, $D1, $64, $F9, $90, $29, $C4, $61
    !byte $00, $A1, $44, $E9, $90, $39, $E4, $91, $40, $F1, $A4, $59, $10, $C9, $84, $41
    !byte $00, $C1, $84, $49, $10, $D9, $A4, $71, $40, $11, $E4, $B9, $90, $69, $44, $21
    !byte $00, $E1, $C4, $A9, $90, $79, $64, $51, $40, $31, $24, $19, $10, $09, $04, $01
    !byte $00, $01, $04, $09, $10, $19, $24, $31, $40, $51, $64, $79, $90, $A9, $C4, $E1
    !byte $00, $21, $44, $69, $90, $B9, $E4, $11, $40, $71, $A4, $D9, $10, $49, $84, $C1
    !byte $00, $41, $84, $C9, $10, $59, $A4, $F1, $40, $91, $E4, $39, $90, $E9, $44, $A1
    !byte $00, $61, $C4, $29, $90, $F9, $64, $D1, $40, $B1, $24, $99, $10, $89, $04, $81
    !byte $00, $81, $04, $89, $10, $99, $24, $B1, $40, $D1, $64, $F9, $90, $29, $C4, $61
    !byte $00, $A1, $44, $E9, $90, $39, $E4, $91, $40, $F1, $A4, $59, $10, $C9, $84, $41
    !byte $00, $C1, $84, $49, $10, $D9, $A4, $71, $40, $11, $E4, $B9, $90, $69, $44, $21
    !byte $00, $E1, $C4, $A9, $90, $79, $64, $51, $40, $31, $24, $19, $10, $09, $04, $01
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $01, $01, $01, $01, $01, $01, $01, $02, $02, $02, $02, $02, $03, $03, $03, $03
    !byte $04, $04, $04, $04, $05, $05, $05, $05, $06, $06, $06, $07, $07, $07, $08, $08
    !byte $09, $09, $09, $0A, $0A, $0A, $0B, $0B, $0C, $0C, $0D, $0D, $0E, $0E, $0F, $0F
    !byte $10, $10, $11, $11, $12, $12, $13, $13, $14, $14, $15, $15, $16, $17, $17, $18
    !byte $19, $19, $1A, $1A, $1B, $1C, $1C, $1D, $1E, $1E, $1F, $20, $21, $21, $22, $23
    !byte $24, $24, $25, $26, $27, $27, $28, $29, $2A, $2B, $2B, $2C, $2D, $2E, $2F, $30
    !byte $31, $31, $32, $33, $34, $35, $36, $37, $38, $39, $3A, $3B, $3C, $3D, $3E, $3F
    !byte $40, $41, $42, $43, $44, $45, $46, $47, $48, $49, $4A, $4B, $4C, $4D, $4E, $4F
    !byte $51, $52, $53, $54, $55, $56, $57, $59, $5A, $5B, $5C, $5D, $5F, $60, $61, $62
    !byte $64, $65, $66, $67, $69, $6A, $6B, $6C, $6E, $6F, $70, $72, $73, $74, $76, $77
    !byte $79, $7A, $7B, $7D, $7E, $7F, $81, $82, $84, $85, $87, $88, $8A, $8B, $8D, $8E
    !byte $90, $91, $93, $94, $96, $97, $99, $9A, $9C, $9D, $9F, $A0, $A2, $A4, $A5, $A7
    !byte $A9, $AA, $AC, $AD, $AF, $B1, $B2, $B4, $B6, $B7, $B9, $BB, $BD, $BE, $C0, $C2
    !byte $C4, $C5, $C7, $C9, $CB, $CC, $CE, $D0, $D2, $D4, $D5, $D7, $D9, $DB, $DD, $DF
    !byte $E1, $E2, $E4, $E6, $E8, $EA, $EC, $EE, $F0, $F2, $F4, $F6, $F8, $FA, $FC, $FE
    !byte $00, $01, $02, $03, $04, $05, $06, $07, $08, $09, $09, $0A, $0B, $0C, $0D, $0E
    !byte $0F, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $1A, $1B, $1C, $1C, $1D
    !byte $1E, $1F, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $2A, $2B, $2C, $2D
    !byte $2E, $2F, $2F, $30, $31, $32, $33, $34, $35, $36, $37, $38, $39, $3A, $3B, $3C
    !byte $3D, $3E, $3F, $40, $41, $41, $42, $43, $44, $45, $46, $47, $48, $49, $4A, $4B
    !byte $4C, $4D, $4E, $4F, $50, $51, $52, $53, $54, $54, $55, $56, $57, $58, $59, $5A
    !byte $5B, $5C, $5D, $5E, $5F, $60, $61, $62, $63, $64, $65, $66, $67, $67, $68, $69
    !byte $6A, $6B, $6C, $6D, $6E, $6F, $70, $71, $72, $73, $74, $75, $76, $77, $78, $79
    !byte $7A, $7A, $7B, $7C, $7D, $7E, $7F, $80, $81, $82, $83, $84, $85, $86, $87, $88
    !byte $89, $8A, $8B, $8C, $8C, $8D, $8E, $8F, $90, $91, $92, $93, $94, $95, $96, $97
    !byte $98, $99, $9A, $9B, $9C, $9D, $9E, $9F, $9F, $A0, $A1, $A2, $A3, $A4, $A5, $A6
    !byte $A7, $A8, $A9, $AA, $AB, $AC, $AD, $AE, $AF, $B0, $B1, $B2, $B2, $B3, $B4, $B5
    !byte $B6, $B7, $B8, $B9, $BA, $BB, $BC, $BD, $BE, $BF, $C0, $C1, $C2, $C3, $C4, $C4
    !byte $C5, $C6, $C7, $C8, $C9, $CA, $CB, $CC, $CD, $CE, $CF, $D0, $D1, $D2, $D3, $D4
    !byte $D5, $D6, $D7, $D7, $D8, $D9, $DA, $DB, $DC, $DD, $DE, $DF, $E0, $E1, $E2, $E3
    !byte $E4, $E5, $E6, $E7, $E8, $E9, $EA, $EA, $EB, $EC, $ED, $EE, $EF, $F0, $F1, $F2
    !byte $00, $00, $01, $01, $02, $02, $03, $03, $03, $04, $04, $05, $05, $05, $06, $06
    !byte $07, $07, $08, $08, $08, $09, $09, $0A, $0A, $0A, $0B, $0B, $0C, $0C, $0D, $0D
    !byte $0D, $0E, $0E, $0F, $0F, $0F, $10, $10, $11, $11, $12, $12, $12, $13, $13, $14
    !byte $14, $14, $15, $15, $16, $16, $17, $17, $17, $18, $18, $19, $19, $19, $1A, $1A
    !byte $1B, $1B, $1C, $1C, $1C, $1D, $1D, $1E, $1E, $1F, $1F, $1F, $20, $20, $21, $21
    !byte $21, $22, $22, $23, $23, $24, $24, $24, $25, $25, $26, $26, $26, $27, $27, $28
    !byte $28, $29, $29, $29, $2A, $2A, $2B, $2B, $2B, $2C, $2C, $2D, $2D, $2E, $2E, $2E
    !byte $2F, $2F, $30, $30, $30, $31, $31, $32, $32, $33, $33, $33, $34, $34, $35, $35
    !byte $36, $36, $36, $37, $37, $38, $38, $38, $39, $39, $3A, $3A, $3B, $3B, $3B, $3C
    !byte $3C, $3D, $3D, $3D, $3E, $3E, $3F, $3F, $40, $40, $40, $41, $41, $42, $42, $42
    !byte $43, $43, $44, $44, $45, $45, $45, $46, $46, $47, $47, $47, $48, $48, $49, $49
    !byte $4A, $4A, $4A, $4B, $4B, $4C, $4C, $4C, $4D, $4D, $4E, $4E, $4F, $4F, $4F, $50
    !byte $50, $51, $51, $52, $52, $52, $53, $53, $54, $54, $54, $55, $55, $56, $56, $57
    !byte $57, $57, $58, $58, $59, $59, $59, $5A, $5A, $5B, $5B, $5C, $5C, $5C, $5D, $5D
    !byte $5E, $5E, $5E, $5F, $5F, $60, $60, $61, $61, $61, $62, $62, $63, $63, $63, $64
    !byte $64, $65, $65, $66, $66, $66, $67, $67, $68, $68, $68, $69, $69, $6A, $6A, $6B

; Source interval $C100-$CBA3
* = REG_GAME
    lda MATH_IO+$10
    sta V1_SCRATCH
    lda MATH_IO+$11
    sta V1_SCRATCH+$01
    lda MATH_IO+$12
    sta V1_SCRATCH+$02
    lda MATH_IO+$13
    sta V1_SCRATCH+$03
    lda MATH_IO+$14
    sta V1_SCRATCH+$04
    lda MATH_IO+$15
    sta V1_SCRATCH+$05
    lda MATH_IO+$16
    sta V1_SCRATCH+$06
    lda MATH_IO+$17
    sta V1_SCRATCH+$07
    jsr REG_GAME+$013E
    rts
    lda MATH_IO+$14
    ora MATH_IO+$15
    ora MATH_IO+$16
    ora MATH_IO+$17
    bne LC146
    jsr REG_LOW+$1A00
    rts
LC146:
    lda MATH_IO+$13
    eor MATH_IO+$17
    and #$80
    sta V1_SCRATCH+$08
    lda MATH_IO+$13
    and #$80
    sta V1_SCRATCH+$09
    lda MATH_IO+$10
    sta V1_SCRATCH
    lda MATH_IO+$11
    sta V1_SCRATCH+$01
    lda MATH_IO+$12
    sta V1_SCRATCH+$02
    lda MATH_IO+$13
    sta V1_SCRATCH+$03
    bpl LC194
    sec
    lda #$00
    sbc V1_SCRATCH
    sta V1_SCRATCH
    lda #$00
    sbc V1_SCRATCH+$01
    sta V1_SCRATCH+$01
    lda #$00
    sbc V1_SCRATCH+$02
    sta V1_SCRATCH+$02
    lda #$00
    sbc V1_SCRATCH+$03
    sta V1_SCRATCH+$03
LC194:
    lda MATH_IO+$14
    sta V1_SCRATCH+$04
    lda MATH_IO+$15
    sta V1_SCRATCH+$05
    lda MATH_IO+$16
    sta V1_SCRATCH+$06
    lda MATH_IO+$17
    sta V1_SCRATCH+$07
    bpl LC1CF
    sec
    lda #$00
    sbc V1_SCRATCH+$04
    sta V1_SCRATCH+$04
    lda #$00
    sbc V1_SCRATCH+$05
    sta V1_SCRATCH+$05
    lda #$00
    sbc V1_SCRATCH+$06
    sta V1_SCRATCH+$06
    lda #$00
    sbc V1_SCRATCH+$07
    sta V1_SCRATCH+$07
LC1CF:
    jsr REG_LOW+$1A1C
    bcs LC221
    lda V1_SCRATCH+$08
    beq LC1FA
    sec
    lda #$00
    sbc MATH_IO+$18
    sta MATH_IO+$18
    lda #$00
    sbc MATH_IO+$19
    sta MATH_IO+$19
    lda #$00
    sbc MATH_IO+$1A
    sta MATH_IO+$1A
    lda #$00
    sbc MATH_IO+$1B
    sta MATH_IO+$1B
LC1FA:
    lda V1_SCRATCH+$09
    beq LC220
    sec
    lda #$00
    sbc MATH_IO+$1C
    sta MATH_IO+$1C
    lda #$00
    sbc MATH_IO+$1D
    sta MATH_IO+$1D
    lda #$00
    sbc MATH_IO+$1E
    sta MATH_IO+$1E
    lda #$00
    sbc MATH_IO+$1F
    sta MATH_IO+$1F
LC220:
    clc
LC221:
    rts
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    sec
    rts
    lda V1_SCRATCH+$04
    ora V1_SCRATCH+$05
    ora V1_SCRATCH+$06
    ora V1_SCRATCH+$07
    bne LC250
    jsr REG_GAME+$0122
    rts
LC250:
    lda V1_SCRATCH+$07
    beq LC258
    jmp REG_GAME+$0223
LC258:
    lda V1_SCRATCH+$06
    beq LC260
    jmp REG_GAME+$031F
LC260:
    lda V1_SCRATCH+$05
    beq LC268
    jmp REG_GAME+$01BB
LC268:
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda V1_SCRATCH+$01
    sta MATH_IO+$19
    lda V1_SCRATCH+$02
    sta MATH_IO+$1A
    lda V1_SCRATCH+$03
    sta MATH_IO+$1B
    lda #$00
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$20
LC290:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1B
    rol MATH_IO+$1C
    bcs LC2A9
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc LC2B6
LC2A9:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    inc MATH_IO+$18
LC2B6:
    dex
    bne LC290
    clc
    rts
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda V1_SCRATCH+$01
    sta MATH_IO+$19
    lda V1_SCRATCH+$02
    sta MATH_IO+$1A
    lda #$00
    sta MATH_IO+$1B
    lda V1_SCRATCH+$03
    sta MATH_IO+$1C
    lda #$00
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$18
LC2E5:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    bcs LC308
    lda MATH_IO+$1D
    cmp V1_SCRATCH+$05
    bcc LC31E
    bne LC308
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc LC31E
LC308:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc V1_SCRATCH+$05
    sta MATH_IO+$1D
    inc MATH_IO+$18
LC31E:
    dex
    bne LC2E5
    clc
    rts
    lda V1_SCRATCH+$03
    cmp V1_SCRATCH+$07
    bcc LC369
    bne LC391
    lda V1_SCRATCH+$02
    cmp V1_SCRATCH+$06
    bcc LC369
    bne LC391
    lda V1_SCRATCH+$01
    cmp V1_SCRATCH+$05
    bcc LC369
    bne LC391
    lda V1_SCRATCH
    cmp V1_SCRATCH+$04
    bcc LC369
    bne LC391
    lda #$01
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    clc
    rts
LC369:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH
    sta MATH_IO+$1C
    lda V1_SCRATCH+$01
    sta MATH_IO+$1D
    lda V1_SCRATCH+$02
    sta MATH_IO+$1E
    lda V1_SCRATCH+$03
    sta MATH_IO+$1F
    clc
    rts
LC391:
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH+$01
    sta MATH_IO+$1C
    lda V1_SCRATCH+$02
    sta MATH_IO+$1D
    lda V1_SCRATCH+$03
    sta MATH_IO+$1E
    lda #$00
    sta MATH_IO+$1F
    ldx #$08
LC3BB:
    asl MATH_IO+$18
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs LC3F2
    lda MATH_IO+$1F
    cmp V1_SCRATCH+$07
    bcc LC41A
    bne LC3F2
    lda MATH_IO+$1E
    cmp V1_SCRATCH+$06
    bcc LC41A
    bne LC3F2
    lda MATH_IO+$1D
    cmp V1_SCRATCH+$05
    bcc LC41A
    bne LC3F2
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc LC41A
LC3F2:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc V1_SCRATCH+$05
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc V1_SCRATCH+$06
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc V1_SCRATCH+$07
    sta MATH_IO+$1F
    inc MATH_IO+$18
LC41A:
    dex
    bne LC3BB
    clc
    rts
    lda V1_SCRATCH+$03
    cmp V1_SCRATCH+$07
    bcc LC465
    bne LC48D
    lda V1_SCRATCH+$02
    cmp V1_SCRATCH+$06
    bcc LC465
    bne LC48D
    lda V1_SCRATCH+$01
    cmp V1_SCRATCH+$05
    bcc LC465
    bne LC48D
    lda V1_SCRATCH
    cmp V1_SCRATCH+$04
    bcc LC465
    bne LC48D
    lda #$01
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    clc
    rts
LC465:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH
    sta MATH_IO+$1C
    lda V1_SCRATCH+$01
    sta MATH_IO+$1D
    lda V1_SCRATCH+$02
    sta MATH_IO+$1E
    lda V1_SCRATCH+$03
    sta MATH_IO+$1F
    clc
    rts
LC48D:
    lda V1_SCRATCH
    sta MATH_IO+$18
    lda V1_SCRATCH+$01
    sta MATH_IO+$19
    lda #$00
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda V1_SCRATCH+$02
    sta MATH_IO+$1C
    lda V1_SCRATCH+$03
    sta MATH_IO+$1D
    lda #$00
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$10
LC4B7:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs LC4F1
    lda MATH_IO+$1F
    cmp V1_SCRATCH+$07
    bcc LC519
    bne LC4F1
    lda MATH_IO+$1E
    cmp V1_SCRATCH+$06
    bcc LC519
    bne LC4F1
    lda MATH_IO+$1D
    cmp V1_SCRATCH+$05
    bcc LC519
    bne LC4F1
    lda MATH_IO+$1C
    cmp V1_SCRATCH+$04
    bcc LC519
LC4F1:
    sec
    lda MATH_IO+$1C
    sbc V1_SCRATCH+$04
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc V1_SCRATCH+$05
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc V1_SCRATCH+$06
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc V1_SCRATCH+$07
    sta MATH_IO+$1F
    inc MATH_IO+$18
LC519:
    dex
    bne LC4B7
    clc
    rts
    jsr REG_API+$0020
    lda MATH_IO+$09
    sta MATH_IO+$08
    lda MATH_IO+$0A
    sta MATH_IO+$09
    lda MATH_IO+$0B
    sta MATH_IO+$0A
    clc
    rts
    jsr REG_API+$0BB0
    lda MATH_IO+$09
    sta MATH_IO+$08
    lda MATH_IO+$0A
    sta MATH_IO+$09
    lda MATH_IO+$0B
    sta MATH_IO+$0A
    clc
    rts
    jsr REG_API+$00B0
    lda MATH_IO+$0A
    sta MATH_IO+$08
    lda MATH_IO+$0B
    sta MATH_IO+$09
    lda MATH_IO+$0C
    sta MATH_IO+$0A
    lda MATH_IO+$0D
    sta MATH_IO+$0B
    lda MATH_IO+$0E
    sta MATH_IO+$0C
    lda MATH_IO+$0F
    sta MATH_IO+$0D
    clc
    rts
    jsr REG_API+$0C40
    lda MATH_IO+$0A
    sta MATH_IO+$08
    lda MATH_IO+$0B
    sta MATH_IO+$09
    lda MATH_IO+$0C
    sta MATH_IO+$0A
    lda MATH_IO+$0D
    sta MATH_IO+$0B
    lda MATH_IO+$0E
    sta MATH_IO+$0C
    lda MATH_IO+$0F
    sta MATH_IO+$0D
    clc
    rts
    lda MATH_IO+$10
    sta V1_SCRATCH
    lda MATH_IO+$11
    sta V1_SCRATCH+$01
    lda MATH_IO+$12
    sta V1_SCRATCH+$02
    lda MATH_IO+$13
    sta V1_SCRATCH+$03
    lda #$00
    sta MATH_IO+$10
    lda V1_SCRATCH
    sta MATH_IO+$11
    lda V1_SCRATCH+$01
    sta MATH_IO+$12
    lda #$00
    sta MATH_IO+$13
    jsr REG_API+$01B0
    lda V1_SCRATCH
    sta MATH_IO+$10
    lda V1_SCRATCH+$01
    sta MATH_IO+$11
    lda V1_SCRATCH+$02
    sta MATH_IO+$12
    lda V1_SCRATCH+$03
    sta MATH_IO+$13
    rts
    lda MATH_IO+$10
    sta V1_SCRATCH
    lda MATH_IO+$11
    sta V1_SCRATCH+$01
    lda MATH_IO+$12
    sta V1_SCRATCH+$02
    lda MATH_IO+$13
    sta V1_SCRATCH+$03
    lda #$00
    sta MATH_IO+$10
    lda V1_SCRATCH
    sta MATH_IO+$11
    lda V1_SCRATCH+$01
    sta MATH_IO+$12
    bpl LC617
    lda #$FF
    bne LC619
LC617:
    lda #$00
LC619:
    sta MATH_IO+$13
    jsr REG_API+$0EE0
    lda V1_SCRATCH
    sta MATH_IO+$10
    lda V1_SCRATCH+$01
    sta MATH_IO+$11
    lda V1_SCRATCH+$02
    sta MATH_IO+$12
    lda V1_SCRATCH+$03
    sta MATH_IO+$13
    rts
    lda MATH_IO+$15
    cmp #$80
    bcc LC64D
    bne LC648
    lda MATH_IO+$14
    cmp #$01
    bcc LC64D
LC648:
    lda #$01
    jmp REG_GAME+$0673
LC64D:
    lda MATH_IO+$15
    cmp #$55
    bcc LC662
    bne LC65D
    lda MATH_IO+$14
    cmp #$56
    bcc LC662
LC65D:
    lda #$02
    jmp REG_GAME+$0673
LC662:
    lda MATH_IO+$15
    cmp #$40
    bcc LC677
    bne LC672
    lda MATH_IO+$14
    cmp #$01
    bcc LC677
LC672:
    lda #$03
    jmp REG_GAME+$0673
LC677:
    lda MATH_IO+$15
    cmp #$33
    bcc LC68C
    bne LC687
    lda MATH_IO+$14
    cmp #$34
    bcc LC68C
LC687:
    lda #$04
    jmp REG_GAME+$0673
LC68C:
    lda MATH_IO+$15
    cmp #$2A
    bcc LC6A1
    bne LC69C
    lda MATH_IO+$14
    cmp #$AB
    bcc LC6A1
LC69C:
    lda #$05
    jmp REG_GAME+$0673
LC6A1:
    lda MATH_IO+$15
    cmp #$24
    bcc LC6B6
    bne LC6B1
    lda MATH_IO+$14
    cmp #$93
    bcc LC6B6
LC6B1:
    lda #$06
    jmp REG_GAME+$0673
LC6B6:
    lda MATH_IO+$15
    cmp #$20
    bcc LC6CB
    bne LC6C6
    lda MATH_IO+$14
    cmp #$01
    bcc LC6CB
LC6C6:
    lda #$07
    jmp REG_GAME+$0673
LC6CB:
    lda MATH_IO+$15
    cmp #$1C
    bcc LC6E0
    bne LC6DB
    lda MATH_IO+$14
    cmp #$72
    bcc LC6E0
LC6DB:
    lda #$08
    jmp REG_GAME+$0673
LC6E0:
    lda MATH_IO+$15
    cmp #$19
    bcc LC6F5
    bne LC6F0
    lda MATH_IO+$14
    cmp #$9A
    bcc LC6F5
LC6F0:
    lda #$09
    jmp REG_GAME+$0673
LC6F5:
    lda MATH_IO+$15
    cmp #$17
    bcc LC70A
    bne LC705
    lda MATH_IO+$14
    cmp #$46
    bcc LC70A
LC705:
    lda #$0A
    jmp REG_GAME+$0673
LC70A:
    lda MATH_IO+$15
    cmp #$15
    bcc LC71F
    bne LC71A
    lda MATH_IO+$14
    cmp #$56
    bcc LC71F
LC71A:
    lda #$0B
    jmp REG_GAME+$0673
LC71F:
    lda MATH_IO+$15
    cmp #$13
    bcc LC734
    bne LC72F
    lda MATH_IO+$14
    cmp #$B2
    bcc LC734
LC72F:
    lda #$0C
    jmp REG_GAME+$0673
LC734:
    lda MATH_IO+$15
    cmp #$12
    bcc LC749
    bne LC744
    lda MATH_IO+$14
    cmp #$4A
    bcc LC749
LC744:
    lda #$0D
    jmp REG_GAME+$0673
LC749:
    lda MATH_IO+$15
    cmp #$11
    bcc LC75E
    bne LC759
    lda MATH_IO+$14
    cmp #$12
    bcc LC75E
LC759:
    lda #$0E
    jmp REG_GAME+$0673
LC75E:
    lda MATH_IO+$15
    cmp #$10
    bcc LC780
    bne LC76E
    lda MATH_IO+$14
    cmp #$01
    bcc LC780
LC76E:
    lda #$0F
    jmp REG_GAME+$0673
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    clc
    rts
LC780:
    lda MATH_IO+$10
    sta V1_SCRATCH+$0E
    lda MATH_IO+$11
    sta V1_SCRATCH+$0F
    lda MATH_IO+$12
    sta V1_SCRATCH+$10
    lda MATH_IO+$13
    sta V1_SCRATCH+$11
    lda MATH_IO+$16
    sta V1_SCRATCH+$14
    lda MATH_IO+$17
    sta V1_SCRATCH+$15
    lda #$00
    sta MATH_IO+$10
    sta MATH_IO+$11
    lda #$01
    sta MATH_IO+$12
    lda #$00
    sta MATH_IO+$13
    sta MATH_IO+$16
    sta MATH_IO+$17
    jsr REG_API+$0170
    lda V1_SCRATCH+$0E
    sta MATH_IO+$10
    lda V1_SCRATCH+$0F
    sta MATH_IO+$11
    lda V1_SCRATCH+$10
    sta MATH_IO+$12
    lda V1_SCRATCH+$11
    sta MATH_IO+$13
    lda V1_SCRATCH+$14
    sta MATH_IO+$16
    lda V1_SCRATCH+$15
    sta MATH_IO+$17
    rts
    ldx MATH_IO
    lda REG_TABLE+$3400,x
    sta MATH_IO+$08
    clc
    rts
    lda MATH_IO
    clc
    adc #$40
    tax
    lda REG_TABLE+$3400,x
    sta MATH_IO+$08
    clc
    rts
    ldx MATH_IO
    lda REG_TABLE+$3400,x
    sta MATH_IO+$08
    txa
    clc
    adc #$40
    tax
    lda REG_TABLE+$3400,x
    sta MATH_IO+$09
    clc
    rts
    lda MATH_IO
    bne LC82F
    lda MATH_IO+$04
    beq LC82A
    bmi LC825
    lda #$40
    jmp REG_GAME+$07D6
LC825:
    lda #$C0
    jmp REG_GAME+$07D6
LC82A:
    lda #$00
    jmp REG_GAME+$07D6
LC82F:
    lda MATH_IO+$04
    bne LC843
    lda MATH_IO
    bmi LC83E
    lda #$00
    jmp REG_GAME+$07D6
LC83E:
    lda #$80
    jmp REG_GAME+$07D6
LC843:
    lda #$00
    sta V1_SCRATCH+$0C
    lda MATH_IO
    bpl LC85E
    lda #$01
    sta V1_SCRATCH+$0C
    sec
    lda #$00
    sbc MATH_IO
    sta V1_SCRATCH+$0A
    jmp REG_GAME+$0761
LC85E:
    sta V1_SCRATCH+$0A
    lda MATH_IO+$04
    bpl LC87A
    lda V1_SCRATCH+$0C
    ora #$02
    sta V1_SCRATCH+$0C
    sec
    lda #$00
    sbc MATH_IO+$04
    sta V1_SCRATCH+$0B
    jmp REG_GAME+$077D
LC87A:
    sta V1_SCRATCH+$0B
    ldx V1_SCRATCH+$0A
    lda REG_TABLE+$3600,x
    ldx V1_SCRATCH+$0B
    sec
    sbc REG_TABLE+$3600,x
    bcc LC896
    tax
    lda REG_TABLE+$3700,x
    sta V1_SCRATCH+$0D
    jmp REG_GAME+$07AB
LC896:
    eor #$FF
    clc
    adc #$01
    tax
    lda REG_TABLE+$3700,x
    sta V1_SCRATCH+$0D
    lda #$40
    sec
    sbc V1_SCRATCH+$0D
    sta V1_SCRATCH+$0D
    lda V1_SCRATCH+$0C
    beq LC8D3
    cmp #$01
    beq LC8CA
    cmp #$03
    beq LC8C1
    lda #$00
    sec
    sbc V1_SCRATCH+$0D
    jmp REG_GAME+$07D6
LC8C1:
    lda #$80
    clc
    adc V1_SCRATCH+$0D
    jmp REG_GAME+$07D6
LC8CA:
    lda #$80
    sec
    sbc V1_SCRATCH+$0D
    jmp REG_GAME+$07D6
LC8D3:
    lda V1_SCRATCH+$0D
    sta MATH_IO+$08
    clc
    rts
    lda #$00
    sta V1_SCRATCH+$13
    lda V1_SCRATCH+$13
    ora #$80
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC8FD
    bne LC900
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC8FD
    beq LC8FD
    jmp REG_GAME+$0800
LC8FD:
    stx V1_SCRATCH+$13
LC900:
    lda V1_SCRATCH+$13
    ora #$40
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC91D
    bne LC920
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC91D
    beq LC91D
    jmp REG_GAME+$0820
LC91D:
    stx V1_SCRATCH+$13
LC920:
    lda V1_SCRATCH+$13
    ora #$20
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC93D
    bne LC940
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC93D
    beq LC93D
    jmp REG_GAME+$0840
LC93D:
    stx V1_SCRATCH+$13
LC940:
    lda V1_SCRATCH+$13
    ora #$10
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC95D
    bne LC960
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC95D
    beq LC95D
    jmp REG_GAME+$0860
LC95D:
    stx V1_SCRATCH+$13
LC960:
    lda V1_SCRATCH+$13
    ora #$08
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC97D
    bne LC980
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC97D
    beq LC97D
    jmp REG_GAME+$0880
LC97D:
    stx V1_SCRATCH+$13
LC980:
    lda V1_SCRATCH+$13
    ora #$04
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC99D
    bne LC9A0
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC99D
    beq LC99D
    jmp REG_GAME+$08A0
LC99D:
    stx V1_SCRATCH+$13
LC9A0:
    lda V1_SCRATCH+$13
    ora #$02
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC9BD
    bne LC9C0
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC9BD
    beq LC9BD
    jmp REG_GAME+$08C0
LC9BD:
    stx V1_SCRATCH+$13
LC9C0:
    lda V1_SCRATCH+$13
    ora #$01
    tax
    lda REG_TABLE+$3900,x
    cmp MATH_IO+$11
    bcc LC9DD
    bne LC9E0
    lda REG_TABLE+$3800,x
    cmp MATH_IO+$10
    bcc LC9DD
    beq LC9DD
    jmp REG_GAME+$08E0
LC9DD:
    stx V1_SCRATCH+$13
LC9E0:
    lda V1_SCRATCH+$13
    sta MATH_IO+$08
    lda #$00
    sta MATH_IO+$09
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00
    ldy #$04
LCA26:
    txa
    asl
    rol V1_SCRATCH+$01
    rol V1_SCRATCH+$02
    rol V1_SCRATCH+$03
    asl
    rol V1_SCRATCH+$01
    rol V1_SCRATCH+$02
    rol V1_SCRATCH+$03
    tax
    asl V1_SCRATCH+$04
    rol V1_SCRATCH+$05
    lda V1_SCRATCH+$04
    asl
    ora #$01
    sta V1_SCRATCH+$06
    lda V1_SCRATCH+$05
    rol
    sta V1_SCRATCH+$07
    bcc LCA5F
    lda V1_SCRATCH+$03
    beq LCA94
    cmp #$01
    bne LCA76
    beq LCA64
LCA5F:
    lda V1_SCRATCH+$03
    bne LCA76
LCA64:
    lda V1_SCRATCH+$02
    cmp V1_SCRATCH+$07
    bcc LCA94
    bne LCA76
    lda V1_SCRATCH+$01
    cmp V1_SCRATCH+$06
    bcc LCA94
LCA76:
    sec
    lda V1_SCRATCH+$01
    sbc V1_SCRATCH+$06
    sta V1_SCRATCH+$01
    lda V1_SCRATCH+$02
    sbc V1_SCRATCH+$07
    sta V1_SCRATCH+$02
    lda V1_SCRATCH+$03
    sbc #$00
    sta V1_SCRATCH+$03
    inc V1_SCRATCH+$04
LCA94:
    dey
    bne LCA26
    rts
    !byte $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA
    !byte $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA
    !byte $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA
    !byte $EA, $EA, $EA, $EA
    lda MATH_IO
    bpl LCAD7
    sec
    lda #$00
    sbc MATH_IO
LCAD7:
    sta V1_SCRATCH+$0A
    lda MATH_IO+$04
    bpl LCAE5
    sec
    lda #$00
    sbc MATH_IO+$04
LCAE5:
    sta V1_SCRATCH+$0B
    cmp V1_SCRATCH+$0A
    bcc LCAFB
    lda V1_SCRATCH+$0A
    pha
    lda V1_SCRATCH+$0B
    sta V1_SCRATCH+$0A
    pla
    sta V1_SCRATCH+$0B
LCAFB:
    rts
    jsr REG_GAME+$09CC
    lda V1_SCRATCH+$0B
    lsr
    clc
    adc V1_SCRATCH+$0A
    sta MATH_IO+$08
    clc
    rts
    jsr REG_GAME+$09CC
    ldx V1_SCRATCH+$0A
    lda REG_TABLE+$3A00,x
    ldx V1_SCRATCH+$0B
    clc
    adc REG_TABLE+$3B00,x
    sta MATH_IO+$08
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta V1_SCRATCH+$08
    lda MATH_IO+$11
    sta V1_SCRATCH+$09
    lda MATH_IO+$12
    sta MATH_IO+$10
    lda MATH_IO+$13
    sta MATH_IO+$11
    jsr REG_GAME_API+$002D
    lda V1_SCRATCH+$08
    sta MATH_IO+$10
    lda V1_SCRATCH+$09
    sta MATH_IO+$11
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
