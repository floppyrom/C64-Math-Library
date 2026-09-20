; Direct UDIV24/UMOD24 using Repose q0counter t13/k13.
; Direct stable-memory ABI: inputs remain in MATH_N/MATH_D and q/r are written directly.
; NMOS 6510 target; decimal mode must be clear.
* = MATH_UDIV24
    jmp DU24F_div_u24
* = MATH_UMOD24
    jmp DU24F_div_u24

* = REG_KERNEL+$0800
DU24F_cg_code_start:
DU24F_zero:
 lda #0
 sta MATH_Q+0
 sta MATH_Q+1
 sta MATH_Q+2
 sta MATH_R+0
 sta MATH_R+1
 sta MATH_R+2
 sec
 rts
DU24F_div_u24:
        !byte $AF,<MATH_N+2,>MATH_N+2 ; LAX abs
 cmp MATH_D+2
 bcs DU24F___relax_0
 jmp DU24F_qzero
DU24F___relax_0:
 beq DU24F_high_equal
 lda MATH_D+2
 beq DU24F_low_d2
 jmp DU24F_high_gt
DU24F_high_equal:
 lda MATH_D+2
 beq DU24F_low_d2_equal
 lda MATH_N+1
 cmp MATH_D+1
 bcc DU24F_qzero
 bne DU24F_equal_ge
 lda MATH_N+0
 cmp MATH_D+0
 bcc DU24F_qzero
DU24F_equal_ge:
 lda MATH_N+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_N+1
 sbc MATH_D+1
 sta MATH_R+1
 lda MATH_N+2
 sbc MATH_D+2
 sta MATH_R+2
 !byte $0b,$00
 sta MATH_Q+1
 sta MATH_Q+2
 lda #1
 sta MATH_Q+0
 rts
DU24F_low_d2_equal:
 lda MATH_D+0
 ora MATH_D+1
 bne DU24F___relax_1
 jmp DU24F_zero
DU24F___relax_1:
 lda MATH_N+1
 cmp MATH_D+1
 bcc DU24F_qzero
 bne DU24F_low_tail0
 lda MATH_N+0
 cmp MATH_D+0
 bcc DU24F_qzero
 bcs DU24F_low_tail0
DU24F_low_d2:
 lda MATH_D+0
 ora MATH_D+1
 bne DU24F___relax_2
 jmp DU24F_zero
DU24F___relax_2:
DU24F_low_tail0:
 lda MATH_N+0
 sta MATH_R+0
 lda MATH_N+1
 sta MATH_R+1
 lda MATH_N+2
 sta MATH_R+2
 lda #0
 sta DU24F_tail_bias+1
 jmp DU24F_tail_setup
DU24F_qzero:
 lda #0
 sta MATH_Q+0
 sta MATH_Q+1
 sta MATH_Q+2
 lda MATH_N+0
 sta MATH_R+0
 lda MATH_N+1
 sta MATH_R+1
 stx MATH_R+2
 rts
DU24F_high_gt:
 lda MATH_N+0
 sec
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_N+1
 sbc MATH_D+1
 sta MATH_R+1
 lda MATH_N+2
 sbc MATH_D+2
 ldx #0
 stx MATH_Q+1
 stx MATH_Q+2
DU24F_q1_test:
 cmp MATH_D+2
 bcc DU24F_q1_ret_live
 bne DU24F_q1_sub_live
 sta MATH_R+2
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_q1_ret_mem
 bne DU24F_q1_sub_mem
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_q1_sub_mem
DU24F_q1_ret_mem:
 lda #1
 sta MATH_Q+0
 rts
DU24F_q1_ret_live:
 sta MATH_R+2
 lda #1
 sta MATH_Q+0
 rts
DU24F_q1_sub_live:
 sta MATH_R+2
DU24F_q1_sub_mem:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 lda MATH_R+2
 sbc MATH_D+2
DU24F_q2_test:
 cmp MATH_D+2
 bcc DU24F_q2_ret_live
 bne DU24F_q2_sub_live
 sta MATH_R+2
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_q2_ret_mem
 bne DU24F_q2_sub_mem
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_q2_sub_mem
DU24F_q2_ret_mem:
 lda #2
 sta MATH_Q+0
 rts
DU24F_q2_ret_live:
 sta MATH_R+2
 lda #2
 sta MATH_Q+0
 rts
DU24F_q2_sub_live:
 sta MATH_R+2
DU24F_q2_sub_mem:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 lda MATH_R+2
 sbc MATH_D+2
 sta MATH_R+2
 lda MATH_D+2
 cmp #13
 bcs DU24F_state3
DU24F_tail3_prepare:
 lda #3
 sta DU24F_tail_bias+1
 jmp DU24F_tail_setup
DU24F_state3:
 lda MATH_R+2
 cmp MATH_D+2
 bcc DU24F_ret3
 bne DU24F_sub3
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret3
 bne DU24F_sub3
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub3
DU24F_ret3:
 lda #3
 sta MATH_Q+0
 rts
DU24F_sub3:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 lda MATH_R+2
 sbc MATH_D+2
DU24F_state4:
 tax
 cmp MATH_D+2
 bcc DU24F_ret4
 bne DU24F_sub4
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret4
 bne DU24F_sub4
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub4
DU24F_ret4:
 stx MATH_R+2
 lda #4
 sta MATH_Q+0
 rts
DU24F_sub4:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state5:
 tax
 cmp MATH_D+2
 bcc DU24F_ret5
 bne DU24F_sub5
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret5
 bne DU24F_sub5
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub5
DU24F_ret5:
 stx MATH_R+2
 lda #5
 sta MATH_Q+0
 rts
DU24F_sub5:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state6:
 tax
 cmp MATH_D+2
 bcc DU24F_ret6
 bne DU24F_sub6
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret6
 bne DU24F_sub6
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub6
DU24F_ret6:
 stx MATH_R+2
 lda #6
 sta MATH_Q+0
 rts
DU24F_sub6:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state7:
 tax
 cmp MATH_D+2
 bcc DU24F_ret7
 bne DU24F_sub7
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret7
 bne DU24F_sub7
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub7
DU24F_ret7:
 stx MATH_R+2
 lda #7
 sta MATH_Q+0
 rts
DU24F_sub7:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state8:
 tax
 cmp MATH_D+2
 bcc DU24F_ret8
 bne DU24F_sub8
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret8
 bne DU24F_sub8
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub8
DU24F_ret8:
 stx MATH_R+2
 lda #8
 sta MATH_Q+0
 rts
DU24F_sub8:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state9:
 tax
 cmp MATH_D+2
 bcc DU24F_ret9
 bne DU24F_sub9
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret9
 bne DU24F_sub9
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub9
DU24F_ret9:
 stx MATH_R+2
 lda #9
 sta MATH_Q+0
 rts
DU24F_sub9:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state10:
 tax
 cmp MATH_D+2
 bcc DU24F_ret10
 bne DU24F_sub10
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret10
 bne DU24F_sub10
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub10
DU24F_ret10:
 stx MATH_R+2
 lda #10
 sta MATH_Q+0
 rts
DU24F_sub10:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state11:
 tax
 cmp MATH_D+2
 bcc DU24F_ret11
 bne DU24F_sub11
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret11
 bne DU24F_sub11
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub11
DU24F_ret11:
 stx MATH_R+2
 lda #11
 sta MATH_Q+0
 rts
DU24F_sub11:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
DU24F_state12:
 tax
 cmp MATH_D+2
 bcc DU24F_ret12
 bne DU24F_sub12
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret12
 bne DU24F_sub12
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub12
DU24F_ret12:
 stx MATH_R+2
 lda #12
 sta MATH_Q+0
 rts
DU24F_sub12:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
 ldx #13
 stx MATH_Q+0
DU24F_state13:
 tax
 cmp MATH_D+2
 bcc DU24F_ret13
 bne DU24F_sub13
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret13
 bne DU24F_sub13
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub13
DU24F_ret13:
 stx MATH_R+2
 rts
DU24F_sub13:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
 inc MATH_Q+0
DU24F_state14:
 tax
 cmp MATH_D+2
 bcc DU24F_ret14
 bne DU24F_sub14
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret14
 bne DU24F_sub14
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub14
DU24F_ret14:
 stx MATH_R+2
 rts
DU24F_sub14:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
 inc MATH_Q+0
