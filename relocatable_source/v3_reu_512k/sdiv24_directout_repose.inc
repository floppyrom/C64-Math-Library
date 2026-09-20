; Direct-output SDIV24/SMOD24 using Repose q0counter t13/k13, using the REU profiles' otherwise-free resident gap.
; Direct stable-memory signed ABI; executable-disjoint private magnitude engine.
; At most nine transient ZP bytes, all inside the common 31-byte window.
D24F_sn0 = MATH_N+0
D24F_sn1 = MATH_N+1
D24F_sn2 = MATH_N+2
D24F_sdin0 = MATH_D+0
D24F_sdin1 = MATH_D+1
D24F_sdin2 = MATH_D+2
D24F_q0 = MATH_Q+0
D24F_q1 = MATH_Q+1
D24F_q2 = MATH_Q+2
D24F_r0 = MATH_R+0
D24F_r1 = MATH_R+1
D24F_r2 = MATH_R+2
D24F_n0 = ZP_MAIN+$0E
D24F_n1 = ZP_MAIN+$0F
D24F_n2 = ZP_MAIN+$10
D24F_d0 = ZP_MAIN+$11
D24F_d1 = ZP_MAIN+$12
D24F_d2 = ZP_MAIN+$13
D24F_sd0 = ZP_MAIN+$14
D24F_sd1 = ZP_MAIN+$15
D24F_sd2 = ZP_MAIN+$16

* = MATH_SDIV24
    jmp D24F_div_s24
* = MATH_SMOD24
    jmp D24F_div_s24

; ============================================================================
; C64 DIVISION REFERENCE LIBRARY — AUTHORITATIVE RELEASE RECORD
; Family: sdiv24
; Tier: Fast
; CPU: NMOS 6502/6510 (C64 target)
; Timing: first entry instruction through final RTS; caller JSR excluded
; Canonical validation cases: 2097152
; Canonical validation errors: 0
; Edge cases: 23336
; Edge errors: 0
; Average cycles: 174.967714
; Minimum cycles: 64
; Maximum cycles: 2408
; Cycle standard deviation: 172.247202
; ZP bytes: 21
; Code bytes: 1876
; Data bytes: 0
; Resident bytes (Code+Data): 1876
; Validation note: 8-bit runs are exhaustive. Wider runs are complete fixed
; canonical 2^21 corpora plus complete generated edge suites; they are not
; exhaustive over the entire mathematical input space.
; This header supersedes any older tuning-result comments retained below.
; ============================================================================
;ABI
;CPU: mos6502
;Operation: sdiv
;Entry: D24F_div_s24
;Input n: int24 = D24F_sn0, D24F_sn1, D24F_sn2
;Input d: int24 = D24F_sdin0, D24F_sdin1, D24F_sdin2
;Output q: int24 = D24F_q0, D24F_q1, D24F_q2
;Remainder r: int24 = D24F_r0, D24F_r1, D24F_r2
;Region ZP: sg_zp_start..sg_zp_end, cg_zp_start..cg_zp_end
;Region Code: D24F_sg_code_start..D24F_sg_code_end, D24F_cg_code_start..D24F_cg_code_end
;End ABI
* = REG_KERNEL+$1A40
D24F_sg_code_start:
D24F_div_s24:
        lda D24F_sn2
        bpl D24F_s_npos_entry
        jmp D24F_s_nneg_dispatch
D24F_s_npos_entry:
        lda D24F_sdin2
        bpl D24F_s_case_pp
        jmp D24F_s_case_pn

D24F_s_case_pp:
        ; Positive divisor can be D24F_zero.  Decide q=0 on untouched signed bytes.
        lda D24F_sdin0
        ora D24F_sdin1
        ora D24F_sdin2
        bne D24F_s_pp_dnz
        jmp D24F_s_zero
D24F_s_pp_dnz:
        !byte $AF,<MATH_N+2,>MATH_N+2
        cmp D24F_sdin2
        bcs D24F_s_pp_hge
        jmp D24F_s_qzero
D24F_s_pp_hge:
        bne D24F_s_pp_ge
        lda D24F_sn1
        cmp D24F_sdin1
        bcs D24F_s_pp_mge
        jmp D24F_s_qzero
D24F_s_pp_mge:
        bne D24F_s_pp_ge
        lda D24F_sn0
        cmp D24F_sdin0
        bcs D24F_s_pp_ge
        jmp D24F_s_qzero
D24F_s_pp_ge:
        lda D24F_sn0
        sta D24F_n0
        lda D24F_sn1
        sta D24F_n1
        stx D24F_n2
        lda D24F_sdin0
        sta D24F_d0
        lda D24F_sdin1
        sta D24F_d1
        lda D24F_sdin2
        sta D24F_d2
        jmp D24F_s_mag_pp

D24F_s_case_pn:
        ; n positive, d negative: form only |d| before q=0 test.
        lda #0
        sec
        sbc D24F_sdin0
        sta D24F_d0
        lda #0
        sbc D24F_sdin1
        sta D24F_d1
        lda #0
        sbc D24F_sdin2
        sta D24F_d2
        !byte $AF,<MATH_N+2,>MATH_N+2
        cmp D24F_d2
        bcs D24F_s_pn_hge
        jmp D24F_s_qzero
D24F_s_pn_hge:
        bne D24F_s_pn_ge
        lda D24F_sn1
        cmp D24F_d1
        bcs D24F_s_pn_mge
        jmp D24F_s_qzero
D24F_s_pn_mge:
        bne D24F_s_pn_ge
        lda D24F_sn0
        cmp D24F_d0
        bcs D24F_s_pn_ge
        jmp D24F_s_qzero
D24F_s_pn_ge:
        lda D24F_sn0
        sta D24F_n0
        lda D24F_sn1
        sta D24F_n1
        stx D24F_n2
        jmp D24F_s_mag_pn

D24F_s_nneg_dispatch:
        lda D24F_sdin2
        bmi D24F_s_case_nn

D24F_s_case_np:
        ; n negative, d positive: D24F_zero-check d, then form only |n|.
        lda D24F_sdin0
        ora D24F_sdin1
        ora D24F_sdin2
        bne D24F_s_np_dnz
        jmp D24F_s_zero
D24F_s_np_dnz:
        lda #0
        sec
        sbc D24F_sn0
        sta D24F_n0
        lda #0
        sbc D24F_sn1
        sta D24F_n1
        lda #0
        sbc D24F_sn2
        sta D24F_n2
        !byte $a7,D24F_n2
        cmp D24F_sdin2
        bcs D24F_s_np_hge
        jmp D24F_s_qzero
D24F_s_np_hge:
        bne D24F_s_np_ge
        lda D24F_n1
        cmp D24F_sdin1
        bcs D24F_s_np_mge
        jmp D24F_s_qzero
D24F_s_np_mge:
        bne D24F_s_np_ge
        lda D24F_n0
        cmp D24F_sdin0
        bcs D24F_s_np_ge
        jmp D24F_s_qzero
D24F_s_np_ge:
        lda D24F_sdin0
        sta D24F_d0
        lda D24F_sdin1
        sta D24F_d1
        lda D24F_sdin2
        sta D24F_d2
        jmp D24F_s_mag_np

D24F_s_case_nn:
        ; Both negative: raw two's-complement ordering is reverse magnitude ordering.
        !byte $AF,<MATH_N+2,>MATH_N+2
        cmp D24F_sdin2
        bcc D24F_s_nn_ge
        beq D24F_s_nn_heq
        jmp D24F_s_qzero
D24F_s_nn_heq:
        lda D24F_sn1
        cmp D24F_sdin1
        bcc D24F_s_nn_ge
        beq D24F_s_nn_meq
        jmp D24F_s_qzero
D24F_s_nn_meq:
        lda D24F_sn0
        cmp D24F_sdin0
        bcc D24F_s_nn_ge
        beq D24F_s_nn_ge
        jmp D24F_s_qzero
