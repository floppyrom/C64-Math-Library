; Experimental stack-free Turbo32 signed composition.
; Base producer: C64-Math-Library Turbo32 135-ZP overlay, published native mean
; 614.275858 cycles, 0 persistent hardware-stack bytes.
; Signed composition derived from Repose OptiSearch and refined here.
!cpu 6510
TABLE_BIAS_AFTER_DIV = 0
RESULT_YX = 1
REG_LOW = $1000
TURBO32_ZP_BASE = $0a
sqr_lo = $7000
sqr_hi = $7200
neg_lo = $7400
neg_hi = $7600
summation = $1100

z00=TURBO32_ZP_BASE+$00
z10=TURBO32_ZP_BASE+$01
z20=TURBO32_ZP_BASE+$02
z30=TURBO32_ZP_BASE+$03
z01=TURBO32_ZP_BASE+$04
z11=TURBO32_ZP_BASE+$05
z21=TURBO32_ZP_BASE+$06
z31=TURBO32_ZP_BASE+$07
z02=TURBO32_ZP_BASE+$08
z12=TURBO32_ZP_BASE+$09
z22=TURBO32_ZP_BASE+$0a
z32=TURBO32_ZP_BASE+$0b
z03=TURBO32_ZP_BASE+$0c
z13=TURBO32_ZP_BASE+$0d
z23=TURBO32_ZP_BASE+$0e
z33=TURBO32_ZP_BASE+$0f
z14=TURBO32_ZP_BASE+$10
z24=TURBO32_ZP_BASE+$11
z34=TURBO32_ZP_BASE+$12
y0=TURBO32_ZP_BASE+$00
y1=TURBO32_ZP_BASE+$01
y2=TURBO32_ZP_BASE+$02
r0=TURBO32_ZP_BASE+$00
r1=TURBO32_ZP_BASE+$01
r2=TURBO32_ZP_BASE+$02
r3=TURBO32_ZP_BASE+$03
r7=TURBO32_ZP_BASE+$12

; ---------------------------------------------------------------------------
; Ordinary-RAM binder and rare carry helpers.  A=x0 at bind_ax0.
; ---------------------------------------------------------------------------
*=$1000
turbo32_bind_full:
        lda x0
turbo32_bind_ax0:
        sta SH0
        eor #$ff
        sta NL0
        sta NH0
        lda x1
        sta SH1
        eor #$ff
        sta NL1
        sta NH1
        lda x2
        sta SH2
        eor #$ff
        sta NL2
        sta NH2
        lda x3
        sta SH3
        eor #$ff
        sta NL3
        sta NH3
turbo32_same_x:
        ldx #4
        sec
        jmp umult32x8_same_x

helper_c3_over:
        inc z32
        bne helper_c3_done
        inc z33
        bne helper_c3_done
        inc r7
helper_c3_done:
        clc
        jmp L112F
helper_c4_over:
        inc z33
        bne helper_c4_done
        inc r7
helper_c4_done:
        jmp L1141

; ---------------------------------------------------------------------------
; Direct column summation, at the same +$0100 geometry as the library overlay.
; ---------------------------------------------------------------------------
*=$1100
summation:
        tay
        clc
        lda z01
        adc z10
        sta r1
        lda z20
        adc z11
        bcc L1110
        inx
        clc
L1110:
        adc z02
        sta r2
        lda z03
        adc z12
        bcc L1128
        iny
        cpx #1
        adc z30
        bcc L112F
        clc
        iny
        bne L112F
        jmp helper_c3_over
L1128:
        adc z30
        bcc L112D
        iny
L112D:
        cpx #1
L112F:
        adc z21
        sta r3
        tya
        ldx z14
        adc z13
        bcs L1168
        adc z31
        bcc L1142
        inx
        beq L1171
L1141:
        clc
L1142:
        adc z22
        tay
        txa
        adc z32
        bcs L1159
        adc z23
        tax
        lda z24
        adc z33
        bcs L1156
        rts
L1154:
        adc #0
L1156:
        inc r7
        rts
L1159:
        clc
        adc z23
        tax
        lda z24
        adc z33
        bcs L1154
        adc #1
        bcs L1156
        rts
L1168:
        inx
        clc
        adc z31
        bcc L1142
        inx
        bne L1141
L1171:
        jmp helper_c4_over

; ---------------------------------------------------------------------------
; 135-byte page-zero overlay: 19 row/result bytes + 116 bytes executable/data.
; ---------------------------------------------------------------------------
*=TURBO32_ZP_BASE
!byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
*=TURBO32_ZP_BASE+$13
cg_zp_code_start:
p1_carry:
        clc
        adc (NL1),y
        sta z01-1,x
        lda #1
        adc (SH1),y
        adc (NH1),y
        adc (SL2),y
        bcc p2_hot
p2_carry:
        clc
        adc (NL2),y
        sta z02-1,x
        lda #1
        adc (SH2),y
        adc (NH2),y
        adc (SL3),y
        bcc p3_hot
