; UMUL32 refresh: private FAST31/V29 q0 producer for the unsigned public API.
; Shares immutable quarter-square tables and scratch storage with the signed family,
; but deliberately duplicates executable code so signed/unsigned API graphs remain disjoint.
!cpu 6510

*= REG_KERNEL+$1800
U32V29_q0_fast_core_start:
U32V29_q0_umult32x32_same_x:
        ldx #3
        sec
        bcs U32V29_q0_kernel

U32V29_q0_H10:
        clc
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda #1
        adc (S32V28_sqr_hi_1),y
        bcc U32V29_q0_p10_tail
U32V29_q0_H20:
        clc
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda #1
        adc (S32V28_sqr_hi_2),y
        bcc U32V29_q0_p20_tail
U32V29_q0_H30:
        clc
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda #1
        adc (S32V28_sqr_hi_3),y
        bcc U32V29_q0_p30_tail

U32V29_q0_row_loop:
        sta S32V28_z14,x
        ldy MATH_IO+$04,x

U32V29_q0_kernel:
U32V29_q0__sqr_lo_0:
        lda S32V28_sqr_lo,y
U32V29_q0__neg_lo_0:
        adc S32V28_neg_sqr_lo,y
        sta S32V28_z00,x
U32V29_q0__sqr_hi_0:
        lda S32V28_sqr_hi,y
U32V29_q0__neg_hi_0:
        adc S32V28_neg_sqr_hi,y

U32V29_q0__sqr_lo_1:
        adc S32V28_sqr_lo,y
        bcs U32V29_q0_H10
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda (S32V28_sqr_hi_1),y
U32V29_q0_p10_tail:
U32V29_q0__neg_hi_1:
        adc S32V28_neg_sqr_hi,y

U32V29_q0__sqr_lo_2:
        adc S32V28_sqr_lo,y
        bcs U32V29_q0_H20
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda (S32V28_sqr_hi_2),y
U32V29_q0_p20_tail:
U32V29_q0__neg_hi_2:
        adc S32V28_neg_sqr_hi,y

U32V29_q0__sqr_lo_3:
        adc S32V28_sqr_lo,y
        bcs U32V29_q0_H30
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda (S32V28_sqr_hi_3),y
U32V29_q0_p30_tail:
U32V29_q0__neg_hi_3:
        adc S32V28_neg_sqr_hi,y

        dex
        bpl U32V29_q0_row_loop

U32V29_q0_summation:
        tax
        ldy S32V28_z14
        clc

        lda S32V28_z01
        adc S32V28_z10
        sta MATH_IO+$09

        lda S32V28_z11
        adc S32V28_z20
        bcc U32V29_q0_c2a_done
        inc S32V28_z30
        beq U32V29_q0_c2a_overflow_tramp
        clc
U32V29_q0_c2a_done:
        adc S32V28_z02
        sta MATH_IO+$0A

        lda S32V28_z12
        adc S32V28_z03
        bcc U32V29_q0_c3a_done
        inx
        clc
U32V29_q0_c3a_done:
        adc S32V28_z30
        bcc U32V29_q0_c3b_done
        inx
        beq U32V29_q0_c3b_overflow_tramp
        clc
U32V29_q0_c3b_done:
        adc S32V28_z21
        sta MATH_IO+$0B

        txa
        adc S32V28_z13
        bcc U32V29_q0_c4a_done
        iny
        clc
U32V29_q0_c4a_done:
        adc S32V28_z31
        bcc U32V29_q0_c4b_done
        iny
        beq U32V29_q0_c4b_overflow
        clc
U32V29_q0_c4b_done:
        adc S32V28_z22
        sta MATH_IO+$0C

        tya
        adc S32V28_z32
        bcc U32V29_q0_c5a_done
        inc S32V28_z24
        clc
U32V29_q0_c5a_done:
        adc S32V28_z23
        sta MATH_IO+$0D

        lda S32V28_z33
        adc S32V28_z24
        sta MATH_IO+$0E
        lda S32V28_r7
        adc #0
        sta MATH_IO+$0F
        lda S32V28_r0
        sta MATH_IO+$08
        rts

U32V29_q0_c2a_overflow_tramp:
        jmp U32V29_q0_c2a_overflow
U32V29_q0_c3b_overflow_tramp:
        jmp U32V29_q0_c3b_overflow

U32V29_q0_c2a_overflow:
        inc S32V28_z31
        bne U32V29_q0_c2a_overflow_done
        inc S32V28_z32
        bne U32V29_q0_c2a_overflow_done
        inc S32V28_z33
        bne U32V29_q0_c2a_overflow_done
        inc S32V28_z34
U32V29_q0_c2a_overflow_done:
        clc
        jmp U32V29_q0_c2a_done

U32V29_q0_c3b_overflow:
        inc S32V28_z32
        bne U32V29_q0_c3b_overflow_done
        inc S32V28_z33
        bne U32V29_q0_c3b_overflow_done
        inc S32V28_z34
U32V29_q0_c3b_overflow_done:
        clc
        jmp U32V29_q0_c3b_done
U32V29_q0_c4b_overflow:
        inc S32V28_z33
        bne U32V29_q0_c4b_overflow_done
        inc S32V28_z34
U32V29_q0_c4b_overflow_done:
        clc
        jmp U32V29_q0_c4b_done
U32V29_q0_cg_code_end:

*= REG_KERNEL+$1900
U32V29_safe_entry:
        lda #>S32V28_neg_sqr_lo
        sta S32V28_neg_lo_1+1
        sta S32V28_neg_lo_2+1
        sta S32V28_neg_lo_3+1
        lda #>S32V28_sqr_hi
        sta S32V28_sqr_hi_1+1
        sta S32V28_sqr_hi_2+1
        sta S32V28_sqr_hi_3+1
U32V29_ready_body:
        lda MATH_IO+$03
        ldx #3
        sec
        ldy MATH_IO+$07
U32V29_bind_q0:
        sta S32V28_x3
        sta U32V29_q0__sqr_lo_3+1
        eor #$ff
        sta S32V28_neg_lo_3
        sta U32V29_q0__neg_hi_3+1
        lda MATH_IO
        sta U32V29_q0__sqr_lo_0+1
        sta U32V29_q0__sqr_hi_0+1
        eor #$ff
        sta U32V29_q0__neg_lo_0+1
        sta U32V29_q0__neg_hi_0+1
        lda MATH_IO+$01
        sta S32V28_x1
        sta U32V29_q0__sqr_lo_1+1
        eor #$ff
        sta S32V28_neg_lo_1
        sta U32V29_q0__neg_hi_1+1
        lda MATH_IO+$02
        sta S32V28_x2
        sta U32V29_q0__sqr_lo_2+1
        eor #$ff
        sta S32V28_neg_lo_2
        sta U32V29_q0__neg_hi_2+1
        jmp U32V29_q0_kernel

*= MATH_UMUL32
U32V29_public:
        jmp U32V29_safe_entry

*= MATH_UMUL32_READY
U32V29_ready_public:
        jmp U32V29_ready_body