D24F_s_nn_ge:
        lda #0
        sec
        sbc D24F_sn0
        sta D24F_n0
        lda #0
        sbc D24F_sn1
        sta D24F_n1
        lda #0
        sbc D24F_sn2
        sta D24F_n2
        lda #0
        sec
        sbc D24F_sdin0
        sta D24F_d0
        lda #0
        sbc D24F_sdin1
        sta D24F_d1
        lda #0
        sbc D24F_sdin2
        sta D24F_d2

        jmp D24F_s_mag_nn

D24F_s_mag_pp:
        sec
        lda D24F_n0
        sbc D24F_d0
        sta D24F_r0
        lda D24F_n1
        sbc D24F_d1
        sta D24F_r1
        lda D24F_n2
        sbc D24F_d2
        sta D24F_r2
        cmp D24F_d2
        bcc D24F_s_qone_pp
        bne D24F_s_qge2_pp
        lda D24F_r1
        cmp D24F_d1
        bcc D24F_s_qone_pp
        bne D24F_s_qge2_pp
        lda D24F_r0
        cmp D24F_d0
        bcs D24F_s_qge2_pp
D24F_s_qone_pp:
        lda #1
        sta D24F_q0
        lda #0
        sta D24F_q1
        sta D24F_q2
        clc
        rts
D24F_s_qge2_pp:
        ldx #0
        stx D24F_q1
        stx D24F_q2
        jsr D24F_q1_sub_mem
        jmp D24F_s_out_pp

D24F_s_mag_pn:
        sec
        lda D24F_n0
        sbc D24F_d0
        sta D24F_r0
        lda D24F_n1
        sbc D24F_d1
        sta D24F_r1
        lda D24F_n2
        sbc D24F_d2
        sta D24F_r2
        cmp D24F_d2
        bcc D24F_s_qone_pn
        bne D24F_s_qge2_pn
        lda D24F_r1
        cmp D24F_d1
        bcc D24F_s_qone_pn
        bne D24F_s_qge2_pn
        lda D24F_r0
        cmp D24F_d0
        bcs D24F_s_qge2_pn
D24F_s_qone_pn:
        lda #$ff
        sta D24F_q0
        sta D24F_q1
        sta D24F_q2
        clc
        rts
D24F_s_qge2_pn:
        ldx #0
        stx D24F_q1
        stx D24F_q2
        jsr D24F_q1_sub_mem
        jmp D24F_s_neg_q_out

D24F_s_mag_np:
        sec
        lda D24F_n0
        sbc D24F_d0
        sta D24F_r0
        lda D24F_n1
        sbc D24F_d1
        sta D24F_r1
        lda D24F_n2
        sbc D24F_d2
        sta D24F_r2
        cmp D24F_d2
        bcc D24F_s_qone_np
        bne D24F_s_qge2_np
        lda D24F_r1
        cmp D24F_d1
        bcc D24F_s_qone_np
        bne D24F_s_qge2_np
        lda D24F_r0
        cmp D24F_d0
        bcs D24F_s_qge2_np
D24F_s_qone_np:
        lda #0
        sec
        sbc D24F_r0
        sta D24F_r0
        lda #0
        sbc D24F_r1
        sta D24F_r1
        lda #0
        sbc D24F_r2
        sta D24F_r2
        lda #$ff
        sta D24F_q0
        sta D24F_q1
        sta D24F_q2
        clc
        rts
D24F_s_qge2_np:
        ldx #0
        stx D24F_q1
        stx D24F_q2
        jsr D24F_q1_sub_mem
        jmp D24F_s_neg_rq_out

D24F_s_mag_nn:
        sec
        lda D24F_n0
        sbc D24F_d0
        sta D24F_r0
        lda D24F_n1
        sbc D24F_d1
        sta D24F_r1
        lda D24F_n2
        sbc D24F_d2
        sta D24F_r2
        cmp D24F_d2
        bcc D24F_s_qone_nn
        bne D24F_s_qge2_nn
        lda D24F_r1
        cmp D24F_d1
        bcc D24F_s_qone_nn
        bne D24F_s_qge2_nn
        lda D24F_r0
        cmp D24F_d0
        bcs D24F_s_qge2_nn
D24F_s_qone_nn:
        lda #0
        sec
        sbc D24F_r0
        sta D24F_r0
        lda #0
        sbc D24F_r1
        sta D24F_r1
        lda #0
        sbc D24F_r2
        sta D24F_r2
        lda #1
        sta D24F_q0
        lda #0
        sta D24F_q1
        sta D24F_q2
        clc
        rts
D24F_s_qge2_nn:
        ldx #0
        stx D24F_q1
        stx D24F_q2
        jsr D24F_q1_sub_mem
        jmp D24F_s_neg_r_out

D24F_s_qzero:
        lda #0
        sta D24F_q0
        sta D24F_q1
        sta D24F_q2
        lda D24F_sn0
        sta D24F_r0
        lda D24F_sn1
        sta D24F_r1
        lda D24F_sn2
        sta D24F_r2
        clc
        rts

D24F_s_out_pp:
        clc
        rts
D24F_s_neg_rq_out:
        lda #0
        sec
        sbc D24F_r0
        sta D24F_r0
        lda #0
        sbc D24F_r1
        sta D24F_r1
        lda #0
        sbc D24F_r2
        sta D24F_r2
D24F_s_neg_q_out:
        lda #0
        sec
        sbc D24F_q0
        sta D24F_q0
        lda #0
        sbc D24F_q1
        sta D24F_q1
        lda #0
        sbc D24F_q2
        sta D24F_q2
        clc
        rts
D24F_s_neg_r_out:
        lda #0
        sec
        sbc D24F_r0
        sta D24F_r0
        lda #0
        sbc D24F_r1
        sta D24F_r1
        lda #0
        sbc D24F_r2
        sta D24F_r2
        clc
        rts
D24F_s_zero:
        lda #0
        sta D24F_q0
        sta D24F_q1
        sta D24F_q2
        sta D24F_r0
        sta D24F_r1
        sta D24F_r2
        sec
        rts
D24F_sg_code_end:

* = REG_TABLE+$2300
D24F_cg_code_start:
D24F_zero:
 lda #0
 ldx #5
D24F_zero_loop:
 sta D24F_q0,x
 dex
 bpl D24F_zero_loop
 sec
 rts
D24F_div_u24:
 !byte $a7,D24F_n2
 cmp D24F_d2
 bcc D24F_qzero
 beq D24F_high_equal
 lda D24F_d2
 beq D24F_low_d2
 jmp D24F_high_gt
D24F_high_equal:
 lda D24F_d2
 beq D24F_low_d2_equal
 lda D24F_n1
 cmp D24F_d1
 bcc D24F_qzero
 bne D24F_equal_ge
 lda D24F_n0
 cmp D24F_d0
 bcc D24F_qzero
D24F_equal_ge:
 lda D24F_n0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_n1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_n2
 sbc D24F_d2
 sta D24F_r2
 !byte $0b,$00
 sta D24F_q1
 sta D24F_q2
 lda #1
 sta D24F_q0
 rts
D24F_low_d2_equal:
 lda D24F_d0
 ora D24F_d1
 beq D24F_zero
 lda D24F_n1
 cmp D24F_d1
 bcc D24F_qzero
 bne D24F_low_tail0
 lda D24F_n0
 cmp D24F_d0
 bcc D24F_qzero
 bcs D24F_low_tail0
D24F_low_d2:
 lda D24F_d0
 ora D24F_d1
 beq D24F_zero
D24F_low_tail0:
 lda D24F_n0
 sta D24F_r0
 lda D24F_n1
 sta D24F_r1
 lda D24F_n2
 sta D24F_r2
 lda #0
 sta D24F_tail_bias+1
 jmp D24F_tail_setup
D24F_qzero:
 lda #0
 sta D24F_q0
 sta D24F_q1
 sta D24F_q2
 lda D24F_n0
 sta D24F_r0
 lda D24F_n1
 sta D24F_r1
 stx D24F_r2
 rts
D24F_high_gt:
 lda D24F_n0
 sec
 sbc D24F_d0
 sta D24F_r0
 lda D24F_n1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_n2
 sbc D24F_d2
 ldx #0
 stx D24F_q1
 stx D24F_q2
D24F_q1_test:
 cmp D24F_d2
 bcc D24F_q1_ret_live
 bne D24F_q1_sub_live
 sta D24F_r2
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_q1_ret_mem
 bne D24F_q1_sub_mem
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_q1_sub_mem
D24F_q1_ret_mem:
 lda #1
 sta D24F_q0
 rts
D24F_q1_ret_live:
 sta D24F_r2
 lda #1
 sta D24F_q0
 rts
D24F_q1_sub_live:
 sta D24F_r2
D24F_q1_sub_mem:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
D24F_q2_test:
 cmp D24F_d2
 bcc D24F_q2_ret_live
 bne D24F_q2_sub_live
 sta D24F_r2
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_q2_ret_mem
 bne D24F_q2_sub_mem
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_q2_sub_mem
D24F_q2_ret_mem:
 lda #2
 sta D24F_q0
 rts
D24F_q2_ret_live:
 sta D24F_r2
 lda #2
 sta D24F_q0
 rts
D24F_q2_sub_live:
 sta D24F_r2
D24F_q2_sub_mem:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 lda D24F_d2
 cmp #13
 bcs D24F_state3
D24F_tail3_prepare:
 lda #3
 sta D24F_tail_bias+1
 jmp D24F_tail_setup
D24F_state3:
 lda D24F_r2
 cmp D24F_d2
 bcc D24F_ret3
 bne D24F_sub3
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret3
 bne D24F_sub3
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub3
D24F_ret3:
 lda #3
 sta D24F_q0
 rts
D24F_sub3:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
D24F_state4:
 tax
 cmp D24F_d2
 bcc D24F_ret4
 bne D24F_sub4
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret4
 bne D24F_sub4
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub4
D24F_ret4:
 stx D24F_r2
 lda #4
 sta D24F_q0
 rts
D24F_sub4:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state5:
 tax
 cmp D24F_d2
 bcc D24F_ret5
 bne D24F_sub5
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret5
 bne D24F_sub5
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub5
D24F_ret5:
 stx D24F_r2
 lda #5
 sta D24F_q0
 rts
D24F_sub5:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state6:
 tax
 cmp D24F_d2
 bcc D24F_ret6
 bne D24F_sub6
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret6
 bne D24F_sub6
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub6
D24F_ret6:
 stx D24F_r2
 lda #6
 sta D24F_q0
 rts
D24F_sub6:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state7:
 tax
 cmp D24F_d2
 bcc D24F_ret7
 bne D24F_sub7
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret7
 bne D24F_sub7
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub7
D24F_ret7:
 stx D24F_r2
 lda #7
 sta D24F_q0
 rts
D24F_sub7:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state8:
 tax
 cmp D24F_d2
 bcc D24F_ret8
 bne D24F_sub8
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret8
 bne D24F_sub8
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub8
D24F_ret8:
 stx D24F_r2
 lda #8
 sta D24F_q0
 rts
D24F_sub8:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state9:
 tax
 cmp D24F_d2
 bcc D24F_ret9
 bne D24F_sub9
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret9
 bne D24F_sub9
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub9
D24F_ret9:
 stx D24F_r2
 lda #9
 sta D24F_q0
 rts
D24F_sub9:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state10:
 tax
 cmp D24F_d2
 bcc D24F_ret10
 bne D24F_sub10
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret10
 bne D24F_sub10
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub10
D24F_ret10:
 stx D24F_r2
 lda #10
 sta D24F_q0
 rts
D24F_sub10:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state11:
 tax
 cmp D24F_d2
 bcc D24F_ret11
 bne D24F_sub11
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret11
 bne D24F_sub11
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub11
D24F_ret11:
 stx D24F_r2
 lda #11
 sta D24F_q0
 rts
D24F_sub11:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
D24F_state12:
 tax
 cmp D24F_d2
 bcc D24F_ret12
 bne D24F_sub12
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret12
 bne D24F_sub12
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub12
D24F_ret12:
 stx D24F_r2
 lda #12
 sta D24F_q0
 rts
D24F_sub12:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
 ldx #13
 stx D24F_q0
D24F_state13:
 tax
 cmp D24F_d2
 bcc D24F_ret13
 bne D24F_sub13
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret13
 bne D24F_sub13
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub13
D24F_ret13:
 stx D24F_r2
 rts
D24F_sub13:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
 inc D24F_q0
D24F_state14:
 tax
 cmp D24F_d2
 bcc D24F_ret14
 bne D24F_sub14
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret14
 bne D24F_sub14
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub14
D24F_ret14:
 stx D24F_r2
 rts
D24F_sub14:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
 inc D24F_q0
D24F_state15:
 tax
 cmp D24F_d2
 bcc D24F_ret15
 bne D24F_sub15
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret15
 bne D24F_sub15
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub15
D24F_ret15:
 stx D24F_r2
 rts
D24F_sub15:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
 inc D24F_q0
D24F_state16:
 tax
 cmp D24F_d2
 bcc D24F_ret16
 bne D24F_sub16
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret16
 bne D24F_sub16
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub16
D24F_ret16:
 stx D24F_r2
 rts
D24F_sub16:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 txa
 sbc D24F_d2
 inc D24F_q0
D24F_state17:
 sta D24F_r2
 cmp D24F_d2
 bcc D24F_ret17
 bne D24F_sub17
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret17
 bne D24F_sub17
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub17
D24F_ret17:
 rts
D24F_sub17:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
 inc D24F_q0
D24F_state18:
 sta D24F_r2
 cmp D24F_d2
 bcc D24F_ret18
 bne D24F_sub18
 lda D24F_r1
 cmp D24F_d1
 bcc D24F_ret18
 bne D24F_sub18
 lda D24F_r0
 cmp D24F_d0
 bcs D24F_sub18
D24F_ret18:
 rts
D24F_sub18:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
 inc D24F_q0
D24F_state19:
 sta D24F_r2
 clc
 rts
D24F_tail_setup:
 lda D24F_d0
 sta D24F_sd0
 lda D24F_d1
 sta D24F_sd1
 lda D24F_d2
 sta D24F_sd2
 ldx #0
 stx D24F_q0
 stx D24F_q1
 stx D24F_q2
D24F_align:
 asl D24F_sd0
 rol D24F_sd1
 rol D24F_sd2
 bcs D24F_overshoot
 lda D24F_r2
 cmp D24F_sd2
 bcc D24F_overshoot
 bne D24F_align_take
 lda D24F_r1
 cmp D24F_sd1
 bcc D24F_overshoot
 bne D24F_align_take
 lda D24F_r0
 cmp D24F_sd0
 bcc D24F_overshoot
D24F_align_take:
 inx
 bne D24F_align
D24F_overshoot:
 ror D24F_sd2
 ror D24F_sd1
 ror D24F_sd0
D24F_bits:
 lda D24F_r2
 cmp D24F_sd2
 bcc D24F_no_sub
 bne D24F_do_sub
 lda D24F_r1
 cmp D24F_sd1
 bcc D24F_no_sub
 bne D24F_do_sub
 lda D24F_r0
 cmp D24F_sd0
 bcc D24F_no_sub
D24F_do_sub:
 lda D24F_r0
 sbc D24F_sd0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_sd1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_sd2
 sta D24F_r2
D24F_no_sub:
 rol D24F_q0
 rol D24F_q1
 rol D24F_q2
 lsr D24F_sd2
 ror D24F_sd1
 ror D24F_sd0
 dex
 bpl D24F_bits
 lda D24F_q0
 clc
D24F_tail_bias:
 adc #0
 sta D24F_q0
 bcc D24F_tail_done
 inc D24F_q1
 bne D24F_tail_clear
 inc D24F_q2
D24F_tail_clear:
 clc
D24F_tail_done:
 rts
D24F_cg_code_end:
