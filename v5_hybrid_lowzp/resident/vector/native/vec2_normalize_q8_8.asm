; MATH_VEC2_NORMALIZE_Q8_8 — standalone native implementation
; Backend: stock-C64 low-ZP backend (V1/V5)
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
; Required map symbols: MATH_IO, ZP_MAIN, REG_TABLE.
; Shared immutable lookup tables are not duplicated here; see README.md.
!cpu 6510

VEC2_NORMALIZE_Q8_8_NATIVE:
VEC2N_0000:
    !byte $AF, <MATH_IO+$01, >MATH_IO+$01    ; LAX abs
    bmi VEC2N_000D
    lda MATH_IO
    sta ZP_MAIN+$18
    jmp VEC2N_0017
VEC2N_000D:
    eor #$FF
    tax
    lda MATH_IO
    eor #$FF
    sta ZP_MAIN+$18
VEC2N_0017:
    lda MATH_IO+$05
    bmi VEC2N_0026
    sta ZP_MAIN+$1B
    lda MATH_IO+$04
    sta ZP_MAIN+$1A
    jmp VEC2N_0031
VEC2N_0026:
    eor #$FF
    sta ZP_MAIN+$1B
    lda MATH_IO+$04
    eor #$FF
    sta ZP_MAIN+$1A
VEC2N_0031:
    cpx ZP_MAIN+$1B
    bcc VEC2N_0075
    bne VEC2N_0078
    txa
    bne VEC2N_0050
    bit MATH_IO+$01
    bpl VEC2N_0045
    inc ZP_MAIN+$18
    bne VEC2N_0045
    dec ZP_MAIN+$18
VEC2N_0045:
    bit MATH_IO+$05
    bpl VEC2N_0050
    inc ZP_MAIN+$1A
    bne VEC2N_0050
    dec ZP_MAIN+$1A
VEC2N_0050:
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1A
    bcc VEC2N_0075
    txa
    bne VEC2N_0079
    lda ZP_MAIN+$18
    bmi VEC2N_0064
    beq VEC2N_006B
VEC2N_005F:
    asl ZP_MAIN+$1A
    asl
    bpl VEC2N_005F
VEC2N_0064:
    ldx ZP_MAIN+$1A
    stx ZP_MAIN+$1B
    tay
    bmi VEC2N_0083
VEC2N_006B:
    ldy #$03
VEC2N_006D:
    sta MATH_IO+$08,y
    dey
    bpl VEC2N_006D
    sec
    rts
VEC2N_0075:
    jmp VEC2N_00F5
VEC2N_0078:
    txa
VEC2N_0079:
    asl ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    asl ZP_MAIN+$18
    rol
    bpl VEC2N_0079
    tay
VEC2N_0083:
    !byte $BF, <REG_TABLE+$0400, >REG_TABLE+$0400    ; LAX abs,Y
    ldy ZP_MAIN+$1B
    stx ZP_MAIN+$12
    stx VEC2N_009B+1
    stx VEC2N_00A1+1
    tya
    sec
    sbc ZP_MAIN+$12
    bcs VEC2N_009A
    sbc #$00
    eor #$FF
VEC2N_009A:
    tax
VEC2N_009B:
    lda REG_TABLE+$2000,y
    sbc REG_TABLE+$2000,x
VEC2N_00A1:
    lda REG_TABLE+$2200,y
    sbc REG_TABLE+$2200,x
    sec
    adc ZP_MAIN+$1B
    tax
    bit MATH_IO+$01
    bmi VEC2N_00BE
    lda REG_TABLE,x
    sta MATH_IO+$08
    lda REG_TABLE+$0100,x
    sta MATH_IO+$09
    bpl VEC2N_00CF
VEC2N_00BE:
    sec
    lda #$00
    sbc REG_TABLE,x
    sta MATH_IO+$08
    lda #$00
    sbc REG_TABLE+$0100,x
    sta MATH_IO+$09
VEC2N_00CF:
    lda MATH_IO+$05
    asl
    bcs VEC2N_00E3
    lda REG_TABLE+$0200,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0300,x
    sta MATH_IO+$0B
    clc
    rts
VEC2N_00E3:
    lda #$00
    sbc REG_TABLE+$0200,x
    sta MATH_IO+$0A
    lda #$00
    sbc REG_TABLE+$0300,x
    sta MATH_IO+$0B
    clc
    rts
VEC2N_00F5:
    lda ZP_MAIN+$1B
    beq VEC2N_0177
    stx ZP_MAIN+$19
VEC2N_00FB:
    asl ZP_MAIN+$18
    rol ZP_MAIN+$19
    asl ZP_MAIN+$1A
    rol
    bpl VEC2N_00FB
    tay
VEC2N_0105:
    !byte $BF, <REG_TABLE+$0400, >REG_TABLE+$0400    ; LAX abs,Y
    ldy ZP_MAIN+$19
    stx ZP_MAIN+$12
    stx VEC2N_011D+1
    stx VEC2N_0123+1
    tya
    sec
    sbc ZP_MAIN+$12
    bcs VEC2N_011C
    sbc #$00
    eor #$FF
VEC2N_011C:
    tax
VEC2N_011D:
    lda REG_TABLE+$2000,y
    sbc REG_TABLE+$2000,x
VEC2N_0123:
    lda REG_TABLE+$2200,y
    sbc REG_TABLE+$2200,x
    sec
    adc ZP_MAIN+$19
    tax
    bit MATH_IO+$01
    bmi VEC2N_0140
    lda REG_TABLE+$0200,x
    sta MATH_IO+$08
    lda REG_TABLE+$0300,x
    sta MATH_IO+$09
    bpl VEC2N_0151
VEC2N_0140:
    sec
    lda #$00
    sbc REG_TABLE+$0200,x
    sta MATH_IO+$08
    lda #$00
    sbc REG_TABLE+$0300,x
    sta MATH_IO+$09
VEC2N_0151:
    lda MATH_IO+$05
    asl
    bcs VEC2N_0165
    lda REG_TABLE,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0100,x
    sta MATH_IO+$0B
    clc
    rts
VEC2N_0165:
    lda #$00
    sbc REG_TABLE,x
    sta MATH_IO+$0A
    lda #$00
    sbc REG_TABLE+$0100,x
    sta MATH_IO+$0B
    clc
    rts
VEC2N_0177:
    lda ZP_MAIN+$1A
    bmi VEC2N_0180
VEC2N_017B:
    asl ZP_MAIN+$18
    asl
    bpl VEC2N_017B
VEC2N_0180:
    tay
    lda ZP_MAIN+$18
    sta ZP_MAIN+$19
    jmp VEC2N_0105
