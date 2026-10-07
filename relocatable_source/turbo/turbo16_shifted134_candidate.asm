; Research Turbo16 shifted-row 134-ZP candidate.
; Based on the validated shifted134 standalone kernel, with its two extra
; planes mapped to pages that are available only during exclusive Turbo mode.
; This file is not selected by the public lifecycle until the candidate gate wins.

sqr_lo=REG_TABLE+$1000
sqr_hi=REG_TABLE+$1200
neg_sqr_lo=REG_TABLE+$1400
neg_sqr_hi=REG_TABLE+$1600
sqr_hi_plus1=REG_TABLE+$0800
neg_sqr_lo_plus1=REG_TABLE+$0A00

* = TURBO16_ZP_BASE
T16X_zp_start:

T16X_umult:
        lda+1 T16X_x1
T16X_umult_ax1:
        sta+1 T16X_sqr_hi_1+1
        eor #$ff
        sta+1 T16X_neg_lo_1+1
        sta+1 T16X_neg_hi_1+1

        lda+1 T16X_x0
        sta+1 T16X_sqr_hi_0+1
        eor #$ff
        sta+1 T16X_neg_lo_0+1
        sta+1 T16X_neg_hi_0+1

T16X_umult_same_x:
        sec
T16X_umult_same_x_ready:

T16X_x0 = *+1
T16X_sqr_lo_0:
        lda sqr_lo,y
T16X_neg_lo_0:
        sbc neg_sqr_lo,y
        sta+1 T16X_z0
T16X_sqr_hi_0:
        lda sqr_hi_plus1,y
T16X_neg_hi_0:
        sbc neg_sqr_hi,y

T16X_x1 = *+1
T16X_sqr_lo_1:
        adc sqr_lo,y
        bcs T16X_p10_carry
T16X_neg_lo_1:
        sbc neg_sqr_lo_plus1,y
        tax
T16X_sqr_hi_1:
        lda sqr_hi,y
T16X_p10_tail:
T16X_neg_hi_1:
        sbc neg_sqr_hi,y
        sta+1 T16X_z2_part1+1

T16X_y1 = *+1
        ldy #0

        lda (T16X_neg_lo_0+1),y
        sbc (T16X_sqr_lo_0+1),y
        sta+1 T16X_z1_part2+1
        lda (T16X_neg_hi_0+1),y
        sbc (T16X_sqr_hi_0+1),y

        sbc (T16X_sqr_lo_1+1),y
        bcc T16X_p11_carry
T16X_p11_hot:
        adc (T16X_neg_lo_1+1),y
T16X_negative_mid_ready:
        sta+1 T16X_z2_part2+1
        lda (T16X_neg_hi_1+1),y
        sbc (T16X_sqr_hi_1+1),y

T16X_negative_high_ready:
        eor #$ff
        tay

        lda #$ff
T16X_z1_part2:
        !byte $cb, 0
T16X_z2_part1:
        lda #0
T16X_z2_part2:
        sbc #0
        bcs T16X_final_carry
        rts
T16X_final_carry:
        iny
        rts

T16X_p10_carry:
        clc
        sbc (T16X_neg_lo_1+1),y
        tax
        lda #1
        adc (T16X_sqr_hi_1+1),y
        sbc (T16X_neg_hi_1+1),y
        sta+1 T16X_z2_part1+1
        ldy+1 T16X_y1
        lda (T16X_neg_lo_0+1),y
        sbc (T16X_sqr_lo_0+1),y
        sta+1 T16X_z1_part2+1
        lda (T16X_neg_hi_0+1),y
        sbc (T16X_sqr_hi_0+1),y
        sbc (T16X_sqr_lo_1+1),y
        bcs T16X_p11_hot

T16X_p11_carry:
        sec
        adc (T16X_neg_lo_1+1),y
        sta+1 T16X_z2_part2+1
        lda #$fe
        sbc (T16X_sqr_hi_1+1),y
        adc (T16X_neg_hi_1+1),y
        bcc T16X_negative_high_ready

T16X_z0: !byte 0
T16X_zp_end:
