; GENERATED CANONICAL SOURCE. Builds the stable 46-entry API from symbolic assembly source.
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
MATH_VEC2_NORMALIZE_Q8_8 = REG_GAME_API+$0039
MATH_REU_UMUL16_BEGIN = REG_API+$0800
MATH_REU_UMUL16 = REG_API+$0840
MATH_REU_UMUL16_END = REG_API+$0880
MATH_REU_UMUL32_BEGIN = REG_API+$08C0
MATH_REU_UMUL32 = REG_API+$0900
MATH_REU_UMUL32_END = REG_API+$0960
MATH_INIT = REG_API+$0280
MATH_X = MATH_IO
MATH_Y = MATH_IO+$04
MATH_Z = MATH_IO+$08
MATH_N = MATH_IO+$10
MATH_D = MATH_IO+$14
MATH_Q = MATH_IO+$18
MATH_R = MATH_IO+$1C


; Source interval $1000-$2FFF
* = REG_LOW
    lda+1 TURBO32_ZP_BASE+$44
    sta+1 TURBO32_ZP_BASE+$4C
    eor #$FF
    sta+1 TURBO32_ZP_BASE+$47
    sta+1 TURBO32_ZP_BASE+$4F
    lda+1 TURBO32_ZP_BASE+$52
    sta+1 TURBO32_ZP_BASE+$5C
    eor #$FF
    sta+1 TURBO32_ZP_BASE+$57
    sta+1 TURBO32_ZP_BASE+$5F
    lda+1 TURBO32_ZP_BASE+$62
    sta+1 TURBO32_ZP_BASE+$6C
    eor #$FF
    sta+1 TURBO32_ZP_BASE+$67
    sta+1 TURBO32_ZP_BASE+$6F
    lda+1 TURBO32_ZP_BASE+$72
    sta+1 TURBO32_ZP_BASE+$7C
    eor #$FF
    sta+1 TURBO32_ZP_BASE+$77
    sta+1 TURBO32_ZP_BASE+$7F
    ldx #$04
    sec
    jmp TURBO32_ZP_BASE+$43
    inc+1 TURBO32_ZP_BASE+$0B
    bne L1038
    inc+1 TURBO32_ZP_BASE+$0F
    bne L1038
    inc+1 TURBO32_ZP_BASE+$12
L1038:
    clc
    jmp REG_LOW+$012F
    inc+1 TURBO32_ZP_BASE+$0F
    bne L1042
    inc+1 TURBO32_ZP_BASE+$12
L1042:
    jmp REG_LOW+$0141
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
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
    tay
    clc
    lda+1 TURBO32_ZP_BASE+$04
    adc+1 TURBO32_ZP_BASE+$01
    sta+1 TURBO32_ZP_BASE+$01
    lda+1 TURBO32_ZP_BASE+$02
    adc+1 TURBO32_ZP_BASE+$05
    bcc L1110
    inx
    clc
L1110:
    adc+1 TURBO32_ZP_BASE+$08
    sta+1 TURBO32_ZP_BASE+$02
    lda+1 TURBO32_ZP_BASE+$0C
    adc+1 TURBO32_ZP_BASE+$09
    bcc L1128
    iny
    cpx #$01
    adc+1 TURBO32_ZP_BASE+$03
    bcc L112F
    clc
    iny
    bne L112F
    jmp REG_LOW+$002E
L1128:
    adc+1 TURBO32_ZP_BASE+$03
    bcc L112D
    iny
L112D:
    cpx #$01
L112F:
    adc+1 TURBO32_ZP_BASE+$06
    sta+1 TURBO32_ZP_BASE+$03
    tya
    ldx+1 TURBO32_ZP_BASE+$10
    adc+1 TURBO32_ZP_BASE+$0D
    bcs L1168
    adc+1 TURBO32_ZP_BASE+$07
    bcc L1142
    inx
    beq L1171
L1141:
    clc
L1142:
    adc+1 TURBO32_ZP_BASE+$0A
    tay
    txa
    adc+1 TURBO32_ZP_BASE+$0B
    bcs L1159
    adc+1 TURBO32_ZP_BASE+$0E
    tax
    lda+1 TURBO32_ZP_BASE+$11
    adc+1 TURBO32_ZP_BASE+$0F
    bcs L1156
    rts
L1154:
    adc #$00
L1156:
    inc+1 TURBO32_ZP_BASE+$12
    rts
L1159:
    clc
    adc+1 TURBO32_ZP_BASE+$0E
    tax
    lda+1 TURBO32_ZP_BASE+$11
    adc+1 TURBO32_ZP_BASE+$0F
    bcs L1154
    adc #$01
    bcs L1156
    rts
L1168:
    inx
    clc
    adc+1 TURBO32_ZP_BASE+$07
    bcc L1142
    inx
    bne L1141
L1171:
    jmp REG_LOW+$003C
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    sta ZP_MAIN+$33
    eor #$FF
    sta ZP_MAIN+$31
    sta ZP_MAIN+$35
    txa
    sta ZP_MAIN+$23
    eor #$FF
    sta ZP_MAIN+$21
    sta ZP_MAIN+$25
    lda ZP_MAIN+$27
    sta ZP_MAIN+$2B
    eor #$FF
    sta ZP_MAIN+$29
    sta ZP_MAIN+$2D
    sec
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta REG_LOW+$051E
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L1473
    adc (ZP_MAIN+$29),y
    sta REG_LOW+$04F2
    lda (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcs L1483
L1438:
    adc (ZP_MAIN+$31),y
    sta REG_LOW+$04F8
    lda (ZP_MAIN+$33),y
    adc (ZP_MAIN+$35),y
    sta REG_LOW+$04FF
    ldy #$00
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta REG_LOW+$04F4
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L1490
    adc (ZP_MAIN+$29),y
    sta REG_LOW+$04FA
    lda (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcs L14A0
L1462:
    adc (ZP_MAIN+$31),y
    sta REG_LOW+$0501
    lda (ZP_MAIN+$33),y
    adc (ZP_MAIN+$35),y
    sta REG_LOW+$0515
    ldy #$00
    jmp REG_LOW+$04CA
L1473:
    clc
    adc (ZP_MAIN+$29),y
    sta REG_LOW+$04F2
    lda #$01
    adc (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcc L1438
L1483:
    clc
    adc (ZP_MAIN+$31),y
    sta REG_LOW+$04F8
    lda #$01
    adc (ZP_MAIN+$33),y
    jmp REG_LOW+$043F
L1490:
    clc
    adc (ZP_MAIN+$29),y
    sta REG_LOW+$04FA
    lda #$01
    adc (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcc L1462
L14A0:
    clc
    adc (ZP_MAIN+$31),y
    sta REG_LOW+$0501
    lda #$01
    adc (ZP_MAIN+$33),y
    jmp REG_LOW+$0469
L14AD:
    clc
    adc (ZP_MAIN+$29),y
    sta REG_LOW+$0511
    lda #$01
    adc (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcc L14E6
L14BD:
    clc
    adc (ZP_MAIN+$31),y
    sta REG_LOW+$0517
    lda #$01
    adc (ZP_MAIN+$33),y
    jmp REG_LOW+$04ED
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta REG_LOW+$050C
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L14AD
    adc (ZP_MAIN+$29),y
    sta REG_LOW+$0511
    lda (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcs L14BD
L14E6:
    adc (ZP_MAIN+$31),y
    sta REG_LOW+$0517
    lda (ZP_MAIN+$33),y
    adc (ZP_MAIN+$35),y
    tax
    clc
    lda #$00
    adc #$00
    sta ZP_MAIN+$29
    lda #$00
    adc #$00
    sta REG_LOW+$050A
    lda #$00
    adc #$00
    tay
    bcc L1509
    clc
    inc REG_LOW+$0515
L1509:
    lda #$00
    adc #$00
    sta ZP_MAIN+$31
    tya
    adc #$00
    sta ZP_MAIN+$25
    lda #$00
    adc #$00
    sta ZP_MAIN+$2D
    txa
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
    !byte $00, $00
    sta REG_LOW+$065D
    sta REG_LOW+$0665
    eor #$FF
    sta REG_LOW+$0660
    sta REG_LOW+$0668
    lda ZP_MAIN+$02
    sta REG_LOW+$066B
    eor #$FF
    sta ZP_MAIN
    sta REG_LOW+$0676
    lda ZP_MAIN+$06
    sta REG_LOW+$0679
    eor #$FF
    sta ZP_MAIN+$04
    sta REG_LOW+$0684
    lda ZP_MAIN+$0A
    sta REG_LOW+$0687
    eor #$FF
    sta ZP_MAIN+$08
    sta REG_LOW+$0692
    ldx #$03
    sec
    bcs L165C
L1637:
    clc
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda #$01
    adc (ZP_MAIN+$02),y
    bcc L1675
L1642:
    clc
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda #$01
    adc (ZP_MAIN+$06),y
    bcc L1683
L164D:
    clc
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda #$01
    adc (ZP_MAIN+$0A),y
    bcc L1691
L1658:
    sta ZP_MAIN+$18,x
    ldy ZP_MAIN+$0C,x
L165C:
    lda REG_TABLE+$1000,y
    adc REG_TABLE+$1400,y
    sta ZP_MAIN+$0C,x
    lda REG_TABLE+$1200,y
    adc REG_TABLE+$1600,y
    adc REG_TABLE+$1000,y
    bcs L1637
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda (ZP_MAIN+$02),y
L1675:
    adc REG_TABLE+$1600,y
    adc REG_TABLE+$1000,y
    bcs L1642
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda (ZP_MAIN+$06),y
L1683:
    adc REG_TABLE+$1600,y
    adc REG_TABLE+$1000,y
    bcs L164D
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda (ZP_MAIN+$0A),y
L1691:
    adc REG_TABLE+$1600,y
    dex
    bpl L1658
    tax
    ldy ZP_MAIN+$18
    clc
    lda ZP_MAIN+$1B
    adc ZP_MAIN+$0D
    sta ZP_MAIN+$0D
    lda ZP_MAIN+$1C
    adc ZP_MAIN+$0E
    bcc L16AC
    inc ZP_MAIN+$0F
    beq L16EB
    clc
L16AC:
    adc ZP_MAIN+$10
    sta ZP_MAIN+$0E
    lda ZP_MAIN+$11
    adc ZP_MAIN+$14
    bcc L16B8
    inx
    clc
L16B8:
    adc ZP_MAIN+$0F
    bcc L16C0
    inx
    beq L16FD
    clc
L16C0:
    adc ZP_MAIN+$1D
    sta ZP_MAIN+$0F
    txa
    adc ZP_MAIN+$15
    bcc L16CB
    iny
    clc
L16CB:
    adc ZP_MAIN+$1E
    bcc L16D3
    iny
    beq L170B
    clc
L16D3:
    adc ZP_MAIN+$12
    tax
    tya
    adc ZP_MAIN+$13
    bcc L16DE
    inc ZP_MAIN+$19
    clc
L16DE:
    adc ZP_MAIN+$16
    tay
    lda ZP_MAIN+$17
    adc ZP_MAIN+$19
    bcs L16E8
    rts
L16E8:
    inc ZP_MAIN+$1A
    rts
L16EB:
    inc ZP_MAIN+$1E
    bne L16F9
    inc ZP_MAIN+$13
    bne L16F9
    inc ZP_MAIN+$17
    bne L16F9
    inc ZP_MAIN+$1A
L16F9:
    clc
    jmp REG_LOW+$06AC
L16FD:
    inc ZP_MAIN+$13
    bne L1707
    inc ZP_MAIN+$17
    bne L1707
    inc ZP_MAIN+$1A
L1707:
    clc
    jmp REG_LOW+$06C0
L170B:
    inc ZP_MAIN+$17
    bne L1711
    inc ZP_MAIN+$1A
L1711:
    clc
    jmp REG_LOW+$06D3
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00
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
    lda ZP_MAIN+$55
    ora ZP_MAIN+$56
    ora ZP_MAIN+$57
    ora ZP_MAIN+$58
    bne L1852
    jsr REG_LOW+$0828
    rts
L1852:
    lda ZP_MAIN+$58
    beq L1859
    jmp REG_LOW+$0914
L1859:
    lda ZP_MAIN+$57
    beq L1860
    jmp REG_LOW+$09F8
L1860:
    lda ZP_MAIN+$56
    beq L1867
    jmp REG_LOW+$08B4
L1867:
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda ZP_MAIN+$52
    sta MATH_IO+$19
    lda ZP_MAIN+$53
    sta MATH_IO+$1A
    lda ZP_MAIN+$54
    sta MATH_IO+$1B
    lda #$00
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$20
L188B:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1B
    rol MATH_IO+$1C
    bcs L18A3
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc L18AF
L18A3:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    inc MATH_IO+$18
L18AF:
    dex
    bne L188B
    clc
    rts
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda ZP_MAIN+$52
    sta MATH_IO+$19
    lda ZP_MAIN+$53
    sta MATH_IO+$1A
    lda #$00
    sta MATH_IO+$1B
    lda ZP_MAIN+$54
    sta MATH_IO+$1C
    lda #$00
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$18
L18DA:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    bcs L18FB
    lda MATH_IO+$1D
    cmp ZP_MAIN+$56
    bcc L190F
    bne L18FB
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc L190F
L18FB:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc ZP_MAIN+$56
    sta MATH_IO+$1D
    inc MATH_IO+$18
L190F:
    dex
    bne L18DA
    clc
    rts
    lda ZP_MAIN+$54
    cmp ZP_MAIN+$58
    bcc L1952
    bne L1976
    lda ZP_MAIN+$53
    cmp ZP_MAIN+$57
    bcc L1952
    bne L1976
    lda ZP_MAIN+$52
    cmp ZP_MAIN+$56
    bcc L1952
    bne L1976
    lda ZP_MAIN+$51
    cmp ZP_MAIN+$55
    bcc L1952
    bne L1976
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
L1952:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$51
    sta MATH_IO+$1C
    lda ZP_MAIN+$52
    sta MATH_IO+$1D
    lda ZP_MAIN+$53
    sta MATH_IO+$1E
    lda ZP_MAIN+$54
    sta MATH_IO+$1F
    clc
    rts
L1976:
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$52
    sta MATH_IO+$1C
    lda ZP_MAIN+$53
    sta MATH_IO+$1D
    lda ZP_MAIN+$54
    sta MATH_IO+$1E
    lda #$00
    sta MATH_IO+$1F
    ldx #$08
L199C:
    asl MATH_IO+$18
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs L19CF
    lda MATH_IO+$1F
    cmp ZP_MAIN+$58
    bcc L19F3
    bne L19CF
    lda MATH_IO+$1E
    cmp ZP_MAIN+$57
    bcc L19F3
    bne L19CF
    lda MATH_IO+$1D
    cmp ZP_MAIN+$56
    bcc L19F3
    bne L19CF
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc L19F3
L19CF:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc ZP_MAIN+$56
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc ZP_MAIN+$57
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc ZP_MAIN+$58
    sta MATH_IO+$1F
    inc MATH_IO+$18
L19F3:
    dex
    bne L199C
    clc
    rts
    lda ZP_MAIN+$54
    cmp ZP_MAIN+$58
    bcc L1A36
    bne L1A5A
    lda ZP_MAIN+$53
    cmp ZP_MAIN+$57
    bcc L1A36
    bne L1A5A
    lda ZP_MAIN+$52
    cmp ZP_MAIN+$56
    bcc L1A36
    bne L1A5A
    lda ZP_MAIN+$51
    cmp ZP_MAIN+$55
    bcc L1A36
    bne L1A5A
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
L1A36:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$51
    sta MATH_IO+$1C
    lda ZP_MAIN+$52
    sta MATH_IO+$1D
    lda ZP_MAIN+$53
    sta MATH_IO+$1E
    lda ZP_MAIN+$54
    sta MATH_IO+$1F
    clc
    rts
L1A5A:
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda ZP_MAIN+$52
    sta MATH_IO+$19
    lda #$00
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$53
    sta MATH_IO+$1C
    lda ZP_MAIN+$54
    sta MATH_IO+$1D
    lda #$00
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$10
L1A80:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs L1AB6
    lda MATH_IO+$1F
    cmp ZP_MAIN+$58
    bcc L1ADA
    bne L1AB6
    lda MATH_IO+$1E
    cmp ZP_MAIN+$57
    bcc L1ADA
    bne L1AB6
    lda MATH_IO+$1D
    cmp ZP_MAIN+$56
    bcc L1ADA
    bne L1AB6
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc L1ADA
L1AB6:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc ZP_MAIN+$56
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc ZP_MAIN+$57
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc ZP_MAIN+$58
    sta MATH_IO+$1F
    inc MATH_IO+$18
L1ADA:
    dex
    bne L1A80
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
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
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
    lda MATH_IO
    sta $DF04
    lda MATH_IO+$04
    sta $DF05
    lda #REU_UMUL8_LO_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$08
    lda #REU_UMUL8_HI_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$09
    lda MATH_IO
    bpl L203B
    sec
    lda MATH_IO+$09
    sbc MATH_IO+$04
    sta MATH_IO+$09
L203B:
    lda MATH_IO+$04
    bpl L204A
    sec
    lda MATH_IO+$09
    sbc MATH_IO
    sta MATH_IO+$09
L204A:
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
    !byte $00, $00, $00, $00
    lda MATH_IO
    sta ZP_SMUL+$19
    lda MATH_IO+$01
    sta ZP_SMUL+$27
    lda MATH_IO+$05
    sta ZP_SMUL+$37
    ldy MATH_IO+$04
    jsr ZP_SMUL
    stx MATH_IO+$0A
    sta MATH_IO+$0B
    lda ZP_SMUL+$72
    sta MATH_IO+$08
    lda ZP_SMUL+$73
    sta MATH_IO+$09
    clc
    rts
    !byte $0A, $C0, $AD, $0B, $C0, $ED, $05, $C0, $8D, $0B, $C0, $AD, $05, $C0, $10, $13
    !byte $38, $AD, $0A, $C0, $ED, $00, $C0, $8D, $0A, $C0, $AD, $0B, $C0, $ED, $01, $C0
    !byte $8D, $0B, $C0, $18, $60, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
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
    lda MATH_IO
    sta ZP_MAIN+$1F
    lda MATH_IO+$01
    sta ZP_MAIN+$27
    lda MATH_IO+$02
    sta ZP_MAIN+$2F
    lda MATH_IO+$05
    sta REG_LOW+$0445
    lda MATH_IO+$06
    sta REG_LOW+$046F
    lda MATH_IO+$02
    ldx MATH_IO
    ldy MATH_IO+$04
    jsr REG_LOW+$0400
    sta MATH_IO+$0D
    lda REG_LOW+$051E
    sta MATH_IO+$08
    lda ZP_MAIN+$29
    sta MATH_IO+$09
    lda ZP_MAIN+$31
    sta MATH_IO+$0A
    lda ZP_MAIN+$25
    sta MATH_IO+$0B
    lda ZP_MAIN+$2D
    sta MATH_IO+$0C
    lda MATH_IO+$02
    bpl L2265
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
L2265:
    lda MATH_IO+$06
    bpl L2286
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
L2286:
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00
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
    jsr REG_LOW+$0600
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
    bpl L2373
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
L2373:
    lda MATH_IO+$07
    bpl L239D
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
L239D:
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
    !byte $00
    lda MATH_IO+$10
    sta ZP_MAIN+$3C
    lda MATH_IO+$14
    sta ZP_MAIN+$3D
    jsr REG_TABLE+$1806
    lda ZP_MAIN+$3F
    sta MATH_IO+$18
    lda ZP_MAIN+$40
    sta MATH_IO+$1C
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$3C
    lda MATH_IO+$11
    sta ZP_MAIN+$3D
    lda MATH_IO+$14
    sta ZP_MAIN+$3E
    lda MATH_IO+$15
    sta ZP_MAIN+$3F
    jsr REG_TABLE+$1A00
    lda ZP_MAIN+$44
    sta MATH_IO+$18
    lda ZP_MAIN+$45
    sta MATH_IO+$19
    lda ZP_MAIN+$46
    sta MATH_IO+$1C
    lda ZP_MAIN+$47
    sta MATH_IO+$1D
    rts
    !byte $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$3C
    lda MATH_IO+$11
    sta ZP_MAIN+$3D
    lda MATH_IO+$12
    sta ZP_MAIN+$3E
    lda MATH_IO+$14
    sta ZP_MAIN+$3F
    lda MATH_IO+$15
    sta ZP_MAIN+$40
    lda MATH_IO+$16
    sta ZP_MAIN+$41
    jsr REG_TABLE+$2100
    lda ZP_MAIN+$48
    sta MATH_IO+$18
    lda ZP_MAIN+$49
    sta MATH_IO+$19
    lda ZP_MAIN+$4A
    sta MATH_IO+$1A
    lda ZP_MAIN+$4B
    sta MATH_IO+$1C
    lda ZP_MAIN+$4C
    sta MATH_IO+$1D
    lda ZP_MAIN+$4D
    sta MATH_IO+$1E
    rts
    lda MATH_IO+$10
    sta ZP_MAIN+$3C
    lda MATH_IO+$11
    sta ZP_MAIN+$3D
    lda MATH_IO+$12
    sta ZP_MAIN+$3E
    lda MATH_IO+$13
    sta ZP_MAIN+$3F
    lda MATH_IO+$14
    sta ZP_MAIN+$40
    lda MATH_IO+$15
    sta ZP_MAIN+$41
    jsr REG_TABLE+$3200
    lda ZP_MAIN+$4C
    sta MATH_IO+$18
    lda ZP_MAIN+$4D
    sta MATH_IO+$19
    lda ZP_MAIN+$46
    sta MATH_IO+$1A
    lda ZP_MAIN+$47
    sta MATH_IO+$1B
    lda ZP_MAIN+$48
    sta MATH_IO+$1C
    lda ZP_MAIN+$49
    sta MATH_IO+$1D
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

; Source interval $3000-$3FFF
* = REG_API
    jmp REG_API+$09C0
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO
    sta ZP_MAIN+$1F
    lda MATH_IO+$01
    sta ZP_MAIN+$27
    lda MATH_IO+$05
    sta REG_KERNEL+$141A
    ldy MATH_IO+$04
    jsr REG_KERNEL+$13EC
    sta MATH_IO+$0A
    stx MATH_IO+$09
    sty MATH_IO+$0B
    lda ZP_MAIN+$2F
    sta MATH_IO+$08
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_API+$04C0
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_API+$0420
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_API+$0420
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $A9, $74, $85
    !byte $03, $85, $07, $85, $0B, $A9, $72, $85, $05, $85, $09, $85, $0D, $4C, $20, $34
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_API+$0A00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$0E
    lda MATH_IO+$11
    sta ZP_MAIN+$0F
    lda MATH_IO+$14
    sta ZP_MAIN+$10
    lda MATH_IO+$15
    sta ZP_MAIN+$11
    jsr REG_KERNEL+$020C
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
    jsr REG_KERNEL+$080B
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
    jsr REG_KERNEL+$0E00
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
    jmp REG_API+$0A40
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jmp REG_API+$0140
    jmp REG_API+$0170
    jmp REG_API+$01B0
    !byte $00, $00, $00, $00, $00, $00, $00, $AD, $08, $C0, $8D, $10, $C0, $AD, $09, $C0
    !byte $8D, $11, $C0, $A9, $00, $8D, $12, $C0, $8D, $13, $C0, $60, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $A2, $03, $BD, $08, $C0, $9D, $10, $C0, $CA
    !byte $10, $F7, $60, $00, $00, $00, $00, $A2, $03, $BD, $18, $C0, $9D, $00, $C0, $CA
    !byte $10, $F7, $60, $00, $00, $00, $00, $AD, $1C, $C0, $8D, $00, $C0, $AD, $1D, $C0
    !byte $8D, $01, $C0, $60, $00, $00, $00
    lda #>REG_TABLE+$1400
    sta ZP_MAIN+$01
    sta ZP_MAIN+$05
    sta ZP_MAIN+$09
    lda #>REG_TABLE+$1200
    sta ZP_MAIN+$03
    sta ZP_MAIN+$07
    sta ZP_MAIN+$0B
    lda #>REG_TABLE
    sta ZP_MAIN+$20
    sta ZP_MAIN+$28
    sta ZP_MAIN+$30
    lda #>REG_TABLE+$0400
    sta ZP_MAIN+$22
    sta ZP_MAIN+$2A
    sta ZP_MAIN+$32
    lda #>REG_TABLE+$0200
    sta ZP_MAIN+$24
    sta ZP_MAIN+$2C
    sta ZP_MAIN+$34
    lda #>REG_TABLE+$0600
    sta ZP_MAIN+$26
    sta ZP_MAIN+$2E
    sta ZP_MAIN+$36
    jsr REG_API+$02C0
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jsr REG_API+$09A0
    ldx #$73
L32C5:
    lda REG_GAME+$0B00,x
    sta ZP_SMUL,x
    dex
    bpl L32C5
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $20, $20, $30, $20, $50, $32, $4C, $B0, $31, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $20, $40, $31, $B0, $1B, $AD, $18, $C0, $8D, $00, $C0, $AD, $19, $C0
    !byte $8D, $01, $C0, $AD, $14, $C0, $8D, $04, $C0, $AD, $15, $C0, $8D, $05, $C0, $20
    !byte $20, $30, $60, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $20, $70, $31, $B0, $14, $A2, $02, $BD, $18, $C0, $9D, $00, $C0, $BD
    !byte $14, $C0, $9D, $04, $C0, $CA, $10, $F1, $20, $60, $30, $60, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $20, $B0, $31, $B0, $22, $A2, $03, $BD, $18, $C0, $9D, $00, $C0, $CA
    !byte $10, $F7, $AD, $14, $C0, $8D, $04, $C0, $AD, $15, $C0, $8D, $05, $C0, $A9, $00
    !byte $8D, $06, $C0, $8D, $07, $C0, $20, $B0, $30, $60, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00
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
    jsr REG_KERNEL+$1800
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
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00
    lda MATH_IO
    sta ZP_MAIN+$1F
    lda MATH_IO+$01
    sta ZP_MAIN+$27
    lda MATH_IO+$02
    sta ZP_MAIN+$2F
    lda MATH_IO+$04
    sta REG_KERNEL+$16F1
    lda MATH_IO+$05
    sta REG_KERNEL+$16C7
    ldy MATH_IO+$06
    jsr REG_KERNEL+$1681
    sta MATH_IO+$0C
    stx MATH_IO+$0D
    sty MATH_IO+$0B
    lda ZP_MAIN+$21
    sta MATH_IO+$08
    lda ZP_MAIN+$25
    sta MATH_IO+$09
    lda ZP_MAIN+$2D
    sta MATH_IO+$0A
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
    !byte $00, $00, $00, $00, $00
    lda #<TURBO16_ZP_BASE
    sta $DF02
    lda #>TURBO16_ZP_BASE
    sta $DF03
    sta $DF04
    sta $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$71
    sta $DF07
    lda #$00
    sta $DF08
    sta $DF0A
    lda #$82
    sta $DF01
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO
    sta+1 TURBO16_ZP_BASE+$16
    lda MATH_IO+$01
    sta+1 TURBO16_ZP_BASE+$24
    lda MATH_IO+$05
    sta+1 TURBO16_ZP_BASE+$34
    ldy MATH_IO+$04
    lda MATH_IO+$01
    jsr TURBO16_ZP_BASE+$02
    sta MATH_IO+$0A
    stx MATH_IO+$09
    sty MATH_IO+$0B
    lda+1 TURBO16_ZP_BASE+$70
    sta MATH_IO+$08
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00
    jsr REG_API+$0800
    jmp REG_API+$09A0
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda #<TURBO32_ZP_BASE
    sta $DF02
    lda #>TURBO32_ZP_BASE
    sta $DF03
    sta $DF04
    sta $DF05
    lda #REU_TURBO32_BANK
    sta $DF06
    lda #$87
    sta $DF07
    lda #$00
    sta $DF08
    sta $DF0A
    lda #$82
    sta $DF01
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00
    lda MATH_IO
    sta+1 TURBO32_ZP_BASE+$44
    lda MATH_IO+$01
    sta+1 TURBO32_ZP_BASE+$52
    lda MATH_IO+$02
    sta+1 TURBO32_ZP_BASE+$62
    lda MATH_IO+$03
    sta+1 TURBO32_ZP_BASE+$72
    lda MATH_IO+$04
    sta+1 TURBO32_ZP_BASE
    lda MATH_IO+$05
    sta+1 TURBO32_ZP_BASE+$01
    lda MATH_IO+$06
    sta+1 TURBO32_ZP_BASE+$02
    ldy MATH_IO+$07
    lda MATH_IO
    jsr REG_LOW+$0002
    sta MATH_IO+$0E
    stx MATH_IO+$0D
    sty MATH_IO+$0C
    lda+1 TURBO32_ZP_BASE
    sta MATH_IO+$08
    lda+1 TURBO32_ZP_BASE+$01
    sta MATH_IO+$09
    lda+1 TURBO32_ZP_BASE+$02
    sta MATH_IO+$0A
    lda+1 TURBO32_ZP_BASE+$03
    sta MATH_IO+$0B
    lda+1 TURBO32_ZP_BASE+$12
    sta MATH_IO+$0F
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    jsr REG_API+$08C0
    jmp REG_API+$09A0
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda #<REU_SCRATCH
    sta $DF02
    lda #>REU_SCRATCH
    sta $DF03
    lda #$01
    sta $DF07
    lda #$00
    sta $DF08
    lda #$C0
    sta $DF0A
    rts
    !byte $00, $00, $00, $00, $00, $00
    lda MATH_IO
    sta $DF04
    lda MATH_IO+$04
    sta $DF05
    lda #REU_UMUL8_LO_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$08
    lda #REU_UMUL8_HI_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$09
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00
    lda MATH_IO+$10
    sta $DF04
    lda MATH_IO+$14
    beq L3A30
    sta $DF05
    lda #REU_UDIV8_Q_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$18
    lda #REU_UDIV8_R_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$1C
    clc
    rts
L3A30:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$1C
    sec
    rts
    !byte $00, $00, $00, $00, $00, $00
    lda MATH_IO+$10
    sta $DF04
    lda MATH_IO+$14
    beq L3A60
    sta $DF05
    lda #REU_UDIV8_R_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$1C
    clc
    rts
L3A60:
    lda #$00
    sta MATH_IO+$1C
    sec
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $A9, $04, $8D, $07, $DF, $A9, $00
    !byte $8D, $0A, $DF, $60, $18, $AD, $00, $C0, $6D, $04, $C0, $85, $10, $AD, $01, $C0
    !byte $6D, $05, $C0, $85, $11, $A9, $00, $69, $00, $85, $12, $AD, $01, $C0, $CD, $05
    !byte $C0, $90, $22, $D0, $08, $AD, $00, $C0, $CD, $04, $C0, $90, $18, $38, $AD, $00
    !byte $C0, $ED, $04, $C0, $85, $13, $AD, $01, $C0, $ED, $05, $C0, $85, $14, $A9, $00
    !byte $85, $15, $4C, $E1, $3A, $38, $AD, $04, $C0, $ED, $00, $C0, $85, $13, $AD, $05
    !byte $C0, $ED, $01, $C0, $85, $14, $A9, $00, $85, $15, $06, $10, $26, $11, $26, $12
    !byte $06, $10, $26, $11, $26, $12, $A5, $10, $8D, $04, $DF, $A5, $11, $8D, $05, $DF
    !byte $A5, $12, $09, $10, $8D, $06, $DF, $A9, $A1, $8D, $01, $DF, $AD, $20, $C0, $85
    !byte $1C, $AD, $21, $C0, $85, $1D, $AD, $22, $C0, $85, $1E, $AD, $23, $C0, $85, $1F
    !byte $06, $13, $26, $14, $26, $15, $06, $13, $26, $14, $26, $15, $A5, $13, $8D, $04
    !byte $DF, $A5, $14, $8D, $05, $DF, $A5, $15, $09, $10, $8D, $06, $DF, $A9, $A1, $8D
    !byte $01, $DF, $38, $A5, $1C, $ED, $20, $C0, $8D, $08, $C0, $A5, $1D, $ED, $21, $C0
    !byte $8D, $09, $C0, $A5, $1E, $ED, $22, $C0, $8D, $0A, $C0, $A5, $1F, $ED, $23, $C0
    !byte $8D, $0B, $C0, $18, $60, $A9, $01, $8D, $07, $DF, $A9, $C0, $8D, $0A, $DF, $60
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00
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
    jmp REG_LOW+$1300
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

; Source interval $4000-$5DFF
* = REG_KERNEL
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $A7, ZP_MAIN+$0F    ; LAX zp
    cmp ZP_MAIN+$11
    bcs L4239
L4212:
    lda #$00
    sta ZP_MAIN+$12
    sta ZP_MAIN+$13
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$14
    stx ZP_MAIN+$15
    rts
L421F:
    lda ZP_MAIN+$0E
    sbc ZP_MAIN+$10
    bcc L4212
    cpx #$01
    bcc L4236
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$15
    sta ZP_MAIN+$13
    lda #$01
    sta ZP_MAIN+$12
    rts
L4236:
    jmp REG_KERNEL+$060E
L4239:
    beq L421F
    lda ZP_MAIN+$0E
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcs L42BB
    sta ZP_MAIN+$15
    lda #$00
    sta ZP_MAIN+$13
    lda #$01
    sta ZP_MAIN+$12
    rts
L4253:
    cmp REG_KERNEL+$064D,x
    bcc L425B
    jmp REG_KERNEL+$04FA
L425B:
    sec
    bcs L42C3
L425E:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L426C
    txa
L4265:
    sta ZP_MAIN+$15
    lda #$02
    sta ZP_MAIN+$12
    rts
L426C:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L4279
L4272:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L4280
    txa
L4279:
    sta ZP_MAIN+$15
    lda #$03
    sta ZP_MAIN+$12
    rts
L4280:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L428D
L4286:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L4294
    txa
L428D:
    sta ZP_MAIN+$15
    lda #$04
    sta ZP_MAIN+$12
    rts
L4294:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    jmp REG_KERNEL+$037B
L429B:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L42AD
    stx ZP_MAIN+$15
    lda #$00
    sta ZP_MAIN+$13
    lda #$01
    sta ZP_MAIN+$12
    rts
L42AD:
    dex
    bpl L42B3
    jmp REG_KERNEL+$060E
L42B3:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$13
    bcc L4265
L42BB:
    beq L429B
    ldx ZP_MAIN+$11
    cpx #$0F
    bcc L4253
L42C3:
    ldy #$00
    sty ZP_MAIN+$13
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L4265
    beq L425E
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L4279
    beq L4272
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L428D
    beq L4286
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L437B
    beq L4374
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L4389
    beq L4382
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L4397
    beq L4390
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L43A5
    beq L439E
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L43B3
    beq L43AC
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L43C1
    beq L43BA
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L43CF
    beq L43C8
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    jmp REG_KERNEL+$0400
L4374:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L43D6
    txa
L437B:
    sta ZP_MAIN+$15
    lda #$05
    sta ZP_MAIN+$12
    rts
L4382:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L43DC
    txa
L4389:
    sta ZP_MAIN+$15
    lda #$06
    sta ZP_MAIN+$12
    rts
L4390:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L43E2
    txa
L4397:
    sta ZP_MAIN+$15
    lda #$07
    sta ZP_MAIN+$12
    rts
L439E:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L43E8
    txa
L43A5:
    sta ZP_MAIN+$15
    lda #$08
    sta ZP_MAIN+$12
    rts
L43AC:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L43EE
    txa
L43B3:
    sta ZP_MAIN+$15
    lda #$09
    sta ZP_MAIN+$12
    rts
L43BA:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L43F4
    txa
L43C1:
    sta ZP_MAIN+$15
    lda #$0A
    sta ZP_MAIN+$12
    rts
L43C8:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L43FA
    txa
L43CF:
    sta ZP_MAIN+$15
    lda #$0B
    sta ZP_MAIN+$12
    rts
L43D6:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L4389
L43DC:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L4397
L43E2:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L43A5
L43E8:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L43B3
L43EE:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L43C1
L43F4:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L43CF
L43FA:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L4457
    cmp ZP_MAIN+$11
    bcc L4457
    beq L4450
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L446B
    beq L4464
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L447F
    beq L4478
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L4493
    beq L448C
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    cmp ZP_MAIN+$11
    bcc L44A7
    beq L44A0
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
L4450:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L445E
    txa
L4457:
    sta ZP_MAIN+$15
    lda #$0C
    sta ZP_MAIN+$12
    rts
L445E:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L446B
L4464:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L4472
    txa
L446B:
    sta ZP_MAIN+$15
    lda #$0D
    sta ZP_MAIN+$12
    rts
L4472:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L447F
L4478:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L4486
    txa
L447F:
    sta ZP_MAIN+$15
    lda #$0E
    sta ZP_MAIN+$12
    rts
L4486:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L4493
L448C:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L449A
    txa
L4493:
    sta ZP_MAIN+$15
    lda #$0F
    sta ZP_MAIN+$12
    rts
L449A:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    bcc L44A7
L44A0:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcs L44AE
    txa
L44A7:
    sta ZP_MAIN+$15
    lda #$10
    sta ZP_MAIN+$12
    rts
L44AE:
    sta ZP_MAIN+$14
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$15
    lda #$11
    sta ZP_MAIN+$12
    rts
L44B9:
    jmp REG_KERNEL+$0612
L44BC:
    jmp REG_KERNEL+$060E
L44BF:
    cpx #$01
    bcc L44BC
    beq L44B9
    lda ZP_MAIN+$0E
    asl
    sta ZP_MAIN+$12
    lda ZP_MAIN+$0F
    rol
    sta ZP_MAIN+$14
    lda #$00
    sta ZP_MAIN+$13
    rol
    rol ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    cmp ZP_MAIN+$11
    bcc L4516
    beq L44EB
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs L4516
L44EB:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcc L44F7
    sta ZP_MAIN+$14
    lda #$00
    bcs L4516
L44F7:
    txa
    bcc L4516
    cpx #$04
    bcc L44BF
    cpx #$08
    bcs L454B
    lda ZP_MAIN+$0E
    asl
    sta ZP_MAIN+$12
    lda ZP_MAIN+$0F
    rol
    sta ZP_MAIN+$14
    lda #$00
    sta ZP_MAIN+$13
    rol
    asl ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
L4516:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    cmp ZP_MAIN+$11
    bcc L4564
    beq L452D
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs L4564
L452D:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcc L4539
    sta ZP_MAIN+$14
    lda #$00
    bcs L4564
L4539:
    txa
    bcc L4564
L453C:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcc L4548
    sta ZP_MAIN+$14
    lda #$00
    bcs L4579
L4548:
    txa
    bcc L4579
L454B:
    lda ZP_MAIN+$0E
    asl
    sta ZP_MAIN+$12
    lda ZP_MAIN+$0F
    rol
    sta ZP_MAIN+$14
    lda #$00
    sta ZP_MAIN+$13
    rol
    asl ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    asl ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
L4564:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    cmp ZP_MAIN+$11
    bcc L4579
    beq L453C
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
L4579:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    cmp ZP_MAIN+$11
    bcc L458E
    beq L45D2
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
L458E:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    cmp ZP_MAIN+$11
    bcc L45A3
    beq L45E1
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
L45A3:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    cmp ZP_MAIN+$11
    bcc L45B8
    beq L45F0
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
L45B8:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$14
    rol
    cmp ZP_MAIN+$11
    bcc L45CD
    beq L45FF
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
L45CD:
    rol ZP_MAIN+$12
    sta ZP_MAIN+$15
    rts
L45D2:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcc L45DE
    sta ZP_MAIN+$14
    lda #$00
    bcs L458E
L45DE:
    txa
    bcc L458E
L45E1:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcc L45ED
    sta ZP_MAIN+$14
    lda #$00
    bcs L45A3
L45ED:
    txa
    bcc L45A3
L45F0:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcc L45FC
    sta ZP_MAIN+$14
    lda #$00
    bcs L45B8
L45FC:
    txa
    bcc L45B8
L45FF:
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    bcc L460B
    sta ZP_MAIN+$14
    lda #$00
    bcs L45CD
L460B:
    txa
    bcc L45CD
    lda ZP_MAIN+$10
    beq L4643
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$12
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$13
    lda #$00
    lsr
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    ldy #$10
L4623:
    rol ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tax
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc L463B
    sta ZP_MAIN+$15
    stx ZP_MAIN+$14
L463B:
    dey
    bne L4623
    rol ZP_MAIN+$12
    rol ZP_MAIN+$13
    rts
L4643:
    sta ZP_MAIN+$12
    sta ZP_MAIN+$13
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    sec
    rts
    !byte $00, $11, $16, $20, $24, $2B, $34, $3D, $3F, $45, $4D, $54, $5B, $62, $68, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00
L4800:
    lda #$00
    ldx #$05
L4804:
    sta ZP_MAIN+$14,x
    dex
    bpl L4804
    sec
    rts
    !byte $A7, ZP_MAIN+$10    ; LAX zp
    cmp ZP_MAIN+$13
    bcc L4879
    beq L481A
    lda ZP_MAIN+$13
    beq L485F
    jmp REG_KERNEL+$088C
L481A:
    lda ZP_MAIN+$13
    beq L4849
    lda ZP_MAIN+$0F
    cmp ZP_MAIN+$12
    bcc L4879
    bne L482C
    lda ZP_MAIN+$0E
    cmp ZP_MAIN+$11
    bcc L4879
L482C:
    lda ZP_MAIN+$0E
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$0F
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$10
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$15
    sta ZP_MAIN+$16
    lda #$01
    sta ZP_MAIN+$14
    rts
L4849:
    lda ZP_MAIN+$11
    ora ZP_MAIN+$12
    beq L4800
    lda ZP_MAIN+$0F
    cmp ZP_MAIN+$12
    bcc L4879
    bne L4865
    lda ZP_MAIN+$0E
    cmp ZP_MAIN+$11
    bcc L4879
    bcs L4865
L485F:
    lda ZP_MAIN+$11
    ora ZP_MAIN+$12
    beq L4800
L4865:
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$17
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$18
    lda ZP_MAIN+$10
    sta ZP_MAIN+$19
    lda #$00
    sta REG_KERNEL+$0C9A
    jmp REG_KERNEL+$0C24
L4879:
    lda #$00
    sta ZP_MAIN+$14
    sta ZP_MAIN+$15
    sta ZP_MAIN+$16
    lda ZP_MAIN+$0E
    sta ZP_MAIN+$17
    lda ZP_MAIN+$0F
    sta ZP_MAIN+$18
    stx ZP_MAIN+$19
    rts
    lda ZP_MAIN+$0E
    sec
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$0F
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$10
    sbc ZP_MAIN+$13
    ldx #$00
    stx ZP_MAIN+$15
    stx ZP_MAIN+$16
    cmp ZP_MAIN+$13
    bcc L48BE
    bne L48C5
    sta ZP_MAIN+$19
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L48B9
    bne L48C7
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L48C7
L48B9:
    lda #$01
    sta ZP_MAIN+$14
    rts
L48BE:
    sta ZP_MAIN+$19
    lda #$01
    sta ZP_MAIN+$14
    rts
L48C5:
    sta ZP_MAIN+$19
L48C7:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    cmp ZP_MAIN+$13
    bcc L48F2
    bne L48F9
    sta ZP_MAIN+$19
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L48ED
    bne L48FB
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L48FB
L48ED:
    lda #$02
    sta ZP_MAIN+$14
    rts
L48F2:
    sta ZP_MAIN+$19
    lda #$02
    sta ZP_MAIN+$14
    rts
L48F9:
    sta ZP_MAIN+$19
L48FB:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    lda ZP_MAIN+$13
    cmp #$0D
    bcc L4916
    jmp REG_KERNEL+$091E
L4916:
    lda #$03
    sta REG_KERNEL+$0C9A
    jmp REG_KERNEL+$0C24
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4934
    bne L4939
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4934
    bne L4939
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4939
L4934:
    lda #$03
    sta ZP_MAIN+$14
    rts
L4939:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$094E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4964
    bne L4969
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4964
    bne L4969
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4969
L4964:
    lda #$04
    sta ZP_MAIN+$14
    rts
L4969:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$097E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4994
    bne L4999
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4994
    bne L4999
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4999
L4994:
    lda #$05
    sta ZP_MAIN+$14
    rts
L4999:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$09AE
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L49C4
    bne L49C9
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L49C4
    bne L49C9
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L49C9
L49C4:
    lda #$06
    sta ZP_MAIN+$14
    rts
L49C9:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$09DE
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L49F4
    bne L49F9
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L49F4
    bne L49F9
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L49F9
L49F4:
    lda #$07
    sta ZP_MAIN+$14
    rts
L49F9:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0A0E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4A24
    bne L4A29
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4A24
    bne L4A29
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4A29
L4A24:
    lda #$08
    sta ZP_MAIN+$14
    rts
L4A29:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0A3E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4A54
    bne L4A59
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4A54
    bne L4A59
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4A59
L4A54:
    lda #$09
    sta ZP_MAIN+$14
    rts
L4A59:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0A6E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4A84
    bne L4A89
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4A84
    bne L4A89
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4A89
L4A84:
    lda #$0A
    sta ZP_MAIN+$14
    rts
L4A89:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0A9E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4AB4
    bne L4AB9
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4AB4
    bne L4AB9
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4AB9
L4AB4:
    lda #$0B
    sta ZP_MAIN+$14
    rts
L4AB9:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0ACE
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4AE4
    bne L4AE9
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4AE4
    bne L4AE9
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4AE9
L4AE4:
    lda #$0C
    sta ZP_MAIN+$14
    rts
L4AE9:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0AFE
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4B14
    bne L4B19
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4B14
    bne L4B19
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4B19
L4B14:
    lda #$0D
    sta ZP_MAIN+$14
    rts
L4B19:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0B2E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4B44
    bne L4B49
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4B44
    bne L4B49
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4B49
L4B44:
    lda #$0E
    sta ZP_MAIN+$14
    rts
L4B49:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0B5E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4B74
    bne L4B79
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4B74
    bne L4B79
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4B79
L4B74:
    lda #$0F
    sta ZP_MAIN+$14
    rts
L4B79:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0B8E
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4BA4
    bne L4BA9
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4BA4
    bne L4BA9
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4BA9
L4BA4:
    lda #$10
    sta ZP_MAIN+$14
    rts
L4BA9:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0BBE
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4BD4
    bne L4BD9
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4BD4
    bne L4BD9
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4BD9
L4BD4:
    lda #$11
    sta ZP_MAIN+$14
    rts
L4BD9:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0BEE
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$13
    bcc L4C04
    bne L4C09
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$12
    bcc L4C04
    bne L4C09
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$11
    bcs L4C09
L4C04:
    lda #$12
    sta ZP_MAIN+$14
    rts
L4C09:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$11
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$12
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$13
    sta ZP_MAIN+$19
    jmp REG_KERNEL+$0C1E
    lda #$13
    sta ZP_MAIN+$14
    clc
    rts
    lda ZP_MAIN+$11
    sta ZP_MAIN+$1A
    lda ZP_MAIN+$12
    sta ZP_MAIN+$1B
    lda ZP_MAIN+$13
    sta ZP_MAIN+$1C
    ldx #$00
    stx ZP_MAIN+$14
    stx ZP_MAIN+$15
    stx ZP_MAIN+$16
L4C38:
    asl ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    rol ZP_MAIN+$1C
    bcs L4C59
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$1C
    bcc L4C59
    bne L4C56
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1B
    bcc L4C59
    bne L4C56
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$1A
    bcc L4C59
L4C56:
    inx
    bne L4C38
L4C59:
    ror ZP_MAIN+$1C
    ror ZP_MAIN+$1B
    ror ZP_MAIN+$1A
L4C5F:
    lda ZP_MAIN+$19
    cmp ZP_MAIN+$1C
    bcc L4C87
    bne L4C75
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1B
    bcc L4C87
    bne L4C75
    lda ZP_MAIN+$17
    cmp ZP_MAIN+$1A
    bcc L4C87
L4C75:
    lda ZP_MAIN+$17
    sbc ZP_MAIN+$1A
    sta ZP_MAIN+$17
    lda ZP_MAIN+$18
    sbc ZP_MAIN+$1B
    sta ZP_MAIN+$18
    lda ZP_MAIN+$19
    sbc ZP_MAIN+$1C
    sta ZP_MAIN+$19
L4C87:
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    rol ZP_MAIN+$16
    lsr ZP_MAIN+$1C
    ror ZP_MAIN+$1B
    ror ZP_MAIN+$1A
    dex
    bpl L4C5F
    lda ZP_MAIN+$14
    clc
    adc #$00
    sta ZP_MAIN+$14
    bcc L4CA6
    inc ZP_MAIN+$15
    bne L4CA5
    inc ZP_MAIN+$16
L4CA5:
    clc
L4CA6:
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
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00
    jsr REG_KERNEL+$020C
    bcc L4E08
    jmp REG_KERNEL+$10DA
L4E08:
    lda ZP_MAIN+$16
    sta ZP_MAIN+$18
    lda ZP_MAIN+$17
    sta ZP_MAIN+$19
    lda ZP_MAIN+$15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4E33
    cmp ZP_MAIN+$11
    bcc L4E3E
    bne L4E27
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4E3E
L4E27:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4E3E
L4E33:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4E3E:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4E5F
    cmp ZP_MAIN+$11
    bcc L4E6A
    bne L4E53
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4E6A
L4E53:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4E6A
L4E5F:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4E6A:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4E8B
    cmp ZP_MAIN+$11
    bcc L4E96
    bne L4E7F
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4E96
L4E7F:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4E96
L4E8B:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4E96:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4EB7
    cmp ZP_MAIN+$11
    bcc L4EC2
    bne L4EAB
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4EC2
L4EAB:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4EC2
L4EB7:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4EC2:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4EE3
    cmp ZP_MAIN+$11
    bcc L4EEE
    bne L4ED7
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4EEE
L4ED7:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4EEE
L4EE3:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4EEE:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4F0F
    cmp ZP_MAIN+$11
    bcc L4F1A
    bne L4F03
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4F1A
L4F03:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4F1A
L4F0F:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4F1A:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4F3B
    cmp ZP_MAIN+$11
    bcc L4F46
    bne L4F2F
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4F46
L4F2F:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4F46
L4F3B:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4F46:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4F67
    cmp ZP_MAIN+$11
    bcc L4F72
    bne L4F5B
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4F72
L4F5B:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4F72
L4F67:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4F72:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4F93
    cmp ZP_MAIN+$11
    bcc L4F9E
    bne L4F87
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4F9E
L4F87:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4F9E
L4F93:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4F9E:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4FBF
    cmp ZP_MAIN+$11
    bcc L4FCA
    bne L4FB3
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4FCA
L4FB3:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4FCA
L4FBF:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4FCA:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L4FEB
    cmp ZP_MAIN+$11
    bcc L4FF6
    bne L4FDF
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L4FF6
L4FDF:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L4FF6
L4FEB:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L4FF6:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L5017
    cmp ZP_MAIN+$11
    bcc L5022
    bne L500B
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L5022
L500B:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L5022
L5017:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L5022:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L5043
    cmp ZP_MAIN+$11
    bcc L504E
    bne L5037
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L504E
L5037:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L504E
L5043:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L504E:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L506F
    cmp ZP_MAIN+$11
    bcc L507A
    bne L5063
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L507A
L5063:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L507A
L506F:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L507A:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L509B
    cmp ZP_MAIN+$11
    bcc L50A6
    bne L508F
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L50A6
L508F:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L50A6
L509B:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L50A6:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol
    bcs L50C7
    cmp ZP_MAIN+$11
    bcc L50D2
    bne L50BB
    ldx ZP_MAIN+$14
    cpx ZP_MAIN+$10
    bcc L50D2
L50BB:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    bcs L50D2
L50C7:
    tax
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    txa
    sbc ZP_MAIN+$11
    sec
L50D2:
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    sta ZP_MAIN+$15
    clc
    rts
    lda #$00
    sta ZP_MAIN+$18
    sta ZP_MAIN+$19
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
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda ZP_MAIN+$1F
    sta ZP_MAIN+$23
    eor #$FF
    sta ZP_MAIN+$21
    sta ZP_MAIN+$25
    lda ZP_MAIN+$27
    sta ZP_MAIN+$2B
    eor #$FF
    sta ZP_MAIN+$29
    sta ZP_MAIN+$2D
    sec
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta ZP_MAIN+$2F
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L5442
    adc (ZP_MAIN+$29),y
    tax
    lda (ZP_MAIN+$2B),y
L5414:
    adc (ZP_MAIN+$2D),y
    sta REG_KERNEL+$143A
    ldy #$00
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta REG_KERNEL+$1437
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L544C
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$143C
    lda (ZP_MAIN+$2B),y
L5431:
    adc (ZP_MAIN+$2D),y
    tay
    clc
    txa
    adc #$00
    tax
    lda #$00
    adc #$00
    bcs L5440
    rts
L5440:
    iny
    rts
L5442:
    clc
    adc (ZP_MAIN+$29),y
    tax
    lda #$01
    adc (ZP_MAIN+$2B),y
    bcc L5414
L544C:
    clc
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$143C
    lda #$01
    adc (ZP_MAIN+$2B),y
    bcc L5431
    lda #$60
    sta ZP_MAIN+$20
    sta ZP_MAIN+$28
    lda #$64
    sta ZP_MAIN+$22
    sta ZP_MAIN+$2A
    lda #$62
    sta ZP_MAIN+$24
    sta ZP_MAIN+$2C
    lda #$66
    sta ZP_MAIN+$26
    sta ZP_MAIN+$2E
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
    !byte $00, $00, $00, $00, $00, $00, $00, $00
L5649:
    clc
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$1734
    lda #$01
    adc (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcc L56BC
L5659:
    clc
    adc (ZP_MAIN+$31),y
    sta REG_KERNEL+$1739
    lda #$01
    adc (ZP_MAIN+$33),y
    bcc L56C3
L5665:
    clc
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$1721
    lda #$01
    adc (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcc L56E4
L5675:
    clc
    adc (ZP_MAIN+$31),y
    sta REG_KERNEL+$172C
    lda #$01
    adc (ZP_MAIN+$33),y
    bcc L56EB
    lda ZP_MAIN+$1F
    sta ZP_MAIN+$23
    eor #$FF
    sta ZP_MAIN+$21
    sta ZP_MAIN+$25
    lda ZP_MAIN+$27
    sta ZP_MAIN+$2B
    eor #$FF
    sta ZP_MAIN+$29
    sta ZP_MAIN+$2D
    lda ZP_MAIN+$2F
    sta ZP_MAIN+$33
    eor #$FF
    sta ZP_MAIN+$31
    sta ZP_MAIN+$35
    sec
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta REG_KERNEL+$1727
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L5649
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$1734
    lda (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcs L5659
L56BC:
    adc (ZP_MAIN+$31),y
    sta REG_KERNEL+$1739
    lda (ZP_MAIN+$33),y
L56C3:
    adc (ZP_MAIN+$35),y
    tax
    ldy #$00
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta REG_KERNEL+$171B
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L5665
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$1721
    lda (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcs L5675
L56E4:
    adc (ZP_MAIN+$31),y
    sta REG_KERNEL+$172C
    lda (ZP_MAIN+$33),y
L56EB:
    adc (ZP_MAIN+$35),y
    sta REG_KERNEL+$1737
    ldy #$00
    lda (ZP_MAIN+$1F),y
    adc (ZP_MAIN+$21),y
    sta ZP_MAIN+$21
    lda (ZP_MAIN+$23),y
    adc (ZP_MAIN+$25),y
    adc (ZP_MAIN+$27),y
    bcs L573F
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$1719
    lda (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcs L574F
L570D:
    adc (ZP_MAIN+$31),y
    sta REG_KERNEL+$171F
    lda (ZP_MAIN+$33),y
L5714:
    adc (ZP_MAIN+$35),y
    tay
    clc
    lda #$00
    adc #$00
    sta ZP_MAIN+$25
    lda #$00
    adc #$00
    bcc L5726
    iny
    clc
L5726:
    adc #$00
    sta ZP_MAIN+$2D
    tya
    adc #$00
    bcc L5733
    clc
    inc REG_KERNEL+$1737
L5733:
    adc #$00
    tay
    lda #$00
    adc #$00
    bcs L573D
    rts
L573D:
    inx
    rts
L573F:
    clc
    adc (ZP_MAIN+$29),y
    sta REG_KERNEL+$1719
    lda #$01
    adc (ZP_MAIN+$2B),y
    adc (ZP_MAIN+$2D),y
    adc (ZP_MAIN+$2F),y
    bcc L570D
L574F:
    clc
    adc (ZP_MAIN+$31),y
    sta REG_KERNEL+$171F
    lda #$01
    adc (ZP_MAIN+$33),y
    bcc L5714
    lda #$60
    sta ZP_MAIN+$20
    sta ZP_MAIN+$28
    sta ZP_MAIN+$30
    lda #$64
    sta ZP_MAIN+$22
    sta ZP_MAIN+$2A
    sta ZP_MAIN+$32
    lda #$62
    sta ZP_MAIN+$24
    sta ZP_MAIN+$2C
    sta ZP_MAIN+$34
    lda #$66
    sta ZP_MAIN+$26
    sta ZP_MAIN+$2E
    sta ZP_MAIN+$36
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
    sta REG_KERNEL+$185D
    sta REG_KERNEL+$1865
    eor #$FF
    sta REG_KERNEL+$1860
    sta REG_KERNEL+$1868
    lda ZP_MAIN+$02
    sta REG_KERNEL+$186B
    eor #$FF
    sta ZP_MAIN
    sta REG_KERNEL+$1876
    lda ZP_MAIN+$06
    sta REG_KERNEL+$1879
    eor #$FF
    sta ZP_MAIN+$04
    sta REG_KERNEL+$1884
    lda ZP_MAIN+$0A
    sta REG_KERNEL+$1887
    eor #$FF
    sta ZP_MAIN+$08
    sta REG_KERNEL+$1892
    ldx #$03
    sec
    bcs L585C
L5837:
    clc
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda #$01
    adc (ZP_MAIN+$02),y
    bcc L5875
L5842:
    clc
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda #$01
    adc (ZP_MAIN+$06),y
    bcc L5883
L584D:
    clc
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda #$01
    adc (ZP_MAIN+$0A),y
    bcc L5891
L5858:
    sta ZP_MAIN+$18,x
    ldy ZP_MAIN+$0C,x
L585C:
    lda REG_TABLE+$1000,y
    adc REG_TABLE+$1400,y
    sta ZP_MAIN+$0C,x
    lda REG_TABLE+$1200,y
    adc REG_TABLE+$1600,y
    adc REG_TABLE+$1000,y
    bcs L5837
    adc (ZP_MAIN),y
    sta ZP_MAIN+$1B,x
    lda (ZP_MAIN+$02),y
L5875:
    adc REG_TABLE+$1600,y
    adc REG_TABLE+$1000,y
    bcs L5842
    adc (ZP_MAIN+$04),y
    sta ZP_MAIN+$10,x
    lda (ZP_MAIN+$06),y
L5883:
    adc REG_TABLE+$1600,y
    adc REG_TABLE+$1000,y
    bcs L584D
    adc (ZP_MAIN+$08),y
    sta ZP_MAIN+$14,x
    lda (ZP_MAIN+$0A),y
L5891:
    adc REG_TABLE+$1600,y
    dex
    bpl L5858
    tax
    ldy ZP_MAIN+$18
    clc
    lda ZP_MAIN+$1B
    adc ZP_MAIN+$0D
    sta ZP_MAIN+$0D
    lda ZP_MAIN+$1C
    adc ZP_MAIN+$0E
    bcc L58AC
    inc ZP_MAIN+$0F
    beq L58EB
    clc
L58AC:
    adc ZP_MAIN+$10
    sta ZP_MAIN+$0E
    lda ZP_MAIN+$11
    adc ZP_MAIN+$14
    bcc L58B8
    inx
    clc
L58B8:
    adc ZP_MAIN+$0F
    bcc L58C0
    inx
    beq L58FD
    clc
L58C0:
    adc ZP_MAIN+$1D
    sta ZP_MAIN+$0F
    txa
    adc ZP_MAIN+$15
    bcc L58CB
    iny
    clc
L58CB:
    adc ZP_MAIN+$1E
    bcc L58D3
    iny
    beq L590B
    clc
L58D3:
    adc ZP_MAIN+$12
    tax
    tya
    adc ZP_MAIN+$13
    bcc L58DE
    inc ZP_MAIN+$19
    clc
L58DE:
    adc ZP_MAIN+$16
    tay
    lda ZP_MAIN+$17
    adc ZP_MAIN+$19
    bcs L58E8
    rts
L58E8:
    inc ZP_MAIN+$1A
    rts
L58EB:
    inc ZP_MAIN+$1E
    bne L58F9
    inc ZP_MAIN+$13
    bne L58F9
    inc ZP_MAIN+$17
    bne L58F9
    inc ZP_MAIN+$1A
L58F9:
    clc
    jmp REG_KERNEL+$18AC
L58FD:
    inc ZP_MAIN+$13
    bne L5907
    inc ZP_MAIN+$17
    bne L5907
    inc ZP_MAIN+$1A
L5907:
    clc
    jmp REG_KERNEL+$18C0
L590B:
    inc ZP_MAIN+$17
    bne L5911
    inc ZP_MAIN+$1A
L5911:
    clc
    jmp REG_KERNEL+$18D3
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
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
    bit ZP_SMUL+$27
    bmi L5A0D
    bit ZP_SMUL+$37
    bmi L5A1C
    tax
    tya
    adc #$00
    rts
L5A0D:
    bit ZP_SMUL+$37
    bmi L5A27
    bcc L5A14
    iny
L5A14:
    sec
    sbc #$00
    tax
    tya
    sbc ZP_SMUL+$37
    rts
L5A1C:
    bcc L5A1F
    iny
L5A1F:
    sec
    sbc ZP_SMUL+$19
    tax
    tya
    sbc ZP_SMUL+$27
    rts
L5A27:
    bcc L5A2A
    iny
L5A2A:
    sec
    sbc REG_KERNEL+$1A16
    tax
    tya
    sbc ZP_SMUL+$37
    tay
    txa
    sec
    sbc ZP_SMUL+$19
    tax
    tya
    sbc ZP_SMUL+$27
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
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
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

; Source interval $5E00-$5FFF
* = REG_GAME_API
    jmp REG_GAME
    jmp REG_GAME
    jmp REG_GAME+$002C
    jmp REG_GAME+$002C
    jmp REG_GAME+$03B5
    jmp REG_GAME+$03CC
    jmp REG_GAME+$03E3
    jmp REG_GAME+$040C
    jmp REG_GAME+$0435
    jmp REG_GAME+$0475
    jmp REG_GAME+$04BB
    jmp REG_GAME+$0666
    jmp REG_GAME+$0671
    jmp REG_GAME+$067C
    jmp REG_GAME+$068D
    jmp REG_GAME+$06AB
    jmp REG_GAME+$0A40
    jmp REG_GAME+$07DB
    jmp REG_GAME+$07E9
; Canonical standalone VEC2 normalization backend for this profile.
!source "../../v4_reu_16m/resident/vector/native/vec2_normalize_q8_8.asm"
    !byte $A5, $14, $30, $05, $06, $12, $0A, $10, $FB, $A8, $A5, $12, $85, $13, $4C, $32
    !byte $5F, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

; Source interval $6000-$9BFF
* = REG_TABLE
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
    !byte $AF, $FF, $FD, $FC, $FA, $F8, $F4, $F1, $ED, $E9, $E4, $DF, $D8, $D2, $CB, $C3
    !byte $BB, $B4, $AA, $A1, $97, $8D, $81, $76, $6A, $5E, $51, $45, $36, $28, $1A, $0B
    !byte $FB, $EB, $DB, $CB, $B8, $A7, $94, $80, $6E, $5B, $46, $31, $1C, $09, $F1, $DC
    !byte $C5, $B0, $95, $7F, $65, $4C, $34, $1B, $01, $E4, $CB, $AF, $93, $78, $5D, $40
    !byte $20, $01, $E6, $C9, $A9, $8A, $6A, $4E, $2C, $0B, $ED, $CA, $A7, $87, $63, $42
    !byte $1D, $FD, $D8, $BA, $91, $6A, $48, $20, $01, $D8, $B3, $8D, $67, $41, $1C, $F3
    !byte $CE, $A6, $7E, $57, $2F, $02, $DD, $AF, $84, $5D, $31, $08, $E2, $B7, $8A, $63
    !byte $35, $08, $DE, $B5, $8A, $5A, $2D, $01, $D5, $A9, $7F, $51, $26, $F7, $CC, $95
    !byte $6B, $31, $0B, $E2, $B0, $84, $58, $28, $F9, $CA, $9E, $6D, $3F, $0E, $E0, $AF
    !byte $80, $51, $1E, $F1, $BD, $8F, $5E, $2E, $F9, $D1, $9C, $6D, $3C, $08, $D7, $A4
    !byte $77, $49, $19, $E7, $B6, $84, $55, $20, $F9, $C0, $94, $5E, $32, $FA, $C3, $98
    !byte $62, $37, $05, $D6, $9F, $6F, $3D, $0B, $DC, $A7, $74, $49, $1F, $E8, $B7, $87
    !byte $52, $22, $F3, $C2, $8A, $60, $29, $00, $C9, $9D, $64, $3A, $06, $CD, $9A, $6C
    !byte $3D, $0D, $DC, $AB, $7C, $4B, $21, $F0, $BE, $90, $61, $32, $02, $CF, $A5, $72
    !byte $40, $10, $D2, $AC, $7B, $4F, $1E, $F2, $B7, $8F, $62, $2D, $03, $D1, $A6, $73
    !byte $48, $1D, $E8, $BC, $92, $68, $35, $0F, $D3, $B0, $7C, $52, $20, $EA, $E3, $C4
    !byte $5A, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F
    !byte $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F
    !byte $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7D, $7D
    !byte $7D, $7D, $7D, $7D, $7D, $7D, $7D, $7D, $7D, $7C, $7C, $7C, $7C, $7C, $7C, $7C
    !byte $7C, $7C, $7B, $7B, $7B, $7B, $7B, $7B, $7B, $7B, $7A, $7A, $7A, $7A, $7A, $7A
    !byte $7A, $79, $79, $79, $79, $79, $79, $79, $79, $78, $78, $78, $78, $78, $78, $77
    !byte $77, $77, $77, $77, $77, $77, $76, $76, $76, $76, $76, $76, $75, $75, $75, $75
    !byte $75, $75, $74, $74, $74, $74, $74, $74, $73, $73, $73, $73, $73, $72, $72, $72
    !byte $72, $72, $72, $71, $71, $71, $71, $71, $70, $70, $70, $70, $70, $70, $6F, $6F
    !byte $6F, $6F, $6F, $6E, $6E, $6E, $6E, $6E, $6D, $6D, $6D, $6D, $6D, $6D, $6C, $6C
    !byte $6C, $6C, $6C, $6B, $6B, $6B, $6B, $6B, $6A, $6A, $6A, $6A, $6A, $69, $69, $69
    !byte $69, $69, $69, $68, $68, $68, $68, $68, $67, $67, $67, $67, $67, $66, $66, $66
    !byte $66, $66, $65, $65, $65, $65, $65, $65, $64, $64, $64, $64, $64, $63, $63, $63
    !byte $63, $63, $62, $62, $62, $62, $62, $61, $61, $61, $61, $61, $61, $60, $60, $60
    !byte $60, $60, $5F, $5F, $5F, $5F, $5F, $5E, $5E, $5E, $5E, $5E, $5E, $5D, $5D, $5D
    !byte $5D, $5D, $5C, $5C, $5C, $5C, $5C, $5C, $5B, $5B, $5B, $5B, $5B, $5A, $5A, $5A
    !byte $55, $7F, $3F, $9F, $3F, $AC, $3F, $AF, $3F, $B3, $3D, $AE, $3A, $B1, $3C, $BC
    !byte $38, $AF, $35, $AD, $35, $AB, $32, $B0, $2C, $A8, $28, $A0, $26, $A6, $1C, $97
    !byte $16, $95, $0F, $83, $0B, $7E, $FE, $82, $F6, $6F, $EF, $6A, $E4, $54, $D6, $4D
    !byte $C7, $36, $BC, $2B, $AB, $27, $98, $0B, $84, $06, $73, $ED, $66, $D7, $48, $BF
    !byte $3C, $B7, $1F, $90, $09, $7B, $F1, $58, $CE, $44, $AC, $25, $9A, $04, $79, $E6
    !byte $5C, $C1, $34, $92, $0E, $85, $EA, $60, $BA, $31, $9A, $03, $6F, $D7, $3B, $AA
    !byte $0E, $77, $E1, $45, $AD, $1F, $7B, $EF, $58, $B7, $22, $83, $DD, $44, $AB, $06
    !byte $70, $D5, $33, $8F, $EF, $57, $B9, $17, $76, $D4, $2C, $8C, $E3, $45, $9C, $0A
    !byte $60, $D3, $1D, $6D, $CF, $24, $77, $D2, $2B, $83, $D4, $2F, $83, $DD, $30, $87
    !byte $DC, $2E, $88, $D6, $2F, $7E, $D2, $24, $7E, $C1, $19, $67, $B7, $0B, $5B, $AE
    !byte $F5, $3E, $8A, $D9, $26, $73, $BC, $0C, $49, $A0, $E2, $32, $74, $C7, $18, $56
    !byte $A6, $E4, $2C, $6F, $BD, $01, $47, $8D, $CF, $18, $5E, $99, $D3, $1D, $5F, $A0
    !byte $E6, $26, $64, $A4, $EE, $25, $6B, $A0, $E7, $1F, $67, $9C, $DE, $25, $63, $9D
    !byte $D6, $12, $4D, $88, $C1, $FC, $2E, $68, $A4, $DB, $12, $48, $80, $BC, $EC, $27
    !byte $60, $96, $DC, $07, $3F, $6F, $A6, $D7, $18, $44, $75, $AF, $DC, $12, $40, $78
    !byte $A5, $D2, $0A, $39, $66, $91, $C7, $ED, $2B, $4F, $84, $B0, $E2, $19, $20, $3F
    !byte $5A, $00, $01, $01, $02, $02, $03, $03, $04, $04, $05, $05, $06, $06, $07, $07
    !byte $08, $08, $09, $09, $0A, $0A, $0B, $0B, $0C, $0C, $0D, $0D, $0E, $0E, $0F, $0F
    !byte $10, $10, $11, $11, $12, $12, $12, $13, $13, $14, $14, $15, $15, $16, $16, $17
    !byte $17, $18, $18, $19, $19, $1A, $1A, $1B, $1B, $1C, $1C, $1C, $1D, $1D, $1E, $1E
    !byte $1F, $1F, $20, $20, $21, $21, $21, $22, $22, $23, $23, $24, $24, $25, $25, $25
    !byte $26, $26, $27, $27, $28, $28, $28, $29, $29, $2A, $2A, $2B, $2B, $2B, $2C, $2C
    !byte $2D, $2D, $2D, $2E, $2E, $2F, $2F, $2F, $30, $30, $31, $31, $31, $32, $32, $33
    !byte $33, $33, $34, $34, $34, $35, $35, $36, $36, $36, $37, $37, $37, $38, $38, $39
    !byte $39, $39, $3A, $3A, $3A, $3B, $3B, $3B, $3C, $3C, $3C, $3D, $3D, $3D, $3E, $3E
    !byte $3E, $3F, $3F, $3F, $40, $40, $40, $41, $41, $41, $42, $42, $42, $43, $43, $43
    !byte $43, $44, $44, $44, $45, $45, $45, $46, $46, $46, $46, $47, $47, $47, $48, $48
    !byte $48, $48, $49, $49, $49, $4A, $4A, $4A, $4A, $4B, $4B, $4B, $4B, $4C, $4C, $4C
    !byte $4C, $4D, $4D, $4D, $4D, $4E, $4E, $4E, $4E, $4F, $4F, $4F, $4F, $50, $50, $50
    !byte $50, $51, $51, $51, $51, $51, $52, $52, $52, $52, $53, $53, $53, $53, $53, $54
    !byte $54, $54, $54, $55, $55, $55, $55, $55, $56, $56, $56, $56, $56, $57, $57, $57
    !byte $57, $57, $58, $58, $58, $58, $58, $58, $59, $59, $59, $59, $59, $5A, $5A, $5A
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $FE, $FB, $F7, $F3, $EF, $EC, $E8, $E4, $E0, $DD, $DA, $D6, $D3, $CF, $CC, $C9
    !byte $C6, $C3, $BF, $BC, $B9, $B6, $B3, $B0, $AD, $AA, $A8, $A5, $A2, $9F, $9D, $9A
    !byte $98, $95, $93, $90, $8E, $8B, $8A, $87, $85, $83, $80, $7E, $7C, $7A, $78, $76
    !byte $73, $71, $6F, $6E, $6B, $69, $66, $65, $64, $61, $60, $5D, $5C, $59, $58, $56
    !byte $55, $53, $50, $4E, $4D, $4B, $49, $49, $46, $44, $44, $42, $40, $3E, $3C, $3C
    !byte $3A, $37, $37, $35, $33, $33, $30, $30, $2D, $2D, $2B, $2A, $28, $27, $25, $24
    !byte $24, $21, $20, $20, $1D, $1C, $1C, $1A, $18, $17, $17, $15, $14, $12, $11, $10
    !byte $10, $0E, $0D, $0C, $0A, $09, $08, $07, $06, $05, $04, $03, $02, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
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
L7800:
    sta ZP_MAIN+$3F
    sta ZP_MAIN+$40
    sec
    rts
    lda ZP_MAIN+$3D
    beq L7800
    bpl L7811
    eor #$FF
    clc
    adc #$01
L7811:
    sta ZP_MAIN+$3E
    lda ZP_MAIN+$3C
    bpl L781C
    eor #$FF
    clc
    adc #$01
L781C:
    cmp ZP_MAIN+$3E
    bcs L7833
    sta ZP_MAIN+$40
    lda #$00
    sta ZP_MAIN+$3F
    bit ZP_MAIN+$3C
    bmi L782C
    clc
    rts
L782C:
    sec
    sbc ZP_MAIN+$40
    sta ZP_MAIN+$40
    clc
    rts
L7833:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7862
    sta ZP_MAIN+$40
    lda #$01
    sta ZP_MAIN+$3F
    bit ZP_MAIN+$3C
    bmi L784F
    bit ZP_MAIN+$3D
    bmi L7849
    clc
    rts
L7849:
    lda #$FF
    sta ZP_MAIN+$3F
    clc
    rts
L784F:
    lda #$00
    sec
    sbc ZP_MAIN+$40
    sta ZP_MAIN+$40
    bit ZP_MAIN+$3D
    bpl L785C
    clc
    rts
L785C:
    lda #$FF
    sta ZP_MAIN+$3F
    clc
    rts
L7862:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7871
    sta ZP_MAIN+$40
    lda #$02
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7871:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7880
    sta ZP_MAIN+$40
    lda #$03
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7880:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L788F
    sta ZP_MAIN+$40
    lda #$04
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L788F:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L789E
    sta ZP_MAIN+$40
    lda #$05
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L789E:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L78AD
    sta ZP_MAIN+$40
    lda #$06
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L78AD:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L78BC
    sta ZP_MAIN+$40
    lda #$07
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L78BC:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L78CB
    sta ZP_MAIN+$40
    lda #$08
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L78CB:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L78DA
    sta ZP_MAIN+$40
    lda #$09
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L78DA:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L78E9
    sta ZP_MAIN+$40
    lda #$0A
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L78E9:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L78F8
    sta ZP_MAIN+$40
    lda #$0B
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L78F8:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7907
    sta ZP_MAIN+$40
    lda #$0C
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7907:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7916
    sta ZP_MAIN+$40
    lda #$0D
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7916:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7925
    sta ZP_MAIN+$40
    lda #$0E
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7925:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7934
    sta ZP_MAIN+$40
    lda #$0F
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7934:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7943
    sta ZP_MAIN+$40
    lda #$10
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7943:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7952
    sta ZP_MAIN+$40
    lda #$11
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7952:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7961
    sta ZP_MAIN+$40
    lda #$12
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7961:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L7970
    sta ZP_MAIN+$40
    lda #$13
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L7970:
    sbc ZP_MAIN+$3E
    cmp ZP_MAIN+$3E
    bcs L797F
    sta ZP_MAIN+$40
    lda #$14
    sta ZP_MAIN+$3F
    jmp REG_TABLE+$19A8
L797F:
    sta ZP_MAIN+$40
    ldx #$00
    stx ZP_MAIN+$3F
L7985:
    lda ZP_MAIN+$3E
    asl
    bcs L7990
    cmp ZP_MAIN+$40
    bcc L79C5
    beq L79C5
L7990:
    lda ZP_MAIN+$40
L7992:
    cmp ZP_MAIN+$3E
    bcc L7998
    sbc ZP_MAIN+$3E
L7998:
    rol ZP_MAIN+$3F
    lsr ZP_MAIN+$3E
    dex
    bpl L7992
    sta ZP_MAIN+$40
    lda ZP_MAIN+$3F
    clc
    adc #$14
    sta ZP_MAIN+$3F
    lda ZP_MAIN+$3C
    bmi L79B1
    eor ZP_MAIN+$3D
    bmi L79BC
    rts
L79B1:
    lda #$00
    sec
    sbc ZP_MAIN+$40
    sta ZP_MAIN+$40
    lda ZP_MAIN+$3D
    bmi L79C3
L79BC:
    lda #$00
    sec
    sbc ZP_MAIN+$3F
    sta ZP_MAIN+$3F
L79C3:
    clc
    rts
L79C5:
    sta ZP_MAIN+$3E
    inx
    bne L7985
    brk
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00
    lda ZP_MAIN+$3D
    bmi L7A60
    lda ZP_MAIN+$3F
    bmi L7A36
    lda ZP_MAIN+$3E
    ora ZP_MAIN+$3F
    bne L7A11
    jmp REG_TABLE+$1BC8
L7A11:
    !byte $A7, ZP_MAIN+$3D    ; LAX zp
    cmp ZP_MAIN+$3F
    bcs L7A1A
    jmp REG_TABLE+$1B8D
L7A1A:
    bne L7A25
    lda ZP_MAIN+$3C
    cmp ZP_MAIN+$3E
    bcs L7A25
    jmp REG_TABLE+$1B8D
L7A25:
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$40
    stx ZP_MAIN+$41
    lda ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda ZP_MAIN+$3F
    sta ZP_MAIN+$43
    jmp REG_TABLE+$1ACC
L7A36:
    lda #$00
    sec
    sbc ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda #$00
    sbc ZP_MAIN+$3F
    sta ZP_MAIN+$43
    !byte $A7, ZP_MAIN+$3D    ; LAX zp
    cmp ZP_MAIN+$43
    bcs L7A4C
    jmp REG_TABLE+$1B8D
L7A4C:
    bne L7A57
    lda ZP_MAIN+$3C
    cmp ZP_MAIN+$42
    bcs L7A57
    jmp REG_TABLE+$1B8D
L7A57:
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$40
    stx ZP_MAIN+$41
    jmp REG_TABLE+$1AF6
L7A60:
    lda ZP_MAIN+$3F
    bmi L7A99
    lda ZP_MAIN+$3E
    ora ZP_MAIN+$3F
    bne L7A6D
    jmp REG_TABLE+$1BC8
L7A6D:
    lda #$00
    sec
    sbc ZP_MAIN+$3C
    sta ZP_MAIN+$40
    lda #$00
    sbc ZP_MAIN+$3D
    sta ZP_MAIN+$41
    !byte $A7, ZP_MAIN+$41    ; LAX zp
    cmp ZP_MAIN+$3F
    bcs L7A83
    jmp REG_TABLE+$1B8D
L7A83:
    bne L7A8E
    lda ZP_MAIN+$40
    cmp ZP_MAIN+$3E
    bcs L7A8E
    jmp REG_TABLE+$1B8D
L7A8E:
    lda ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda ZP_MAIN+$3F
    sta ZP_MAIN+$43
    jmp REG_TABLE+$1B1F
L7A99:
    !byte $A7, ZP_MAIN+$3D    ; LAX zp
    cmp ZP_MAIN+$3F
    bcc L7AAF
    beq L7AA4
    jmp REG_TABLE+$1B8D
L7AA4:
    lda ZP_MAIN+$3C
    cmp ZP_MAIN+$3E
    bcc L7AAF
    beq L7AAF
    jmp REG_TABLE+$1B8D
L7AAF:
    lda #$00
    sec
    sbc ZP_MAIN+$3C
    sta ZP_MAIN+$40
    lda #$00
    sbc ZP_MAIN+$3D
    sta ZP_MAIN+$41
    lda #$00
    sec
    sbc ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda #$00
    sbc ZP_MAIN+$3F
    sta ZP_MAIN+$43
    jmp REG_TABLE+$1B55
    sec
    lda ZP_MAIN+$40
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    lda ZP_MAIN+$41
    sbc ZP_MAIN+$43
    sta ZP_MAIN+$47
    cmp ZP_MAIN+$43
    bcc L7AE5
    bne L7AEF
    lda ZP_MAIN+$46
    cmp ZP_MAIN+$42
    bcs L7AEF
L7AE5:
    lda #$01
    sta ZP_MAIN+$44
    lda #$00
    sta ZP_MAIN+$45
    clc
    rts
L7AEF:
    lda ZP_MAIN+$47
    jsr REG_TABLE+$1CBD
    clc
    rts
    sec
    lda ZP_MAIN+$40
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    lda ZP_MAIN+$41
    sbc ZP_MAIN+$43
    sta ZP_MAIN+$47
    cmp ZP_MAIN+$43
    bcc L7B0F
    bne L7B17
    lda ZP_MAIN+$46
    cmp ZP_MAIN+$42
    bcs L7B17
L7B0F:
    lda #$FF
    sta ZP_MAIN+$44
    sta ZP_MAIN+$45
    clc
    rts
L7B17:
    lda ZP_MAIN+$47
    jsr REG_TABLE+$1CBD
    jmp REG_TABLE+$1BAA
    sec
    lda ZP_MAIN+$40
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    lda ZP_MAIN+$41
    sbc ZP_MAIN+$43
    sta ZP_MAIN+$47
    cmp ZP_MAIN+$43
    bcc L7B38
    bne L7B4D
    lda ZP_MAIN+$46
    cmp ZP_MAIN+$42
    bcs L7B4D
L7B38:
    lda #$00
    sec
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$47
    lda #$FF
    sta ZP_MAIN+$44
    sta ZP_MAIN+$45
    clc
    rts
L7B4D:
    lda ZP_MAIN+$47
    jsr REG_TABLE+$1CBD
    jmp REG_TABLE+$1B9D
    sec
    lda ZP_MAIN+$40
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    lda ZP_MAIN+$41
    sbc ZP_MAIN+$43
    sta ZP_MAIN+$47
    cmp ZP_MAIN+$43
    bcc L7B6E
    bne L7B85
    lda ZP_MAIN+$46
    cmp ZP_MAIN+$42
    bcs L7B85
L7B6E:
    lda #$00
    sec
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$47
    lda #$01
    sta ZP_MAIN+$44
    lda #$00
    sta ZP_MAIN+$45
    clc
    rts
L7B85:
    lda ZP_MAIN+$47
    jsr REG_TABLE+$1CBD
    jmp REG_TABLE+$1BB9
    lda #$00
    sta ZP_MAIN+$44
    sta ZP_MAIN+$45
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$46
    lda ZP_MAIN+$3D
    sta ZP_MAIN+$47
    clc
    rts
    lda #$00
    sec
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$47
    lda #$00
    sec
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$44
    lda #$00
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$45
    clc
    rts
    lda #$00
    sec
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$47
    clc
    rts
    lda #$00
    sta ZP_MAIN+$44
    sta ZP_MAIN+$45
    sta ZP_MAIN+$46
    sta ZP_MAIN+$47
    sec
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $A7, $43, $C5, $45, $B0, $27, $A9, $00
    !byte $85, $46, $85, $47, $A5, $42, $85, $48, $86, $49, $60, $A5, $42, $E5, $44, $90
    !byte $ED, $E0, $01, $90, $0D, $85, $48, $0B, $00, $85, $49, $85, $47, $A9, $01, $85
    !byte $46, $60, $4C, $0E, $80, $F0, $E4, $A5, $42, $E5, $44, $85, $48, $8A, $E5, $45
    !byte $C5, $45, $B0, $73, $85, $49, $A9, $00, $85, $47, $A9, $01, $85, $46, $60
L7C53:
    cmp REG_TABLE+$204D,x
    bcc L7C5B
    jmp REG_TABLE+$1EFA
L7C5B:
    sec
    bcs L7CC3
L7C5E:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7C6C
    txa
L7C65:
    sta ZP_MAIN+$47
    lda #$02
    sta ZP_MAIN+$44
    rts
L7C6C:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7C79
L7C72:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7C80
    txa
L7C79:
    sta ZP_MAIN+$47
    lda #$03
    sta ZP_MAIN+$44
    rts
L7C80:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7C8D
L7C86:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7C94
    txa
L7C8D:
    sta ZP_MAIN+$47
    lda #$04
    sta ZP_MAIN+$44
    rts
L7C94:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    jmp REG_TABLE+$1D7B
    !byte $AA, $A5, $48, $E5, $44, $B0, $0B, $86, $49, $A9, $00, $85, $47, $A9, $01, $85
    !byte $46, $60, $CA, $10, $03, $4C, $0E, $80, $85, $48, $0B, $00, $85, $47, $90, $AA
    !byte $F0, $DE
    ldx ZP_MAIN+$43
    cpx #$0F
    bcc L7C53
L7CC3:
    ldy #$00
    sty ZP_MAIN+$45
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7C65
    beq L7C5E
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7C79
    beq L7C72
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7C8D
    beq L7C86
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7D7B
    beq L7D74
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7D89
    beq L7D82
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7D97
    beq L7D90
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7DA5
    beq L7D9E
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7DB3
    beq L7DAC
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7DC1
    beq L7DBA
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7DCF
    beq L7DC8
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    jmp REG_TABLE+$1E00
L7D74:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7DD6
    txa
L7D7B:
    sta ZP_MAIN+$47
    lda #$05
    sta ZP_MAIN+$44
    rts
L7D82:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7DDC
    txa
L7D89:
    sta ZP_MAIN+$47
    lda #$06
    sta ZP_MAIN+$44
    rts
L7D90:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7DE2
    txa
L7D97:
    sta ZP_MAIN+$47
    lda #$07
    sta ZP_MAIN+$44
    rts
L7D9E:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7DE8
    txa
L7DA5:
    sta ZP_MAIN+$47
    lda #$08
    sta ZP_MAIN+$44
    rts
L7DAC:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7DEE
    txa
L7DB3:
    sta ZP_MAIN+$47
    lda #$09
    sta ZP_MAIN+$44
    rts
L7DBA:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7DF4
    txa
L7DC1:
    sta ZP_MAIN+$47
    lda #$0A
    sta ZP_MAIN+$44
    rts
L7DC8:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7DFA
    txa
L7DCF:
    sta ZP_MAIN+$47
    lda #$0B
    sta ZP_MAIN+$44
    rts
L7DD6:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7D89
L7DDC:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7D97
L7DE2:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7DA5
L7DE8:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7DB3
L7DEE:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7DC1
L7DF4:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7DCF
L7DFA:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7E57
    cmp ZP_MAIN+$43
    bcc L7E57
    beq L7E50
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7E6B
    beq L7E64
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7E7F
    beq L7E78
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7E93
    beq L7E8C
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    cmp ZP_MAIN+$43
    bcc L7EA7
    beq L7EA0
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
L7E50:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7E5E
    txa
L7E57:
    sta ZP_MAIN+$47
    lda #$0C
    sta ZP_MAIN+$44
    rts
L7E5E:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7E6B
L7E64:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7E72
    txa
L7E6B:
    sta ZP_MAIN+$47
    lda #$0D
    sta ZP_MAIN+$44
    rts
L7E72:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7E7F
L7E78:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7E86
    txa
L7E7F:
    sta ZP_MAIN+$47
    lda #$0E
    sta ZP_MAIN+$44
    rts
L7E86:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7E93
L7E8C:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7E9A
    txa
L7E93:
    sta ZP_MAIN+$47
    lda #$0F
    sta ZP_MAIN+$44
    rts
L7E9A:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    bcc L7EA7
L7EA0:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcs L7EAE
    txa
L7EA7:
    sta ZP_MAIN+$47
    lda #$10
    sta ZP_MAIN+$44
    rts
L7EAE:
    sta ZP_MAIN+$46
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$47
    lda #$11
    sta ZP_MAIN+$44
    rts
L7EB9:
    jmp REG_TABLE+$2012
L7EBC:
    jmp REG_TABLE+$200E
L7EBF:
    cpx #$01
    bcc L7EBC
    beq L7EB9
    lda ZP_MAIN+$40
    asl
    sta ZP_MAIN+$44
    lda ZP_MAIN+$41
    rol
    sta ZP_MAIN+$46
    lda #$00
    sta ZP_MAIN+$45
    rol
    rol ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    cmp ZP_MAIN+$43
    bcc L7F16
    beq L7EEB
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    bcs L7F16
L7EEB:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcc L7EF7
    sta ZP_MAIN+$46
    lda #$00
    bcs L7F16
L7EF7:
    txa
    bcc L7F16
    cpx #$04
    bcc L7EBF
    cpx #$08
    bcs L7F4B
    lda ZP_MAIN+$40
    asl
    sta ZP_MAIN+$44
    lda ZP_MAIN+$41
    rol
    sta ZP_MAIN+$46
    lda #$00
    sta ZP_MAIN+$45
    rol
    asl ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
L7F16:
    rol ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    cmp ZP_MAIN+$43
    bcc L7F64
    beq L7F2D
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
    bcs L7F64
L7F2D:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcc L7F39
    sta ZP_MAIN+$46
    lda #$00
    bcs L7F64
L7F39:
    txa
    bcc L7F64
L7F3C:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcc L7F48
    sta ZP_MAIN+$46
    lda #$00
    bcs L7F79
L7F48:
    txa
    bcc L7F79
L7F4B:
    lda ZP_MAIN+$40
    asl
    sta ZP_MAIN+$44
    lda ZP_MAIN+$41
    rol
    sta ZP_MAIN+$46
    lda #$00
    sta ZP_MAIN+$45
    rol
    asl ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    asl ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
L7F64:
    rol ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    cmp ZP_MAIN+$43
    bcc L7F79
    beq L7F3C
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
L7F79:
    rol ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    cmp ZP_MAIN+$43
    bcc L7F8E
    beq L7FD2
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
L7F8E:
    rol ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    cmp ZP_MAIN+$43
    bcc L7FA3
    beq L7FE1
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
L7FA3:
    rol ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    cmp ZP_MAIN+$43
    bcc L7FB8
    beq L7FF0
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
L7FB8:
    rol ZP_MAIN+$44
    rol ZP_MAIN+$46
    rol
    cmp ZP_MAIN+$43
    bcc L7FCD
    beq L7FFF
    tay
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    sta ZP_MAIN+$46
    tya
    sbc ZP_MAIN+$43
L7FCD:
    rol ZP_MAIN+$44
    sta ZP_MAIN+$47
    rts
L7FD2:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcc L7FDE
    sta ZP_MAIN+$46
    lda #$00
    bcs L7F8E
L7FDE:
    txa
    bcc L7F8E
L7FE1:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcc L7FED
    sta ZP_MAIN+$46
    lda #$00
    bcs L7FA3
L7FED:
    txa
    bcc L7FA3
L7FF0:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcc L7FFC
    sta ZP_MAIN+$46
    lda #$00
    bcs L7FB8
L7FFC:
    txa
    bcc L7FB8
L7FFF:
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    bcc L800B
    sta ZP_MAIN+$46
    lda #$00
    bcs L7FCD
L800B:
    txa
    bcc L7FCD
    lda ZP_MAIN+$42
    beq L8043
    lda ZP_MAIN+$40
    sta ZP_MAIN+$44
    lda ZP_MAIN+$41
    sta ZP_MAIN+$45
    lda #$00
    lsr
    sta ZP_MAIN+$46
    sta ZP_MAIN+$47
    ldy #$10
L8023:
    rol ZP_MAIN+$44
    rol ZP_MAIN+$45
    rol ZP_MAIN+$46
    rol ZP_MAIN+$47
    sec
    lda ZP_MAIN+$46
    sbc ZP_MAIN+$42
    tax
    lda ZP_MAIN+$47
    sbc ZP_MAIN+$43
    bcc L803B
    sta ZP_MAIN+$47
    stx ZP_MAIN+$46
L803B:
    dey
    bne L8023
    rol ZP_MAIN+$44
    rol ZP_MAIN+$45
    rts
L8043:
    sta ZP_MAIN+$44
    sta ZP_MAIN+$45
    sta ZP_MAIN+$46
    sta ZP_MAIN+$47
    sec
    rts
    !byte $00, $11, $16, $20, $24, $2B, $34, $3D, $3F, $45, $4D, $54, $5B, $62, $68, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00
    lda ZP_MAIN+$3E
    bpl L8107
    jmp REG_TABLE+$2190
L8107:
    lda ZP_MAIN+$41
    bpl L810E
    jmp REG_TABLE+$2151
L810E:
    lda ZP_MAIN+$3F
    ora ZP_MAIN+$40
    ora ZP_MAIN+$41
    bne L8119
    jmp REG_TABLE+$239D
L8119:
    !byte $A7, ZP_MAIN+$3E    ; LAX zp
    cmp ZP_MAIN+$41
    bcs L8122
    jmp REG_TABLE+$2348
L8122:
    bne L8138
    lda ZP_MAIN+$3D
    cmp ZP_MAIN+$40
    bcs L812D
    jmp REG_TABLE+$2348
L812D:
    bne L8138
    lda ZP_MAIN+$3C
    cmp ZP_MAIN+$3F
    bcs L8138
    jmp REG_TABLE+$2348
L8138:
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$42
    lda ZP_MAIN+$3D
    sta ZP_MAIN+$43
    stx ZP_MAIN+$44
    lda ZP_MAIN+$3F
    sta ZP_MAIN+$45
    lda ZP_MAIN+$40
    sta ZP_MAIN+$46
    lda ZP_MAIN+$41
    sta ZP_MAIN+$47
    jmp REG_TABLE+$222A
    lda #$00
    sec
    sbc ZP_MAIN+$3F
    sta ZP_MAIN+$45
    lda #$00
    sbc ZP_MAIN+$40
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$41
    sta ZP_MAIN+$47
    !byte $A7, ZP_MAIN+$3E    ; LAX zp
    cmp ZP_MAIN+$47
    bcs L816D
    jmp REG_TABLE+$2348
L816D:
    bne L8183
    lda ZP_MAIN+$3D
    cmp ZP_MAIN+$46
    bcs L8178
    jmp REG_TABLE+$2348
L8178:
    bne L8183
    lda ZP_MAIN+$3C
    cmp ZP_MAIN+$45
    bcs L8183
    jmp REG_TABLE+$2348
L8183:
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$42
    lda ZP_MAIN+$3D
    sta ZP_MAIN+$43
    stx ZP_MAIN+$44
    jmp REG_TABLE+$2269
    lda ZP_MAIN+$41
    bmi L81E0
    lda ZP_MAIN+$3F
    ora ZP_MAIN+$40
    ora ZP_MAIN+$41
    bne L819F
    jmp REG_TABLE+$239D
L819F:
    lda #$00
    sec
    sbc ZP_MAIN+$3C
    sta ZP_MAIN+$42
    lda #$00
    sbc ZP_MAIN+$3D
    sta ZP_MAIN+$43
    lda #$00
    sbc ZP_MAIN+$3E
    sta ZP_MAIN+$44
    !byte $A7, ZP_MAIN+$44    ; LAX zp
    cmp ZP_MAIN+$41
    bcs L81BB
    jmp REG_TABLE+$2348
L81BB:
    bne L81D1
    lda ZP_MAIN+$43
    cmp ZP_MAIN+$40
    bcs L81C6
    jmp REG_TABLE+$2348
L81C6:
    bne L81D1
    lda ZP_MAIN+$42
    cmp ZP_MAIN+$3F
    bcs L81D1
    jmp REG_TABLE+$2348
L81D1:
    lda ZP_MAIN+$3F
    sta ZP_MAIN+$45
    lda ZP_MAIN+$40
    sta ZP_MAIN+$46
    lda ZP_MAIN+$41
    sta ZP_MAIN+$47
    jmp REG_TABLE+$22A6
L81E0:
    !byte $A7, ZP_MAIN+$3E    ; LAX zp
    cmp ZP_MAIN+$41
    bcc L8201
    beq L81EB
    jmp REG_TABLE+$2348
L81EB:
    lda ZP_MAIN+$3D
    cmp ZP_MAIN+$40
    bcc L8201
    beq L81F6
    jmp REG_TABLE+$2348
L81F6:
    lda ZP_MAIN+$3C
    cmp ZP_MAIN+$3F
    bcc L8201
    beq L8201
    jmp REG_TABLE+$2348
L8201:
    lda #$00
    sec
    sbc ZP_MAIN+$3C
    sta ZP_MAIN+$42
    lda #$00
    sbc ZP_MAIN+$3D
    sta ZP_MAIN+$43
    lda #$00
    sbc ZP_MAIN+$3E
    sta ZP_MAIN+$44
    lda #$00
    sec
    sbc ZP_MAIN+$3F
    sta ZP_MAIN+$45
    lda #$00
    sbc ZP_MAIN+$40
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$41
    sta ZP_MAIN+$47
    jmp REG_TABLE+$22F6
    sec
    lda ZP_MAIN+$42
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$43
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$44
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8251
    bne L825D
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8251
    bne L825D
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L825D
L8251:
    lda #$01
    sta ZP_MAIN+$48
    lda #$00
    sta ZP_MAIN+$49
    sta ZP_MAIN+$4A
    clc
    rts
L825D:
    ldx #$00
    stx ZP_MAIN+$49
    stx ZP_MAIN+$4A
    jsr REG_TABLE+$24C7
    jmp REG_TABLE+$235E
    sec
    lda ZP_MAIN+$42
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$43
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$44
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8290
    bne L829A
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8290
    bne L829A
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L829A
L8290:
    lda #$FF
    sta ZP_MAIN+$48
    sta ZP_MAIN+$49
    sta ZP_MAIN+$4A
    clc
    rts
L829A:
    ldx #$00
    stx ZP_MAIN+$49
    stx ZP_MAIN+$4A
    jsr REG_TABLE+$24C7
    jmp REG_TABLE+$2373
    sec
    lda ZP_MAIN+$42
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$43
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$44
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L82CD
    bne L82EA
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L82CD
    bne L82EA
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L82EA
L82CD:
    lda #$00
    sec
    sbc ZP_MAIN+$4B
    sta ZP_MAIN+$4B
    lda #$00
    sbc ZP_MAIN+$4C
    sta ZP_MAIN+$4C
    lda #$00
    sbc ZP_MAIN+$4D
    sta ZP_MAIN+$4D
    lda #$FF
    sta ZP_MAIN+$48
    sta ZP_MAIN+$49
    sta ZP_MAIN+$4A
    clc
    rts
L82EA:
    ldx #$00
    stx ZP_MAIN+$49
    stx ZP_MAIN+$4A
    jsr REG_TABLE+$24C7
    jmp REG_TABLE+$2360
    sec
    lda ZP_MAIN+$42
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$43
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$44
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L831D
    bne L833C
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L831D
    bne L833C
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L833C
L831D:
    lda #$00
    sec
    sbc ZP_MAIN+$4B
    sta ZP_MAIN+$4B
    lda #$00
    sbc ZP_MAIN+$4C
    sta ZP_MAIN+$4C
    lda #$00
    sbc ZP_MAIN+$4D
    sta ZP_MAIN+$4D
    lda #$01
    sta ZP_MAIN+$48
    lda #$00
    sta ZP_MAIN+$49
    sta ZP_MAIN+$4A
    clc
    rts
L833C:
    ldx #$00
    stx ZP_MAIN+$49
    stx ZP_MAIN+$4A
    jsr REG_TABLE+$24C7
    jmp REG_TABLE+$2388
    lda #$00
    sta ZP_MAIN+$48
    sta ZP_MAIN+$49
    sta ZP_MAIN+$4A
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$3D
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$3E
    sta ZP_MAIN+$4D
    clc
    rts
    clc
    rts
    lda #$00
    sec
    sbc ZP_MAIN+$4B
    sta ZP_MAIN+$4B
    lda #$00
    sbc ZP_MAIN+$4C
    sta ZP_MAIN+$4C
    lda #$00
    sbc ZP_MAIN+$4D
    sta ZP_MAIN+$4D
    lda #$00
    sec
    sbc ZP_MAIN+$48
    sta ZP_MAIN+$48
    lda #$00
    sbc ZP_MAIN+$49
    sta ZP_MAIN+$49
    lda #$00
    sbc ZP_MAIN+$4A
    sta ZP_MAIN+$4A
    clc
    rts
    lda #$00
    sec
    sbc ZP_MAIN+$4B
    sta ZP_MAIN+$4B
    lda #$00
    sbc ZP_MAIN+$4C
    sta ZP_MAIN+$4C
    lda #$00
    sbc ZP_MAIN+$4D
    sta ZP_MAIN+$4D
    clc
    rts
    lda #$00
    sta ZP_MAIN+$48
    sta ZP_MAIN+$49
    sta ZP_MAIN+$4A
    sta ZP_MAIN+$4B
    sta ZP_MAIN+$4C
    sta ZP_MAIN+$4D
    sec
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $A9, $00, $A2, $05, $95, $4A, $CA, $10, $FB, $38, $60, $A7, $46
    !byte $C5, $49, $90, $68, $F0, $07, $A5, $49, $F0, $48, $4C, $8C, $84, $A5, $49, $F0
    !byte $2B, $A5, $45, $C5, $48, $90, $55, $D0, $06, $A5, $44, $C5, $47, $90, $4D, $A5
    !byte $44, $E5, $47, $85, $4D, $A5, $45, $E5, $48, $85, $4E, $A5, $46, $E5, $49, $85
    !byte $4F, $0B, $00, $85, $4B, $85, $4C, $A9, $01, $85, $4A, $60, $A5, $47, $05, $48
    !byte $F0, $B1, $A5, $45, $C5, $48, $90, $24, $D0, $0E, $A5, $44, $C5, $47, $90, $1C
    !byte $B0, $06, $A5, $47, $05, $48, $F0, $9B, $A5, $44, $85, $4D, $A5, $45, $85, $4E
    !byte $A5, $46, $85, $4F, $A9, $00, $8D, $9A, $88, $4C, $24, $88, $A9, $00, $85, $4A
    !byte $85, $4B, $85, $4C, $A5, $44, $85, $4D, $A5, $45, $85, $4E, $86, $4F, $60, $A5
    !byte $44, $38, $E5, $47, $85, $4D, $A5, $45, $E5, $48, $85, $4E, $A5, $46, $E5, $49
    !byte $A2, $00, $86, $4B, $86, $4C, $C5, $49, $90, $17, $D0, $1C, $85, $4F, $A5, $4E
    !byte $C5, $48, $90, $08, $D0, $14, $A5, $4D, $C5, $47, $B0, $0E, $A9, $01, $85, $4A
    !byte $60, $85, $4F, $A9, $01, $85, $4A, $60, $85, $4F
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    cmp ZP_MAIN+$47
    bcc L84F2
    bne L84F9
    sta ZP_MAIN+$4D
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L84ED
    bne L84FB
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L84FB
L84ED:
    lda #$02
    sta ZP_MAIN+$48
    rts
L84F2:
    sta ZP_MAIN+$4D
    lda #$02
    sta ZP_MAIN+$48
    rts
L84F9:
    sta ZP_MAIN+$4D
L84FB:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    lda ZP_MAIN+$47
    cmp #$0D
    bcc L8516
    jmp REG_TABLE+$251E
L8516:
    lda #$03
    sta REG_TABLE+$289A
    jmp REG_TABLE+$2824
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8534
    bne L8539
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8534
    bne L8539
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8539
L8534:
    lda #$03
    sta ZP_MAIN+$48
    rts
L8539:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$254E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8564
    bne L8569
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8564
    bne L8569
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8569
L8564:
    lda #$04
    sta ZP_MAIN+$48
    rts
L8569:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$257E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8594
    bne L8599
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8594
    bne L8599
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8599
L8594:
    lda #$05
    sta ZP_MAIN+$48
    rts
L8599:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$25AE
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L85C4
    bne L85C9
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L85C4
    bne L85C9
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L85C9
L85C4:
    lda #$06
    sta ZP_MAIN+$48
    rts
L85C9:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$25DE
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L85F4
    bne L85F9
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L85F4
    bne L85F9
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L85F9
L85F4:
    lda #$07
    sta ZP_MAIN+$48
    rts
L85F9:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$260E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8624
    bne L8629
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8624
    bne L8629
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8629
L8624:
    lda #$08
    sta ZP_MAIN+$48
    rts
L8629:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$263E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8654
    bne L8659
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8654
    bne L8659
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8659
L8654:
    lda #$09
    sta ZP_MAIN+$48
    rts
L8659:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$266E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8684
    bne L8689
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8684
    bne L8689
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8689
L8684:
    lda #$0A
    sta ZP_MAIN+$48
    rts
L8689:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$269E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L86B4
    bne L86B9
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L86B4
    bne L86B9
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L86B9
L86B4:
    lda #$0B
    sta ZP_MAIN+$48
    rts
L86B9:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$26CE
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L86E4
    bne L86E9
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L86E4
    bne L86E9
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L86E9
L86E4:
    lda #$0C
    sta ZP_MAIN+$48
    rts
L86E9:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$26FE
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8714
    bne L8719
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8714
    bne L8719
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8719
L8714:
    lda #$0D
    sta ZP_MAIN+$48
    rts
L8719:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$272E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8744
    bne L8749
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8744
    bne L8749
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8749
L8744:
    lda #$0E
    sta ZP_MAIN+$48
    rts
L8749:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$275E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8774
    bne L8779
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8774
    bne L8779
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8779
L8774:
    lda #$0F
    sta ZP_MAIN+$48
    rts
L8779:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$278E
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L87A4
    bne L87A9
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L87A4
    bne L87A9
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L87A9
L87A4:
    lda #$10
    sta ZP_MAIN+$48
    rts
L87A9:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$27BE
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L87D4
    bne L87D9
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L87D4
    bne L87D9
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L87D9
L87D4:
    lda #$11
    sta ZP_MAIN+$48
    rts
L87D9:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$27EE
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$47
    bcc L8804
    bne L8809
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$46
    bcc L8804
    bne L8809
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$45
    bcs L8809
L8804:
    lda #$12
    sta ZP_MAIN+$48
    rts
L8809:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$45
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$4D
    jmp REG_TABLE+$281E
    lda #$13
    sta ZP_MAIN+$48
    clc
    rts
    lda ZP_MAIN+$45
    sta ZP_MAIN+$4E
    lda ZP_MAIN+$46
    sta ZP_MAIN+$4F
    lda ZP_MAIN+$47
    sta ZP_MAIN+$50
    ldx #$00
    stx ZP_MAIN+$48
    stx ZP_MAIN+$49
    stx ZP_MAIN+$4A
L8838:
    asl ZP_MAIN+$4E
    rol ZP_MAIN+$4F
    rol ZP_MAIN+$50
    bcs L8859
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$50
    bcc L8859
    bne L8856
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$4F
    bcc L8859
    bne L8856
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$4E
    bcc L8859
L8856:
    inx
    bne L8838
L8859:
    ror ZP_MAIN+$50
    ror ZP_MAIN+$4F
    ror ZP_MAIN+$4E
L885F:
    lda ZP_MAIN+$4D
    cmp ZP_MAIN+$50
    bcc L8887
    bne L8875
    lda ZP_MAIN+$4C
    cmp ZP_MAIN+$4F
    bcc L8887
    bne L8875
    lda ZP_MAIN+$4B
    cmp ZP_MAIN+$4E
    bcc L8887
L8875:
    lda ZP_MAIN+$4B
    sbc ZP_MAIN+$4E
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$4C
    sbc ZP_MAIN+$4F
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4D
    sbc ZP_MAIN+$50
    sta ZP_MAIN+$4D
L8887:
    rol ZP_MAIN+$48
    rol ZP_MAIN+$49
    rol ZP_MAIN+$4A
    lsr ZP_MAIN+$50
    ror ZP_MAIN+$4F
    ror ZP_MAIN+$4E
    dex
    bpl L885F
    lda ZP_MAIN+$48
    clc
    adc #$00
    sta ZP_MAIN+$48
    bcc L88A6
    inc ZP_MAIN+$49
    bne L88A5
    inc ZP_MAIN+$4A
L88A5:
    clc
L88A6:
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00
    !byte $A7, ZP_MAIN+$43    ; LAX zp
    cmp ZP_MAIN+$45
    bcs L8939
L8912:
    lda #$00
    sta ZP_MAIN+$46
    sta ZP_MAIN+$47
    lda ZP_MAIN+$42
    sta ZP_MAIN+$48
    stx ZP_MAIN+$49
    rts
L891F:
    lda ZP_MAIN+$42
    sbc ZP_MAIN+$44
    bcc L8912
    cpx #$01
    bcc L8936
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$49
    sta ZP_MAIN+$47
    lda #$01
    sta ZP_MAIN+$46
    rts
L8936:
    jmp REG_TABLE+$2D0E
L8939:
    beq L891F
    lda ZP_MAIN+$42
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcs L89BB
    sta ZP_MAIN+$49
    lda #$00
    sta ZP_MAIN+$47
    lda #$01
    sta ZP_MAIN+$46
    rts
L8953:
    cmp REG_TABLE+$2D4D,x
    bcc L895B
    jmp REG_TABLE+$2BFA
L895B:
    sec
    bcs L89C3
L895E:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L896C
    txa
L8965:
    sta ZP_MAIN+$49
    lda #$02
    sta ZP_MAIN+$46
    rts
L896C:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8979
L8972:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8980
    txa
L8979:
    sta ZP_MAIN+$49
    lda #$03
    sta ZP_MAIN+$46
    rts
L8980:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L898D
L8986:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8994
    txa
L898D:
    sta ZP_MAIN+$49
    lda #$04
    sta ZP_MAIN+$46
    rts
L8994:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    jmp REG_TABLE+$2A7B
L899B:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L89AD
    stx ZP_MAIN+$49
    lda #$00
    sta ZP_MAIN+$47
    lda #$01
    sta ZP_MAIN+$46
    rts
L89AD:
    dex
    bpl L89B3
    jmp REG_TABLE+$2D0E
L89B3:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$47
    bcc L8965
L89BB:
    beq L899B
    ldx ZP_MAIN+$45
    cpx #$0F
    bcc L8953
L89C3:
    ldy #$00
    sty ZP_MAIN+$47
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8965
    beq L895E
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8979
    beq L8972
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L898D
    beq L8986
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8A7B
    beq L8A74
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8A89
    beq L8A82
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8A97
    beq L8A90
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8AA5
    beq L8A9E
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8AB3
    beq L8AAC
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8AC1
    beq L8ABA
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8ACF
    beq L8AC8
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    jmp REG_TABLE+$2B00
L8A74:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8AD6
    txa
L8A7B:
    sta ZP_MAIN+$49
    lda #$05
    sta ZP_MAIN+$46
    rts
L8A82:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8ADC
    txa
L8A89:
    sta ZP_MAIN+$49
    lda #$06
    sta ZP_MAIN+$46
    rts
L8A90:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8AE2
    txa
L8A97:
    sta ZP_MAIN+$49
    lda #$07
    sta ZP_MAIN+$46
    rts
L8A9E:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8AE8
    txa
L8AA5:
    sta ZP_MAIN+$49
    lda #$08
    sta ZP_MAIN+$46
    rts
L8AAC:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8AEE
    txa
L8AB3:
    sta ZP_MAIN+$49
    lda #$09
    sta ZP_MAIN+$46
    rts
L8ABA:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8AF4
    txa
L8AC1:
    sta ZP_MAIN+$49
    lda #$0A
    sta ZP_MAIN+$46
    rts
L8AC8:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8AFA
    txa
L8ACF:
    sta ZP_MAIN+$49
    lda #$0B
    sta ZP_MAIN+$46
    rts
L8AD6:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8A89
L8ADC:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8A97
L8AE2:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8AA5
L8AE8:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8AB3
L8AEE:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8AC1
L8AF4:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8ACF
L8AFA:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8B57
    cmp ZP_MAIN+$45
    bcc L8B57
    beq L8B50
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8B6B
    beq L8B64
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8B7F
    beq L8B78
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8B93
    beq L8B8C
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    cmp ZP_MAIN+$45
    bcc L8BA7
    beq L8BA0
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
L8B50:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8B5E
    txa
L8B57:
    sta ZP_MAIN+$49
    lda #$0C
    sta ZP_MAIN+$46
    rts
L8B5E:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8B6B
L8B64:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8B72
    txa
L8B6B:
    sta ZP_MAIN+$49
    lda #$0D
    sta ZP_MAIN+$46
    rts
L8B72:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8B7F
L8B78:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8B86
    txa
L8B7F:
    sta ZP_MAIN+$49
    lda #$0E
    sta ZP_MAIN+$46
    rts
L8B86:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8B93
L8B8C:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8B9A
    txa
L8B93:
    sta ZP_MAIN+$49
    lda #$0F
    sta ZP_MAIN+$46
    rts
L8B9A:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    bcc L8BA7
L8BA0:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcs L8BAE
    txa
L8BA7:
    sta ZP_MAIN+$49
    lda #$10
    sta ZP_MAIN+$46
    rts
L8BAE:
    sta ZP_MAIN+$48
    !byte $0B, $00    ; ANC #imm
    sta ZP_MAIN+$49
    lda #$11
    sta ZP_MAIN+$46
    rts
L8BB9:
    jmp REG_TABLE+$2D12
L8BBC:
    jmp REG_TABLE+$2D0E
L8BBF:
    cpx #$01
    bcc L8BBC
    beq L8BB9
    lda ZP_MAIN+$42
    asl
    sta ZP_MAIN+$46
    lda ZP_MAIN+$43
    rol
    sta ZP_MAIN+$48
    lda #$00
    sta ZP_MAIN+$47
    rol
    rol ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    cmp ZP_MAIN+$45
    bcc L8C16
    beq L8BEB
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    bcs L8C16
L8BEB:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcc L8BF7
    sta ZP_MAIN+$48
    lda #$00
    bcs L8C16
L8BF7:
    txa
    bcc L8C16
    cpx #$04
    bcc L8BBF
    cpx #$08
    bcs L8C4B
    lda ZP_MAIN+$42
    asl
    sta ZP_MAIN+$46
    lda ZP_MAIN+$43
    rol
    sta ZP_MAIN+$48
    lda #$00
    sta ZP_MAIN+$47
    rol
    asl ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
L8C16:
    rol ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    cmp ZP_MAIN+$45
    bcc L8C64
    beq L8C2D
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
    bcs L8C64
L8C2D:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcc L8C39
    sta ZP_MAIN+$48
    lda #$00
    bcs L8C64
L8C39:
    txa
    bcc L8C64
L8C3C:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcc L8C48
    sta ZP_MAIN+$48
    lda #$00
    bcs L8C79
L8C48:
    txa
    bcc L8C79
L8C4B:
    lda ZP_MAIN+$42
    asl
    sta ZP_MAIN+$46
    lda ZP_MAIN+$43
    rol
    sta ZP_MAIN+$48
    lda #$00
    sta ZP_MAIN+$47
    rol
    asl ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    asl ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
L8C64:
    rol ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    cmp ZP_MAIN+$45
    bcc L8C79
    beq L8C3C
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
L8C79:
    rol ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    cmp ZP_MAIN+$45
    bcc L8C8E
    beq L8CD2
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
L8C8E:
    rol ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    cmp ZP_MAIN+$45
    bcc L8CA3
    beq L8CE1
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
L8CA3:
    rol ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    cmp ZP_MAIN+$45
    bcc L8CB8
    beq L8CF0
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
L8CB8:
    rol ZP_MAIN+$46
    rol ZP_MAIN+$48
    rol
    cmp ZP_MAIN+$45
    bcc L8CCD
    beq L8CFF
    tay
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    tya
    sbc ZP_MAIN+$45
L8CCD:
    rol ZP_MAIN+$46
    sta ZP_MAIN+$49
    rts
L8CD2:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcc L8CDE
    sta ZP_MAIN+$48
    lda #$00
    bcs L8C8E
L8CDE:
    txa
    bcc L8C8E
L8CE1:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcc L8CED
    sta ZP_MAIN+$48
    lda #$00
    bcs L8CA3
L8CED:
    txa
    bcc L8CA3
L8CF0:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcc L8CFC
    sta ZP_MAIN+$48
    lda #$00
    bcs L8CB8
L8CFC:
    txa
    bcc L8CB8
L8CFF:
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    bcc L8D0B
    sta ZP_MAIN+$48
    lda #$00
    bcs L8CCD
L8D0B:
    txa
    bcc L8CCD
    lda ZP_MAIN+$44
    beq L8D43
    lda ZP_MAIN+$42
    sta ZP_MAIN+$46
    lda ZP_MAIN+$43
    sta ZP_MAIN+$47
    lda #$00
    lsr
    sta ZP_MAIN+$48
    sta ZP_MAIN+$49
    ldy #$10
L8D23:
    rol ZP_MAIN+$46
    rol ZP_MAIN+$47
    rol ZP_MAIN+$48
    rol ZP_MAIN+$49
    sec
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    tax
    lda ZP_MAIN+$49
    sbc ZP_MAIN+$45
    bcc L8D3B
    sta ZP_MAIN+$49
    stx ZP_MAIN+$48
L8D3B:
    dey
    bne L8D23
    rol ZP_MAIN+$46
    rol ZP_MAIN+$47
    rts
L8D43:
    sta ZP_MAIN+$46
    sta ZP_MAIN+$47
    sta ZP_MAIN+$48
    sta ZP_MAIN+$49
    sec
    rts
    !byte $00, $11, $16, $20, $24, $2B, $34, $3D, $3F, $45, $4D, $54, $5B, $62, $68, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00
    jsr REG_TABLE+$290C
    bcc L8E08
    jmp REG_TABLE+$30DA
L8E08:
    lda ZP_MAIN+$4A
    sta ZP_MAIN+$4C
    lda ZP_MAIN+$4B
    sta ZP_MAIN+$4D
    lda ZP_MAIN+$49
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8E33
    cmp ZP_MAIN+$45
    bcc L8E3E
    bne L8E27
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8E3E
L8E27:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8E3E
L8E33:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8E3E:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8E5F
    cmp ZP_MAIN+$45
    bcc L8E6A
    bne L8E53
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8E6A
L8E53:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8E6A
L8E5F:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8E6A:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8E8B
    cmp ZP_MAIN+$45
    bcc L8E96
    bne L8E7F
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8E96
L8E7F:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8E96
L8E8B:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8E96:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8EB7
    cmp ZP_MAIN+$45
    bcc L8EC2
    bne L8EAB
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8EC2
L8EAB:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8EC2
L8EB7:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8EC2:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8EE3
    cmp ZP_MAIN+$45
    bcc L8EEE
    bne L8ED7
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8EEE
L8ED7:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8EEE
L8EE3:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8EEE:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8F0F
    cmp ZP_MAIN+$45
    bcc L8F1A
    bne L8F03
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8F1A
L8F03:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8F1A
L8F0F:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8F1A:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8F3B
    cmp ZP_MAIN+$45
    bcc L8F46
    bne L8F2F
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8F46
L8F2F:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8F46
L8F3B:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8F46:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8F67
    cmp ZP_MAIN+$45
    bcc L8F72
    bne L8F5B
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8F72
L8F5B:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8F72
L8F67:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8F72:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8F93
    cmp ZP_MAIN+$45
    bcc L8F9E
    bne L8F87
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8F9E
L8F87:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8F9E
L8F93:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8F9E:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8FBF
    cmp ZP_MAIN+$45
    bcc L8FCA
    bne L8FB3
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8FCA
L8FB3:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8FCA
L8FBF:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8FCA:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L8FEB
    cmp ZP_MAIN+$45
    bcc L8FF6
    bne L8FDF
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L8FF6
L8FDF:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L8FF6
L8FEB:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L8FF6:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L9017
    cmp ZP_MAIN+$45
    bcc L9022
    bne L900B
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L9022
L900B:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L9022
L9017:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L9022:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L9043
    cmp ZP_MAIN+$45
    bcc L904E
    bne L9037
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L904E
L9037:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L904E
L9043:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L904E:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L906F
    cmp ZP_MAIN+$45
    bcc L907A
    bne L9063
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L907A
L9063:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L907A
L906F:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L907A:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L909B
    cmp ZP_MAIN+$45
    bcc L90A6
    bne L908F
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L90A6
L908F:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L90A6
L909B:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L90A6:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    rol ZP_MAIN+$48
    rol
    bcs L90C7
    cmp ZP_MAIN+$45
    bcc L90D2
    bne L90BB
    ldx ZP_MAIN+$48
    cpx ZP_MAIN+$44
    bcc L90D2
L90BB:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    bcs L90D2
L90C7:
    tax
    lda ZP_MAIN+$48
    sbc ZP_MAIN+$44
    sta ZP_MAIN+$48
    txa
    sbc ZP_MAIN+$45
    sec
L90D2:
    rol ZP_MAIN+$4C
    rol ZP_MAIN+$4D
    sta ZP_MAIN+$49
    clc
    rts
    lda #$00
    sta ZP_MAIN+$4C
    sta ZP_MAIN+$4D
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
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    lda ZP_MAIN+$41
    bmi L9278
    bne L9216
    lda ZP_MAIN+$40
    bne L920D
    jmp REG_TABLE+$32E2
L920D:
    sta ZP_MAIN+$44
    lda #$00
    sta ZP_MAIN+$45
    jmp REG_TABLE+$321C
L9216:
    sta ZP_MAIN+$45
    lda ZP_MAIN+$40
    sta ZP_MAIN+$44
    lda ZP_MAIN+$3F
    bmi L9234
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$4A
    lda ZP_MAIN+$3D
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda ZP_MAIN+$3F
    sta ZP_MAIN+$43
    jsr REG_TABLE+$2E00
    rts
L9234:
    lda #$00
    sec
    sbc ZP_MAIN+$3C
    sta ZP_MAIN+$4A
    lda #$00
    sbc ZP_MAIN+$3D
    sta ZP_MAIN+$4B
    lda #$00
    sbc ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda #$00
    sbc ZP_MAIN+$3F
    sta ZP_MAIN+$43
    jsr REG_TABLE+$2E00
    lda #$00
    sec
    sbc ZP_MAIN+$48
    sta ZP_MAIN+$48
    lda #$00
    sbc ZP_MAIN+$49
    sta ZP_MAIN+$49
    lda #$00
    sec
    sbc ZP_MAIN+$4C
    sta ZP_MAIN+$4C
    lda #$00
    sbc ZP_MAIN+$4D
    sta ZP_MAIN+$4D
    lda #$00
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$47
    clc
    rts
L9278:
    lda #$00
    sec
    sbc ZP_MAIN+$40
    sta ZP_MAIN+$44
    lda #$00
    sbc ZP_MAIN+$41
    sta ZP_MAIN+$45
    lda ZP_MAIN+$3F
    bmi L92B7
    lda ZP_MAIN+$3C
    sta ZP_MAIN+$4A
    lda ZP_MAIN+$3D
    sta ZP_MAIN+$4B
    lda ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda ZP_MAIN+$3F
    sta ZP_MAIN+$43
    jsr REG_TABLE+$2E00
    lda #$00
    sec
    sbc ZP_MAIN+$4C
    sta ZP_MAIN+$4C
    lda #$00
    sbc ZP_MAIN+$4D
    sta ZP_MAIN+$4D
    lda #$00
    sbc ZP_MAIN+$46
    sta ZP_MAIN+$46
    lda #$00
    sbc ZP_MAIN+$47
    sta ZP_MAIN+$47
    clc
    rts
L92B7:
    lda #$00
    sec
    sbc ZP_MAIN+$3C
    sta ZP_MAIN+$4A
    lda #$00
    sbc ZP_MAIN+$3D
    sta ZP_MAIN+$4B
    lda #$00
    sbc ZP_MAIN+$3E
    sta ZP_MAIN+$42
    lda #$00
    sbc ZP_MAIN+$3F
    sta ZP_MAIN+$43
    jsr REG_TABLE+$2E00
    lda #$00
    sec
    sbc ZP_MAIN+$48
    sta ZP_MAIN+$48
    lda #$00
    sbc ZP_MAIN+$49
    sta ZP_MAIN+$49
    clc
    rts
    sta ZP_MAIN+$44
    sta ZP_MAIN+$45
    jmp REG_TABLE+$2E00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $03, $06, $09, $0C, $10, $13, $16, $19
    !byte $1C, $1F, $22, $25, $28, $2B, $2E, $31, $33, $36, $39, $3C, $3F, $41, $44, $47
    !byte $49, $4C, $4E, $51, $53, $55, $58, $5A, $5C, $5E, $60, $62, $64, $66, $68, $6A
    !byte $6B, $6D, $6F, $70, $71, $73, $74, $75, $76, $78, $79, $7A, $7A, $7B, $7C, $7D
    !byte $7D, $7E, $7E, $7E, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7E, $7E, $7E, $7D, $7D
    !byte $7C, $7B, $7A, $7A, $79, $78, $76, $75, $74, $73, $71, $70, $6F, $6D, $6B, $6A
    !byte $68, $66, $64, $62, $60, $5E, $5C, $5A, $58, $55, $53, $51, $4E, $4C, $49, $47
    !byte $44, $41, $3F, $3C, $39, $36, $33, $31, $2E, $2B, $28, $25, $22, $1F, $1C, $19
    !byte $16, $13, $10, $0C, $09, $06, $03, $00, $FD, $FA, $F7, $F4, $F0, $ED, $EA, $E7
    !byte $E4, $E1, $DE, $DB, $D8, $D5, $D2, $CF, $CD, $CA, $C7, $C4, $C1, $BF, $BC, $B9
    !byte $B7, $B4, $B2, $AF, $AD, $AB, $A8, $A6, $A4, $A2, $A0, $9E, $9C, $9A, $98, $96
    !byte $95, $93, $91, $90, $8F, $8D, $8C, $8B, $8A, $88, $87, $86, $86, $85, $84, $83
    !byte $83, $82, $82, $82, $81, $81, $81, $81, $81, $81, $81, $82, $82, $82, $83, $83
    !byte $84, $85, $86, $86, $87, $88, $8A, $8B, $8C, $8D, $8F, $90, $91, $93, $95, $96
    !byte $98, $9A, $9C, $9E, $A0, $A2, $A4, $A6, $A8, $AB, $AD, $AF, $B2, $B4, $B7, $B9
    !byte $BC, $BF, $C1, $C4, $C7, $CA, $CD, $CF, $D2, $D5, $D8, $DB, $DE, $E1, $E4, $E7
    !byte $EA, $ED, $F0, $F4, $F7, $FA, $FD, $7F, $7F, $7F, $7F, $7E, $7E, $7E, $7D, $7D
    !byte $7C, $7B, $7A, $7A, $79, $78, $76, $75, $74, $73, $71, $70, $6F, $6D, $6B, $6A
    !byte $68, $66, $64, $62, $60, $5E, $5C, $5A, $58, $55, $53, $51, $4E, $4C, $49, $47
    !byte $44, $41, $3F, $3C, $39, $36, $33, $31, $2E, $2B, $28, $25, $22, $1F, $1C, $19
    !byte $16, $13, $10, $0C, $09, $06, $03, $00, $FD, $FA, $F7, $F4, $F0, $ED, $EA, $E7
    !byte $E4, $E1, $DE, $DB, $D8, $D5, $D2, $CF, $CD, $CA, $C7, $C4, $C1, $BF, $BC, $B9
    !byte $B7, $B4, $B2, $AF, $AD, $AB, $A8, $A6, $A4, $A2, $A0, $9E, $9C, $9A, $98, $96
    !byte $95, $93, $91, $90, $8F, $8D, $8C, $8B, $8A, $88, $87, $86, $86, $85, $84, $83
    !byte $83, $82, $82, $82, $81, $81, $81, $81, $81, $81, $81, $82, $82, $82, $83, $83
    !byte $84, $85, $86, $86, $87, $88, $8A, $8B, $8C, $8D, $8F, $90, $91, $93, $95, $96
    !byte $98, $9A, $9C, $9E, $A0, $A2, $A4, $A6, $A8, $AB, $AD, $AF, $B2, $B4, $B7, $B9
    !byte $BC, $BF, $C1, $C4, $C7, $CA, $CD, $CF, $D2, $D5, $D8, $DB, $DE, $E1, $E4, $E7
    !byte $EA, $ED, $F0, $F4, $F7, $FA, $FD, $00, $03, $06, $09, $0C, $10, $13, $16, $19
    !byte $1C, $1F, $22, $25, $28, $2B, $2E, $31, $33, $36, $39, $3C, $3F, $41, $44, $47
    !byte $49, $4C, $4E, $51, $53, $55, $58, $5A, $5C, $5E, $60, $62, $64, $66, $68, $6A
    !byte $6B, $6D, $6F, $70, $71, $73, $74, $75, $76, $78, $79, $7A, $7A, $7B, $7C, $7D
    !byte $7D, $7E, $7E, $7E, $7F, $7F, $7F, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $01, $04, $09, $10, $19, $24, $31, $40
    !byte $51, $64, $79, $90, $A9, $C4, $E1, $00, $21, $44, $69, $90, $B9, $E4, $11, $40
    !byte $71, $A4, $D9, $10, $49, $84, $C1, $00, $41, $84, $C9, $10, $59, $A4, $F1, $40
    !byte $91, $E4, $39, $90, $E9, $44, $A1, $00, $61, $C4, $29, $90, $F9, $64, $D1, $40
    !byte $B1, $24, $99, $10, $89, $04, $81, $00, $81, $04, $89, $10, $99, $24, $B1, $40
    !byte $D1, $64, $F9, $90, $29, $C4, $61, $00, $A1, $44, $E9, $90, $39, $E4, $91, $40
    !byte $F1, $A4, $59, $10, $C9, $84, $41, $00, $C1, $84, $49, $10, $D9, $A4, $71, $40
    !byte $11, $E4, $B9, $90, $69, $44, $21, $00, $E1, $C4, $A9, $90, $79, $64, $51, $40
    !byte $31, $24, $19, $10, $09, $04, $01, $00, $01, $04, $09, $10, $19, $24, $31, $40
    !byte $51, $64, $79, $90, $A9, $C4, $E1, $00, $21, $44, $69, $90, $B9, $E4, $11, $40
    !byte $71, $A4, $D9, $10, $49, $84, $C1, $00, $41, $84, $C9, $10, $59, $A4, $F1, $40
    !byte $91, $E4, $39, $90, $E9, $44, $A1, $00, $61, $C4, $29, $90, $F9, $64, $D1, $40
    !byte $B1, $24, $99, $10, $89, $04, $81, $00, $81, $04, $89, $10, $99, $24, $B1, $40
    !byte $D1, $64, $F9, $90, $29, $C4, $61, $00, $A1, $44, $E9, $90, $39, $E4, $91, $40
    !byte $F1, $A4, $59, $10, $C9, $84, $41, $00, $C1, $84, $49, $10, $D9, $A4, $71, $40
    !byte $11, $E4, $B9, $90, $69, $44, $21, $00, $E1, $C4, $A9, $90, $79, $64, $51, $40
    !byte $31, $24, $19, $10, $09, $04, $01, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $01, $01, $01, $01, $01, $01, $01, $02, $02
    !byte $02, $02, $02, $03, $03, $03, $03, $04, $04, $04, $04, $05, $05, $05, $05, $06
    !byte $06, $06, $07, $07, $07, $08, $08, $09, $09, $09, $0A, $0A, $0A, $0B, $0B, $0C
    !byte $0C, $0D, $0D, $0E, $0E, $0F, $0F, $10, $10, $11, $11, $12, $12, $13, $13, $14
    !byte $14, $15, $15, $16, $17, $17, $18, $19, $19, $1A, $1A, $1B, $1C, $1C, $1D, $1E
    !byte $1E, $1F, $20, $21, $21, $22, $23, $24, $24, $25, $26, $27, $27, $28, $29, $2A
    !byte $2B, $2B, $2C, $2D, $2E, $2F, $30, $31, $31, $32, $33, $34, $35, $36, $37, $38
    !byte $39, $3A, $3B, $3C, $3D, $3E, $3F, $40, $41, $42, $43, $44, $45, $46, $47, $48
    !byte $49, $4A, $4B, $4C, $4D, $4E, $4F, $51, $52, $53, $54, $55, $56, $57, $59, $5A
    !byte $5B, $5C, $5D, $5F, $60, $61, $62, $64, $65, $66, $67, $69, $6A, $6B, $6C, $6E
    !byte $6F, $70, $72, $73, $74, $76, $77, $79, $7A, $7B, $7D, $7E, $7F, $81, $82, $84
    !byte $85, $87, $88, $8A, $8B, $8D, $8E, $90, $91, $93, $94, $96, $97, $99, $9A, $9C
    !byte $9D, $9F, $A0, $A2, $A4, $A5, $A7, $A9, $AA, $AC, $AD, $AF, $B1, $B2, $B4, $B6
    !byte $B7, $B9, $BB, $BD, $BE, $C0, $C2, $C4, $C5, $C7, $C9, $CB, $CC, $CE, $D0, $D2
    !byte $D4, $D5, $D7, $D9, $DB, $DD, $DF, $E1, $E2, $E4, $E6, $E8, $EA, $EC, $EE, $F0
    !byte $F2, $F4, $F6, $F8, $FA, $FC, $FE, $00, $01, $02, $03, $04, $05, $06, $07, $08
    !byte $09, $09, $0A, $0B, $0C, $0D, $0E, $0F, $10, $11, $12, $13, $14, $15, $16, $17
    !byte $18, $19, $1A, $1B, $1C, $1C, $1D, $1E, $1F, $20, $21, $22, $23, $24, $25, $26
    !byte $27, $28, $29, $2A, $2B, $2C, $2D, $2E, $2F, $2F, $30, $31, $32, $33, $34, $35
    !byte $36, $37, $38, $39, $3A, $3B, $3C, $3D, $3E, $3F, $40, $41, $41, $42, $43, $44
    !byte $45, $46, $47, $48, $49, $4A, $4B, $4C, $4D, $4E, $4F, $50, $51, $52, $53, $54
    !byte $54, $55, $56, $57, $58, $59, $5A, $5B, $5C, $5D, $5E, $5F, $60, $61, $62, $63
    !byte $64, $65, $66, $67, $67, $68, $69, $6A, $6B, $6C, $6D, $6E, $6F, $70, $71, $72
    !byte $73, $74, $75, $76, $77, $78, $79, $7A, $7A, $7B, $7C, $7D, $7E, $7F, $80, $81
    !byte $82, $83, $84, $85, $86, $87, $88, $89, $8A, $8B, $8C, $8C, $8D, $8E, $8F, $90
    !byte $91, $92, $93, $94, $95, $96, $97, $98, $99, $9A, $9B, $9C, $9D, $9E, $9F, $9F
    !byte $A0, $A1, $A2, $A3, $A4, $A5, $A6, $A7, $A8, $A9, $AA, $AB, $AC, $AD, $AE, $AF
    !byte $B0, $B1, $B2, $B2, $B3, $B4, $B5, $B6, $B7, $B8, $B9, $BA, $BB, $BC, $BD, $BE
    !byte $BF, $C0, $C1, $C2, $C3, $C4, $C4, $C5, $C6, $C7, $C8, $C9, $CA, $CB, $CC, $CD
    !byte $CE, $CF, $D0, $D1, $D2, $D3, $D4, $D5, $D6, $D7, $D7, $D8, $D9, $DA, $DB, $DC
    !byte $DD, $DE, $DF, $E0, $E1, $E2, $E3, $E4, $E5, $E6, $E7, $E8, $E9, $EA, $EA, $EB
    !byte $EC, $ED, $EE, $EF, $F0, $F1, $F2, $00, $00, $01, $01, $02, $02, $03, $03, $03
    !byte $04, $04, $05, $05, $05, $06, $06, $07, $07, $08, $08, $08, $09, $09, $0A, $0A
    !byte $0A, $0B, $0B, $0C, $0C, $0D, $0D, $0D, $0E, $0E, $0F, $0F, $0F, $10, $10, $11
    !byte $11, $12, $12, $12, $13, $13, $14, $14, $14, $15, $15, $16, $16, $17, $17, $17
    !byte $18, $18, $19, $19, $19, $1A, $1A, $1B, $1B, $1C, $1C, $1C, $1D, $1D, $1E, $1E
    !byte $1F, $1F, $1F, $20, $20, $21, $21, $21, $22, $22, $23, $23, $24, $24, $24, $25
    !byte $25, $26, $26, $26, $27, $27, $28, $28, $29, $29, $29, $2A, $2A, $2B, $2B, $2B
    !byte $2C, $2C, $2D, $2D, $2E, $2E, $2E, $2F, $2F, $30, $30, $30, $31, $31, $32, $32
    !byte $33, $33, $33, $34, $34, $35, $35, $36, $36, $36, $37, $37, $38, $38, $38, $39
    !byte $39, $3A, $3A, $3B, $3B, $3B, $3C, $3C, $3D, $3D, $3D, $3E, $3E, $3F, $3F, $40
    !byte $40, $40, $41, $41, $42, $42, $42, $43, $43, $44, $44, $45, $45, $45, $46, $46
    !byte $47, $47, $47, $48, $48, $49, $49, $4A, $4A, $4A, $4B, $4B, $4C, $4C, $4C, $4D
    !byte $4D, $4E, $4E, $4F, $4F, $4F, $50, $50, $51, $51, $52, $52, $52, $53, $53, $54
    !byte $54, $54, $55, $55, $56, $56, $57, $57, $57, $58, $58, $59, $59, $59, $5A, $5A
    !byte $5B, $5B, $5C, $5C, $5C, $5D, $5D, $5E, $5E, $5E, $5F, $5F, $60, $60, $61, $61
    !byte $61, $62, $62, $63, $63, $63, $64, $64, $65, $65, $66, $66, $66, $67, $67, $68
    !byte $68, $68, $69, $69, $6A, $6A, $6B

; Source interval $C100-$CC73
* = REG_GAME
    lda MATH_IO+$10
    sta ZP_MAIN+$51
    lda MATH_IO+$11
    sta ZP_MAIN+$52
    lda MATH_IO+$12
    sta ZP_MAIN+$53
    lda MATH_IO+$13
    sta ZP_MAIN+$54
    lda MATH_IO+$14
    sta ZP_MAIN+$55
    lda MATH_IO+$15
    sta ZP_MAIN+$56
    lda MATH_IO+$16
    sta ZP_MAIN+$57
    lda MATH_IO+$17
    sta ZP_MAIN+$58
    jsr REG_GAME+$011A
    rts
    lda MATH_IO+$14
    ora MATH_IO+$15
    ora MATH_IO+$16
    ora MATH_IO+$17
    bne LC13E
    jsr REG_LOW+$0828
    rts
LC13E:
    lda MATH_IO+$13
    eor MATH_IO+$17
    and #$80
    sta ZP_MAIN+$59
    lda MATH_IO+$13
    and #$80
    sta ZP_MAIN+$5A
    lda MATH_IO+$10
    sta ZP_MAIN+$51
    lda MATH_IO+$11
    sta ZP_MAIN+$52
    lda MATH_IO+$12
    sta ZP_MAIN+$53
    lda MATH_IO+$13
    sta ZP_MAIN+$54
    bpl LC17E
    sec
    lda #$00
    sbc ZP_MAIN+$51
    sta ZP_MAIN+$51
    lda #$00
    sbc ZP_MAIN+$52
    sta ZP_MAIN+$52
    lda #$00
    sbc ZP_MAIN+$53
    sta ZP_MAIN+$53
    lda #$00
    sbc ZP_MAIN+$54
    sta ZP_MAIN+$54
LC17E:
    lda MATH_IO+$14
    sta ZP_MAIN+$55
    lda MATH_IO+$15
    sta ZP_MAIN+$56
    lda MATH_IO+$16
    sta ZP_MAIN+$57
    lda MATH_IO+$17
    sta ZP_MAIN+$58
    bpl LC1AD
    sec
    lda #$00
    sbc ZP_MAIN+$55
    sta ZP_MAIN+$55
    lda #$00
    sbc ZP_MAIN+$56
    sta ZP_MAIN+$56
    lda #$00
    sbc ZP_MAIN+$57
    sta ZP_MAIN+$57
    lda #$00
    sbc ZP_MAIN+$58
    sta ZP_MAIN+$58
LC1AD:
    jsr REG_LOW+$0844
    bcs LC1FD
    lda ZP_MAIN+$59
    beq LC1D7
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
LC1D7:
    lda ZP_MAIN+$5A
    beq LC1FC
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
LC1FC:
    clc
LC1FD:
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
    lda ZP_MAIN+$55
    ora ZP_MAIN+$56
    ora ZP_MAIN+$57
    ora ZP_MAIN+$58
    bne LC228
    jsr REG_GAME+$00FE
    rts
LC228:
    lda ZP_MAIN+$58
    beq LC22F
    jmp REG_GAME+$01EA
LC22F:
    lda ZP_MAIN+$57
    beq LC236
    jmp REG_GAME+$02CE
LC236:
    lda ZP_MAIN+$56
    beq LC23D
    jmp REG_GAME+$018A
LC23D:
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda ZP_MAIN+$52
    sta MATH_IO+$19
    lda ZP_MAIN+$53
    sta MATH_IO+$1A
    lda ZP_MAIN+$54
    sta MATH_IO+$1B
    lda #$00
    sta MATH_IO+$1C
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$20
LC261:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1B
    rol MATH_IO+$1C
    bcs LC279
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc LC285
LC279:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    inc MATH_IO+$18
LC285:
    dex
    bne LC261
    clc
    rts
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda ZP_MAIN+$52
    sta MATH_IO+$19
    lda ZP_MAIN+$53
    sta MATH_IO+$1A
    lda #$00
    sta MATH_IO+$1B
    lda ZP_MAIN+$54
    sta MATH_IO+$1C
    lda #$00
    sta MATH_IO+$1D
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$18
LC2B0:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1A
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    bcs LC2D1
    lda MATH_IO+$1D
    cmp ZP_MAIN+$56
    bcc LC2E5
    bne LC2D1
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc LC2E5
LC2D1:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc ZP_MAIN+$56
    sta MATH_IO+$1D
    inc MATH_IO+$18
LC2E5:
    dex
    bne LC2B0
    clc
    rts
    lda ZP_MAIN+$54
    cmp ZP_MAIN+$58
    bcc LC328
    bne LC34C
    lda ZP_MAIN+$53
    cmp ZP_MAIN+$57
    bcc LC328
    bne LC34C
    lda ZP_MAIN+$52
    cmp ZP_MAIN+$56
    bcc LC328
    bne LC34C
    lda ZP_MAIN+$51
    cmp ZP_MAIN+$55
    bcc LC328
    bne LC34C
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
LC328:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$51
    sta MATH_IO+$1C
    lda ZP_MAIN+$52
    sta MATH_IO+$1D
    lda ZP_MAIN+$53
    sta MATH_IO+$1E
    lda ZP_MAIN+$54
    sta MATH_IO+$1F
    clc
    rts
LC34C:
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$52
    sta MATH_IO+$1C
    lda ZP_MAIN+$53
    sta MATH_IO+$1D
    lda ZP_MAIN+$54
    sta MATH_IO+$1E
    lda #$00
    sta MATH_IO+$1F
    ldx #$08
LC372:
    asl MATH_IO+$18
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs LC3A5
    lda MATH_IO+$1F
    cmp ZP_MAIN+$58
    bcc LC3C9
    bne LC3A5
    lda MATH_IO+$1E
    cmp ZP_MAIN+$57
    bcc LC3C9
    bne LC3A5
    lda MATH_IO+$1D
    cmp ZP_MAIN+$56
    bcc LC3C9
    bne LC3A5
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc LC3C9
LC3A5:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc ZP_MAIN+$56
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc ZP_MAIN+$57
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc ZP_MAIN+$58
    sta MATH_IO+$1F
    inc MATH_IO+$18
LC3C9:
    dex
    bne LC372
    clc
    rts
    lda ZP_MAIN+$54
    cmp ZP_MAIN+$58
    bcc LC40C
    bne LC430
    lda ZP_MAIN+$53
    cmp ZP_MAIN+$57
    bcc LC40C
    bne LC430
    lda ZP_MAIN+$52
    cmp ZP_MAIN+$56
    bcc LC40C
    bne LC430
    lda ZP_MAIN+$51
    cmp ZP_MAIN+$55
    bcc LC40C
    bne LC430
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
LC40C:
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$51
    sta MATH_IO+$1C
    lda ZP_MAIN+$52
    sta MATH_IO+$1D
    lda ZP_MAIN+$53
    sta MATH_IO+$1E
    lda ZP_MAIN+$54
    sta MATH_IO+$1F
    clc
    rts
LC430:
    lda ZP_MAIN+$51
    sta MATH_IO+$18
    lda ZP_MAIN+$52
    sta MATH_IO+$19
    lda #$00
    sta MATH_IO+$1A
    sta MATH_IO+$1B
    lda ZP_MAIN+$53
    sta MATH_IO+$1C
    lda ZP_MAIN+$54
    sta MATH_IO+$1D
    lda #$00
    sta MATH_IO+$1E
    sta MATH_IO+$1F
    ldx #$10
LC456:
    asl MATH_IO+$18
    rol MATH_IO+$19
    rol MATH_IO+$1C
    rol MATH_IO+$1D
    rol MATH_IO+$1E
    rol MATH_IO+$1F
    bcs LC48C
    lda MATH_IO+$1F
    cmp ZP_MAIN+$58
    bcc LC4B0
    bne LC48C
    lda MATH_IO+$1E
    cmp ZP_MAIN+$57
    bcc LC4B0
    bne LC48C
    lda MATH_IO+$1D
    cmp ZP_MAIN+$56
    bcc LC4B0
    bne LC48C
    lda MATH_IO+$1C
    cmp ZP_MAIN+$55
    bcc LC4B0
LC48C:
    sec
    lda MATH_IO+$1C
    sbc ZP_MAIN+$55
    sta MATH_IO+$1C
    lda MATH_IO+$1D
    sbc ZP_MAIN+$56
    sta MATH_IO+$1D
    lda MATH_IO+$1E
    sbc ZP_MAIN+$57
    sta MATH_IO+$1E
    lda MATH_IO+$1F
    sbc ZP_MAIN+$58
    sta MATH_IO+$1F
    inc MATH_IO+$18
LC4B0:
    dex
    bne LC456
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
    sta ZP_MAIN+$51
    lda MATH_IO+$11
    sta ZP_MAIN+$52
    lda MATH_IO+$12
    sta ZP_MAIN+$53
    lda MATH_IO+$13
    sta ZP_MAIN+$54
    lda #$00
    sta MATH_IO+$10
    lda ZP_MAIN+$51
    sta MATH_IO+$11
    lda ZP_MAIN+$52
    sta MATH_IO+$12
    lda #$00
    sta MATH_IO+$13
    jsr REG_API+$01B0
    lda ZP_MAIN+$51
    sta MATH_IO+$10
    lda ZP_MAIN+$52
    sta MATH_IO+$11
    lda ZP_MAIN+$53
    sta MATH_IO+$12
    lda ZP_MAIN+$54
    sta MATH_IO+$13
    rts
    lda MATH_IO+$10
    sta ZP_MAIN+$51
    lda MATH_IO+$11
    sta ZP_MAIN+$52
    lda MATH_IO+$12
    sta ZP_MAIN+$53
    lda MATH_IO+$13
    sta ZP_MAIN+$54
    lda #$00
    sta MATH_IO+$10
    lda ZP_MAIN+$51
    sta MATH_IO+$11
    lda ZP_MAIN+$52
    sta MATH_IO+$12
    bpl LC59E
    lda #$FF
    bne LC5A0
LC59E:
    lda #$00
LC5A0:
    sta MATH_IO+$13
    jsr REG_API+$0EE0
    lda ZP_MAIN+$51
    sta MATH_IO+$10
    lda ZP_MAIN+$52
    sta MATH_IO+$11
    lda ZP_MAIN+$53
    sta MATH_IO+$12
    lda ZP_MAIN+$54
    sta MATH_IO+$13
    rts
    lda MATH_IO+$15
    cmp #$80
    bcc LC5D0
    bne LC5CB
    lda MATH_IO+$14
    cmp #$01
    bcc LC5D0
LC5CB:
    lda #$01
    jmp REG_GAME+$05F6
LC5D0:
    lda MATH_IO+$15
    cmp #$55
    bcc LC5E5
    bne LC5E0
    lda MATH_IO+$14
    cmp #$56
    bcc LC5E5
LC5E0:
    lda #$02
    jmp REG_GAME+$05F6
LC5E5:
    lda MATH_IO+$15
    cmp #$40
    bcc LC5FA
    bne LC5F5
    lda MATH_IO+$14
    cmp #$01
    bcc LC5FA
LC5F5:
    lda #$03
    jmp REG_GAME+$05F6
LC5FA:
    lda MATH_IO+$15
    cmp #$33
    bcc LC60F
    bne LC60A
    lda MATH_IO+$14
    cmp #$34
    bcc LC60F
LC60A:
    lda #$04
    jmp REG_GAME+$05F6
LC60F:
    lda MATH_IO+$15
    cmp #$2A
    bcc LC624
    bne LC61F
    lda MATH_IO+$14
    cmp #$AB
    bcc LC624
LC61F:
    lda #$05
    jmp REG_GAME+$05F6
LC624:
    lda MATH_IO+$15
    cmp #$24
    bcc LC639
    bne LC634
    lda MATH_IO+$14
    cmp #$93
    bcc LC639
LC634:
    lda #$06
    jmp REG_GAME+$05F6
LC639:
    lda MATH_IO+$15
    cmp #$20
    bcc LC64E
    bne LC649
    lda MATH_IO+$14
    cmp #$01
    bcc LC64E
LC649:
    lda #$07
    jmp REG_GAME+$05F6
LC64E:
    lda MATH_IO+$15
    cmp #$1C
    bcc LC663
    bne LC65E
    lda MATH_IO+$14
    cmp #$72
    bcc LC663
LC65E:
    lda #$08
    jmp REG_GAME+$05F6
LC663:
    lda MATH_IO+$15
    cmp #$19
    bcc LC678
    bne LC673
    lda MATH_IO+$14
    cmp #$9A
    bcc LC678
LC673:
    lda #$09
    jmp REG_GAME+$05F6
LC678:
    lda MATH_IO+$15
    cmp #$17
    bcc LC68D
    bne LC688
    lda MATH_IO+$14
    cmp #$46
    bcc LC68D
LC688:
    lda #$0A
    jmp REG_GAME+$05F6
LC68D:
    lda MATH_IO+$15
    cmp #$15
    bcc LC6A2
    bne LC69D
    lda MATH_IO+$14
    cmp #$56
    bcc LC6A2
LC69D:
    lda #$0B
    jmp REG_GAME+$05F6
LC6A2:
    lda MATH_IO+$15
    cmp #$13
    bcc LC6B7
    bne LC6B2
    lda MATH_IO+$14
    cmp #$B2
    bcc LC6B7
LC6B2:
    lda #$0C
    jmp REG_GAME+$05F6
LC6B7:
    lda MATH_IO+$15
    cmp #$12
    bcc LC6CC
    bne LC6C7
    lda MATH_IO+$14
    cmp #$4A
    bcc LC6CC
LC6C7:
    lda #$0D
    jmp REG_GAME+$05F6
LC6CC:
    lda MATH_IO+$15
    cmp #$11
    bcc LC6E1
    bne LC6DC
    lda MATH_IO+$14
    cmp #$12
    bcc LC6E1
LC6DC:
    lda #$0E
    jmp REG_GAME+$05F6
LC6E1:
    lda MATH_IO+$15
    cmp #$10
    bcc LC703
    bne LC6F1
    lda MATH_IO+$14
    cmp #$01
    bcc LC703
LC6F1:
    lda #$0F
    jmp REG_GAME+$05F6
    sta MATH_IO+$18
    lda #$00
    sta MATH_IO+$19
    sta MATH_IO+$1A
    clc
    rts
LC703:
    lda MATH_IO+$14
    ora MATH_IO+$15
    bne LC718
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    sta MATH_IO+$1A
    sec
    rts
LC718:
    lda MATH_IO+$15
    bne LC733
    lda MATH_IO+$14
    cmp #$01
    bne LC733
    lda #$00
    sta MATH_IO+$18
    sta MATH_IO+$19
    lda #$01
    sta MATH_IO+$1A
    clc
    rts
LC733:
    lda MATH_IO+$14
    sta $DF04
    lda MATH_IO+$15
    sta $DF05
    lda #REU_RECIP_LO_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$18
    lda #REU_RECIP_HI_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$19
    lda #$00
    sta MATH_IO+$1A
    clc
    rts
    ldx MATH_IO
    lda REG_TABLE+$3400,x
    sta MATH_IO+$08
    clc
    rts
    ldx MATH_IO
    lda REG_TABLE+$3500,x
    sta MATH_IO+$08
    clc
    rts
    ldx MATH_IO
    lda REG_TABLE+$3400,x
    sta MATH_IO+$08
    lda REG_TABLE+$3500,x
    sta MATH_IO+$09
    clc
    rts
    lda MATH_IO
    sta $DF04
    lda MATH_IO+$04
    sta $DF05
    lda #REU_ATAN2_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$08
    clc
    rts
    lda MATH_IO+$10
    sta $DF04
    lda MATH_IO+$11
    sta $DF05
    lda #REU_ISQRT16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_IO+$08
    lda #$00
    sta MATH_IO+$09
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00
    ldy #$04
LC832:
    txa
    asl
    rol ZP_MAIN+$52
    rol ZP_MAIN+$53
    rol ZP_MAIN+$54
    asl
    rol ZP_MAIN+$52
    rol ZP_MAIN+$53
    rol ZP_MAIN+$54
    tax
    asl ZP_MAIN+$55
    rol ZP_MAIN+$56
    lda ZP_MAIN+$55
    asl
    ora #$01
    sta ZP_MAIN+$57
    lda ZP_MAIN+$56
    rol
    sta ZP_MAIN+$58
    bcc LC85E
    lda ZP_MAIN+$54
    beq LC885
    cmp #$01
    bne LC870
    beq LC862
LC85E:
    lda ZP_MAIN+$54
    bne LC870
LC862:
    lda ZP_MAIN+$53
    cmp ZP_MAIN+$58
    bcc LC885
    bne LC870
    lda ZP_MAIN+$52
    cmp ZP_MAIN+$57
    bcc LC885
LC870:
    sec
    lda ZP_MAIN+$52
    sbc ZP_MAIN+$57
    sta ZP_MAIN+$52
    lda ZP_MAIN+$53
    sbc ZP_MAIN+$58
    sta ZP_MAIN+$53
    lda ZP_MAIN+$54
    sbc #$00
    sta ZP_MAIN+$54
    inc ZP_MAIN+$55
LC885:
    dey
    bne LC832
    rts
    !byte $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA
    !byte $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA
    !byte $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA, $EA
    lda MATH_IO
    bpl LC8BD
    sec
    lda #$00
    sbc MATH_IO
LC8BD:
    sta ZP_MAIN+$5B
    lda MATH_IO+$04
    bpl LC8CA
    sec
    lda #$00
    sbc MATH_IO+$04
LC8CA:
    sta ZP_MAIN+$5C
    cmp ZP_MAIN+$5B
    bcc LC8DA
    lda ZP_MAIN+$5B
    pha
    lda ZP_MAIN+$5C
    sta ZP_MAIN+$5B
    pla
    sta ZP_MAIN+$5C
LC8DA:
    rts
    jsr REG_GAME+$07B2
    lda ZP_MAIN+$5C
    lsr
    clc
    adc ZP_MAIN+$5B
    sta MATH_IO+$08
    clc
    rts
    jsr REG_GAME+$07B2
    ldx ZP_MAIN+$5B
    lda REG_TABLE+$3A00,x
    ldx ZP_MAIN+$5C
    clc
    adc REG_TABLE+$3B00,x
    sta MATH_IO+$08
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
    !byte $00, $00, $00, $00
    lda MATH_IO+$10
    sta ZP_MAIN+$59
    lda MATH_IO+$11
    sta ZP_MAIN+$5A
    lda MATH_IO+$12
    sta MATH_IO+$10
    lda MATH_IO+$13
    sta MATH_IO+$11
    jsr REG_GAME_API+$002D
    lda ZP_MAIN+$59
    sta MATH_IO+$10
    lda ZP_MAIN+$5A
    sta MATH_IO+$11
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
    jsr REG_GAME+$0730
    ldx MATH_IO+$10
    jsr REG_GAME+$0730
    lda ZP_MAIN+$55
    sta MATH_IO+$08
    lda ZP_MAIN+$56
    sta MATH_IO+$09
    clc
    rts
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00
; MATH_INIT-installed native SMUL16 executable-ZP image, assembled symbolically.
* = REG_GAME+$0B00
    sty REG_KERNEL+$1A16
    lda ZP_SMUL+$27
    sta ZP_SMUL+$4B
    eor #$FF
    sta ZP_SMUL+$2C
    sta ZP_SMUL+$32
    lda ZP_SMUL+$19
    sta ZP_SMUL+$21
    eor #$FF
    sta ZP_SMUL+$1C
    sta ZP_SMUL+$24
    sec
    lda REG_LOW+$1800,y
    adc REG_LOW+$1C00,y
    sta ZP_SMUL+$72
    lda REG_LOW+$1A00,y
    adc REG_LOW+$1E00,y
    adc REG_LOW+$1800,y
    bcs ZCDD
    adc REG_LOW+$1C00,y
    tax
    lda (ZP_SMUL+$4B),y
ZCB1:
    adc REG_LOW+$1E00,y
    sta ZP_SMUL+$57
    ldy #$00
    lda (ZP_SMUL+$19),y
    adc (ZP_SMUL+$1C),y
    sta ZP_SMUL+$53
    lda (ZP_SMUL+$21),y
    adc (ZP_SMUL+$24),y
    adc (ZP_SMUL+$27),y
    bcs ZCE7
    adc (ZP_SMUL+$2C),y
    sta ZP_SMUL+$59
    lda REG_LOW+$1A00,y
ZCCD:
    adc (ZP_SMUL+$32),y
    tay
    clc
    txa
    adc #$00
    sta ZP_SMUL+$73
    lda #$00
    adc #$00
    jmp REG_KERNEL+$1A00
ZCDD:
    clc
    adc (ZP_SMUL+$2C),y
    tax
    lda #$01
    adc (ZP_SMUL+$4B),y
    bcc ZCB1
ZCE7:
    clc
    adc (ZP_SMUL+$2C),y
    sta ZP_SMUL+$59
    lda #$01
    adc (ZP_SMUL+$4B),y
    bcc ZCCD
    brk
    brk
