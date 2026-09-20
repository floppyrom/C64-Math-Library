; V2 direct-output fast SDIV16/SMOD16; tight repack inside existing signed window.
; Direct stable-memory signed ABI; executable-disjoint private magnitude engine.
; Six transient ZP bytes, all inside the common 31-byte window.
D16F_sn0 = MATH_N+0
D16F_sn1 = MATH_N+1
D16F_sd_in0 = MATH_D+0
D16F_sd_in1 = MATH_D+1
D16F_sdin0 = MATH_D+0
D16F_sdin1 = MATH_D+1
D16F_q0 = MATH_Q+0
D16F_q1 = MATH_Q+1
D16F_r0 = MATH_R+0
D16F_r1 = MATH_R+1
D16F_n0 = ZP_MAIN+$0E
D16F_n1 = ZP_MAIN+$0F
D16F_d0 = ZP_MAIN+$10
D16F_d1 = ZP_MAIN+$11
D16F_sd0 = ZP_MAIN+$12
D16F_sd1 = ZP_MAIN+$13

* = MATH_SDIV16
    jmp D16F_div_s16
* = MATH_SMOD16
    jmp D16F_div_s16

;ABI
;CPU: mos6502
;Operation: sdiv
;Entry: D16F_div_s16
;Input n: int16 = D16F_sn0, D16F_sn1
;Input d: int16 = D16F_sdin0, D16F_sdin1
;Output q: int16 = D16F_q0, D16F_q1
;Remainder r: int16 = D16F_r0, D16F_r1
;Region ZP: sg_zp_start..sg_zp_end, cg_zp_start..cg_zp_end
;Region Code: D16F_sg_code_start..D16F_sg_code_end, D16F_cg_code_start..D16F_cg_code_end
;End ABI
; ============================================================================
; FIREMONGER C64 DIVISION REFERENCE — PUBLICATION COPY
; Family       : sdiv16
; Tier         : fast
; Target       : NMOS 6502/6510, decimal mode clear
; Measurement  : canonical 2,097,152-case SplitMix64 corpus; seed $C0FFEE where random
; Timing       : entry instruction through final RTS; caller JSR excluded
; Avg cycles   : 127.807033
; Min / Max    : 43 / 977
; Stddev       : 122.173941
; Resident     : 1572 bytes (Code 1572 + Data 0); ZP 12 bytes separate
; Validation   : 2097152 cases, 0 errors
; Edge suite   : 10276 cases in canonical run, 0 errors
; Architecture : Four sign-case continuations remove post-core sign rediscovery.
;
; NOTE: this publication block is comments only and does not alter the exact
; assembled image that produced the result. Raw canonical JSON is supplied
; beside the source when available. See TECHNICAL_ASSESSMENT.md for caveats.
; ============================================================================
; ============================================================================
; DIV_U16 SIZE LIBRARY — FAST TIER
; Unsigned 16/16 -> quotient + remainder for NMOS 6502/6510
;
; Size-oriented descendant of the 63-cycle hybrid family.
;
; Design:
;   * q=0 and q=1 are handled immediately (dominant random cases).
;   * D16F_d1 >= $0f uses the fast unrolled small-quotient subtraction chain.
;   * D16F_d1=2..14 uses a width-skipping restoring tail.
;   * D16F_d1=0 and D16F_d1=1 share one compact full restoring divider.
;   * NO quotient-estimate tables and NO quarter-square tables.
;
; ABI:
;   input  D16F_n1:D16F_n0 = dividend, D16F_d1:D16F_d0 = divisor (preserved)
;   output D16F_q1:D16F_q0 = quotient, D16F_r1:D16F_r0 = remainder
;          C=0 success
;          C=1 divide by zero, q=r=0
;   A/X/Y clobbered. Decimal mode MUST be clear (D=0).
;
; Uses stable NMOS undocumented opcodes inherited from the speed core:
;   LAX zp ($A7), ANC #0 ($0B)
;
; Branch-state size-Fast release:
;   implementation image : 1,104 bytes ($100c-$145b)
;   ZP ABI               : 8 bytes ($10-$17)
;   tables               : 0
;   common 300k $C0FFEE  : 69.313143 cycles average, 0 mismatches
;   1M $C0FFEE average   : 69.321223 cycles (min/max 31/871)
;
; Relative to the immediate 1,129-byte / 69.331250-on-the-common-300k build,
; this version folds known carry states into guaranteed branches, removes an
; unnecessary q=17 jump and carry clear, and retunes the physical origin to
; avoid losing the local savings to a page crossing.
;   576 structured edge pairs: 0 mismatches
; ============================================================================



