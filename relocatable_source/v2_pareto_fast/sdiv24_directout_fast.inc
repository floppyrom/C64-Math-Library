; V2 direct-output size-fast-small SDIV24/SMOD24; selected to preserve always-visible resident geometry.
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
; ============================================================================
; FIREMONGER C64 DIVISION REFERENCE — PUBLICATION COPY
; Family       : sdiv24
; Tier         : size-fast-small
; Target       : NMOS 6502/6510, decimal mode clear
; Measurement  : canonical 2,097,152-case SplitMix64 corpus; seed $C0FFEE where random
; Timing       : entry instruction through final RTS; caller JSR excluded
; Avg cycles   : 187.626437
; Min / Max    : 94 / 2416
; Stddev       : 167.129105
; Resident     : 1497 bytes (Code 1497 + Data 0); ZP 21 bytes separate
; Validation   : 2097152 cases, 0 errors
; Edge suite   : 23336 cases in canonical run, 0 errors
; Architecture : q=0/q=±1 specialization over the 1.2 KB unsigned fast architecture.
;
; NOTE: this publication block is comments only and does not alter the exact
; assembled image that produced the result. Raw canonical JSON is supplied
; beside the source when available. See TECHNICAL_ASSESSMENT.md for caveats.
; ============================================================================

* = REG_TABLE+$2178
D24F_sg_code_start:
D24F_div_s24:
        ; Divisor magnitude. D24F_d2==0 is the only class that needs a low-word D24F_zero test.
        !byte $AF,<MATH_D+2,>MATH_D+2
        beq D24F_sd_high_zero
        bmi D24F_sd_negative
D24F_sd_positive:
        lda D24F_sdin0
        sta D24F_d0
        lda D24F_sdin1
        sta D24F_d1
        stx D24F_d2
        jmp D24F_sn_make
D24F_sd_high_zero:
        lda D24F_sdin0
        ora D24F_sdin1
        bne D24F_sd_low_nonzero
        jmp D24F_s_zero
D24F_sd_low_nonzero:
        lda D24F_sdin0
        sta D24F_d0
        lda D24F_sdin1
        sta D24F_d1
        stx D24F_d2
        jmp D24F_sn_make
D24F_sd_negative:
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
D24F_sn_make:
        !byte $AF,<MATH_N+2,>MATH_N+2
        bmi D24F_sn_negative
        lda D24F_sn0
        sta D24F_n0
        lda D24F_sn1
        sta D24F_n1
        stx D24F_n2
        jmp D24F_sq0_test
D24F_sn_negative:
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

D24F_sq0_test:
        !byte $a7,D24F_n2
        cmp D24F_d2
        bcc D24F_sqzero
        bne D24F_sfirst_sub
        lda D24F_n1
        cmp D24F_d1
        bcc D24F_sqzero
        bne D24F_sfirst_sub
        lda D24F_n0
        cmp D24F_d0
        bcc D24F_sqzero
D24F_sfirst_sub:
        lda D24F_n0
        sbc D24F_d0
        sta D24F_r0
        lda D24F_n1
        sbc D24F_d1
        sta D24F_r1
        txa
        sbc D24F_d2
        sta D24F_r2
        ; Is a second divisor still <= residual?
        cmp D24F_d2
        bcc D24F_sqone
        bne D24F_sqge2
        lda D24F_r1
        cmp D24F_d1
        bcc D24F_sqone
        bne D24F_sqge2
        lda D24F_r0
        cmp D24F_d0
        bcc D24F_sqone
D24F_sqge2:
        ; D24F_q1_sub_mem expects r=|n|-|d| and C=1. It performs the guaranteed
        ; second subtraction and continues directly through the q>=2 core.
        ldx #0
        stx D24F_q1
        stx D24F_q2
        jsr D24F_q1_sub_mem
        jmp D24F_s_sign_outputs

D24F_sqzero:
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

D24F_sqone:
        ; Sign remainder first, then emit +/-1 directly.
        lda D24F_sn2
        bpl D24F_sqone_r_done
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
D24F_sqone_r_done:
        lda D24F_sn2
        eor D24F_sdin2
        bmi D24F_sqone_neg
        lda #1
        sta D24F_q0
        lda #0
        sta D24F_q1
        sta D24F_q2
        clc
        rts
D24F_sqone_neg:
        lda #$ff
        sta D24F_q0
        sta D24F_q1
        sta D24F_q2
        clc
        rts

D24F_s_sign_outputs:
        lda D24F_sn2
        bpl D24F_sr_done
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
D24F_sr_done:
        lda D24F_sn2
        eor D24F_sdin2
        bpl D24F_s_success
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
D24F_s_success:
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

* = REG_TABLE+$22EE
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
 bcc D24F_tail3_prepare
 jmp D24F_state3
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
 sta D24F_r2
 jmp D24F_state4
D24F_state4:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state5
D24F_state5:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state6
D24F_state6:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state7
D24F_state7:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state8
D24F_state8:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state9
D24F_state9:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state10
D24F_state10:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state11
D24F_state11:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state12
D24F_state12:
 lda D24F_r2
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
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state13
D24F_state13:
 lda D24F_r2
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
 lda #13
 sta D24F_q0
 rts
D24F_sub13:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state14
D24F_state14:
 lda D24F_r2
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
 lda #14
 sta D24F_q0
 rts
D24F_sub14:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state15
D24F_state15:
 lda D24F_r2
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
 lda #15
 sta D24F_q0
 rts
D24F_sub15:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state16
D24F_state16:
 lda D24F_r2
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
 lda #16
 sta D24F_q0
 rts
D24F_sub16:
 lda D24F_r0
 sbc D24F_d0
 sta D24F_r0
 lda D24F_r1
 sbc D24F_d1
 sta D24F_r1
 lda D24F_r2
 sbc D24F_d2
 sta D24F_r2
 jmp D24F_state17
D24F_state17:
 lda D24F_r2
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
 lda #17
 sta D24F_q0
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
 sta D24F_r2
 jmp D24F_state18
D24F_state18:
 lda D24F_r2
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
 lda #18
 sta D24F_q0
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
 sta D24F_r2
 jmp D24F_state19
D24F_state19:
 lda #19
 sta D24F_q0
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
