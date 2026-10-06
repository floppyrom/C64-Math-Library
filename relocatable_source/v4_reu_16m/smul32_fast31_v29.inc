; SMUL32 FAST31 V29 — canonical compact-placement integration of V28 arithmetic
; 31 ZP, 0 persistent stack. Speed-first signed 32x32 -> 64.
; Canonical overlay: leaves the shared resident UMUL32 producer at $3800 intact.
; MATH_SMUL32_READY is redirected to FAST31 below; MATH_SMUL32_SHR16 already
; calls MATH_SMUL32 and therefore inherits FAST31 automatically.
;
; Required external symbols: REG_LOW, REG_API, REG_KERNEL, REG_TABLE, REG_GAME,
; ZP_MAIN, MATH_IO. All code origins are region-relative and preserve the
; validated low-byte phase under the reference and alternate maps.
; Table planes are shared with resident UMUL32 and are not emitted here.
!cpu 6510

S32V28_sqr_lo      = REG_TABLE+$1000
S32V28_sqr_hi      = REG_TABLE+$1200
S32V28_neg_sqr_lo  = REG_TABLE+$1400
S32V28_neg_sqr_hi  = REG_TABLE+$1600

; Exact 31-byte FAST31 footprint, split across the profile-owned ZP map.
; Every pointer LOW byte is rebound from the operand on every call.  Only the
; six HIGH bytes must persist across mixed calls, so the pairs deliberately
; straddle already-owned bytes and otherwise-unused high-byte holes.
; Reference map highs: $3E,$40,$42,$50,$52,$69 (all outside other stable paths).
S32V28_neg_lo_1 = ZP_MAIN+$3B   ; ref $3D-$3E
S32V28_sqr_hi_1 = ZP_MAIN+$3D   ; ref $3F-$40
S32V28_neg_lo_2 = ZP_MAIN+$3F   ; ref $41-$42
S32V28_sqr_hi_2 = ZP_MAIN+$4D   ; ref $4F-$50
S32V28_neg_lo_3 = ZP_MAIN+$4F   ; ref $51-$52
S32V28_sqr_hi_3 = ZP_MAIN+$66   ; ref $68-$69
S32V28_z00 = ZP_MAIN+$0C
S32V28_z10 = ZP_MAIN+$0D
S32V28_z20 = ZP_MAIN+$0E
S32V28_z30 = ZP_MAIN+$0F
S32V28_z02 = ZP_MAIN+$10
S32V28_z12 = ZP_MAIN+$11
S32V28_z22 = ZP_MAIN+$12
S32V28_z32 = ZP_MAIN+$13
S32V28_z03 = ZP_MAIN+$14
S32V28_z13 = ZP_MAIN+$15
S32V28_z23 = ZP_MAIN+$16
S32V28_z33 = ZP_MAIN+$17
S32V28_z14 = ZP_MAIN+$18
S32V28_z24 = ZP_MAIN+$19
S32V28_z34 = ZP_MAIN+$1A
S32V28_z01 = ZP_MAIN+$1B
S32V28_z11 = ZP_MAIN+$1C
S32V28_z21 = ZP_MAIN+$1D
S32V28_z31 = ZP_MAIN+$1E
S32V28_x1 = S32V28_sqr_hi_1
S32V28_x2 = S32V28_sqr_hi_2
S32V28_x3 = S32V28_sqr_hi_3
S32V28_y0 = S32V28_z00
S32V28_y1 = S32V28_z10
S32V28_y2 = S32V28_z20
S32V28_r0 = S32V28_z00
S32V28_r1 = S32V28_z10
S32V28_r2 = S32V28_z20
S32V28_r3 = S32V28_z30
S32V28_r7 = S32V28_z34

*= REG_KERNEL+$1132
S32V28_fast_base_core_start:
S32V28_umult32x32_same_x:
        ldx #3
        sec
        bcs S32V28_kernel

S32V28_H10:
        clc
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda #1
        adc (S32V28_sqr_hi_1),y
        bcc S32V28_p10_tail
S32V28_H20:
        clc
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda #1
        adc (S32V28_sqr_hi_2),y
        bcc S32V28_p20_tail
S32V28_H30:
        clc
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda #1
        adc (S32V28_sqr_hi_3),y
        bcc S32V28_p30_tail

S32V28_row_loop:
        sta S32V28_z14,x
        ldy S32V28_y0,x

S32V28_kernel:
S32V28__sqr_lo_0:
        lda S32V28_sqr_lo,y
S32V28__neg_lo_0:
        adc S32V28_neg_sqr_lo,y
        sta S32V28_z00,x
S32V28__sqr_hi_0:
        lda S32V28_sqr_hi,y
S32V28__neg_hi_0:
        adc S32V28_neg_sqr_hi,y

S32V28__sqr_lo_1:
        adc S32V28_sqr_lo,y
        bcs S32V28_H10
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda (S32V28_sqr_hi_1),y
S32V28_p10_tail:
S32V28__neg_hi_1:
        adc S32V28_neg_sqr_hi,y

S32V28__sqr_lo_2:
        adc S32V28_sqr_lo,y
        bcs S32V28_H20
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda (S32V28_sqr_hi_2),y
S32V28_p20_tail:
S32V28__neg_hi_2:
        adc S32V28_neg_sqr_hi,y

S32V28__sqr_lo_3:
        adc S32V28_sqr_lo,y
        bcs S32V28_H30
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda (S32V28_sqr_hi_3),y
S32V28_p30_tail:
S32V28__neg_hi_3:
        adc S32V28_neg_sqr_hi,y

        dex
        bpl S32V28_row_loop

S32V28_summation:
        tax
        ldy S32V28_z14
        clc

        lda S32V28_z01
        adc S32V28_z10
        sta MATH_IO+$09

        lda S32V28_z11
        adc S32V28_z20
        bcc S32V28_c2a_done
        inc S32V28_z30
        beq S32V28_c2a_overflow
        clc
S32V28_c2a_done:
        adc S32V28_z02
        sta MATH_IO+$0A

        lda S32V28_z12
        adc S32V28_z03
        bcc S32V28_c3a_done
        inx
        clc
S32V28_c3a_done:
        adc S32V28_z30
        bcc S32V28_c3b_done
        inx
        ; NN feeds |X| <= $80000000 to the producer.  X entered summation as
        ; row0 byte4=floor(|X|*y0/2^32) <= $7f; two carry increments cannot wrap.
        clc
S32V28_c3b_done:
        adc S32V28_z21
        sta MATH_IO+$0B

        txa
        adc S32V28_z13
        bcs S32V28_c4a_carry
S32V28_c4a_done:
        adc S32V28_z31
        bcc S32V28_c4b_done
        iny
        ; z14 is row1 byte4 with the same <= $7f bound; the second increment
        ; therefore cannot wrap in the NN-only base producer.
        clc
S32V28_c4b_done:
        adc S32V28_z22
        sta MATH_IO+$0C

        tya
        adc S32V28_z32
        bcs S32V28_c5a_carry
S32V28_c5a_done:
        adc S32V28_z23
        sta MATH_IO+$0D

        lda S32V28_z33
        adc S32V28_z24
        ; FAST31 base producer is private to NN. Materialize the byte6 carry
        ; directly into result byte7, avoiding BCC/INC and the later reload.
        sta MATH_IO+$0E
        lda S32V28_r7
        adc #0
        sta MATH_IO+$0F
        lda S32V28_r0
        sta MATH_IO+$08
        rts

S32V28_c4a_carry:
        iny
        clc
        jmp S32V28_c4a_done

S32V28_c5a_carry:
        inc S32V28_z24
        clc
        jmp S32V28_c5a_done

S32V28_c2a_overflow:
        inc S32V28_z31
        bne S32V28_c2a_overflow_done
        inc S32V28_z32
        bne S32V28_c2a_overflow_done
        inc S32V28_z33
        bne S32V28_c2a_overflow_done
        inc S32V28_z34
S32V28_c2a_overflow_done:
        clc
        jmp S32V28_c2a_done

S32V28_c3b_overflow:
        inc S32V28_z32
        bne S32V28_c3b_overflow_done
        inc S32V28_z33
        bne S32V28_c3b_overflow_done
        inc S32V28_z34
S32V28_c3b_overflow_done:
        clc
        jmp S32V28_c3b_done
S32V28_c4b_overflow:
        inc S32V28_z33
        bne S32V28_c4b_overflow_done
        inc S32V28_z34
S32V28_c4b_overflow_done:
        clc
        jmp S32V28_c4b_done
S32V28_cg_code_end:
; MATH_INIT installs all six pointer high bytes; five now persist in profile-owned ZP holes.
*= REG_KERNEL+$1500
S32V28_q2_fast_core_start:
S32V28_q2_umult32x32_same_x:
        ldx #3
        sec
        bcs S32V28_q2_kernel

S32V28_q2_H10:
        clc
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda #1
        adc (S32V28_sqr_hi_1),y
        bcc S32V28_q2_p10_tail
S32V28_q2_H20:
        clc
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda #1
        adc (S32V28_sqr_hi_2),y
        bcc S32V28_q2_p20_tail
S32V28_q2_H30:
        clc
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda #1
        adc (S32V28_sqr_hi_3),y
        bcc S32V28_q2_p30_tail

S32V28_q2_row_loop:
        sta S32V28_z14,x
        ldy MATH_IO+$04,x

S32V28_q2_kernel:
S32V28_q2__sqr_lo_0:
        lda S32V28_sqr_lo,y
S32V28_q2__neg_lo_0:
        adc S32V28_neg_sqr_lo,y
        sta S32V28_z00,x
S32V28_q2__sqr_hi_0:
        lda S32V28_sqr_hi,y
S32V28_q2__neg_hi_0:
        adc S32V28_neg_sqr_hi,y

S32V28_q2__sqr_lo_1:
        adc S32V28_sqr_lo,y
        bcs S32V28_q2_H10
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda (S32V28_sqr_hi_1),y
S32V28_q2_p10_tail:
S32V28_q2__neg_hi_1:
        adc S32V28_neg_sqr_hi,y

S32V28_q2__sqr_lo_2:
        adc S32V28_sqr_lo,y
        bcs S32V28_q2_H20
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda (S32V28_sqr_hi_2),y
S32V28_q2_p20_tail:
S32V28_q2__neg_hi_2:
        adc S32V28_neg_sqr_hi,y

S32V28_q2__sqr_lo_3:
        adc S32V28_sqr_lo,y
        bcs S32V28_q2_H30
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda (S32V28_sqr_hi_3),y
S32V28_q2_p30_tail:
S32V28_q2__neg_hi_3:
        adc S32V28_neg_sqr_hi,y

        dex
        bpl S32V28_q2_row_loop

S32V28_q2_summation:
        ; Bounded-carry transplant from the validated compact126/UMUL32 family.
        ; FAST31 exits the descending producer with X=$FF and the row-0 top byte
        ; in A; INX/TAY converts that to the compact summation invariant X=0,Y=A.
        inx
        tay
        clc

        lda S32V28_z01
        adc S32V28_z10
        sta MATH_IO+$09

        lda S32V28_z20
        adc S32V28_z11
        bcc S32V28_q2_hy_c2_first_done
        inx
        clc
S32V28_q2_hy_c2_first_done:
        adc S32V28_z02
        sta MATH_IO+$0A

        lda S32V28_z03
        adc S32V28_z12
        bcc S32V28_q2_hy_c3_path0
        iny
        cpx #1
        adc S32V28_z30
        bcc S32V28_q2_hy_c3_done
        clc
        iny
        bne S32V28_q2_hy_c3_done
        jmp S32V28_q2_hy_c3_over_imp
S32V28_q2_hy_c3_path0:
        adc S32V28_z30
        bcc S32V28_q2_hy_c3_path0_noinc
        iny
S32V28_q2_hy_c3_path0_noinc:
        cpx #1
S32V28_q2_hy_c3_done:
        adc S32V28_z21
        sta MATH_IO+$0B

        tya
        adc S32V28_z22
        bcs S32V28_q2_bc_c4a_k1
        adc S32V28_z31
        bcs S32V28_q2_bc_c4b_k1
S32V28_q2_bc_c4_k0_common:
        adc S32V28_z13
        tay
        lda S32V28_z14
        adc S32V28_z32
        bcs S32V28_q2_bc_c5b_k1_m0
        adc S32V28_z23
        tax
        lda S32V28_z24
        adc S32V28_z33
        bcc S32V28_q2_signed_correction_ready
S32V28_q2_bc_final_carry:
        inc S32V28_r7
S32V28_q2_signed_correction_ready:
        ; Bounded summation returns raw upper bytes as Y,X,A,r7.
        sta S32V28_z33
        tya
        sec
        sbc MATH_IO+$04
        sta MATH_IO+$0C
        txa
        sbc MATH_IO+$05
        sta MATH_IO+$0D
        lda S32V28_z33
        sbc MATH_IO+$06
        sta MATH_IO+$0E
        lda S32V28_r7
        sbc MATH_IO+$07
        sta MATH_IO+$0F
        lda S32V28_r0
        sta MATH_IO+$08
        clc
        rts

S32V28_q2_bc_c5b_k1_m0:
        clc
S32V28_q2_bc_c5b_k1_m1:
        adc S32V28_z23
        tax
        lda S32V28_z24
        adc S32V28_z33
        bcs S32V28_q2_bc_c6_done
        adc #1
        bcs S32V28_q2_bc_final_carry
        ; Carry is clear on BCS fallthrough: same 3 cycles as JMP, one byte shorter.
        ; Pulling the later helper back by one byte removes a hot page-cross branch.
        bcc S32V28_q2_signed_correction_ready
S32V28_q2_bc_c6_done:
        adc #0
        jmp S32V28_q2_bc_final_carry
S32V28_q2_bc_c4a_k1:
        clc
        adc S32V28_z31
        bcc S32V28_q2_bc_c4b_one_clear
S32V28_q2_bc_c4b_k2:
        inc S32V28_z14
S32V28_q2_bc_c4b_k1:
        clc
S32V28_q2_bc_c4b_one_clear:
        adc S32V28_z13
        tay
        lda S32V28_z14
        adc S32V28_z32
        bcs S32V28_q2_bc_c5b_k1_m1
S32V28_q2_bc_c5b_k0_m1_alt:
        sec
S32V28_q2_bc_c5b_k0_m0_alt:
        adc S32V28_z23
        tax
        lda S32V28_z24
        adc S32V28_z33
        bcs S32V28_q2_bc_final_carry
        jmp S32V28_q2_signed_correction_ready

S32V28_q2_hy_c3_over_imp:
        inc S32V28_z32
        bne S32V28_q2_hy_c3_over_done
        inc S32V28_z33
        bne S32V28_q2_hy_c3_over_done
        inc S32V28_r7
S32V28_q2_hy_c3_over_done:
        clc
        jmp S32V28_q2_hy_c3_done
S32V28_q2_cg_code_end:

*= REG_API+$0500
S32V28_q0_fast_core_start:
S32V28_q0_umult32x32_same_x:
        ldx #3
        sec
        bcs S32V28_q0_kernel

S32V28_q0_H10:
        clc
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda #1
        adc (S32V28_sqr_hi_1),y
        bcc S32V28_q0_p10_tail
S32V28_q0_H20:
        clc
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda #1
        adc (S32V28_sqr_hi_2),y
        bcc S32V28_q0_p20_tail
S32V28_q0_H30:
        clc
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda #1
        adc (S32V28_sqr_hi_3),y
        bcc S32V28_q0_p30_tail

S32V28_q0_row_loop:
        sta S32V28_z14,x
        ldy MATH_IO+$04,x

S32V28_q0_kernel:
S32V28_q0__sqr_lo_0:
        lda S32V28_sqr_lo,y
S32V28_q0__neg_lo_0:
        adc S32V28_neg_sqr_lo,y
        sta S32V28_z00,x
S32V28_q0__sqr_hi_0:
        lda S32V28_sqr_hi,y
S32V28_q0__neg_hi_0:
        adc S32V28_neg_sqr_hi,y

S32V28_q0__sqr_lo_1:
        adc S32V28_sqr_lo,y
        bcs S32V28_q0_H10
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda (S32V28_sqr_hi_1),y
S32V28_q0_p10_tail:
S32V28_q0__neg_hi_1:
        adc S32V28_neg_sqr_hi,y

S32V28_q0__sqr_lo_2:
        adc S32V28_sqr_lo,y
        bcs S32V28_q0_H20
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda (S32V28_sqr_hi_2),y
S32V28_q0_p20_tail:
S32V28_q0__neg_hi_2:
        adc S32V28_neg_sqr_hi,y

S32V28_q0__sqr_lo_3:
        adc S32V28_sqr_lo,y
        bcs S32V28_q0_H30
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda (S32V28_sqr_hi_3),y
S32V28_q0_p30_tail:
S32V28_q0__neg_hi_3:
        adc S32V28_neg_sqr_hi,y

        dex
        bpl S32V28_q0_row_loop

S32V28_q0_summation:
        tax
        ldy S32V28_z14
        clc

        lda S32V28_z01
        adc S32V28_z10
        sta MATH_IO+$09

        lda S32V28_z11
        adc S32V28_z20
        bcc S32V28_q0_c2a_done
        inc S32V28_z30
        beq S32V28_q0_c2a_overflow_tramp
        clc
S32V28_q0_c2a_done:
        adc S32V28_z02
        sta MATH_IO+$0A

        lda S32V28_z12
        adc S32V28_z03
        bcc S32V28_q0_c3a_done
        inx
        clc
S32V28_q0_c3a_done:
        adc S32V28_z30
        bcc S32V28_q0_c3b_done
        inx
        ; q0 has X < $80000000, so row0 byte4 <= $7f and cannot wrap here.
        clc
S32V28_q0_c3b_done:
        adc S32V28_z21
        sta MATH_IO+$0B

        txa
        adc S32V28_z13
        bcs S32V28_q0_c4a_carry
S32V28_q0_c4a_done:
        adc S32V28_z31
        bcc S32V28_q0_c4b_done
        iny
        ; z14 is row1 byte4 <= $7f for q0, so this second increment cannot wrap.
        clc
S32V28_q0_c4b_done:
        adc S32V28_z22
        sta MATH_IO+$0C

        tya
        adc S32V28_z32
        bcs S32V28_q0_c5a_carry
S32V28_q0_c5a_done:
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

S32V28_q0_c4a_carry:
        iny
        clc
        jmp S32V28_q0_c4a_done

S32V28_q0_c5a_carry:
        inc S32V28_z24
        clc
        jmp S32V28_q0_c5a_done

S32V28_q0_c2a_overflow_tramp:
        jmp S32V28_q0_c2a_overflow
S32V28_q0_c3b_overflow_tramp:
        jmp S32V28_q0_c3b_overflow

S32V28_q0_c2a_overflow:
        inc S32V28_z31
        bne S32V28_q0_c2a_overflow_done
        inc S32V28_z32
        bne S32V28_q0_c2a_overflow_done
        inc S32V28_z33
        bne S32V28_q0_c2a_overflow_done
        inc S32V28_z34
S32V28_q0_c2a_overflow_done:
        clc
        jmp S32V28_q0_c2a_done

S32V28_q0_c3b_overflow:
        inc S32V28_z32
        bne S32V28_q0_c3b_overflow_done
        inc S32V28_z33
        bne S32V28_q0_c3b_overflow_done
        inc S32V28_z34
S32V28_q0_c3b_overflow_done:
        clc
        jmp S32V28_q0_c3b_done
S32V28_q0_c4b_overflow:
        inc S32V28_z33
        bne S32V28_q0_c4b_overflow_done
        inc S32V28_z34
S32V28_q0_c4b_overflow_done:
        clc
        jmp S32V28_q0_c4b_done
S32V28_q0_cg_code_end:
*= REG_TABLE+$0C41
S32V28_api_s31_v25_xcarry:
        ; Rare x0==0 path. Branches here preserve C=1 from the low-byte negate.
        lda #0
        sbc MATH_IO+$01
        sta S32V28_x1
        sta S32V28__sqr_lo_1+1
        eor #$ff
        sta S32V28_neg_lo_1
        sta S32V28__neg_hi_1+1
        lda #0
        sbc MATH_IO+$02
        sta S32V28_x2
        sta S32V28__sqr_lo_2+1
        eor #$ff
        sta S32V28_neg_lo_2
        sta S32V28__neg_hi_2+1
        lda #0
        sbc MATH_IO+$03
        sta S32V28_x3
        sta S32V28__sqr_lo_3+1
        eor #$ff
        sta S32V28_neg_lo_3
        sta S32V28__neg_hi_3+1
        jmp S32V28_api_s31_v25_xdone


