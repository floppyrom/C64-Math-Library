; FAST24 signed 24x24 composition using the qualified 24-ZP carry producer.
; Native signed executable path; shares immutable quarter-square tables only.
!cpu 6510
S24_sl = REG_TABLE+$0000
S24_sh = REG_TABLE+$0200
S24_nl = REG_TABLE+$0400
S24_nh = REG_TABLE+$0600
S24_p0 = ZP_MAIN+$1F
S24_p1 = S24_p0+$02
S24_p2 = S24_p0+$04
S24_p3 = S24_p0+$06
S24_p4 = S24_p0+$08
S24_p5 = S24_p0+$0A
S24_p6 = S24_p0+$0C
S24_p7 = S24_p0+$0E
S24_p8 = S24_p0+$10
S24_p9 = S24_p0+$12
S24_p10 = S24_p0+$14
S24_p11 = S24_p0+$16
S24_x0 = S24_p0
S24_x1 = S24_p4
S24_x2 = S24_p8
S24_r0 = S24_p1
S24_r1 = S24_p3
S24_r2 = S24_p7

* = REG_GAME+$0C00
S24_c0_1:
        clc
        adc (S24_p5),y
        sta S24_v21+1
        lda #1
        adc (S24_p6),y
        adc (S24_p7),y
        adc (S24_p8),y
        bcc S24_h0_2
S24_c0_2:
        clc
        adc (S24_p9),y
        sta S24_v22+1
        lda #1
        adc (S24_p10),y
        bcc S24_t0_2
S24_c1_1:
        clc
        adc (S24_p5),y
        sta S24_v11+1
        lda #1
        adc (S24_p6),y
        adc (S24_p7),y
        adc (S24_p8),y
        bcc S24_h1_2
S24_c1_2:
        clc
        adc (S24_p9),y
        sta S24_v12+1
        lda #1
        adc (S24_p10),y
        bcc S24_t1_2
S24_bind_primed:
        sta S24_p10
        eor #$ff
        sta S24_p9
        sta S24_p11
        lda S24_x0
        sta S24_p2
        eor #$ff
        sta S24_p1
        sta S24_p3
        lda S24_x1
        sta S24_p6
        eor #$ff
        sta S24_p5
        sta S24_p7
S24_row0:
        lda (S24_p0),y
        adc (S24_p1),y
        sta S24_v20+1
        lda (S24_p2),y
        adc (S24_p3),y
        adc (S24_p4),y
        bcs S24_c0_1
S24_h0_1:
        adc (S24_p5),y
        sta S24_v21+1
        lda (S24_p6),y
S24_t0_1:
        adc (S24_p7),y
        adc (S24_p8),y
        bcs S24_c0_2
S24_h0_2:
        adc (S24_p9),y
        sta S24_v22+1
        lda (S24_p10),y
S24_t0_2:
        adc (S24_p11),y
        tax
S24_y1=*+1
        ldy #0
S24_row1:
        lda (S24_p0),y
        adc (S24_p1),y
        sta S24_v10+1
        lda (S24_p2),y
        adc (S24_p3),y
        adc (S24_p4),y
        bcs S24_c1_1
S24_h1_1:
        adc (S24_p5),y
        sta S24_v11+1
        lda (S24_p6),y
S24_t1_1:
        adc (S24_p7),y
        adc (S24_p8),y
        bcs S24_c1_2
S24_h1_2:
        adc (S24_p9),y
        sta S24_v12+1
        lda (S24_p10),y
S24_t1_2:
        adc (S24_p11),y
        sta S24_v13+1
S24_y0=*+1
        ldy #0
S24_row2:
        lda (S24_p0),y
        adc (S24_p1),y
        sta MATH_IO+$08
        lda (S24_p2),y
        adc (S24_p3),y
        adc (S24_p4),y
        bcs S24_c2_1
S24_h2_1:
        adc (S24_p5),y
        sta S24_v01+1
        lda (S24_p6),y
S24_t2_1:
        adc (S24_p7),y
        adc (S24_p8),y
        bcs S24_c2_2
S24_h2_2:
        adc (S24_p9),y
        sta S24_v02+1
        lda (S24_p10),y
S24_t2_2:
        adc (S24_p11),y
        tay
S24_summation:
        clc
S24_v01:    lda #0
S24_v10:    adc #0
        sta MATH_IO+$09
S24_v02:    lda #0
S24_v11:    adc #0
        bcc S24_column2
        iny
        clc
S24_column2:
S24_v20:    adc #0
        sta MATH_IO+$0A
        tya
S24_v12:    adc #0
        bcc S24_column3
        clc
        inc S24_v13+1
S24_column3:
S24_v21:    adc #0
        tay
S24_v13:    lda #0
S24_v22:    adc #0
        bcs S24_final
        rts
S24_final:
        inx
        rts
S24_c2_1:
        clc
        adc (S24_p5),y
        sta S24_v01+1
        lda #1
        adc (S24_p6),y
        adc (S24_p7),y
        adc (S24_p8),y
        bcc S24_h2_2
S24_c2_2:
        clc
        adc (S24_p9),y
        sta S24_v02+1
        lda #1
        adc (S24_p10),y
        bcc S24_t2_2

; Repose OptiSearchV2 carry-prime signed composition.
; CPY #0 both tests y2's sign and establishes C=1 for all byte values.
; Binding uses only loads/stores/EOR, preserving C into the first product.
; S24_p2 is dead after the producer, so its low byte holds correction A.
S24_smul24_composed:
        cpy #0
        bmi S24_smul24_yneg
        lda S24_x2
        bmi S24_smul24_xneg
        jmp S24_bind_primed

; x<0, y>=0: subtract the original y from the upper product half.
S24_smul24_xneg:
        ; Re-read stable public Y2 after the producer (upstream q2 optimization).
        jsr S24_bind_primed
        sta S24_p2
        tya
        sec
        sbc S24_y0
        tay
        lda S24_p2
        sbc S24_y1
        sta S24_p2
        txa
        sbc MATH_IO+$06
        tax
        lda S24_p2
        rts

; x>=0, y<0: subtract the original x from the upper product half.
S24_smul24_yneg:
        lda S24_x2
        bmi S24_smul24_nn
        jsr S24_bind_primed
        sta S24_p2
        tya
        sec
        sbc S24_x0
        tay
        lda S24_p2
        sbc S24_x1
        sta S24_p2
        txa
        sbc S24_x2
        tax
        lda S24_p2
        rts

; x<0, y<0: negate both operands. Entry C=1 negates y. Since y2
; is negative, EOR/ADC leaves C=0; LDA #1/SBC x0 starts -x exactly.
S24_smul24_nn:
        lda #0
        sbc S24_y0
        sta S24_y0
        lda #0
        sbc S24_y1
        sta S24_y1
        tya
        eor #$ff
        adc #0
        tay
        lda #1
        sbc S24_x0
        sta S24_x0
        sta S24_p2
        eor #$ff
        sta S24_p1
        sta S24_p3
        lda #0
        sbc S24_x1
        sta S24_x1
        sta S24_p6
        eor #$ff
        sta S24_p5
        sta S24_p7
        lda #0
        sbc S24_x2
        sta S24_x2
        sta S24_p10
        eor #$ff
        sta S24_p9
        sta S24_p11
        sec
        jmp S24_row0
S24_smul24_composed_end:

S24_public_impl:
        ; V2-V4: MATH_INIT owns these twelve pointer high bytes.
        ; The existing UMUL24 path uses the same persistent state.
        lda MATH_IO+$00
        sta S24_x0
        lda MATH_IO+$01
        sta S24_x1
        lda MATH_IO+$02
        sta S24_x2
        lda MATH_IO+$04
        sta S24_y0
        lda MATH_IO+$05
        sta S24_y1
        ldy MATH_IO+$06
        jsr S24_smul24_composed
        sta MATH_IO+$0C
        stx MATH_IO+$0D
        sty MATH_IO+$0B
        clc
        rts

* = MATH_SMUL24
S24_public:
        jmp S24_public_impl
