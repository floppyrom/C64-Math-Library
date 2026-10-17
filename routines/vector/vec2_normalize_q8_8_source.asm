; Source-linked standalone V1/V5 logarithmic-ratio normalizer.
; Literal algorithm and exact generated table bytes transplanted from the
; certified V1 native module; loadable as one self-contained 6502 source.
; Packed RAM span: 14 pages plus 3-byte export JMP; 4 reusable ZP bytes.
; Code and tables must start at an aligned 256-byte page boundary; code RAM
; writable because the certified quadrant backend uses operand self-patching.
; Signed Q8.8 X16/Y16 preserved; Q1.15 X/Y in Z[0..3]; C=1 iff zero.
; Uses stable NMOS LAX abs opcode AF (existing certified V1 source).
!cpu 6510
KERNEL_CODE = $8000
INPUT_X = $C000
TEMP_ZP = $0050
REG_LOW = KERNEL_CODE
REG_TABLE = REG_LOW+$0900
REG_GAME_API = REG_LOW+$0DC7
MATH_IO = INPUT_X
ZP_MAIN = TEMP_ZP-$18
* = REG_GAME_API+$0039

; MATH_VEC2_NORMALIZE_Q8_8: signed Q8.8 X/Y -> signed Q1.15 unit vector.
; Input: MATH_IO+$00..$01 (X), MATH_IO+$04..$05 (Y), preserved.
; Output: MATH_IO+$08..$0B; A/X/Y volatile; D=0 required.
; C=0 for nonzero vectors; (0,0) returns four zero bytes and C=1.
; Scratch: ZP_MAIN+$18..+$1B, inside the existing 31-byte union.
; Accuracy: <=0.3621 degrees and <=202 component LSB over the full domain.
;
; Sign dispatch selects a quadrant once. Each path computes magnitudes and
; writes signed results directly, avoiding repeated input-sign tests.
; Negative magnitudes use one's complement; the small-vector paths correct
; this to saturated absolute bytes, exactly as in the original reduction.
;
; Small-vector paths pass the minor byte directly to the lookup.
; Quadrant islands keep reduction branches within their 256-byte page.
;
; Stock backend: log-ratio index with a full-domain interval certificate.
; Code body: REG_LOW+$0500; four ratio pages + log-low page at REG_LOW.
; Component/log-high planes retain their profile-specific locations.
; This source owns its code/table islands and restores PC to the end of
; the stable public JMP slot. See README.md for the complete memory map.

VEC2_NORMALIZE_Q8_8_NATIVE:

    jmp norm_entry
* = REG_LOW+$0500
norm_entry:
    !byte $AF, <MATH_IO+$01, >MATH_IO+$01
    bmi sign_x_negative
    lda MATH_IO+$05
    bpl pp_entry
sign_y_negative:
    eor #$FF
    jmp pn_entry
sign_x_negative:
    eor #$FF
    tax
    lda MATH_IO+$05
    bmi sign_both_negative
    jmp np_entry
sign_both_negative:
    eor #$FF
    jmp nn_entry
; Quadrant: X positive, Y positive.
pp_entry:
    sta ZP_MAIN+$1B
    lda MATH_IO
    sta ZP_MAIN+$18
    lda MATH_IO+$04
    sta ZP_MAIN+$1A
    cpx ZP_MAIN+$1B
    bcc pp_to_y_major
    bne pp_x_major
pp_compare_low:
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1A
    bcc pp_to_y_major
    txa
    bne pp_x_shift
    lda ZP_MAIN+$18
    bmi pp_x_low_done
    beq pp_zero
pp_x_low_loop:
    asl ZP_MAIN+$1A
    asl
    bpl pp_x_low_loop
pp_x_low_done:
    tay
    ldx ZP_MAIN+$1A
    jmp pp_x_index
pp_zero:
    sta MATH_IO+$08
    sta MATH_IO+$09
    sta MATH_IO+$0A
    sta MATH_IO+$0B
    sec
    rts
pp_to_y_major:
    jmp pp_y_major
pp_x_major:
    txa
pp_x_shift:
    asl ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    asl ZP_MAIN+$18
    rol
    bpl pp_x_shift
    tay