* = REG_TABLE+$1A00
D16F_sg_code_start:
D16F_div_s16:
        lda D16F_sn1
        bmi D16F_s_nneg_dispatch
        lda D16F_sdin1
        bmi D16F_s_case_pn

        ; ++: q=0 can be decided on original bytes; no magnitude copy yet.
D16F_s_case_pp:
        lda D16F_sdin0
        ora D16F_sdin1
        bne D16F_s_pp_dnz
        jmp D16F_s_zero
D16F_s_pp_dnz:
        !byte $AF,<MATH_N+1,>MATH_N+1
        cmp D16F_sdin1
        bcs D16F_s_pp_high_ge
        jmp D16F_s_qzero
D16F_s_pp_high_ge:
        bne D16F_s_pp_ge
        lda D16F_sn0
        cmp D16F_sdin0
        bcs D16F_s_pp_ge
        jmp D16F_s_qzero
D16F_s_pp_ge:
        lda D16F_sn0
        sta D16F_n0
        stx D16F_n1
        lda D16F_sdin0
        sta D16F_d0
        lda D16F_sdin1
        sta D16F_d1
        jmp D16F_s_mag_pp

D16F_s_case_pn:
        ; +-, form only |d| before the q=0 test.
        lda #0
        sec
        sbc D16F_sdin0
        sta D16F_d0
        lda #0
        sbc D16F_sdin1
        sta D16F_d1
        !byte $AF,<MATH_N+1,>MATH_N+1
        cmp D16F_d1
        bcs D16F_s_pn_high_ge
        jmp D16F_s_qzero
D16F_s_pn_high_ge:
        bne D16F_s_pn_ge
        lda D16F_sn0
        cmp D16F_d0
        bcs D16F_s_pn_ge
        jmp D16F_s_qzero
D16F_s_pn_ge:
        lda D16F_sn0
        sta D16F_n0
        stx D16F_n1
        jmp D16F_s_mag_pn

D16F_s_nneg_dispatch:
        lda D16F_sdin1
        bmi D16F_s_case_nn

        ; -+: form only |n| first. Positive divisor may be zero.
D16F_s_case_np:
        lda D16F_sdin0
        ora D16F_sdin1
        bne D16F_s_np_dnz
        jmp D16F_s_zero
D16F_s_np_dnz:
        lda #0
        sec
        sbc D16F_sn0
        sta D16F_n0
        lda #0
        sbc D16F_sn1
        sta D16F_n1
        !byte $a7,D16F_n1
        cmp D16F_sdin1
        bcs D16F_s_np_high_ge
        jmp D16F_s_qzero
D16F_s_np_high_ge:
        bne D16F_s_np_ge
        lda D16F_n0
        cmp D16F_sdin0
        bcs D16F_s_np_ge
        jmp D16F_s_qzero
D16F_s_np_ge:
        lda D16F_sdin0
        sta D16F_d0
        lda D16F_sdin1
        sta D16F_d1
        jmp D16F_s_mag_np

D16F_s_case_nn:
        ; --: raw two's-complement order reverses magnitude order.
        !byte $AF,<MATH_N+1,>MATH_N+1
        cmp D16F_sdin1
        bcc D16F_s_nn_ge
        beq D16F_s_nn_high_eq
        jmp D16F_s_qzero
D16F_s_nn_high_eq:
        lda D16F_sn0
        cmp D16F_sdin0
        bcc D16F_s_nn_ge
        beq D16F_s_nn_ge
        jmp D16F_s_qzero
D16F_s_nn_ge:
        lda #0
        sec
        sbc D16F_sn0
        sta D16F_n0
        lda #0
        sbc D16F_sn1
        sta D16F_n1
        lda #0
        sec
        sbc D16F_sdin0
        sta D16F_d0
        lda #0
        sbc D16F_sdin1
        sta D16F_d1
        jmp D16F_s_mag_nn

D16F_s_mag_pp:
        sec
        lda D16F_n0
        sbc D16F_d0
        sta D16F_r0
        lda D16F_n1
        sbc D16F_d1
        sta D16F_r1
        cmp D16F_d1
        bcc D16F_s_qone_pp
        bne D16F_s_qge2_pp
        lda D16F_r0
        cmp D16F_d0
        bcs D16F_s_qge2_pp
D16F_s_qone_pp:
        lda #1
        sta D16F_q0
        lda #0
        sta D16F_q1
        clc
        rts
D16F_s_qge2_pp:
        lda D16F_r1
        jsr D16F_quotient_ge_two
        clc
        rts

D16F_s_mag_pn:
        sec
        lda D16F_n0
        sbc D16F_d0
        sta D16F_r0
        lda D16F_n1
        sbc D16F_d1
        sta D16F_r1
        cmp D16F_d1
        bcc D16F_s_qone_pn
        bne D16F_s_qge2_pn
        lda D16F_r0
        cmp D16F_d0
        bcs D16F_s_qge2_pn
D16F_s_qone_pn:
        lda #$ff
        sta D16F_q0
        sta D16F_q1
        clc
        rts
D16F_s_qge2_pn:
        lda D16F_r1
        jsr D16F_quotient_ge_two
        jmp D16F_s_neg_q_out

D16F_s_mag_np:
        sec
        lda D16F_n0
        sbc D16F_d0
        sta D16F_r0
        lda D16F_n1
        sbc D16F_d1
        sta D16F_r1
        cmp D16F_d1
        bcc D16F_s_qone_np
        bne D16F_s_qge2_np
        lda D16F_r0
        cmp D16F_d0
        bcs D16F_s_qge2_np
D16F_s_qone_np:
        lda #0
        sec
        sbc D16F_r0
        sta D16F_r0
        lda #0
        sbc D16F_r1
        sta D16F_r1
        lda #$ff
        sta D16F_q0
        sta D16F_q1
        clc
        rts
D16F_s_qge2_np:
        lda D16F_r1
        jsr D16F_quotient_ge_two
        jmp D16F_s_neg_rq_out

D16F_s_mag_nn:
        sec
        lda D16F_n0
        sbc D16F_d0
        sta D16F_r0
        lda D16F_n1
        sbc D16F_d1
        sta D16F_r1
        cmp D16F_d1
        bcc D16F_s_qone_nn
        bne D16F_s_qge2_nn
        lda D16F_r0
        cmp D16F_d0
        bcs D16F_s_qge2_nn
D16F_s_qone_nn:
        lda #0
        sec
        sbc D16F_r0
        sta D16F_r0
        lda #0
        sbc D16F_r1
        sta D16F_r1
        lda #1
        sta D16F_q0
        lda #0
        sta D16F_q1
        clc
        rts
D16F_s_qge2_nn:
        lda D16F_r1
        jsr D16F_quotient_ge_two
        jmp D16F_s_neg_r_out

D16F_s_qzero:
        lda #0
        sta D16F_q0
        sta D16F_q1
        lda D16F_sn0
        sta D16F_r0
        lda D16F_sn1
        sta D16F_r1
        clc
        rts