p3_carry:
        clc
        adc (NL3),y
        sta z03-1,x
        lda #1
        adc (SH3),y
        adc (NH3),y
        dex
        beq sum_trampoline
loop:
        sta z14-1,x
        ldy y0-1,x

umult32x8_same_x:
x0=*+1
        lda sqr_lo,y
NL0=*+1
        adc neg_lo,y
        sta z00-1,x
SH0=*+1
        lda sqr_hi,y
NH0=*+1
        adc neg_hi,y
x1=*+1
        adc sqr_lo,y
        bcs p1_carry
p1_hot:
NL1=*+1
        adc neg_lo,y
        sta z01-1,x
SH1=*+1
        lda sqr_hi,y
NH1=*+1
        adc neg_hi,y
x2=*+1
SL2=*+1
        adc sqr_lo,y
        bcs p2_carry
p2_hot:
NL2=*+1
        adc neg_lo,y
        sta z02-1,x
SH2=*+1
        lda sqr_hi,y
NH2=*+1
        adc neg_hi,y
x3=*+1
SL3=*+1
        adc sqr_lo,y
        bcs p3_carry
p3_hot:
NL3=*+1
        adc neg_lo,y
        sta z03-1,x
SH3=*+1
        lda sqr_hi,y
NH3=*+1
        adc neg_hi,y
        dex
        bne loop
sum_trampoline:
        jmp summation
cg_zp_end:

; ---------------------------------------------------------------------------
; Signed composition.  Same quadrant strategy as the 31-ZP candidate.
; ---------------------------------------------------------------------------
*=$1200
smul32_turbo_composed:
        bit x3
        bmi smul32_turbo_xneg
        cpy #$80
        bcs smul32_turbo_yneg_only
        jmp turbo32_bind_ax0

smul32_turbo_xneg:
        cpy #$80
        bcs smul32_turbo_nn
        ; Preserve aliased Y bytes with X as transfer register; A=x0/Y=y3 survive.
        ldx y0
        stx smul32_turbo_saved_y0+1
        ldx y1
        stx smul32_turbo_saved_y1+1
        ldx y2
        stx smul32_turbo_saved_y2+1
        sty smul32_turbo_saved_y3+1
        jsr turbo32_bind_ax0
        sta smul32_turbo_xneg_orig_a+1
        tya
        sec
smul32_turbo_saved_y0:
        sbc #0
        tay
        txa
smul32_turbo_saved_y1:
        sbc #0
        tax
smul32_turbo_xneg_orig_a:
        lda #0
smul32_turbo_saved_y2:
        sbc #0
        sta smul32_turbo_xneg_restore_a+1
        lda r7
smul32_turbo_saved_y3:
        sbc #0
        sta r7
smul32_turbo_xneg_restore_a:
        lda #0
        rts

smul32_turbo_yneg_only:
        jsr turbo32_bind_ax0
        sta smul32_turbo_yneg_orig_a+1
        tya
        sec
        sbc x0
        tay
        txa
        sbc x1
        tax
smul32_turbo_yneg_orig_a:
        lda #0
        sbc x2
        sta smul32_turbo_yneg_restore_a+1
        lda r7
        sbc x3
        sta r7
smul32_turbo_yneg_restore_a:
        lda #0
        rts

smul32_turbo_nn:
        ; x0 uses the carry left set by CPY #$80 on the NN branch.
        eor #$ff
        adc #0
        sta x0
        sta SH0
        eor #$ff
        sta NL0
        sta NH0
        lda #0
        sbc x1
        sta x1
        sta SH1
        eor #$ff
        sta NL1
        sta NH1
        lda #0
        sbc x2
        sta x2
        sta SH2
        eor #$ff
        sta NL2
        sta NH2
        lda #0
        sbc x3
        sta x3
        sta SH3
        eor #$ff
        sta NL3
        sta NH3

        sec
        lda #0
        sbc y0
        sta y0
        lda #0
        sbc y1
        sta y1
        lda #0
        sbc y2
        sta y2
        tya
        eor #$ff
        adc #0
        tay
        jmp turbo32_same_x
smul32_turbo_composed_end:

; ---------------------------------------------------------------------------
; Quarter-square planes used by the record family: bias after floor(i*i/4).
; ---------------------------------------------------------------------------
*=$7000
sqr_lo:
!for i,0,510 { !byte <((i*i)/4 + 202*(i&1)) }
!align 255,0,0
sqr_hi:
!for i,0,510 { !byte >((i*i)/4 + 202*(i&1)) }
!align 255,0,0
neg_lo:
!for i,0,510 { !byte 255-(<(((255-i)*(255-i))/4 + 202*((255-i)&1))) }
!align 255,0,0
neg_hi:
!for i,0,510 { !byte 255-(>(((255-i)*(255-i))/4 + 202*((255-i)&1))) }
