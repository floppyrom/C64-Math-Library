; Build-time relocatable Turbo16 zero-page overlay.
; Arithmetic body derived from the validated Firemonger Turbo16 source retained
; in the complete developer archive. Runtime relocation is not used.

sqr_lo=REG_TABLE+$1000
sqr_hi=REG_TABLE+$1200
neg_sqr_lo=REG_TABLE+$1400
neg_sqr_hi=REG_TABLE+$1600

* = TURBO16_ZP_BASE
cg_zp_start:

; Main entry: x0/x1 are aliases to the two sqr_lo operand bytes below.
umult:
        lda+1 x1
umult_ax1:
        sta+1 _sqr_hi_1+1
        eor #$ff
        sta+1 _neg_lo_1+1
        sta+1 _neg_hi_1+1

        lda+1 x0
        sta+1 _sqr_hi_0+1
        eor #$ff
        sta+1 _neg_lo_0+1
        sta+1 _neg_hi_0+1

; Repeated-X entry. Caller supplies Y=y0; main entry falls through.
umult_same_x:
        sec
; Fully ready entry. Caller additionally supplies C=1.
umult_same_x_ready:

x0 = *+1
_sqr_lo_0:
        lda sqr_lo,y
_neg_lo_0:
        adc neg_sqr_lo,y
        sta+1 z0
_sqr_hi_0:
        lda sqr_hi,y
_neg_hi_0:
        adc neg_sqr_hi,y

x1 = *+1
_sqr_lo_1:
        adc sqr_lo,y
        bcs _p10_carry
_neg_lo_1:
        adc neg_sqr_lo,y
        tax
        lda (_sqr_hi_1+1),y
_p10_tail:
_neg_hi_1:
        adc neg_sqr_hi,y
        sta+1 _z2_part1+1

y1 = *+1
        ldy #0

        lda (_sqr_lo_0+1),y
        adc (_neg_lo_0+1),y
        sta+1 _z1_part2+1
        lda (_sqr_hi_0+1),y
        adc (_neg_hi_0+1),y

        adc (_sqr_lo_1+1),y
        bcs _p11_carry
        adc (_neg_lo_1+1),y
        sta+1 _z2_part2+1
_sqr_hi_1:
        lda sqr_hi,y
_p11_tail:
        adc (_neg_hi_1+1),y
        tay

        clc
        txa
_z1_part2:
        adc #0
        tax
_z2_part1:
        lda #0
_z2_part2:
        adc #0
        bcs _final_carry
        rts
_final_carry:
        iny
        rts

_p10_carry:
        clc
        adc (_neg_lo_1+1),y
        tax
        lda #1
        adc (_sqr_hi_1+1),y
        bcc _p10_tail              ; provably taken; one byte below JMP

_p11_carry:
        clc
        adc (_neg_lo_1+1),y
        sta+1 _z2_part2+1
        lda #1
        adc (_sqr_hi_1+1),y
        bcc _p11_tail              ; provably taken; one byte below JMP

z0:    !byte 0