pp_x_ratio:
    ldx ZP_MAIN+$1B
pp_x_index:
    beq pp_x_output
pp_x_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta pp_x_lookup+2
pp_x_lookup:
    ldx REG_LOW,y
pp_x_output:
    lda REG_TABLE,x
    sta MATH_IO+$08
    lda REG_TABLE+$0100,x
    sta MATH_IO+$09
    lda REG_TABLE+$0200,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0300,x
    sta MATH_IO+$0B
    clc
    rts
pp_y_major:
    lda ZP_MAIN+$1B
    beq pp_y_low
    stx ZP_MAIN+$19
pp_y_shift:
    asl ZP_MAIN+$18
    rol ZP_MAIN+$19
    asl ZP_MAIN+$1A
    rol
    bpl pp_y_shift
    tay
pp_y_ratio:
    ldx ZP_MAIN+$19
pp_y_index:
    beq pp_y_output
pp_y_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta pp_y_lookup+2
pp_y_lookup:
    ldx REG_LOW,y
pp_y_output:
    lda REG_TABLE+$0200,x
    sta MATH_IO+$08
    lda REG_TABLE+$0300,x
    sta MATH_IO+$09
    lda REG_TABLE,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0100,x
    sta MATH_IO+$0B
    clc
    rts
pp_y_low:
    lda ZP_MAIN+$1A
    bmi pp_y_low_done
pp_y_low_loop:
    asl ZP_MAIN+$18
    asl
    bpl pp_y_low_loop
pp_y_low_done:
    tay
    ldx ZP_MAIN+$18
    jmp pp_y_index
; Quadrant: X positive, Y negative.
* = REG_LOW+$0600
pn_entry:
    sta ZP_MAIN+$1B
    lda MATH_IO
    sta ZP_MAIN+$18
    lda MATH_IO+$04
    eor #$FF
    sta ZP_MAIN+$1A
    cpx ZP_MAIN+$1B
    bcc pn_to_y_major
    bne pn_x_major
    txa
    bne pn_compare_low
    inc ZP_MAIN+$1A
    bne pn_low_fix1_done
    dec ZP_MAIN+$1A
pn_low_fix1_done:
pn_compare_low:
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1A
    bcc pn_to_y_major
    txa
    bne pn_x_shift
    lda ZP_MAIN+$18
    bmi pn_x_low_done
pn_x_low_loop:
    asl ZP_MAIN+$1A
    asl
    bpl pn_x_low_loop
pn_x_low_done:
    tay
    ldx ZP_MAIN+$1A
    jmp pn_x_index
pn_to_y_major:
    jmp pn_y_major
pn_x_major:
    txa
pn_x_shift:
    asl ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    asl ZP_MAIN+$18
    rol
    bpl pn_x_shift
    tay
pn_x_ratio:
    ldx ZP_MAIN+$1B
pn_x_index:
    beq pn_x_output
pn_x_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta pn_x_lookup+2
pn_x_lookup:
    ldx REG_LOW,y
pn_x_output:
    lda REG_TABLE,x
    sta MATH_IO+$08
    lda REG_TABLE+$0100,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE+$0200,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0300,x
    sta MATH_IO+$0B
    rts
pn_y_major:
    lda ZP_MAIN+$1B
    beq pn_y_low
    stx ZP_MAIN+$19
pn_y_shift:
    asl ZP_MAIN+$18
    rol ZP_MAIN+$19
    asl ZP_MAIN+$1A
    rol
    bpl pn_y_shift
    tay
pn_y_ratio:
    ldx ZP_MAIN+$19
pn_y_index:
    beq pn_y_output
pn_y_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta pn_y_lookup+2
pn_y_lookup:
    ldx REG_LOW,y
pn_y_output:
    lda REG_TABLE+$0200,x
    sta MATH_IO+$08
    lda REG_TABLE+$0300,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0100,x
    sta MATH_IO+$0B
    rts
pn_y_low:
    lda ZP_MAIN+$1A
    bmi pn_y_low_done
pn_y_low_loop:
    asl ZP_MAIN+$18
    asl
    bpl pn_y_low_loop
pn_y_low_done:
    tay
    ldx ZP_MAIN+$18
    jmp pn_y_index
; Quadrant: X negative, Y positive.
* = REG_LOW+$0700
np_entry:
    sta ZP_MAIN+$1B
    lda MATH_IO
    eor #$FF
    sta ZP_MAIN+$18
    lda MATH_IO+$04
    sta ZP_MAIN+$1A
    cpx ZP_MAIN+$1B
    bcc np_to_y_major
    bne np_x_major
    txa
    bne np_compare_low
    inc ZP_MAIN+$18
    bne np_low_fix0_done
    dec ZP_MAIN+$18
np_low_fix0_done:
np_compare_low:
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1A
    bcc np_to_y_major
    txa
    bne np_x_shift
    lda ZP_MAIN+$18
    bmi np_x_low_done
np_x_low_loop:
    asl ZP_MAIN+$1A
    asl
    bpl np_x_low_loop
np_x_low_done:
    tay
    ldx ZP_MAIN+$1A
    jmp np_x_index
np_to_y_major:
    jmp np_y_major
np_x_major:
    txa
np_x_shift:
    asl ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    asl ZP_MAIN+$18
    rol
    bpl np_x_shift
    tay
np_x_ratio:
    ldx ZP_MAIN+$1B
np_x_index:
    beq np_x_output
np_x_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta np_x_lookup+2
np_x_lookup:
    ldx REG_LOW,y
np_x_output:
    sec
    lda #0
    sbc REG_TABLE,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0100,x
    sta MATH_IO+$09
    lda REG_TABLE+$0200,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0300,x
    sta MATH_IO+$0B
    rts
np_y_major:
    lda ZP_MAIN+$1B
    beq np_y_low
    stx ZP_MAIN+$19
np_y_shift:
    asl ZP_MAIN+$18
    rol ZP_MAIN+$19
    asl ZP_MAIN+$1A
    rol
    bpl np_y_shift
    tay
np_y_ratio:
    ldx ZP_MAIN+$19
np_y_index:
    beq np_y_output
np_y_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta np_y_lookup+2
np_y_lookup:
    ldx REG_LOW,y
np_y_output:
    sec
    lda #0
    sbc REG_TABLE+$0200,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0300,x
    sta MATH_IO+$09
    lda REG_TABLE,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0100,x
    sta MATH_IO+$0B
    rts
np_y_low:
    lda ZP_MAIN+$1A
    bmi np_y_low_done
np_y_low_loop:
    asl ZP_MAIN+$18
    asl
    bpl np_y_low_loop
np_y_low_done:
    tay
    ldx ZP_MAIN+$18
    jmp np_y_index
; Quadrant: X negative, Y negative.
* = REG_LOW+$0800
nn_entry:
    sta ZP_MAIN+$1B
    lda MATH_IO
    eor #$FF
    sta ZP_MAIN+$18
    lda MATH_IO+$04
    eor #$FF
    sta ZP_MAIN+$1A
    cpx ZP_MAIN+$1B
    bcc nn_to_y_major
    bne nn_x_major
    txa
    bne nn_compare_low
    inc ZP_MAIN+$18
    bne nn_low_fix0_done
    dec ZP_MAIN+$18
nn_low_fix0_done:
    inc ZP_MAIN+$1A
    bne nn_low_fix1_done
    dec ZP_MAIN+$1A
nn_low_fix1_done:
nn_compare_low:
    lda ZP_MAIN+$18
    cmp ZP_MAIN+$1A
    bcc nn_to_y_major
    txa
    bne nn_x_shift
    lda ZP_MAIN+$18
    bmi nn_x_low_done
nn_x_low_loop:
    asl ZP_MAIN+$1A
    asl
    bpl nn_x_low_loop
nn_x_low_done:
    tay
    ldx ZP_MAIN+$1A
    jmp nn_x_index
nn_to_y_major:
    jmp nn_y_major
nn_x_major:
    txa
nn_x_shift:
    asl ZP_MAIN+$1A
    rol ZP_MAIN+$1B
    asl ZP_MAIN+$18
    rol
    bpl nn_x_shift
    tay
nn_x_ratio:
    ldx ZP_MAIN+$1B
nn_x_index:
    beq nn_x_output
nn_x_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta nn_x_lookup+2
nn_x_lookup:
    ldx REG_LOW,y
nn_x_output:
    sec
    lda #0
    sbc REG_TABLE,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0100,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE+$0200,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0300,x
    sta MATH_IO+$0B
    rts
nn_y_major:
    lda ZP_MAIN+$1B
    beq nn_y_low
    stx ZP_MAIN+$19
nn_y_shift:
    asl ZP_MAIN+$18
    rol ZP_MAIN+$19
    asl ZP_MAIN+$1A
    rol
    bpl nn_y_shift
    tay
nn_y_ratio:
    ldx ZP_MAIN+$19
nn_y_index:
    beq nn_y_output
nn_y_log:
    lda REG_LOW+$0400,y
    sec
    sbc REG_LOW+$0400,x
    tay
    lda #>REG_LOW
    sbc REG_TABLE+$0400,x
    sta nn_y_lookup+2
nn_y_lookup:
    ldx REG_LOW,y
nn_y_output:
    sec
    lda #0
    sbc REG_TABLE+$0200,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0300,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0100,x
    sta MATH_IO+$0B
    rts
nn_y_low:
    lda ZP_MAIN+$1A
    bmi nn_y_low_done
nn_y_low_loop:
    asl ZP_MAIN+$18
    asl
    bpl nn_y_low_loop
nn_y_low_done:
    tay
    ldx ZP_MAIN+$18
    jmp nn_y_index

VEC2_NORMALIZE_CODE_END:
; Generated by tools/generate_normalize_tables.py; certified signed-Q8.8 domain.
; Four ratio-index pages, one log-low page, one log-high page, four component pages.
* = REG_LOW
    !byte $FF, $FE, $FE, $FD, $FC, $FB, $FA, $F9, $F8, $F7, $F6, $F5, $F4, $F3, $F2, $F1
    !byte $F0, $EF, $EE, $ED, $EC, $EB, $EA, $E9, $E8, $E7, $E6, $E5, $E4, $E3, $E2, $E1
    !byte $E0, $DF, $DE, $DD, $DC, $DB, $DA, $D9, $D8, $D7, $D6, $D5, $D4, $D3, $D2, $D1
    !byte $D0, $CF, $CE, $CD, $CC, $CB, $CA, $C9, $C8, $C7, $C6, $C5, $C4, $C3, $C2, $C1
    !byte $C0, $BF, $BE, $BD, $BC, $BB, $BA, $B9, $B8, $B8, $B7, $B6, $B5, $B4, $B4, $B3
    !byte $B2, $B1, $B0, $AF, $AE, $AD, $AC, $AB, $AA, $A9, $A8, $A7, $A6, $A5, $A4, $A3
    !byte $A2, $A1, $A0, $9F, $9E, $9D, $9C, $9B, $9A, $99, $98, $97, $96, $95, $94, $93
    !byte $92, $91, $90, $8F, $8E, $8D, $8C, $8B, $8A, $89, $88, $87, $86, $85, $84, $83
    !byte $82, $82, $81, $81, $80, $80, $7F, $7E, $7D, $7C, $7B, $7A, $79, $78, $77, $76
    !byte $75, $74, $74, $73, $72, $71, $70, $6F, $6F, $6E, $6D, $6C, $6C, $6B, $6A, $6A
    !byte $69, $68, $68, $67, $66, $65, $65, $64, $63, $63, $62, $61, $60, $60, $5F, $5E
    !byte $5E, $5D, $5C, $5B, $5B, $5A, $5A, $59, $59, $58, $58, $57, $57, $56, $56, $55
    !byte $55, $54, $54, $53, $53, $52, $52, $51, $51, $50, $50, $4F, $4F, $4E, $4E, $4E
    !byte $4D, $4D, $4D, $4C, $4C, $4B, $4B, $4A, $4A, $49, $49, $48, $48, $47, $47, $46
    !byte $46, $46, $45, $45, $45, $44, $44, $43, $43, $43, $42, $42, $41, $41, $41, $40
    !byte $40, $3F, $3F, $3F, $3E, $3E, $3E, $3D, $3D, $3D, $3C, $3C, $3B, $3B, $3A, $3A
    !byte $3A, $3A, $39, $39, $39, $38, $38, $38, $37, $37, $37, $36, $36, $36, $35, $35
    !byte $35, $34, $34, $34, $33, $33, $33, $32, $32, $32, $31, $31, $31, $30, $30, $30
    !byte $2F, $2F, $2F, $2E, $2E, $2E, $2D, $2D, $2D, $2D, $2C, $2C, $2C, $2C, $2B, $2B
    !byte $2B, $2B, $2A, $2A, $2A, $2A, $29, $29, $29, $29, $28, $28, $28, $28, $27, $27
    !byte $27, $27, $26, $26, $26, $26, $25, $25, $25, $25, $24, $24, $24, $24, $23, $23
    !byte $23, $23, $23, $23, $22, $22, $22, $22, $21, $21, $21, $21, $21, $20, $20, $20
    !byte $20, $20, $1F, $1F, $1F, $1F, $1F, $1F, $1E, $1E, $1E, $1E, $1E, $1E, $1D, $1D
    !byte $1D, $1D, $1D, $1C, $1C, $1C, $1C, $1C, $1C, $1B, $1B, $1B, $1B, $1B, $1B, $1A
    !byte $1A, $1A, $1A, $1A, $1A, $19, $19, $19, $19, $18, $19, $18, $18, $18, $18, $18
    !byte $18, $17, $17, $17, $17, $17, $17, $17, $16, $16, $16, $16, $16, $16, $16, $15
    !byte $15, $15, $15, $15, $15, $14, $15, $14, $14, $14, $14, $14, $14, $14, $13, $13
    !byte $13, $13, $13, $13, $13, $13, $12, $12, $12, $12, $12, $12, $12, $12, $11, $11
    !byte $11, $11, $11, $11, $11, $11, $11, $10, $10, $10, $10, $10, $10, $10, $10, $10
    !byte $10, $0F, $0F, $0F, $0F, $0F, $0F, $0F, $0F, $0F, $0F, $0E, $0E, $0E, $0E, $0E
    !byte $0E, $0E, $0E, $0E, $0E, $0E, $0D, $0D, $0D, $0D, $0D, $0D, $0D, $0D, $0D, $0D
    !byte $0D, $0D, $0D, $0C, $0C, $0C, $0C, $0C, $0C, $0C, $0C, $0B, $0C, $0C, $0C, $0C
    !byte $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0B, $0A, $0A
    !byte $0A, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $09, $0A, $09
    !byte $09, $09, $09, $09, $09, $09, $09, $09, $09, $09, $09, $09, $09, $08, $09, $09
    !byte $08, $08, $08, $08, $08, $08, $08, $08, $08, $08, $08, $08, $08, $08, $08, $08
    !byte $08, $08, $07, $08, $08, $07, $07, $07, $07, $07, $07, $07, $07, $07, $07, $06
    !byte $07, $07, $07, $07, $06, $07, $07, $07, $06, $07, $07, $06, $06, $06, $06, $06
    !byte $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06
    !byte $05, $06, $06, $05, $05, $05, $05, $05, $05, $05, $05, $05, $05, $05, $05, $05
    !byte $05, $05, $05, $05, $05, $05, $05, $05, $05, $05, $05, $05, $04, $05, $05, $05
    !byte $04, $05, $05, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04
    !byte $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $03, $04, $04, $03, $03
    !byte $03, $03, $03, $03, $04, $04, $03, $04, $04, $03, $03, $03, $03, $03, $03, $03
    !byte $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03, $03
    !byte $03, $03, $03, $03, $03, $03, $03, $03, $03, $02, $03, $03, $03, $03, $03, $03
    !byte $02, $03, $03, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02
    !byte $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02
    !byte $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02, $02
    !byte $02, $02, $02, $02, $02, $02, $02, $02, $02, $01, $02, $02, $02, $02, $01, $02
    !byte $02, $02, $02, $02, $01, $02, $02, $02, $02, $02, $02, $01, $02, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $00, $01, $01, $01, $01, $01, $01, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01, $01
    !byte $01, $01, $01, $01, $01, $01, $01, $01, $00, $00, $00, $00, $00, $00, $00, $01
    !byte $01, $00, $01, $01, $00, $01, $01, $01, $00, $01, $01, $01, $00, $01, $01, $01
    !byte $00, $01, $01, $01, $00, $01, $01, $01, $01, $00, $01, $01, $01, $01, $00, $01
    !byte $01, $01, $01, $01, $00, $01, $01, $01, $01, $01, $01, $00, $01, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
* = REG_LOW+$0400
    !byte $81, $81, $01, $4C, $81, $AA, $CB, $E8, $01, $16, $2A, $3B, $4B, $5A, $68, $74
    !byte $80, $8C, $96, $A0, $AA, $B3, $BB, $C3, $CB, $D3, $DA, $E1, $E8, $EE, $F4, $FA
    !byte $00, $06, $0B, $11, $16, $1B, $20, $25, $29, $2E, $32, $37, $3B, $3F, $43, $47
    !byte $4B, $4F, $53, $56, $5A, $5D, $61, $64, $67, $6B, $6E, $71, $74, $77, $7A, $7D
    !byte $80, $83, $86, $89, $8B, $8E, $91, $93, $96, $98, $9B, $9D, $A0, $A2, $A5, $A7
    !byte $A9, $AC, $AE, $B0, $B2, $B4, $B7, $B9, $BB, $BD, $BF, $C1, $C3, $C5, $C7, $C9
    !byte $CB, $CD, $CF, $D1, $D2, $D4, $D6, $D8, $DA, $DB, $DD, $DF, $E1, $E2, $E4, $E6
    !byte $E7, $E9, $EB, $EC, $EE, $EF, $F1, $F3, $F4, $F6, $F7, $F9, $FA, $FC, $FD, $FF
    !byte $00, $01, $03, $04, $06, $07, $08, $0A, $0B, $0C, $0E, $0F, $10, $12, $13, $14
    !byte $16, $17, $18, $19, $1B, $1C, $1D, $1E, $20, $21, $22, $23, $24, $26, $27, $28
    !byte $29, $2A, $2B, $2D, $2E, $2F, $30, $31, $32, $33, $34, $35, $36, $38, $39, $3A
    !byte $3B, $3C, $3D, $3E, $3F, $40, $41, $42, $43, $44, $45, $46, $47, $48, $49, $4A
    !byte $4B, $4C, $4D, $4E, $4F, $4F, $50, $51, $52, $53, $54, $55, $56, $57, $58, $59
    !byte $5A, $5A, $5B, $5C, $5D, $5E, $5F, $60, $60, $61, $62, $63, $64, $65, $66, $66
    !byte $67, $68, $69, $6A, $6A, $6B, $6C, $6D, $6E, $6E, $6F, $70, $71, $72, $72, $73
    !byte $74, $75, $75, $76, $77, $78, $78, $79, $7A, $7B, $7B, $7C, $7D, $7E, $7E, $7F
* = REG_TABLE+$0400
    !byte $FC, $FC, $FD, $FD, $FD, $FD, $FD, $FD, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE
    !byte $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE, $FE
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
* = REG_TABLE
    !byte $FE, $FD, $FA, $F5, $F1, $EC, $E6, $DF, $D8, $CF, $C7, $BD, $B3, $A9, $9D, $92
    !byte $86, $7A, $6D, $61, $53, $46, $37, $28, $19, $0A, $FB, $EA, $D9, $C6, $B5, $A0
    !byte $8C, $77, $65, $4E, $37, $22, $0F, $FA, $E6, $CE, $B7, $9F, $83, $66, $50, $3A
    !byte $24, $0D, $F7, $DB, $C3, $A9, $8E, $74, $59, $3C, $17, $F6, $E4, $C8, $A6, $85
    !byte $67, $48, $2A, $0A, $E7, $C7, $A1, $78, $61, $42, $22, $04, $E7, $C0, $94, $63
    !byte $48, $1F, $02, $D8, $B5, $8F, $6B, $45, $1E, $F9, $D0, $A8, $89, $73, $4D, $36
    !byte $12, $EF, $D7, $B9, $93, $71, $4D, $31, $14, $ED, $C7, $A5, $7A, $57, $38, $15
    !byte $EF, $D3, $B8, $9C, $73, $4C, $2A, $12, $F6, $D2, $BE, $A0, $7D, $65, $4A, $27
    !byte $F9, $D1, $7B, $50, $2A, $0D, $EB, $CB, $AB, $8A, $6B, $49, $24, $01, $E4, $BA
    !byte $9A, $76, $56, $33, $02, $E9, $C3, $9F, $79, $4C, $30, $0D, $DF, $BE, $98, $72
    !byte $48, $21, $01, $D5, $A8, $7E, $5F, $2E, $04, $E4, $B5, $8C, $57, $3E, $03, $E2
    !byte $A9, $8B, $5F, $2C, $F2, $A6, $7B, $58, $0E, $C6, $98, $67, $37, $0E, $DB, $AF
    !byte $79, $52, $19, $F0, $B4, $8B, $59, $27, $F1, $C4, $91, $5B, $1F, $F4, $C1, $8B
    !byte $5F, $25, $F2, $B8, $84, $4D, $1F, $E5, $AC, $7A, $4A, $0F, $CC, $A0, $67, $30
    !byte $FA, $BB, $86, $50, $11, $DB, $A3, $6E, $2E, $F1, $BD, $84, $46, $0F, $D3, $9B
    !byte $5A, $1D, $E6, $A9, $6C, $2F, $ED, $B5, $78, $31, $FA, $BB, $7E, $41, $09, $A6
* = REG_TABLE+$0100
    !byte $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F
    !byte $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7F, $7E, $7E, $7E, $7E, $7E, $7E
    !byte $7E, $7E, $7E, $7E, $7E, $7E, $7E, $7D, $7D, $7D, $7D, $7D, $7D, $7D, $7D, $7D
    !byte $7D, $7D, $7C, $7C, $7C, $7C, $7C, $7C, $7C, $7C, $7C, $7B, $7B, $7B, $7B, $7B
    !byte $7B, $7B, $7B, $7B, $7A, $7A, $7A, $7A, $7A, $7A, $7A, $7A, $79, $79, $79, $79
    !byte $79, $79, $79, $78, $78, $78, $78, $78, $78, $77, $77, $77, $77, $77, $77, $77
    !byte $77, $76, $76, $76, $76, $76, $76, $76, $76, $75, $75, $75, $75, $75, $75, $75
    !byte $74, $74, $74, $74, $74, $74, $74, $74, $73, $73, $73, $73, $73, $73, $73, $73
    !byte $72, $72, $72, $72, $72, $72, $71, $71, $71, $71, $71, $71, $71, $71, $70, $70
    !byte $70, $70, $70, $70, $70, $6F, $6F, $6F, $6F, $6F, $6F, $6F, $6E, $6E, $6E, $6E
    !byte $6E, $6E, $6E, $6D, $6D, $6D, $6D, $6D, $6D, $6C, $6C, $6C, $6C, $6C, $6C, $6B
    !byte $6B, $6B, $6B, $6B, $6A, $6A, $6A, $6A, $6A, $69, $69, $69, $69, $69, $68, $68
    !byte $68, $68, $68, $67, $67, $67, $67, $67, $66, $66, $66, $66, $66, $65, $65, $65
    !byte $65, $65, $64, $64, $64, $64, $64, $63, $63, $63, $63, $63, $62, $62, $62, $62
    !byte $61, $61, $61, $61, $61, $60, $60, $60, $60, $5F, $5F, $5F, $5F, $5F, $5E, $5E
    !byte $5E, $5E, $5D, $5D, $5D, $5D, $5C, $5C, $5C, $5C, $5B, $5B, $5B, $5B, $5B, $5A
* = REG_TABLE+$0200
    !byte $C8, $90, $54, $1A, $B1, $59, $0A, $9E, $3D, $E8, $80, $22, $B0, $45, $E0, $6B
    !byte $00, $87, $15, $8F, $17, $93, $21, $A2, $25, $9C, $16, $9B, $1A, $A5, $22, $B1
    !byte $38, $BD, $2F, $BE, $45, $C1, $2E, $A7, $15, $96, $0D, $8B, $18, $A6, $12, $7D
    !byte $E2, $4F, $B3, $30, $95, $09, $7A, $E7, $58, $CD, $60, $E2, $2A, $93, $12, $8E
    !byte $FB, $6C, $D5, $47, $BF, $2D, $AE, $36, $82, $E4, $4B, $AB, $06, $7F, $04, $98
    !byte $EA, $64, $B6, $2F, $94, $FF, $64, $CC, $35, $9B, $09, $72, $C3, $FE, $5E, $99
    !byte $F6, $4F, $8B, $D6, $33, $87, $DD, $20, $66, $C3, $1E, $6E, $D0, $21, $68, $B8
    !byte $0D, $4C, $89, $C6, $20, $75, $C0, $F4, $30, $7C, $A7, $E5, $30, $61, $99, $E3
    !byte $41, $93, $3F, $94, $E0, $19, $5C, $9A, $D9, $17, $53, $94, $D9, $1C, $52, $A1
    !byte $DC, $1E, $59, $99, $F1, $1F, $64, $A4, $E7, $37, $68, $A5, $F6, $2F, $70, $B1
    !byte $F8, $3A, $70, $BB, $05, $4A, $7E, $CE, $12, $46, $92, $D4, $28, $50, $AD, $E2
    !byte $3A, $69, $AD, $FB, $54, $C6, $07, $3B, $AA, $13, $57, $9E, $E4, $1E, $68, $A6
    !byte $F3, $2A, $7A, $B3, $06, $3F, $83, $C8, $10, $4E, $92, $DA, $2A, $63, $A6, $EC
    !byte $26, $71, $B3, $FC, $3E, $84, $BE, $06, $4E, $8B, $C7, $0F, $60, $96, $DA, $1D
    !byte $5D, $A8, $E6, $26, $6F, $AD, $EE, $2B, $74, $B9, $F5, $35, $7A, $B7, $FA, $37
    !byte $7D, $C0, $FC, $3D, $7F, $C0, $05, $40, $80, $CB, $03, $44, $82, $C1, $FA, $5E
* = REG_TABLE+$0300
    !byte $00, $01, $02, $03, $03, $04, $05, $05, $06, $06, $07, $08, $08, $09, $09, $0A
    !byte $0B, $0B, $0C, $0C, $0D, $0D, $0E, $0E, $0F, $0F, $10, $10, $11, $11, $12, $12
    !byte $13, $13, $14, $14, $15, $15, $16, $16, $17, $17, $18, $18, $19, $19, $1A, $1A
    !byte $1A, $1B, $1B, $1C, $1C, $1D, $1D, $1D, $1E, $1E, $1F, $1F, $20, $20, $21, $21
    !byte $21, $22, $22, $23, $23, $24, $24, $25, $25, $25, $26, $26, $27, $27, $28, $28
    !byte $28, $29, $29, $2A, $2A, $2A, $2B, $2B, $2C, $2C, $2D, $2D, $2D, $2D, $2E, $2E
    !byte $2E, $2F, $2F, $2F, $30, $30, $30, $31, $31, $31, $32, $32, $32, $33, $33, $33
    !byte $34, $34, $34, $34, $35, $35, $35, $35, $36, $36, $36, $36, $37, $37, $37, $37
    !byte $38, $38, $39, $39, $39, $3A, $3A, $3A, $3A, $3B, $3B, $3B, $3B, $3C, $3C, $3C
    !byte $3C, $3D, $3D, $3D, $3D, $3E, $3E, $3E, $3E, $3F, $3F, $3F, $3F, $40, $40, $40
    !byte $40, $41, $41, $41, $42, $42, $42, $42, $43, $43, $43, $43, $44, $44, $44, $44
    !byte $45, $45, $45, $45, $46, $46, $47, $47, $47, $48, $48, $48, $48, $49, $49, $49
    !byte $49, $4A, $4A, $4A, $4B, $4B, $4B, $4B, $4C, $4C, $4C, $4C, $4D, $4D, $4D, $4D
    !byte $4E, $4E, $4E, $4E, $4F, $4F, $4F, $50, $50, $50, $50, $51, $51, $51, $51, $52
    !byte $52, $52, $52, $53, $53, $53, $53, $54, $54, $54, $54, $55, $55, $55, $55, $56
    !byte $56, $56, $56, $57, $57, $57, $58, $58, $58, $58, $59, $59, $59, $59, $59, $5A
* = REG_GAME_API+$003C