D16F_s_neg_rq_out:
        lda #0
        sec
        sbc D16F_r0
        sta D16F_r0
        lda #0
        sbc D16F_r1
        sta D16F_r1
D16F_s_neg_q_out:
        lda #0
        sec
        sbc D16F_q0
        sta D16F_q0
        lda #0
        sbc D16F_q1
        sta D16F_q1
        clc
        rts
D16F_s_neg_r_out:
        lda #0
        sec
        sbc D16F_r0
        sta D16F_r0
        lda #0
        sbc D16F_r1
        sta D16F_r1
        clc
        rts
D16F_s_zero:
        lda #0
        sta D16F_q0
        sta D16F_q1
        sta D16F_r0
        sta D16F_r1
        sec
        rts
D16F_sg_code_end:

* = REG_TABLE+$1C2B
D16F_cg_code_start:
; ----------------------------------------------------------------------------
; ENTRY / DOMINANT q=0 PRECHECK
; First compare only the high bytes.  The common n<d case exits before any
; specialized divisor dispatch is paid.  Equality is kept out of the hot path.
; ----------------------------------------------------------------------------
D16F_div_u16
        !byte $a7,D16F_n1
        cmp D16F_d1
        bcs D16F_precheck_high_ge
D16F_quotient_zero
        lda #0
        sta D16F_q0
        sta D16F_q1
        lda D16F_n0
        sta D16F_r0
        stx D16F_r1
        rts
; ----------------------------------------------------------------------------
; HIGH-BYTE EQUALITY SPECIAL CASE
; With D16F_n1==D16F_d1, a successful low-byte subtraction leaves a remainder <256.
; For D16F_d1>0 that proves q=1 immediately; D16F_d1=0 is handed to the 16/8 path.
; ----------------------------------------------------------------------------
D16F_precheck_high_equal
        lda D16F_n0
        sbc D16F_d0
        bcc D16F_quotient_zero
        cpx #1
        bcc D16F_precheck_equal_d8
        sta D16F_r0
        !byte $0b,$00
        sta D16F_r1
        sta D16F_q1
        lda #1
        sta D16F_q0
        rts
D16F_precheck_equal_d8
        jmp D16F_divisor_byte
D16F_precheck_high_ge
        beq D16F_precheck_high_equal
D16F_dividend_ge_divisor
        lda D16F_n0
        sbc D16F_d0
        sta D16F_r0
        txa
        sbc D16F_d1
        cmp D16F_d1
        bcc D16F___rx0
        jmp D16F_q1_high_ge
D16F___rx0:
D16F_quotient_one_a
        sta D16F_r1
        lda #0
        sta D16F_q1
        lda #1
        sta D16F_q0
        rts
D16F_low_d1_stub
        cmp D16F_chain_cut,x
        bcc D16F_low_d1_to_chain
        jmp D16F_low_d1
D16F_low_d1_to_chain
        sec
        bcc D16F___rx6
        jmp D16F_chain_start
D16F___rx6:
D16F_chain_q2_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q2_equal_take
        txa
D16F_chain_q2_done
        sta D16F_r1
        lda #2
        sta D16F_q0
        rts
D16F_chain_q2_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcs D16F___rx5
        jmp D16F_chain_q3_done
D16F___rx5:
D16F_chain_q3_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q3_equal_take
        txa
D16F_chain_q3_done
        sta D16F_r1
        lda #3
        sta D16F_q0
        rts
D16F_chain_q3_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcs D16F___rx9
        jmp D16F_chain_q4_done
D16F___rx9:
D16F_chain_q4_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q4_equal_take
        txa
D16F_chain_q4_done
        sta D16F_r1
        lda #4
        sta D16F_q0
        rts
D16F_chain_q4_equal_take
        sta D16F_r0
        !byte $0b,$00
        jmp D16F_chain_q5_done
