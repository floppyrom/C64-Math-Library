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
; Small-vector paths pass the minor byte directly to the DMA setup.
;
; REU backend: existing 32 KiB ratio-index plane in REU_TURBO16_BANK.
; Code body: REG_LOW+$0200; component planes supplied by the local include.
; This source owns its code/table islands and restores PC to the end of
; the stable public JMP slot. See README.md for the complete memory map.
!cpu 6510

VEC2_NORMALIZE_Q8_8_NATIVE:

    jmp norm_entry
* = REG_LOW+$0200
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
    lda ZP_MAIN+$1A
    jmp pp_x_dma
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
    lda ZP_MAIN+$1B
pp_x_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    lda REG_TABLE+$0800,x
    sta MATH_IO+$08
    lda REG_TABLE+$0900,x
    sta MATH_IO+$09
    lda REG_TABLE+$0A00,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0B00,x
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
    lda ZP_MAIN+$19
pp_y_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    lda REG_TABLE+$0A00,x
    sta MATH_IO+$08
    lda REG_TABLE+$0B00,x
    sta MATH_IO+$09
    lda REG_TABLE+$0800,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0900,x
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
    lda ZP_MAIN+$18
    jmp pp_y_dma
; Quadrant: X positive, Y negative.
* = REG_LOW+$0300
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
    lda ZP_MAIN+$1A
    jmp pn_x_dma
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
    lda ZP_MAIN+$1B
pn_x_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    lda REG_TABLE+$0800,x
    sta MATH_IO+$08
    lda REG_TABLE+$0900,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE+$0A00,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0B00,x
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
    lda ZP_MAIN+$19
pn_y_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    lda REG_TABLE+$0A00,x
    sta MATH_IO+$08
    lda REG_TABLE+$0B00,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE+$0800,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0900,x
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
    lda ZP_MAIN+$18
    jmp pn_y_dma
; Quadrant: X negative, Y positive.
* = REG_LOW+$0B00
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
    lda ZP_MAIN+$1A
    jmp np_x_dma
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
    lda ZP_MAIN+$1B
np_x_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    sec
    lda #0
    sbc REG_TABLE+$0800,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0900,x
    sta MATH_IO+$09
    lda REG_TABLE+$0A00,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0B00,x
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
    lda ZP_MAIN+$19
np_y_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    sec
    lda #0
    sbc REG_TABLE+$0A00,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0B00,x
    sta MATH_IO+$09
    lda REG_TABLE+$0800,x
    sta MATH_IO+$0A
    lda REG_TABLE+$0900,x
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
    lda ZP_MAIN+$18
    jmp np_y_dma
; Quadrant: X negative, Y negative.
* = REG_LOW+$0720
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
    lda ZP_MAIN+$1A
    jmp nn_x_dma
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
    lda ZP_MAIN+$1B
nn_x_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    sec
    lda #0
    sbc REG_TABLE+$0800,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0900,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE+$0A00,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0B00,x
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
    lda ZP_MAIN+$19
nn_y_dma:
    sta $DF04
    sty $DF05
    lda #REU_TURBO16_BANK
    sta $DF06
    lda #$81
    sta $DF01
    ldx REU_SCRATCH
    sec
    lda #0
    sbc REG_TABLE+$0A00,x
    sta MATH_IO+$08
    lda #0
    sbc REG_TABLE+$0B00,x
    sta MATH_IO+$09
    sec
    lda #0
    sbc REG_TABLE+$0800,x
    sta MATH_IO+$0A
    lda #0
    sbc REG_TABLE+$0900,x
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
    lda ZP_MAIN+$18
    jmp nn_y_dma

VEC2_NORMALIZE_CODE_END:
!source "vec2_normalize_tables.asm"
* = REG_GAME_API+$003C