DU24F_state15:
 tax
 cmp MATH_D+2
 bcc DU24F_ret15
 bne DU24F_sub15
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret15
 bne DU24F_sub15
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub15
DU24F_ret15:
 stx MATH_R+2
 rts
DU24F_sub15:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
 inc MATH_Q+0
DU24F_state16:
 tax
 cmp MATH_D+2
 bcc DU24F_ret16
 bne DU24F_sub16
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret16
 bne DU24F_sub16
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub16
DU24F_ret16:
 stx MATH_R+2
 rts
DU24F_sub16:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 txa
 sbc MATH_D+2
 inc MATH_Q+0
DU24F_state17:
 sta MATH_R+2
 cmp MATH_D+2
 bcc DU24F_ret17
 bne DU24F_sub17
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret17
 bne DU24F_sub17
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub17
DU24F_ret17:
 rts
DU24F_sub17:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 lda MATH_R+2
 sbc MATH_D+2
 inc MATH_Q+0
        jmp DU24F_state18

* = REG_KERNEL+$12DE
DU24F_state18:
 sta MATH_R+2
 cmp MATH_D+2
 bcc DU24F_ret18
 bne DU24F_sub18
 lda MATH_R+1
 cmp MATH_D+1
 bcc DU24F_ret18
 bne DU24F_sub18
 lda MATH_R+0
 cmp MATH_D+0
 bcs DU24F_sub18
DU24F_ret18:
 rts
DU24F_sub18:
 lda MATH_R+0
 sbc MATH_D+0
 sta MATH_R+0
 lda MATH_R+1
 sbc MATH_D+1
 sta MATH_R+1
 lda MATH_R+2
 sbc MATH_D+2
 inc MATH_Q+0
DU24F_state19:
 sta MATH_R+2
 clc
 rts
DU24F_tail_setup:
 lda MATH_D+0
 sta ZP_MAIN+$0E
 lda MATH_D+1
 sta ZP_MAIN+$0F
 lda MATH_D+2
 sta ZP_MAIN+$10
 ldx #0
 stx MATH_Q+0
 stx MATH_Q+1
 stx MATH_Q+2
DU24F_align:
 asl ZP_MAIN+$0E
 rol ZP_MAIN+$0F
 rol ZP_MAIN+$10
 bcs DU24F_overshoot
 lda MATH_R+2
 cmp ZP_MAIN+$10
 bcc DU24F_overshoot
 bne DU24F_align_take
 lda MATH_R+1
 cmp ZP_MAIN+$0F
 bcc DU24F_overshoot
 bne DU24F_align_take
 lda MATH_R+0
 cmp ZP_MAIN+$0E
 bcc DU24F_overshoot
DU24F_align_take:
 inx
 bne DU24F_align
DU24F_overshoot:
 ror ZP_MAIN+$10
 ror ZP_MAIN+$0F
 ror ZP_MAIN+$0E
DU24F_bits:
 lda MATH_R+2
 cmp ZP_MAIN+$10
 bcc DU24F_no_sub
 bne DU24F_do_sub
 lda MATH_R+1
 cmp ZP_MAIN+$0F
 bcc DU24F_no_sub
 bne DU24F_do_sub
 lda MATH_R+0
 cmp ZP_MAIN+$0E
 bcc DU24F_no_sub
DU24F_do_sub:
 lda MATH_R+0
 sbc ZP_MAIN+$0E
 sta MATH_R+0
 lda MATH_R+1
 sbc ZP_MAIN+$0F
 sta MATH_R+1
 lda MATH_R+2
 sbc ZP_MAIN+$10
 sta MATH_R+2
DU24F_no_sub:
 rol MATH_Q+0
 rol MATH_Q+1
 rol MATH_Q+2
 lsr ZP_MAIN+$10
 ror ZP_MAIN+$0F
 ror ZP_MAIN+$0E
 dex
 bpl DU24F_bits
 lda MATH_Q+0
 clc
DU24F_tail_bias:
 adc #0
 sta MATH_Q+0
 bcc DU24F_tail_done
 inc MATH_Q+1
 bne DU24F_tail_clear
 inc MATH_Q+2
DU24F_tail_clear:
 clc
DU24F_tail_done:
 rts
DU24F_cg_code_end:
