; FAST17 low-ZP signed 16x16 composition for V1/V5.
; Uses a private copy of the qualified 17-ZP UMUL16 magnitude core so signed and
; unsigned executable graphs remain disjoint. Immutable quarter-square tables are shared.
!cpu 6510
S16_sl = REG_TABLE+$2400
S16_sh = REG_TABLE+$2600
S16_nl = REG_TABLE+$2800
S16_nh = REG_TABLE+$2A00
S16_p0 = ZP_MAIN+$07
S16_p1 = S16_p0+$02
S16_p2 = S16_p0+$04
S16_p3 = S16_p0+$06
S16_p4 = S16_p0+$08
S16_p5 = S16_p0+$0A
S16_p6 = S16_p0+$0C
S16_p7 = S16_p0+$0E
S16_z0 = S16_p0+$10
S16_x0 = S16_p0
S16_x1 = S16_p4

* = REG_GAME+$0D00
S16_composed:
        lda S16_x1
        bmi S16_xneg
        bit S16_y1
        bmi S16_yneg_only
        jmp S16_umult
S16_xneg:
        bit S16_y1
        bmi S16_nn
        sty S16_saved_y0+1
        jsr S16_umult
        sec
S16_saved_y0:
        sbc #$00
        sta S16_restore_a1+1
        tya
        sbc S16_y1
        tay
S16_restore_a1:
        lda #$00
        rts
S16_yneg_only:
        jsr S16_umult
        sec
        sbc S16_x0
        sta S16_restore_a2+1
        tya
        sbc S16_x1
        tay
S16_restore_a2:
        lda #$00
        rts
S16_nn:
        sty S16_nn_y0+1
        sec
        lda #$00
S16_nn_y0:
        sbc #$00
        tay
        lda #$00
        sbc S16_y1
        sta S16_y1
        sec
        lda #$00
        sbc S16_x0
        sta S16_x0
        sta S16_p2
        eor #$ff
        sta S16_p1
        sta S16_p3
        lda #$00
        sbc S16_x1
        sta S16_x1
        sta S16_p6
        eor #$ff
        sta S16_p5
        sta S16_p7
        jmp S16_same_x

* = REG_GAME+$0DEC
S16_umult:
        lda S16_x0
        sta S16_p2
        eor #$ff
        sta S16_p1
        sta S16_p3
        lda S16_x1
        sta S16_p6
        eor #$ff
        sta S16_p5
        sta S16_p7
S16_same_x:
        sec
        lda (S16_p0),y
        adc (S16_p1),y
        sta S16_z0
        lda (S16_p2),y
        adc (S16_p3),y
        adc (S16_p4),y
        bcs S16_carry0
        adc (S16_p5),y
        tax
        lda (S16_p6),y
S16_tail0:
        adc (S16_p7),y
        sta S16_high0+1
S16_y1=*+1
        ldy #0
        lda (S16_p0),y
        adc (S16_p1),y
        sta S16_low1+1
        lda (S16_p2),y
        adc (S16_p3),y
        adc (S16_p4),y
        bcs S16_carry1
        adc (S16_p5),y
        sta S16_high1+1
        lda (S16_p6),y
S16_tail1:
        adc (S16_p7),y
        tay
        clc
        txa
S16_low1: adc #0
        tax
S16_high0: lda #0
S16_high1: adc #0
        bcs S16_final
        rts
S16_final:
        iny
        rts
S16_carry0:
        clc
        adc (S16_p5),y
        tax
        lda #1
        adc (S16_p6),y
        bcc S16_tail0
S16_carry1:
        clc
        adc (S16_p5),y
        sta S16_high1+1
        lda #1
        adc (S16_p6),y
        bcc S16_tail1

* = MATH_SMUL16
S16_public:
        lda #>S16_sl
        sta S16_p0+1
        sta S16_p4+1
        lda #>S16_nl
        sta S16_p1+1
        sta S16_p5+1
        lda #>S16_sh
        sta S16_p2+1
        sta S16_p6+1
        lda #>S16_nh
        sta S16_p3+1
        sta S16_p7+1
        lda MATH_IO+$00
        sta S16_x0
        lda MATH_IO+$01
        sta S16_x1
        lda MATH_IO+$05
        sta S16_y1
        ldy MATH_IO+$04
        jsr S16_composed
        sta MATH_IO+$0A
        stx MATH_IO+$09
        sty MATH_IO+$0B
        lda S16_z0
        sta MATH_IO+$08
        clc
        rts