*= REG_KERNEL+$067C
S32V28_q1_fast_core_start:
S32V28_q1_umult32x32_same_x:
        ldx #3
        sec
        bcs S32V28_q1_kernel

S32V28_q1_H10:
        clc
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda #1
        adc (S32V28_sqr_hi_1),y
        bcc S32V28_q1_p10_tail
S32V28_q1_H20:
        clc
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda #1
        adc (S32V28_sqr_hi_2),y
        bcc S32V28_q1_p20_tail
S32V28_q1_H30:
        clc
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda #1
        adc (S32V28_sqr_hi_3),y
        bcc S32V28_q1_p30_tail

S32V28_q1_row_loop:
        sta S32V28_z14,x
        ldy MATH_IO+$04,x

S32V28_q1_kernel:
S32V28_q1__sqr_lo_0:
        lda S32V28_sqr_lo,y
S32V28_q1__neg_lo_0:
        adc S32V28_neg_sqr_lo,y
        sta S32V28_z00,x
S32V28_q1__sqr_hi_0:
        lda S32V28_sqr_hi,y
S32V28_q1__neg_hi_0:
        adc S32V28_neg_sqr_hi,y

S32V28_q1__sqr_lo_1:
        adc S32V28_sqr_lo,y
        bcs S32V28_q1_H10
        adc (S32V28_neg_lo_1),y
        sta S32V28_z01,x
        lda (S32V28_sqr_hi_1),y
S32V28_q1_p10_tail:
S32V28_q1__neg_hi_1:
        adc S32V28_neg_sqr_hi,y

S32V28_q1__sqr_lo_2:
        adc S32V28_sqr_lo,y
        bcs S32V28_q1_H20
        adc (S32V28_neg_lo_2),y
        sta S32V28_z02,x
        lda (S32V28_sqr_hi_2),y
S32V28_q1_p20_tail:
S32V28_q1__neg_hi_2:
        adc S32V28_neg_sqr_hi,y

S32V28_q1__sqr_lo_3:
        adc S32V28_sqr_lo,y
        bcs S32V28_q1_H30
        adc (S32V28_neg_lo_3),y
        sta S32V28_z03,x
        lda (S32V28_sqr_hi_3),y
S32V28_q1_p30_tail:
S32V28_q1__neg_hi_3:
        adc S32V28_neg_sqr_hi,y

        dex
        bpl S32V28_q1_row_loop

S32V28_q1_summation:
        tax
        ldy S32V28_z14
        clc

        lda S32V28_z01
        adc S32V28_z10
        sta MATH_IO+$09

        lda S32V28_z11
        adc S32V28_z20
        bcc S32V28_q1_c2a_done
        inc S32V28_z30
        beq S32V28_q1_c2a_overflow_tramp
        clc
S32V28_q1_c2a_done:
        adc S32V28_z02
        sta MATH_IO+$0A

        lda S32V28_z12
        adc S32V28_z03
        bcc S32V28_q1_c3a_done
        inx
        clc
S32V28_q1_c3a_done:
        adc S32V28_z30
        bcc S32V28_q1_c3b_done
        inx
        ; q1 also has X < $80000000; row0 byte4 <= $7f, so no wrap is possible.
        clc
S32V28_q1_c3b_done:
        adc S32V28_z21
        sta MATH_IO+$0B

        txa
        adc S32V28_z13
        bcs S32V28_q1_c4a_carry
S32V28_q1_c4a_done:
        adc S32V28_z31
        bcc S32V28_q1_c4b_done
        iny
        ; z14 is row1 byte4 <= $7f for q1, so the second increment cannot wrap.
        clc
S32V28_q1_c4b_done:
        adc S32V28_z22
        tax

        tya
        adc S32V28_z32
        bcs S32V28_q1_c5a_carry
S32V28_q1_c5a_done:
        adc S32V28_z23
        tay

        lda S32V28_z33
        adc S32V28_z24
        bcs S32V28_q1_final_carry
S32V28_q1_signed_correction_ready:
        sta S32V28_z33
        txa
        sec
        sbc MATH_IO
        sta MATH_IO+$0C
        tya
        sbc S32V28_x1
        sta MATH_IO+$0D
        lda S32V28_z33
        sbc S32V28_x2
        sta MATH_IO+$0E
        lda S32V28_r7
        sbc S32V28_x3
        sta MATH_IO+$0F
        lda S32V28_r0
        sta MATH_IO+$08
        clc
        rts

S32V28_q1_c4a_carry:
        iny
        clc
        jmp S32V28_q1_c4a_done

S32V28_q1_c5a_carry:
        inc S32V28_z24
        clc
        jmp S32V28_q1_c5a_done

S32V28_q1_final_carry:
        inc S32V28_r7
        jmp S32V28_q1_signed_correction_ready

S32V28_q1_c2a_overflow_tramp:
        jmp S32V28_q1_c2a_overflow
S32V28_q1_c3b_overflow_tramp:
        jmp S32V28_q1_c3b_overflow

S32V28_q1_c2a_overflow:
        inc S32V28_z31
        bne S32V28_q1_c2a_overflow_done
        inc S32V28_z32
        bne S32V28_q1_c2a_overflow_done
        inc S32V28_z33
        bne S32V28_q1_c2a_overflow_done
        inc S32V28_z34
S32V28_q1_c2a_overflow_done:
        clc
        jmp S32V28_q1_c2a_done

S32V28_q1_c3b_overflow:
        inc S32V28_z32
        bne S32V28_q1_c3b_overflow_done
        inc S32V28_z33
        bne S32V28_q1_c3b_overflow_done
        inc S32V28_z34
S32V28_q1_c3b_overflow_done:
        clc
        jmp S32V28_q1_c3b_done
S32V28_q1_c4b_overflow:
        inc S32V28_z33
        bne S32V28_q1_c4b_overflow_done
        inc S32V28_z34
S32V28_q1_c4b_overflow_done:
        clc
        jmp S32V28_q1_c4b_done
S32V28_q1_cg_code_end:

*= REG_TABLE+$0C00
S32V28_api_s31_v25_bind_q2:
        sta S32V28_x3
        sta S32V28_q2__sqr_lo_3+1
        eor #$ff
        sta S32V28_neg_lo_3
        sta S32V28_q2__neg_hi_3+1
        lda MATH_IO
        sta S32V28_q2__sqr_lo_0+1
        sta S32V28_q2__sqr_hi_0+1
        eor #$ff
        sta S32V28_q2__neg_lo_0+1
        sta S32V28_q2__neg_hi_0+1
        lda MATH_IO+$01
        sta S32V28_x1
        sta S32V28_q2__sqr_lo_1+1
        eor #$ff
        sta S32V28_neg_lo_1
        sta S32V28_q2__neg_hi_1+1
        lda MATH_IO+$02
        sta S32V28_x2
        sta S32V28_q2__sqr_lo_2+1
        eor #$ff
        sta S32V28_neg_lo_2
        sta S32V28_q2__neg_hi_2+1
        ldx #3
        sec
        jmp S32V28_q2_kernel

*= REG_API+$0C00
S32V28_api_s31_v25_bind_q1:
        sta S32V28_x3
        sta S32V28_q1__sqr_lo_3+1
        eor #$ff
        sta S32V28_neg_lo_3
        sta S32V28_q1__neg_hi_3+1
        lda MATH_IO
        sta S32V28_q1__sqr_lo_0+1
        sta S32V28_q1__sqr_hi_0+1
        eor #$ff
        sta S32V28_q1__neg_lo_0+1
        sta S32V28_q1__neg_hi_0+1
        lda MATH_IO+$01
        sta S32V28_x1
        sta S32V28_q1__sqr_lo_1+1
        eor #$ff
        sta S32V28_neg_lo_1
        sta S32V28_q1__neg_hi_1+1
        lda MATH_IO+$02
        sta S32V28_x2
        sta S32V28_q1__sqr_lo_2+1
        eor #$ff
        sta S32V28_neg_lo_2
        sta S32V28_q1__neg_hi_2+1
        jmp S32V28_q1_kernel
