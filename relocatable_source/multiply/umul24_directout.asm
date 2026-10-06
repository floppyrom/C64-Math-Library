; Optimized fixed-profile V2/V3/V4 UMUL24 public producer.
; Keeps the selected 24-ZP reverse/carry quarter-square core and persistent
; pointer-high image. The only arithmetic change is result placement: once
; p1/p3/p7 are dead as table-pointer lows, product bytes z0/z1/z2 are written
; directly to the public result block instead of being staged in ZP and copied
; by the adapter.
!cpu 6510

R24_sl = REG_TABLE+$0000
R24_sh = REG_TABLE+$0200
R24_nl = REG_TABLE+$0400
R24_nh = REG_TABLE+$0600

R24_p0  = ZP_MAIN+$1F
R24_p1  = R24_p0+$02
R24_p2  = R24_p0+$04
R24_p3  = R24_p0+$06
R24_p4  = R24_p0+$08
R24_p5  = R24_p0+$0A
R24_p6  = R24_p0+$0C
R24_p7  = R24_p0+$0E
R24_p8  = R24_p0+$10
R24_p9  = R24_p0+$12
R24_p10 = R24_p0+$14
R24_p11 = R24_p0+$16

R24_x0 = R24_p0
R24_x1 = R24_p4
R24_x2 = R24_p8

* = REG_KERNEL+$1649
R24_c0_1:
        clc
        adc (R24_p5),y
        sta R24_v21+1
        lda #1
        adc (R24_p6),y
        adc (R24_p7),y
        adc (R24_p8),y
        bcc R24_h0_2
R24_c0_2:
        clc
        adc (R24_p9),y
        sta R24_v22+1
        lda #1
        adc (R24_p10),y
        bcc R24_t0_2
R24_c1_1:
        clc
        adc (R24_p5),y
        sta R24_v11+1
        lda #1
        adc (R24_p6),y
        adc (R24_p7),y
        adc (R24_p8),y
        bcc R24_h1_2
R24_c1_2:
        clc
        adc (R24_p9),y
        sta R24_v12+1
        lda #1
        adc (R24_p10),y
        bcc R24_t1_2

R24_umult:
        lda R24_x0
        sta R24_p2
        eor #$ff
        sta R24_p1
        sta R24_p3
        lda R24_x1
        sta R24_p6
        eor #$ff
        sta R24_p5
        sta R24_p7
        lda R24_x2
        sta R24_p10
        eor #$ff
        sta R24_p9
        sta R24_p11
R24_bound_entry:
        sec
R24_row0:
        lda (R24_p0),y
        adc (R24_p1),y
        sta R24_v20+1
        lda (R24_p2),y
        adc (R24_p3),y
        adc (R24_p4),y
        bcs R24_c0_1
R24_h0_1:
        adc (R24_p5),y
        sta R24_v21+1
        lda (R24_p6),y
R24_t0_1:
        adc (R24_p7),y
        adc (R24_p8),y
        bcs R24_c0_2
R24_h0_2:
        adc (R24_p9),y
        sta R24_v22+1
        lda (R24_p10),y
R24_t0_2:
        adc (R24_p11),y
        tax
R24_y1=*+1
        ldy #0

R24_row1:
        lda (R24_p0),y
        adc (R24_p1),y
        sta R24_v10+1
        lda (R24_p2),y
        adc (R24_p3),y
        adc (R24_p4),y
        bcs R24_c1_1
R24_h1_1:
        adc (R24_p5),y
        sta R24_v11+1
        lda (R24_p6),y
R24_t1_1:
        adc (R24_p7),y
        adc (R24_p8),y
        bcs R24_c1_2
R24_h1_2:
        adc (R24_p9),y
        sta R24_v12+1
        lda (R24_p10),y
R24_t1_2:
        adc (R24_p11),y
        sta R24_v13+1
R24_y0=*+1
        ldy #0

R24_row2:
        lda (R24_p0),y
        adc (R24_p1),y
        sta MATH_IO+$08
        lda (R24_p2),y
        adc (R24_p3),y
        adc (R24_p4),y
        bcs R24_c2_1
R24_h2_1:
        adc (R24_p5),y
        sta R24_v01+1
        lda (R24_p6),y
R24_t2_1:
        adc (R24_p7),y
        adc (R24_p8),y
        bcs R24_c2_2
R24_h2_2:
        adc (R24_p9),y
        sta R24_v02+1
        lda (R24_p10),y
R24_t2_2:
        adc (R24_p11),y
        tay

R24_summation:
        clc
R24_v01:    lda #0
R24_v10:    adc #0
        sta MATH_IO+$09
R24_v02:    lda #0
R24_v11:    adc #0
        bcc R24_column2
        iny
        clc
R24_column2:
R24_v20:    adc #0
        sta MATH_IO+$0A
        tya
R24_v12:    adc #0
        bcc R24_column3
        clc
        inc R24_v13+1
R24_column3:
R24_v21:    adc #0
        tay
R24_v13:    lda #0
R24_v22:    adc #0
        bcs R24_final
        rts
R24_final:
        inx
        rts

R24_c2_1:
        clc
        adc (R24_p5),y
        sta R24_v01+1
        lda #1
        adc (R24_p6),y
        adc (R24_p7),y
        adc (R24_p8),y
        bcc R24_h2_2
R24_c2_2:
        clc
        adc (R24_p9),y
        sta R24_v02+1
        lda #1
        adc (R24_p10),y
        bcc R24_t2_2

R24_init:
        lda #>R24_sl
        sta R24_p0+1
        sta R24_p4+1
        sta R24_p8+1
        lda #>R24_nl
        sta R24_p1+1
        sta R24_p5+1
        sta R24_p9+1
        lda #>R24_sh
        sta R24_p2+1
        sta R24_p6+1
        sta R24_p10+1
        lda #>R24_nh
        sta R24_p3+1
        sta R24_p7+1
        sta R24_p11+1
        rts

* = REG_API+$04C0
R24_public_impl:
        lda MATH_IO+$00
        sta R24_x0
        lda MATH_IO+$01
        sta R24_x1
        lda MATH_IO+$02
        sta R24_x2
        lda MATH_IO+$04
        sta R24_y0
        lda MATH_IO+$05
        sta R24_y1
        ldy MATH_IO+$06
        jsr R24_umult
        sta MATH_IO+$0C
        stx MATH_IO+$0D
        sty MATH_IO+$0B
        clc
        rts
