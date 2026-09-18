; MATH_VEC2_NORMALIZE_Q8_8 — standalone native implementation
; Backend: REU direct ratio-index backend (V3/V4)
;
; Canonical build: this file is included directly by math_relocatable.asm.
; To reuse independently, define the symbols listed below, set the assembly
; PC to the desired entry address, and include/assemble this file.
;
; Contract:
;   input  MATH_IO+$00..$01 = signed Q8.8 X
;          MATH_IO+$04..$05 = signed Q8.8 Y
;   output MATH_IO+$08..$09 = signed Q1.15 normalized X
;          MATH_IO+$0A..$0B = signed Q1.15 normalized Y
;   input operands are preserved
;   C=0 for non-zero vectors; C=1 and zero output for (0,0)
;   A/X/Y volatile
;
; Required map symbols: MATH_IO, ZP_MAIN, REG_TABLE, REU_SCRATCH,
;                       REU_TURBO16_BANK.
; Shared immutable lookup tables are not duplicated here; see README.md.
!cpu 6510

VEC2_NORMALIZE_Q8_8_NATIVE:
VEC2N_0000:
    lda #REU_TURBO16_BANK
    sta $DF06
    !byte $AF, <MATH_IO+$01, >MATH_IO+$01    ; LAX abs
    bmi VEC2N_0012
    lda MATH_IO
    sta ZP_MAIN+$10
    jmp VEC2N_001C
VEC2N_0012:
    eor #$FF
    tax
    lda MATH_IO
    eor #$FF
    sta ZP_MAIN+$10
VEC2N_001C:
    lda MATH_IO+$05
    bmi VEC2N_002B
    sta ZP_MAIN+$13
    lda MATH_IO+$04
    sta ZP_MAIN+$12
    jmp VEC2N_0036
VEC2N_002B:
    eor #$FF
    sta ZP_MAIN+$13
    lda MATH_IO+$04
    eor #$FF
    sta ZP_MAIN+$12
VEC2N_0036:
    cpx ZP_MAIN+$13
    bcc VEC2N_0079
    bne VEC2N_007C
    txa
    bne VEC2N_0055
    bit MATH_IO+$01
    bpl VEC2N_004A
    inc ZP_MAIN+$10
    bne VEC2N_004A
    dec ZP_MAIN+$10
VEC2N_004A:
    bit MATH_IO+$05
    bpl VEC2N_0055
    inc ZP_MAIN+$12
    bne VEC2N_0055
    dec ZP_MAIN+$12
VEC2N_0055:
    lda ZP_MAIN+$10
    cmp ZP_MAIN+$12
    bcc VEC2N_0079
    txa
    bne VEC2N_007D
    lda ZP_MAIN+$10
    bmi VEC2N_0069
    beq VEC2N_0070
VEC2N_0064:
    asl ZP_MAIN+$12
    asl
    bpl VEC2N_0064
VEC2N_0069:
    ldx ZP_MAIN+$12
    stx ZP_MAIN+$13
    tay
    bmi VEC2N_0087
VEC2N_0070:
    ldy #$03
VEC2N_0072:
    sta MATH_IO+$08,y
    dey
    bpl VEC2N_0072
    rts
VEC2N_0079:
    jmp VEC2N_00DF
VEC2N_007C:
    txa
VEC2N_007D:
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    asl ZP_MAIN+$10
    rol
    bpl VEC2N_007D
    tay
VEC2N_0087:
    lda ZP_MAIN+$13
    sta $DF04
    sty $DF05
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    bit MATH_IO+$01
    bmi VEC2N_00AA
    lda REG_TABLE+$0800,x
    sta MATH_IO+$08
    lda REG_TABLE+$0900,x
    sta MATH_IO+$09
    bpl VEC2N_00BB
VEC2N_00AA:
    sec
    lda #$00
    sbc REG_TABLE+$0800,x
    sta MATH_IO+$08
    lda #$00
    sbc REG_TABLE+$0900,x
    sta MATH_IO+$09
VEC2N_00BB:
    lda MATH_IO+$05
    asl
    bcs VEC2N_00CE
    lda REG_TABLE+$0A00,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0B00,x
    sta MATH_IO+$0B
    rts
VEC2N_00CE:
    lda #$00
    sbc REG_TABLE+$0A00,x
    sta MATH_IO+$0A
    lda #$00
    sbc REG_TABLE+$0B00,x
    sta MATH_IO+$0B
    rts
VEC2N_00DF:
    lda ZP_MAIN+$13
    beq VEC2N_0147
    stx ZP_MAIN+$11
VEC2N_00E5:
    asl ZP_MAIN+$10
    rol ZP_MAIN+$11
    asl ZP_MAIN+$12
    rol
    bpl VEC2N_00E5
    tay
VEC2N_00EF:
    lda ZP_MAIN+$11
    sta $DF04
    sty $DF05
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    bit MATH_IO+$01
    bmi VEC2N_0112
    lda REG_TABLE+$0A00,x
    sta MATH_IO+$08
    lda REG_TABLE+$0B00,x
    sta MATH_IO+$09
    bpl VEC2N_0123
VEC2N_0112:
    sec
    lda #$00
    sbc REG_TABLE+$0A00,x
    sta MATH_IO+$08
    lda #$00
    sbc REG_TABLE+$0B00,x
    sta MATH_IO+$09
VEC2N_0123:
    lda MATH_IO+$05
    asl
    bcs VEC2N_0136
    lda REG_TABLE+$0800,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0900,x
    sta MATH_IO+$0B
    rts
VEC2N_0136:
    lda #$00
    sbc REG_TABLE+$0800,x
    sta MATH_IO+$0A
    lda #$00
    sbc REG_TABLE+$0900,x
    sta MATH_IO+$0B
    rts
VEC2N_0147:
    lda ZP_MAIN+$12
    bmi VEC2N_0150
VEC2N_014B:
    asl ZP_MAIN+$10
    asl
    bpl VEC2N_014B
VEC2N_0150:
    tay
    lda ZP_MAIN+$10
    sta ZP_MAIN+$11
    bcc VEC2N_00EF
    cpy #$18
    rts