; Compatibility label retained in the old binder island.  All six pointer
; high bytes now persist in profile-owned ZP, so no mixed-call repair remains.
*= REG_GAME_API+$01C8
S32V29_safe_entry:
        jmp S32V28_api_smul32_speed31_v26

*= REG_API+$0C40
; Stable public entry now falls directly into the dispatcher.  The old
; self-JMP cost 3 cycles on every ordinary SMUL32/SHR16 call.
SMUL32_FAST31_V29_ENTRY:
S32V28_api_smul32_speed31_v26:
        lda MATH_IO+$03
        bpl S32V28_api_s31_v26_xpos
        ldy MATH_IO+$07
        bmi S32V28_api_s31_v25_nn
        jmp S32V28_api_s31_v25_bind_q2

S32V28_api_s31_v26_xpos:
        ldx #3
        sec
        ldy MATH_IO+$07
        bmi S32V28_api_s31_v25_bind_q1
S32V28_api_s31_v25_bind_q0:
        sta S32V28_x3
        sta S32V28_q0__sqr_lo_3+1
        eor #$ff
        sta S32V28_neg_lo_3
        sta S32V28_q0__neg_hi_3+1
        lda MATH_IO
        sta S32V28_q0__sqr_lo_0+1
        sta S32V28_q0__sqr_hi_0+1
        eor #$ff
        sta S32V28_q0__neg_lo_0+1
        sta S32V28_q0__neg_hi_0+1
        lda MATH_IO+$01
        sta S32V28_x1
        sta S32V28_q0__sqr_lo_1+1
        eor #$ff
        sta S32V28_neg_lo_1
        sta S32V28_q0__neg_hi_1+1
        lda MATH_IO+$02
        sta S32V28_x2
        sta S32V28_q0__sqr_lo_2+1
        eor #$ff
        sta S32V28_neg_lo_2
        sta S32V28_q0__neg_hi_2+1
        jmp S32V28_q0_kernel

*= REG_API+$0CA3
S32V28_api_s31_v25_nn_xcarry_tramp:
        jmp S32V28_api_s31_v25_xcarry

*= REG_API+$0CA6
S32V28_api_s31_v25_nn:
        ; BMI does not set carry; seed the two's-complement chain explicitly.
        sec
        lda #0
        sbc MATH_IO
        sta S32V28__sqr_lo_0+1
        sta S32V28__sqr_hi_0+1
        eor #$ff
        sta S32V28__neg_lo_0+1
        sta S32V28__neg_hi_0+1
        ; Common case: x0!=0, so C is permanently clear. High |X| bytes are
        ; just ~X and their negative bindings are the original X bytes.
        bcs S32V28_api_s31_v25_nn_xcarry_tramp
        lda MATH_IO+$01
        sta S32V28_neg_lo_1
        sta S32V28__neg_hi_1+1
        eor #$ff
        sta S32V28_x1
        sta S32V28__sqr_lo_1+1
        lda MATH_IO+$02
        sta S32V28_neg_lo_2
        sta S32V28__neg_hi_2+1
        eor #$ff
        sta S32V28_x2
        sta S32V28__sqr_lo_2+1
        lda MATH_IO+$03
        sta S32V28_neg_lo_3
        sta S32V28__neg_hi_3+1
        eor #$ff
        sta S32V28_x3
        sta S32V28__sqr_lo_3+1
S32V28_api_s31_v25_xdone:
        sec
        lda #0
        sbc MATH_IO+$04
        sta S32V28_y0
        lda #0
        sbc MATH_IO+$05
        sta S32V28_y1
        lda #0
        sbc MATH_IO+$06
        sta S32V28_y2
        lda #0
        sbc MATH_IO+$07
        tay
        ldx #3
        sec
        jmp S32V28_kernel



; Stable READY API redirect. Existing V2 documentation keeps the initialized-state
; requirement; FAST31 uses the same MATH_INIT-installed table-pointer high bytes.
*=REG_API+$0FE0
S32V29_ready_redirect:
        jmp S32V28_api_smul32_speed31_v26
