; UMUL24 refresh: private FAST24 24-ZP carry producer for public unsigned API.
; This is an executable clone of the qualified FAST24 arithmetic core so the
; signed and unsigned public APIs share immutable tables but never executable code.
!cpu 6510

U24_sl = S24_sl
U24_sh = S24_sh
U24_nl = S24_nl
U24_nh = S24_nh
U24_p0 = S24_p0
U24_p1 = S24_p1
U24_p2 = S24_p2
U24_p3 = S24_p3
U24_p4 = S24_p4
U24_p5 = S24_p5
U24_p6 = S24_p6
U24_p7 = S24_p7
U24_p8 = S24_p8
U24_p9 = S24_p9
U24_p10 = S24_p10
U24_p11 = S24_p11
U24_x0 = S24_x0
U24_x1 = S24_x1
U24_x2 = S24_x2
U24_r0 = S24_r0
U24_r1 = S24_r1
U24_r2 = S24_r2

* = REG_LOW+$1D00
U24_c0_1:
        clc
        adc (U24_p5),y
        sta U24_v21+1
        lda #1
        adc (U24_p6),y
        adc (U24_p7),y
        adc (U24_p8),y
        bcc U24_h0_2
U24_c0_2:
        clc
        adc (U24_p9),y
        sta U24_v22+1
        lda #1
        adc (U24_p10),y
        bcc U24_t0_2
U24_c1_1:
        clc
        adc (U24_p5),y
        sta U24_v11+1
        lda #1
        adc (U24_p6),y
        adc (U24_p7),y
        adc (U24_p8),y
        bcc U24_h1_2
U24_c1_2:
        clc
        adc (U24_p9),y
        sta U24_v12+1
        lda #1
        adc (U24_p10),y
        bcc U24_t1_2
U24_umult:
        lda U24_x0
        sta U24_p2
        eor #$ff
        sta U24_p1
        sta U24_p3
        lda U24_x1
        sta U24_p6
        eor #$ff
        sta U24_p5
        sta U24_p7
        lda U24_x2
        sta U24_p10
        eor #$ff
        sta U24_p9
        sta U24_p11
U24_bound_entry:
        sec
U24_row0:
        lda (U24_p0),y
        adc (U24_p1),y
        sta U24_v20+1
        lda (U24_p2),y
        adc (U24_p3),y
        adc (U24_p4),y
        bcs U24_c0_1
U24_h0_1:
        adc (U24_p5),y
        sta U24_v21+1
        lda (U24_p6),y
U24_t0_1:
        adc (U24_p7),y
        adc (U24_p8),y
        bcs U24_c0_2
U24_h0_2:
        adc (U24_p9),y
        sta U24_v22+1
        lda (U24_p10),y
U24_t0_2:
        adc (U24_p11),y
        tax
U24_y1=*+1
        ldy #0
U24_row1:
        lda (U24_p0),y
        adc (U24_p1),y
        sta U24_v10+1
        lda (U24_p2),y
        adc (U24_p3),y
        adc (U24_p4),y
        bcs U24_c1_1
U24_h1_1:
        adc (U24_p5),y
        sta U24_v11+1
        lda (U24_p6),y
U24_t1_1:
        adc (U24_p7),y
        adc (U24_p8),y
        bcs U24_c1_2
U24_h1_2:
        adc (U24_p9),y
        sta U24_v12+1
        lda (U24_p10),y
U24_t1_2:
        adc (U24_p11),y
        sta U24_v13+1
U24_y0=*+1
        ldy #0
U24_row2:
        lda (U24_p0),y
        adc (U24_p1),y
        sta U24_r0
        lda (U24_p2),y
        adc (U24_p3),y
        adc (U24_p4),y
        bcs U24_c2_1
U24_h2_1:
        adc (U24_p5),y
        sta U24_v01+1
        lda (U24_p6),y
U24_t2_1:
        adc (U24_p7),y
        adc (U24_p8),y
        bcs U24_c2_2
U24_h2_2:
        adc (U24_p9),y
        sta U24_v02+1
        lda (U24_p10),y
U24_t2_2:
        adc (U24_p11),y
        tay
U24_summation:
        clc
U24_v01:    lda #0
U24_v10:    adc #0
        sta U24_r1
U24_v02:    lda #0
U24_v11:    adc #0
        bcc U24_column2
        iny
        clc
U24_column2:
U24_v20:    adc #0
        sta U24_r2
        tya
U24_v12:    adc #0
        bcc U24_column3
        clc
        inc U24_v13+1
U24_column3:
U24_v21:    adc #0
        tay
U24_v13:    lda #0
U24_v22:    adc #0
        bcs U24_final
        rts
U24_final:
        inx
        rts
U24_c2_1:
        clc
        adc (U24_p5),y
        sta U24_v01+1
        lda #1
        adc (U24_p6),y
        adc (U24_p7),y
        adc (U24_p8),y
        bcc U24_h2_2
U24_c2_2:
        clc
        adc (U24_p9),y
        sta U24_v02+1
        lda #1
        adc (U24_p10),y
        bcc U24_t2_2


*= REG_LOW+$1700
U24_FAST24_public_impl:
        lda #>U24_sl
        sta U24_p0+1
        sta U24_p4+1
        sta U24_p8+1
        lda #>U24_nl
        sta U24_p1+1
        sta U24_p5+1
        sta U24_p9+1
        lda #>U24_sh
        sta U24_p2+1
        sta U24_p6+1
        sta U24_p10+1
        lda #>U24_nh
        sta U24_p3+1
        sta U24_p7+1
        sta U24_p11+1
        lda MATH_IO+$00
        sta U24_x0
        lda MATH_IO+$01
        sta U24_x1
        lda MATH_IO+$02
        sta U24_x2
        lda MATH_IO+$04
        sta U24_y0
        lda MATH_IO+$05
        sta U24_y1
        ldy MATH_IO+$06
        jsr U24_umult
        sta MATH_IO+$0C
        stx MATH_IO+$0D
        sty MATH_IO+$0B
        lda U24_r0
        sta MATH_IO+$08
        lda U24_r1
        sta MATH_IO+$09
        lda U24_r2
        sta MATH_IO+$0A
        clc
        rts

*= MATH_UMUL24
U24_FAST24_public:
        jmp U24_FAST24_public_impl