D16F_q1_high_equal
        tax
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_q1_equal_ge
D16F_quotient_one_x
        stx D16F_r1
        lda #0
        sta D16F_q1
        lda #1
        sta D16F_q0
        rts
D16F_q1_equal_ge
        dex
        bpl D16F_q1_equal_q2
        jmp D16F_divisor_byte
D16F_q1_equal_q2
        sta D16F_r0
        !byte $0b,$00
        sta D16F_q1
        bcs D16F___rx2
        jmp D16F_chain_q2_done
D16F___rx2:
D16F_q1_high_ge
        beq D16F_q1_high_equal
; ----------------------------------------------------------------------------
; q >= 2 DISPATCH
; Large divisor high bytes use the very cheap repeated-subtraction chain.
; Small high bytes use a chain cutoff first, then the width-skipping divider.
; There are no tables in this size-library build.
; ----------------------------------------------------------------------------
D16F_quotient_ge_two
        ldx D16F_d1
        cpx #$0f
        bcs D16F___rx1
        jmp D16F_low_d1_stub
D16F___rx1:
; ----------------------------------------------------------------------------
; SMALL-QUOTIENT SUBTRACTION CHAIN
; The high-subtract continuation is the fall-through hot path.  Equality is
; cold and handled out of line.  Carry is deliberately reused between 16-bit
; subtractions; the chain is split only where relative-branch reach requires.
; ----------------------------------------------------------------------------
D16F_chain_start
        ldy #0
        sty D16F_q1
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q2_test
        cmp D16F_d1
        bcs D16F___rx3
        jmp D16F_chain_q2_done
D16F___rx3:
        bne D16F___rx4
        jmp D16F_chain_q2_equal
D16F___rx4:
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q3_test
        cmp D16F_d1
        bcs D16F___rx7
        jmp D16F_chain_q3_done
D16F___rx7:
        bne D16F___rx8
        jmp D16F_chain_q3_equal
D16F___rx8:
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q4_test
        cmp D16F_d1
        bcs D16F___rx10
        jmp D16F_chain_q4_done
D16F___rx10:
        bne D16F___rx11
        jmp D16F_chain_q4_equal
D16F___rx11:
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q5_test
        cmp D16F_d1
        bcs D16F___rx12
        jmp D16F_chain_q5_done
D16F___rx12:
        bne D16F___rx15
        jmp D16F_chain_q5_equal
D16F___rx15:
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q6_test
        cmp D16F_d1
        bcs D16F___rx13
        jmp D16F_chain_q6_done
D16F___rx13:
        bne D16F___rx17
        jmp D16F_chain_q6_equal
D16F___rx17:
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q7_test
        cmp D16F_d1
        bcs D16F___rx14
        jmp D16F_chain_q7_done
D16F___rx14:
        bne D16F___rx20
        jmp D16F_chain_q7_equal
D16F___rx20:
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q8_test
        cmp D16F_d1
        bcs D16F___rx16
        jmp D16F_chain_q8_done
D16F___rx16:
        beq D16F_chain_q8_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q9_test
        cmp D16F_d1
        bcs D16F___rx18
        jmp D16F_chain_q9_done
D16F___rx18:
        beq D16F_chain_q9_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q10_test
        cmp D16F_d1
        bcs D16F___rx19
        jmp D16F_chain_q10_done
D16F___rx19:
        beq D16F_chain_q10_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q11_test
        cmp D16F_d1
        bcc D16F_chain_q11_done
        beq D16F_chain_q11_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
        jmp D16F_chain_q12_test
D16F_chain_q5_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q5_equal_take
        txa
D16F_chain_q5_done
        sta D16F_r1
        lda #5
        sta D16F_q0
        rts
D16F_chain_q6_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q6_equal_take
        txa
D16F_chain_q6_done
        sta D16F_r1
        lda #6
        sta D16F_q0
        rts
D16F_chain_q7_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q7_equal_take
        txa
D16F_chain_q7_done
        sta D16F_r1
        lda #7
        sta D16F_q0
        rts
D16F_chain_q8_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q8_equal_take
        txa
D16F_chain_q8_done
        sta D16F_r1
        lda #8
        sta D16F_q0
        rts
D16F_chain_q9_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q9_equal_take
        txa
D16F_chain_q9_done
        sta D16F_r1
        lda #9
        sta D16F_q0
        rts
D16F_chain_q10_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q10_equal_take
        txa
D16F_chain_q10_done
        sta D16F_r1
        lda #10
        sta D16F_q0
        rts
D16F_chain_q11_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q11_equal_take
        txa
D16F_chain_q11_done
        sta D16F_r1
        lda #11
        sta D16F_q0
        rts
D16F_chain_q5_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q6_done
D16F_chain_q6_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q7_done
D16F_chain_q7_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q8_done
D16F_chain_q8_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q9_done
D16F_chain_q9_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q10_done
D16F_chain_q10_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q11_done
D16F_chain_q11_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q12_done
D16F_chain_q12_test
        cmp D16F_d1
        bcc D16F_chain_q12_done
        beq D16F_chain_q12_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q13_test
        cmp D16F_d1
        bcc D16F_chain_q13_done
        beq D16F_chain_q13_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q14_test
        cmp D16F_d1
        bcc D16F_chain_q14_done
        beq D16F_chain_q14_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q15_test
        cmp D16F_d1
        bcc D16F_chain_q15_done
        beq D16F_chain_q15_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q16_test
        cmp D16F_d1
        bcc D16F_chain_q16_done
        beq D16F_chain_q16_equal
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_chain_q12_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q12_equal_take
        txa
D16F_chain_q12_done
        sta D16F_r1
        lda #12
        sta D16F_q0
        rts
D16F_chain_q12_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q13_done         ; ANC #0 guarantees C=0
D16F_chain_q13_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q13_equal_take
        txa
D16F_chain_q13_done
        sta D16F_r1
        lda #13
        sta D16F_q0
        rts
D16F_chain_q13_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q14_done         ; ANC #0 guarantees C=0
D16F_chain_q14_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q14_equal_take
        txa
D16F_chain_q14_done
        sta D16F_r1
        lda #14
        sta D16F_q0
        rts
D16F_chain_q14_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q15_done         ; ANC #0 guarantees C=0
D16F_chain_q15_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q15_equal_take
        txa
D16F_chain_q15_done
        sta D16F_r1
        lda #15
        sta D16F_q0
        rts
D16F_chain_q15_equal_take
        sta D16F_r0
        !byte $0b,$00
        bcc D16F_chain_q16_done         ; ANC #0 guarantees C=0
D16F_chain_q16_equal
        lda D16F_r0
        sbc D16F_d0
        bcs D16F_chain_q16_equal_take
        txa
D16F_chain_q16_done
        sta D16F_r1
        lda #16
        sta D16F_q0
        rts
D16F_chain_q16_equal_take
        sta D16F_r0
        !byte $0b,$00
D16F_chain_q17_done
        sta D16F_r1
        lda #17
        sta D16F_q0
        rts
D16F_tree_setup_s0
        jmp D16F_generic_long_setup
D16F_divisor_byte_stub
        jmp D16F_divisor_byte
D16F_low_d1_lt4
        cpx #1
        bcc D16F_divisor_byte_stub
        beq D16F_tree_setup_s0
        ; D16F_d1=2..3: fall through
D16F_tree_setup_s1
        lda D16F_n0
        asl
        sta D16F_q0
        lda D16F_n1
        rol
        sta D16F_r0
        lda #0
        sta D16F_q1
        rol
D16F_tree_linear_s1
        rol D16F_q0
        rol D16F_r0
        rol
        cmp D16F_d1
        bcc D16F_tree_linear_s2
        beq D16F_tree_eq_s1_stub
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
        bcs D16F_tree_linear_s2
D16F_tree_eq_s1_stub
        lda D16F_r0
        sbc D16F_d0
        bcc D16F_tree_eq_s1_no
        sta D16F_r0
        lda #0
        bcs D16F_tree_linear_s2         ; successful SBC left quotient bit C=1
D16F_tree_eq_s1_no
        txa
        bcc D16F_tree_linear_s2         ; failed SBC left quotient bit C=0
D16F_low_d1
        cpx #4
        bcc D16F_low_d1_lt4
        cpx #8
        bcs D16F_tree_setup_s3
        ; D16F_d1=4..7: fall through
; ----------------------------------------------------------------------------
; WIDTH-SKIPPING RESTORING DIVIDER (small nonzero divisor high bytes)
; Guaranteed leading zero quotient bits are pre-applied in setup.  Each later
; comparison leaves the new quotient bit in C, and ROL D16F_q0 both shifts the
; source dividend and records that quotient bit.  No generated 256-leaf tree
; is required.
; ----------------------------------------------------------------------------
D16F_tree_setup_s2
        lda D16F_n0
        asl
        sta D16F_q0
        lda D16F_n1
        rol
        sta D16F_r0
        lda #0
        sta D16F_q1
        rol
        asl D16F_q0
        rol D16F_r0
        rol
D16F_tree_linear_s2
        rol D16F_q0
        rol D16F_r0
        rol
        cmp D16F_d1
        bcc D16F_tree_linear_s3
        beq D16F_tree_eq_s2_stub
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
        bcs D16F_tree_linear_s3
D16F_tree_eq_s2_stub
        lda D16F_r0
        sbc D16F_d0
        bcc D16F_tree_eq_s2_no
        sta D16F_r0
        lda #0
        bcs D16F_tree_linear_s3
D16F_tree_eq_s2_no
        txa
        bcc D16F_tree_linear_s3
D16F_tree_eq_s3
        lda D16F_r0
        sbc D16F_d0
        bcc D16F_tree_eq_s3_no
        sta D16F_r0
        lda #0
        bcs D16F_tree_linear_s4
D16F_tree_eq_s3_no
        txa
        bcc D16F_tree_linear_s4
D16F_tree_setup_s3
        lda D16F_n0
        asl
        sta D16F_q0
        lda D16F_n1
        rol
        sta D16F_r0
        lda #0
        sta D16F_q1
        rol
        asl D16F_q0
        rol D16F_r0
        rol
        asl D16F_q0
        rol D16F_r0
        rol
D16F_tree_linear_s3
        rol D16F_q0
        rol D16F_r0
        rol
        cmp D16F_d1
        bcc D16F_tree_linear_s4
        beq D16F_tree_eq_s3
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_tree_linear_s4
        rol D16F_q0
        rol D16F_r0
        rol
        cmp D16F_d1
        bcc D16F_tree_linear_s5
        beq D16F_tree_eq_s4
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_tree_linear_s5
        rol D16F_q0
        rol D16F_r0
        rol
        cmp D16F_d1
        bcc D16F_tree_linear_s6
        beq D16F_tree_eq_s5
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_tree_linear_s6
        rol D16F_q0
        rol D16F_r0
        rol
        cmp D16F_d1
        bcc D16F_tree_linear_s7
        beq D16F_tree_eq_s6
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_tree_linear_s7
        rol D16F_q0
        rol D16F_r0
        rol
        cmp D16F_d1
        bcc D16F_tree_finish
        beq D16F_tree_eq_s7
        tay
        lda D16F_r0
        sbc D16F_d0
        sta D16F_r0
        tya
        sbc D16F_d1
D16F_tree_finish
        rol D16F_q0
        sta D16F_r1
        rts
D16F_tree_eq_s4
        lda D16F_r0
        sbc D16F_d0
        bcc D16F_tree_eq_s4_no
        sta D16F_r0
        lda #0
        bcs D16F_tree_linear_s5
D16F_tree_eq_s4_no
        txa
        bcc D16F_tree_linear_s5
D16F_tree_eq_s5
        lda D16F_r0
        sbc D16F_d0
        bcc D16F_tree_eq_s5_no
        sta D16F_r0
        lda #0
        bcs D16F_tree_linear_s6
D16F_tree_eq_s5_no
        txa
        bcc D16F_tree_linear_s6
D16F_tree_eq_s6
        lda D16F_r0
        sbc D16F_d0
        bcc D16F_tree_eq_s6_no
        sta D16F_r0
        lda #0
        bcs D16F_tree_linear_s7
D16F_tree_eq_s6_no
        txa
        bcc D16F_tree_linear_s7
D16F_tree_eq_s7
        lda D16F_r0
        sbc D16F_d0
        bcc D16F_tree_eq_s7_no
        sta D16F_r0
        lda #0
        bcs D16F_tree_finish
D16F_tree_eq_s7_no
        txa
        bcc D16F_tree_finish
; D16F_d1=0 enters here to test the low divisor byte. If nonzero, fall directly
; into the shared restoring setup instead of paying a JMP. D16F_d1=1 callers jump
; straight to D16F_generic_long_setup and skip this test.
D16F_divisor_byte
        lda D16F_d0
        beq D16F_divide_by_zero

; D16F_d1=1 uses a compact full restoring divider instead of an 8 KiB estimator.
D16F_generic_long_setup
        lda D16F_n0
        sta D16F_q0
        lda D16F_n1
        sta D16F_q1
        lda #0
        ; Prime C=0 for delayed quotient insertion while keeping A=0.
        lsr
        sta D16F_r0
        sta D16F_r1
        ldy #16
D16F_generic_long_loop
        rol D16F_q0
        rol D16F_q1
        rol D16F_r0
        rol D16F_r1
        sec
        lda D16F_r0
        sbc D16F_d0
        tax
        lda D16F_r1
        sbc D16F_d1
        bcc D16F_generic_long_no_sub
        sta D16F_r1
        stx D16F_r0
D16F_generic_long_no_sub
        ; C is the current quotient bit. DEY/BNE preserve it for the next ROL.
        dey
        bne D16F_generic_long_loop
        ; Append the final delayed bit. The placeholder shifted out of D16F_q1 is 0,
        ; so C also returns clear for the success ABI.
        rol D16F_q0
        rol D16F_q1
        rts

; ----------------------------------------------------------------------------
; DIVIDE BY ZERO ABI
; ----------------------------------------------------------------------------
D16F_divide_by_zero
        ; Reached from D16F_divisor_byte only when A=D16F_d0=0.
        sta D16F_q0
        sta D16F_q1
        sta D16F_r0
        sta D16F_r1
        sec
        rts
; ----------------------------------------------------------------------------
; LOW-D16F_d1 CHAIN/TREE CUTOFFS
; If the high byte of the remainder after the first subtraction is below this
; threshold, repeated subtraction wins; otherwise use the specialized low-D16F_d1
; path.
;
; IMPORTANT correctness bound for D16F_d1=1:
;   after the first successful subtraction, chain entry sees remainder r.
;   The unrolled chain can return at most q=17, so we must guarantee
;       floor(r/d) <= 16.
;   With D16F_d1=1 and only D16F_r1 known, D16F_r1 < 17 implies r <= $10ff while d >= $0100,
;   hence floor(r/d) <= 16.  A cutoff of 18 would admit D16F_r1=17 and can require
;   q=18, which the chain cannot represent.  Therefore 17 is the maximum safe
;   cutoff as well as the fastest valid value in the retune.
;
; The other entries retain the previous benchmark-tuned values because their
; width-skipping paths were not changed by this Firemonger pass.
; ----------------------------------------------------------------------------
D16F_chain_cut
        !byte 0,17,22,32,36,43,52,61,63,69,77,84,91,98,104
D16F_cg_code_end:
