; MATH_VEC2_NORMALIZE_Q8_8 — standalone native implementation
; Backend: stock-C64 Pareto-fast backend (V2)
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
; Required map symbols: MATH_IO, ZP_MAIN, REG_TABLE, REG_LOW, REG_KERNEL.
; Shared immutable lookup tables are not duplicated here; see README.md.
!cpu 6510

VEC2_NORMALIZE_Q8_8_NATIVE:
VEC2N_0000:
    !byte $AF, <MATH_IO+$01, >MATH_IO+$01    ; LAX abs
    bmi VEC2N_000D
    lda MATH_IO
    sta ZP_MAIN+$10
    jmp VEC2N_0017
VEC2N_000D:
    eor #$FF
    tax
    lda MATH_IO
    eor #$FF
    sta ZP_MAIN+$10
VEC2N_0017:
    lda MATH_IO+$05
    bmi VEC2N_0026
    sta ZP_MAIN+$13
    lda MATH_IO+$04
    sta ZP_MAIN+$12
    jmp VEC2N_0031
VEC2N_0026:
    eor #$FF
    sta ZP_MAIN+$13
    lda MATH_IO+$04
    eor #$FF
    sta ZP_MAIN+$12
VEC2N_0031:
    cpx ZP_MAIN+$13
    bcc VEC2N_0074
    bne VEC2N_0081
    txa
    bne VEC2N_0050
    bit MATH_IO+$01
    bpl VEC2N_0045
    inc ZP_MAIN+$10
    bne VEC2N_0045
    dec ZP_MAIN+$10
VEC2N_0045:
    bit MATH_IO+$05
    bpl VEC2N_0050
    inc ZP_MAIN+$12
    bne VEC2N_0050
    dec ZP_MAIN+$12
VEC2N_0050:
    lda ZP_MAIN+$10
    cmp ZP_MAIN+$12
    bcc VEC2N_0074
    txa
    bne VEC2N_0082
    lda ZP_MAIN+$10
    bmi VEC2N_0064
    beq VEC2N_006B
VEC2N_005F:
    asl ZP_MAIN+$12
    asl
    bpl VEC2N_005F
VEC2N_0064:
    ldx ZP_MAIN+$12
    stx ZP_MAIN+$13
    tay
    bmi VEC2N_008C
VEC2N_006B:
    ldy #$03
VEC2N_006D:
    sta MATH_IO+$08,y
    dey
    bpl VEC2N_006D
    rts
VEC2N_0074:
    jmp VEC2N_00F0
VEC2N_0077:
    sbc REG_TABLE+$0800,x
    lda (ZP_MAIN+$39),y
    sbc REG_TABLE+$0A00,x
    bpl VEC2N_00A5
VEC2N_0081:
    txa
VEC2N_0082:
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    asl ZP_MAIN+$10
    rol
    bpl VEC2N_0082
    tay
VEC2N_008C:
    !byte $BF, <REG_TABLE+$3300, >REG_TABLE+$3300    ; LAX abs,Y
    ldy ZP_MAIN+$13
    sec
    stx ZP_MAIN+$37
    stx ZP_MAIN+$39
    sbc ZP_MAIN+$13
    tax
    lda (ZP_MAIN+$37),y
    bcs VEC2N_0077
    sbc REG_TABLE+$0C00,x
    lda (ZP_MAIN+$39),y
    sbc REG_TABLE+$0D00,x
VEC2N_00A5:
    adc ZP_MAIN+$13
    tax
    bit MATH_IO+$01
    bmi VEC2N_00BB
    lda REG_LOW+$1400,x
    sta MATH_IO+$08
    lda REG_LOW+$1700,x
    sta MATH_IO+$09
    bpl VEC2N_00CC
VEC2N_00BB:
    sec
    lda #$00
    sbc REG_LOW+$1400,x
    sta MATH_IO+$08
    lda #$00
    sbc REG_LOW+$1700,x
    sta MATH_IO+$09
VEC2N_00CC:
    lda MATH_IO+$05
    asl
    bcs VEC2N_00DF
    lda REG_KERNEL+$0700,x
    sta MATH_IO+$0A
    lda REG_KERNEL+$0D00,x
    sta MATH_IO+$0B
    rts
VEC2N_00DF:
    lda #$00
    sbc REG_KERNEL+$0700,x
    sta MATH_IO+$0A
    lda #$00
    sbc REG_KERNEL+$0D00,x
    sta MATH_IO+$0B
    rts
VEC2N_00F0:
    lda ZP_MAIN+$13
    beq VEC2N_016E
    stx ZP_MAIN+$11
VEC2N_00F6:
    asl ZP_MAIN+$10
    rol ZP_MAIN+$11
    asl ZP_MAIN+$12
    rol
    bpl VEC2N_00F6
    tay
VEC2N_0100:
    !byte $BF, <REG_TABLE+$3300, >REG_TABLE+$3300    ; LAX abs,Y
    ldy ZP_MAIN+$11
    sec
    stx ZP_MAIN+$37
    stx ZP_MAIN+$39
    sbc ZP_MAIN+$11
    tax
    lda (ZP_MAIN+$37),y
    bcs VEC2N_0164
    sbc REG_TABLE+$0C00,x
    lda (ZP_MAIN+$39),y
    sbc REG_TABLE+$0D00,x
VEC2N_0119:
    adc ZP_MAIN+$11
    tax
    bit MATH_IO+$01
    bmi VEC2N_012F
    lda REG_KERNEL+$0700,x
    sta MATH_IO+$08
    lda REG_KERNEL+$0D00,x
    sta MATH_IO+$09
    bpl VEC2N_0140
VEC2N_012F:
    sec
    lda #$00
    sbc REG_KERNEL+$0700,x
    sta MATH_IO+$08
    lda #$00
    sbc REG_KERNEL+$0D00,x
    sta MATH_IO+$09
VEC2N_0140:
    lda MATH_IO+$05
    asl
    bcs VEC2N_0153
    lda REG_LOW+$1400,x
    sta MATH_IO+$0A
    lda REG_LOW+$1700,x
    sta MATH_IO+$0B
    rts
VEC2N_0153:
    lda #$00
    sbc REG_LOW+$1400,x
    sta MATH_IO+$0A
    lda #$00
    sbc REG_LOW+$1700,x
    sta MATH_IO+$0B
    rts
VEC2N_0164:
    sbc REG_TABLE+$0800,x
    lda (ZP_MAIN+$39),y
    sbc REG_TABLE+$0A00,x
    bpl VEC2N_0119
VEC2N_016E:
    lda ZP_MAIN+$12
    bmi VEC2N_0177
VEC2N_0172:
    asl ZP_MAIN+$10
    asl
    bpl VEC2N_0172
VEC2N_0177:
    tay
    lda ZP_MAIN+$10
    sta ZP_MAIN+$11
    bcc VEC2N_0100
    brk
