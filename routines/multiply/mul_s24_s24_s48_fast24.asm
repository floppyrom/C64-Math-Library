; Qualified 24-ZP signed 24x24 -> 48 composition with carry-primed dispatch
; Base: C64-Math-Library record_umul24_24zp_carry.a (357.041715 mean)
; Signed composition: Repose OptiSearch; carry-prime refinement from OptiSearchV2
; 2026-10-06 smul24-carry-prime-dead-zp-v2, adapted with one shared binder.
; PP=unsigned; mixed quadrants=upper-half correction; NN=negate + fused X bind.
; ABI (native kernel):
;   x = x0,x1,x2 (24-bit two's complement)
;   y = y0,y1,Y  (24-bit two's complement; Y is y2)
;   out = r0,r1,r2,Y,A,X (48-bit two's complement)
; Inputs/private SMC may be clobbered. D=0. Non-reentrant.
!cpu 6510
BIAS=202
*=$0021
zp_start:
p0: !word sl
p1: !word nl
p2: !word sh
p3: !word nh
p4: !word sl
p5: !word nl
p6: !word sh
p7: !word nh
p8: !word sl
p9: !word nl
p10: !word sh
p11: !word nh
zp_end:
*=$0600
ram_start:
ram_end:
x0 = p0
x1 = p4
x2 = p8
r0 = p1
r1 = p3
r2 = p7

*=$5649
code_start:
c0_1:
        clc
        adc (p5),y
        sta v21+1
        lda #1
        adc (p6),y
        adc (p7),y
        adc (p8),y
        bcc h0_2
c0_2:
        clc
        adc (p9),y
        sta v22+1
        lda #1
        adc (p10),y
        bcc t0_2
c1_1:
        clc
        adc (p5),y
        sta v11+1
        lda #1
        adc (p6),y
        adc (p7),y
        adc (p8),y
        bcc h1_2
c1_2:
        clc
        adc (p9),y
        sta v12+1
        lda #1
        adc (p10),y
        bcc t1_2
bind_primed:
        sta p10
        eor #$ff
        sta p9
        sta p11
        lda x0
        sta p2
        eor #$ff
        sta p1
        sta p3
        lda x1
        sta p6
        eor #$ff
        sta p5
        sta p7
row0:
        lda (p0),y
        adc (p1),y
        sta v20+1
        lda (p2),y
        adc (p3),y
        adc (p4),y
        bcs c0_1
h0_1:
        adc (p5),y
        sta v21+1
        lda (p6),y
t0_1:
        adc (p7),y
        adc (p8),y
        bcs c0_2
h0_2:
        adc (p9),y
        sta v22+1
        lda (p10),y
t0_2:
        adc (p11),y
        tax
y1=*+1
        ldy #0
row1:
        lda (p0),y
        adc (p1),y
        sta v10+1
        lda (p2),y
        adc (p3),y
        adc (p4),y
        bcs c1_1
h1_1:
        adc (p5),y
        sta v11+1
        lda (p6),y
t1_1:
        adc (p7),y
        adc (p8),y
        bcs c1_2
h1_2:
        adc (p9),y
        sta v12+1
        lda (p10),y
t1_2:
        adc (p11),y
        sta v13+1
y0=*+1
        ldy #0
row2:
        lda (p0),y
        adc (p1),y
        sta r0
        lda (p2),y
        adc (p3),y
        adc (p4),y
        bcs c2_1
h2_1:
        adc (p5),y
        sta v01+1
        lda (p6),y
t2_1:
        adc (p7),y
        adc (p8),y
        bcs c2_2
h2_2:
        adc (p9),y
        sta v02+1
        lda (p10),y
t2_2:
        adc (p11),y
        tay
summation:
        clc
v01:    lda #0
v10:    adc #0
        sta r1
v02:    lda #0
v11:    adc #0
        bcc column2
        iny
        clc
column2:
v20:    adc #0
        sta r2
        tya
v12:    adc #0
        bcc column3
        clc
        inc v13+1
column3:
v21:    adc #0
        tay
v13:    lda #0
v22:    adc #0
        bcs final
        rts
final:
        inx
        rts
c2_1:
        clc
        adc (p5),y
        sta v01+1
        lda #1
        adc (p6),y
        adc (p7),y
        adc (p8),y
        bcc h2_2
c2_2:
        clc
        adc (p9),y
        sta v02+1
        lda #1
        adc (p10),y
        bcc t2_2

; Repose OptiSearchV2 carry-prime signed composition.
; CPY #0 both tests y2's sign and establishes C=1 for all byte values.
; Binding uses only loads/stores/EOR, preserving C into the first product.
; p2 is dead after the producer, so its low byte holds correction A.
smul24_composed:
        cpy #0
        bmi smul24_yneg
        lda x2
        bmi smul24_xneg
        jmp bind_primed

; x<0, y>=0: subtract the original y from the upper product half.
smul24_xneg:
        sty smul24_saved_y2+1
        jsr bind_primed
        sta p2
        tya
        sec
        sbc y0
        tay
        lda p2
        sbc y1
        sta p2
        txa
smul24_saved_y2:
        sbc #0
        tax
        lda p2
        rts

; x>=0, y<0: subtract the original x from the upper product half.
smul24_yneg:
        lda x2
        bmi smul24_nn
        jsr bind_primed
        sta p2
        tya
        sec
        sbc x0
        tay
        lda p2
        sbc x1
        sta p2
        txa
        sbc x2
        tax
        lda p2
        rts

; x<0, y<0: negate both operands. Entry C=1 negates y. Since y2
; is negative, EOR/ADC leaves C=0; LDA #1/SBC x0 starts -x exactly.
smul24_nn:
        lda #0
        sbc y0
        sta y0
        lda #0
        sbc y1
        sta y1
        tya
        eor #$ff
        adc #0
        tay
        lda #1
        sbc x0
        sta x0
        sta p2
        eor #$ff
        sta p1
        sta p3
        lda #0
        sbc x1
        sta x1
        sta p6
        eor #$ff
        sta p5
        sta p7
        lda #0
        sbc x2
        sta x2
        sta p10
        eor #$ff
        sta p9
        sta p11
        sec
        jmp row0
smul24_composed_end:

code_end:
init:
        lda #>sl
        sta p0+1
        sta p4+1
        sta p8+1
        lda #>nl
        sta p1+1
        sta p5+1
        sta p9+1
        lda #>sh
        sta p2+1
        sta p6+1
        sta p10+1
        lda #>nh
        sta p3+1
        sta p7+1
        sta p11+1
        rts
init_end:
*=$6000
t0_start:
sl: !for i,0,510 { !byte <((i*i)/4 + BIAS*(i&1)) }
t0_end:
*=$6200
t1_start:
sh: !for i,0,510 { !byte >((i*i)/4 + BIAS*(i&1)) }
t1_end:
*=$6400
t2_start:
nl: !for i,0,510 { !byte (255-(<(((255-i)*(255-i))/4 + BIAS*((255-i)&1)))) }
t2_end:
*=$6600
t3_start:
nh: !for i,0,510 { !byte (255-(>(((255-i)*(255-i))/4 + BIAS*((255-i)&1)))) }
t3_end:
