; Historical V2 direct Repose 24/24 DIV/MOD, relocated from canonical source.
; Original: relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc
; Preserves the complete original 1244+217-byte executable source;
; public fixed-address JMP stubs are removed. Two public aliases share one entry.
; Uses 3 ZP bytes and writable source: DU24F_tail_bias+1 is self-modified.
; Does not require tables, REU, or initialization. CLD required.
!cpu 6510
KERNEL_CODE = $8000
KERNEL_AUX = $84DC
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_ZP = $90
* = KERNEL_CODE
DU24F_cg_code_start:
DU24F_zero:
 lda #0
 sta OUTPUT_QUOT+0
 sta OUTPUT_QUOT+1
 sta OUTPUT_QUOT+2
 sta OUTPUT_REM+0
 sta OUTPUT_REM+1
 sta OUTPUT_REM+2
 sec
 rts
DU24F_div_u24:
        lax INPUT_NUM+2
 cmp INPUT_DIV+2
 bcs DU24F___relax_0
 jmp DU24F_qzero
DU24F___relax_0:
 beq DU24F_high_equal
 lda INPUT_DIV+2
 beq DU24F_low_d2
 jmp DU24F_high_gt
DU24F_high_equal:
 txa  ; X=N2=D2 proved by preceding CMP+BEQ; saves 2 cycles
 beq DU24F_low_d2_equal
 lda INPUT_NUM+1
 cmp INPUT_DIV+1
 bcc DU24F_qzero
 bne DU24F_equal_ge
 lda INPUT_NUM+0
 cmp INPUT_DIV+0
 bcc DU24F_qzero
DU24F_equal_ge:
 lda INPUT_NUM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda INPUT_NUM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 lda INPUT_NUM+2
 sbc INPUT_DIV+2
 sta OUTPUT_REM+2
 anc #0
 sta OUTPUT_QUOT+1
 sta OUTPUT_QUOT+2
 lda #1
 sta OUTPUT_QUOT+0
 rts
DU24F_low_d2_equal:
 lda INPUT_DIV+0
 ora INPUT_DIV+1
 bne DU24F___relax_1
 jmp DU24F_zero
DU24F___relax_1:
 lda INPUT_NUM+1
 cmp INPUT_DIV+1
 bcc DU24F_qzero
 bne DU24F_low_tail0
 lda INPUT_NUM+0
 cmp INPUT_DIV+0
 bcc DU24F_qzero
 bcs DU24F_low_tail0
DU24F_low_d2:
 lda INPUT_DIV+0
 ora INPUT_DIV+1
 bne DU24F___relax_2
 jmp DU24F_zero
DU24F___relax_2:
DU24F_low_tail0:
 lda INPUT_NUM+0
 sta OUTPUT_REM+0
 lda INPUT_NUM+1
 sta OUTPUT_REM+1
 lda INPUT_NUM+2
 sta OUTPUT_REM+2
 lda #0
 sta DU24F_tail_bias+1
 jmp DU24F_tail_setup
DU24F_qzero:
 lda #0
 sta OUTPUT_QUOT+0
 sta OUTPUT_QUOT+1
 sta OUTPUT_QUOT+2
 lda INPUT_NUM+0
 sta OUTPUT_REM+0
 lda INPUT_NUM+1
 sta OUTPUT_REM+1
 stx OUTPUT_REM+2
 rts
DU24F_high_gt:
 lda INPUT_NUM+0
 sec
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda INPUT_NUM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
 ldx #0
 stx OUTPUT_QUOT+1
 stx OUTPUT_QUOT+2
DU24F_q1_test:
 cmp INPUT_DIV+2
 bcc DU24F_q1_ret_live
 bne DU24F_q1_sub_live
 sta OUTPUT_REM+2
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_q1_ret_mem
 bne DU24F_q1_sub_mem
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_q1_sub_mem
DU24F_q1_ret_mem:
 lda #1
 sta OUTPUT_QUOT+0
 rts
DU24F_q1_ret_live:
 sta OUTPUT_REM+2
 lda #1
 sta OUTPUT_QUOT+0
 rts
DU24F_q1_sub_live:
 sta OUTPUT_REM+2
DU24F_q1_sub_mem:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 lda OUTPUT_REM+2
 sbc INPUT_DIV+2
DU24F_q2_test:
 cmp INPUT_DIV+2
 bcc DU24F_q2_ret_live
 bne DU24F_q2_sub_live
 sta OUTPUT_REM+2
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_q2_ret_mem
 bne DU24F_q2_sub_mem
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_q2_sub_mem
DU24F_q2_ret_mem:
 lda #2
 sta OUTPUT_QUOT+0
 rts
DU24F_q2_ret_live:
 sta OUTPUT_REM+2
 lda #2
 sta OUTPUT_QUOT+0
 rts
DU24F_q2_sub_live:
 sta OUTPUT_REM+2
DU24F_q2_sub_mem:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 lda OUTPUT_REM+2
 sbc INPUT_DIV+2
 sta OUTPUT_REM+2
 lda INPUT_DIV+2
 cmp #13
 bcs DU24F_state3
DU24F_tail3_prepare:
 lda #3
 sta DU24F_tail_bias+1
 jmp DU24F_tail_setup
DU24F_state3:
 lda OUTPUT_REM+2
 cmp INPUT_DIV+2
 bcc DU24F_ret3
 bne DU24F_sub3
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret3
 bne DU24F_sub3
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub3
DU24F_ret3:
 lda #3
 sta OUTPUT_QUOT+0
 rts
DU24F_sub3:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 lda OUTPUT_REM+2
 sbc INPUT_DIV+2
DU24F_state4:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret4
 bne DU24F_sub4
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret4
 bne DU24F_sub4
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub4
DU24F_ret4:
 stx OUTPUT_REM+2
 lda #4
 sta OUTPUT_QUOT+0
 rts
DU24F_sub4:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state5:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret5
 bne DU24F_sub5
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret5
 bne DU24F_sub5
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub5
DU24F_ret5:
 stx OUTPUT_REM+2
 lda #5
 sta OUTPUT_QUOT+0
 rts
DU24F_sub5:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state6:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret6
 bne DU24F_sub6
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret6
 bne DU24F_sub6
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub6
DU24F_ret6:
 stx OUTPUT_REM+2
 lda #6
 sta OUTPUT_QUOT+0
 rts
DU24F_sub6:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state7:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret7
 bne DU24F_sub7
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret7
 bne DU24F_sub7
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub7
DU24F_ret7:
 stx OUTPUT_REM+2
 lda #7
 sta OUTPUT_QUOT+0
 rts
DU24F_sub7:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state8:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret8
 bne DU24F_sub8
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret8
 bne DU24F_sub8
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub8
DU24F_ret8:
 stx OUTPUT_REM+2
 lda #8
 sta OUTPUT_QUOT+0
 rts
DU24F_sub8:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state9:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret9
 bne DU24F_sub9
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret9
 bne DU24F_sub9
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub9
DU24F_ret9:
 stx OUTPUT_REM+2
 lda #9
 sta OUTPUT_QUOT+0
 rts
DU24F_sub9:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state10:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret10
 bne DU24F_sub10
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret10
 bne DU24F_sub10
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub10
DU24F_ret10:
 stx OUTPUT_REM+2
 lda #10
 sta OUTPUT_QUOT+0
 rts
DU24F_sub10:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state11:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret11
 bne DU24F_sub11
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret11
 bne DU24F_sub11
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub11
DU24F_ret11:
 stx OUTPUT_REM+2
 lda #11
 sta OUTPUT_QUOT+0
 rts
DU24F_sub11:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
DU24F_state12:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret12
 bne DU24F_sub12
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret12
 bne DU24F_sub12
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub12
DU24F_ret12:
 stx OUTPUT_REM+2
 lda #12
 sta OUTPUT_QUOT+0
 rts
DU24F_sub12:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
 ldx #13
 stx OUTPUT_QUOT+0
DU24F_state13:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret13
 bne DU24F_sub13
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret13
 bne DU24F_sub13
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub13
DU24F_ret13:
 stx OUTPUT_REM+2
 rts
DU24F_sub13:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
 inc OUTPUT_QUOT+0
DU24F_state14:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret14
 bne DU24F_sub14
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret14
 bne DU24F_sub14
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub14
DU24F_ret14:
 stx OUTPUT_REM+2
 rts
DU24F_sub14:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
 inc OUTPUT_QUOT+0
DU24F_state15:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret15
 bne DU24F_sub15
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret15
 bne DU24F_sub15
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub15
DU24F_ret15:
 stx OUTPUT_REM+2
 rts
DU24F_sub15:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
 inc OUTPUT_QUOT+0
DU24F_state16:
 tax
 cmp INPUT_DIV+2
 bcc DU24F_ret16
 bne DU24F_sub16
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret16
 bne DU24F_sub16
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub16
DU24F_ret16:
 stx OUTPUT_REM+2
 rts
DU24F_sub16:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 txa
 sbc INPUT_DIV+2
 inc OUTPUT_QUOT+0
DU24F_state17:
 sta OUTPUT_REM+2
 cmp INPUT_DIV+2
 bcc DU24F_ret17
 bne DU24F_sub17
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret17
 bne DU24F_sub17
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub17
DU24F_ret17:
 rts
DU24F_sub17:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 lda OUTPUT_REM+2
 sbc INPUT_DIV+2
 inc OUTPUT_QUOT+0
        jmp DU24F_state18

* = KERNEL_AUX
DU24F_state18:
 sta OUTPUT_REM+2
 cmp INPUT_DIV+2
 bcc DU24F_ret18
 bne DU24F_sub18
 lda OUTPUT_REM+1
 cmp INPUT_DIV+1
 bcc DU24F_ret18
 bne DU24F_sub18
 lda OUTPUT_REM+0
 cmp INPUT_DIV+0
 bcs DU24F_sub18
DU24F_ret18:
 rts
DU24F_sub18:
 lda OUTPUT_REM+0
 sbc INPUT_DIV+0
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc INPUT_DIV+1
 sta OUTPUT_REM+1
 lda OUTPUT_REM+2
 sbc INPUT_DIV+2
 inc OUTPUT_QUOT+0
DU24F_state19:
 sta OUTPUT_REM+2
 clc
 rts
DU24F_tail_setup:
 lda INPUT_DIV+0
 sta TEMP_ZP
 lda INPUT_DIV+1
 sta TEMP_ZP+1
 lda INPUT_DIV+2
 sta TEMP_ZP+2
 ldx #0
 stx OUTPUT_QUOT+0
 stx OUTPUT_QUOT+1
 stx OUTPUT_QUOT+2
DU24F_align:
 asl TEMP_ZP
 rol TEMP_ZP+1
 rol TEMP_ZP+2
 bcs DU24F_overshoot
 lda OUTPUT_REM+2
 cmp TEMP_ZP+2
 bcc DU24F_overshoot
 bne DU24F_align_take
 lda OUTPUT_REM+1
 cmp TEMP_ZP+1
 bcc DU24F_overshoot
 bne DU24F_align_take
 lda OUTPUT_REM+0
 cmp TEMP_ZP
 bcc DU24F_overshoot
DU24F_align_take:
 inx
 bne DU24F_align
DU24F_overshoot:
 ror TEMP_ZP+2
 ror TEMP_ZP+1
 ror TEMP_ZP
DU24F_bits:
 lda OUTPUT_REM+2
 cmp TEMP_ZP+2
 bcc DU24F_no_sub
 bne DU24F_do_sub
 lda OUTPUT_REM+1
 cmp TEMP_ZP+1
 bcc DU24F_no_sub
 bne DU24F_do_sub
 lda OUTPUT_REM+0
 cmp TEMP_ZP
 bcc DU24F_no_sub
DU24F_do_sub:
 lda OUTPUT_REM+0
 sbc TEMP_ZP
 sta OUTPUT_REM+0
 lda OUTPUT_REM+1
 sbc TEMP_ZP+1
 sta OUTPUT_REM+1
 lda OUTPUT_REM+2
 sbc TEMP_ZP+2
 sta OUTPUT_REM+2
DU24F_no_sub:
 rol OUTPUT_QUOT+0
 rol OUTPUT_QUOT+1
 rol OUTPUT_QUOT+2
 lsr TEMP_ZP+2
 ror TEMP_ZP+1
 ror TEMP_ZP
 dex
 bpl DU24F_bits
 lda OUTPUT_QUOT+0
 clc
DU24F_tail_bias:
 adc #0
 sta OUTPUT_QUOT+0
 bcc DU24F_tail_done
 inc OUTPUT_QUOT+1
 bne DU24F_tail_clear
 inc OUTPUT_QUOT+2
DU24F_tail_clear:
 clc
DU24F_tail_done:
 rts
DU24F_cg_code_end:
