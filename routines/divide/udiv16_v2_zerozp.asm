; Relocatable 0-ZP historical V2 size-fast unsigned 16/16 public divider.
; Canonical source: relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc
; Original fixed-address public JMP stubs omitted. Source original remainder.
; Returns complete Q16, R16, C (D=0). Caller inputs are untouched, CLD required.
; NMOS 6510 LAX/ANC, no writable code; no ZP, scratch, or init.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
* = KERNEL_CODE
DU16F_cg_code_start:
; ----------------------------------------------------------------------------
; ENTRY / DOMINANT q=0 PRECHECK
; First compare only the high bytes.  The common n<d case exits before any
; specialized divisor dispatch is paid.  Equality is kept out of the hot path.
; ----------------------------------------------------------------------------
DU16F_div_u16
        !byte $AF,<INPUT_NUM+1,>INPUT_NUM+1 ; LAX abs
        cmp INPUT_DIV+1
        bcs DU16F_precheck_high_ge
DU16F_quotient_zero
        lda #0
        sta OUTPUT_QUOT+0
        sta OUTPUT_QUOT+1
        lda INPUT_NUM+0
        sta OUTPUT_REM+0
        stx OUTPUT_REM+1
        rts
; ----------------------------------------------------------------------------
; HIGH-BYTE EQUALITY SPECIAL CASE
; With INPUT_NUM+1==INPUT_DIV+1, a successful low-byte subtraction leaves a remainder <256.
; For INPUT_DIV+1>0 that proves q=1 immediately; INPUT_DIV+1=0 is handed to the 16/8 path.
; ----------------------------------------------------------------------------
DU16F_precheck_high_equal
        lda INPUT_NUM+0
        sbc INPUT_DIV+0
        bcc DU16F_quotient_zero
        cpx #1
        bcc DU16F_precheck_equal_d8
        sta OUTPUT_REM+0
        !byte $0b,$00
        sta OUTPUT_REM+1
        sta OUTPUT_QUOT+1
        lda #1
        sta OUTPUT_QUOT+0
        rts
DU16F_precheck_equal_d8
        jmp DU16F_divisor_byte
DU16F_precheck_high_ge
        beq DU16F_precheck_high_equal
DU16F_dividend_ge_divisor
        lda INPUT_NUM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        txa
        sbc INPUT_DIV+1
        cmp INPUT_DIV+1
        bcc DU16F___relax_0
        jmp DU16F_q1_high_ge
DU16F___relax_0:
DU16F_quotient_one_a
        sta OUTPUT_REM+1
        lda #0
        sta OUTPUT_QUOT+1
        lda #1
        sta OUTPUT_QUOT+0
        rts
DU16F_low_d1_stub
        cmp DU16F_chain_cut,x
        bcc DU16F_low_d1_to_chain
        jmp DU16F_low_d1
DU16F_low_d1_to_chain
        sec
        jmp DU16F_chain_start
        nop                     ; preserve instruction locations, never reached
        nop                     ; fixed 6-byte source-level branch simplification
DU16F___relax_3:
DU16F_chain_q2_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q2_equal_take
        txa
DU16F_chain_q2_done
        sta OUTPUT_REM+1
        lda #2
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q2_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        jmp DU16F_chain_q3_done
        nop
        nop                  ; C=0 after ANC #0, preserve code addresses
DU16F___relax_6:
DU16F_chain_q3_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q3_equal_take
        txa
DU16F_chain_q3_done
        sta OUTPUT_REM+1
        lda #3
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q3_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        jmp DU16F_chain_q4_done
        nop
        nop                  ; C=0 after ANC #0, preserve code addresses
DU16F___relax_9:
DU16F_chain_q4_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q4_equal_take
        txa
DU16F_chain_q4_done
        sta OUTPUT_REM+1
        lda #4
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q4_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        jmp DU16F_chain_q5_done
DU16F_q1_high_equal
        tax
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_q1_equal_ge
DU16F_quotient_one_x
        stx OUTPUT_REM+1
        lda #0
        sta OUTPUT_QUOT+1
        lda #1
        sta OUTPUT_QUOT+0
        rts
DU16F_q1_equal_ge
        dex
        bpl DU16F_q1_equal_q2
        jmp DU16F_divisor_byte
DU16F_q1_equal_q2
        sta OUTPUT_REM+0
        !byte $0b,$00
        sta OUTPUT_QUOT+1
        jmp DU16F_chain_q2_done
        nop
        nop                  ; C=0 after ANC #0 and STA, preserve code addresses
DU16F___relax_2:
DU16F_q1_high_ge
        beq DU16F_q1_high_equal
; ----------------------------------------------------------------------------
; q >= 2 DISPATCH
; Large divisor high bytes use the very cheap repeated-subtraction chain.
; Small high bytes use a chain cutoff first, then the width-skipping divider.
; There are no tables in this size-library build.
; ----------------------------------------------------------------------------
DU16F_quotient_ge_two
        ldx INPUT_DIV+1
        cpx #$0f
        bcs DU16F___relax_1
        jmp DU16F_low_d1_stub
DU16F___relax_1:
; ----------------------------------------------------------------------------
; SMALL-QUOTIENT SUBTRACTION CHAIN
; The high-subtract continuation is the fall-through hot path.  Equality is
; cold and handled out of line.  Carry is deliberately reused between 16-bit
; subtractions; the chain is split only where relative-branch reach requires.
; ----------------------------------------------------------------------------
DU16F_chain_start
        ldy #0
        sty OUTPUT_QUOT+1
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q2_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_4
        jmp DU16F_chain_q2_done
DU16F___relax_4:
        bne DU16F___relax_5
        jmp DU16F_chain_q2_equal
DU16F___relax_5:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q3_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_7
        jmp DU16F_chain_q3_done
DU16F___relax_7:
        bne DU16F___relax_8
        jmp DU16F_chain_q3_equal
DU16F___relax_8:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q4_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_10
        jmp DU16F_chain_q4_done
DU16F___relax_10:
        bne DU16F___relax_11
        jmp DU16F_chain_q4_equal
DU16F___relax_11:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q5_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_12
        jmp DU16F_chain_q5_done
DU16F___relax_12:
        bne DU16F___relax_13
        jmp DU16F_chain_q5_equal
DU16F___relax_13:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q6_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_14
        jmp DU16F_chain_q6_done
DU16F___relax_14:
        bne DU16F___relax_15
        jmp DU16F_chain_q6_equal
DU16F___relax_15:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q7_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_16
        jmp DU16F_chain_q7_done
DU16F___relax_16:
        bne DU16F___relax_17
        jmp DU16F_chain_q7_equal
DU16F___relax_17:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q8_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_18
        jmp DU16F_chain_q8_done
DU16F___relax_18:
        bne DU16F___relax_19
        jmp DU16F_chain_q8_equal
DU16F___relax_19:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q9_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_20
        jmp DU16F_chain_q9_done
DU16F___relax_20:
        bne DU16F___relax_21
        jmp DU16F_chain_q9_equal
DU16F___relax_21:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q10_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_22
        jmp DU16F_chain_q10_done
DU16F___relax_22:
        bne DU16F___relax_23
        jmp DU16F_chain_q10_equal
DU16F___relax_23:
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q11_test
        cmp INPUT_DIV+1
        bcs DU16F___relax_24
        jmp DU16F_chain_q11_done
DU16F___relax_24:
        beq DU16F_chain_q11_equal
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
        jmp DU16F_chain_q12_test
DU16F_chain_q5_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q5_equal_take
        txa
DU16F_chain_q5_done
        sta OUTPUT_REM+1
        lda #5
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q6_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q6_equal_take
        txa
DU16F_chain_q6_done
        sta OUTPUT_REM+1
        lda #6
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q7_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q7_equal_take
        txa
DU16F_chain_q7_done
        sta OUTPUT_REM+1
        lda #7
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q8_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q8_equal_take
        txa
DU16F_chain_q8_done
        sta OUTPUT_REM+1
        lda #8
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q9_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q9_equal_take
        txa
DU16F_chain_q9_done
        sta OUTPUT_REM+1
        lda #9
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q10_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q10_equal_take
        txa
DU16F_chain_q10_done
        sta OUTPUT_REM+1
        lda #10
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q11_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q11_equal_take
        txa
DU16F_chain_q11_done
        sta OUTPUT_REM+1
        lda #11
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q5_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q6_done
DU16F_chain_q6_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q7_done
DU16F_chain_q7_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q8_done
DU16F_chain_q8_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q9_done
DU16F_chain_q9_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q10_done
DU16F_chain_q10_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q11_done
DU16F_chain_q11_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q12_done
DU16F_chain_q12_test
        cmp INPUT_DIV+1
        bcc DU16F_chain_q12_done
        beq DU16F_chain_q12_equal
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q13_test
        cmp INPUT_DIV+1
        bcc DU16F_chain_q13_done
        beq DU16F_chain_q13_equal
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q14_test
        cmp INPUT_DIV+1
        bcc DU16F_chain_q14_done
        beq DU16F_chain_q14_equal
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q15_test
        cmp INPUT_DIV+1
        bcc DU16F_chain_q15_done
        beq DU16F_chain_q15_equal
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q16_test
        cmp INPUT_DIV+1
        bcc DU16F_chain_q16_done
        beq DU16F_chain_q16_equal
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_chain_q12_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q12_equal_take
        txa
DU16F_chain_q12_done
        sta OUTPUT_REM+1
        lda #12
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q12_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q13_done         ; ANC #0 guarantees C=0
DU16F_chain_q13_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q13_equal_take
        txa
DU16F_chain_q13_done
        sta OUTPUT_REM+1
        lda #13
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q13_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q14_done         ; ANC #0 guarantees C=0
DU16F_chain_q14_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q14_equal_take
        txa
DU16F_chain_q14_done
        sta OUTPUT_REM+1
        lda #14
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q14_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q15_done         ; ANC #0 guarantees C=0
DU16F_chain_q15_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q15_equal_take
        txa
DU16F_chain_q15_done
        sta OUTPUT_REM+1
        lda #15
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q15_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
        bcc DU16F_chain_q16_done         ; ANC #0 guarantees C=0
DU16F_chain_q16_equal
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcs DU16F_chain_q16_equal_take
        txa
DU16F_chain_q16_done
        sta OUTPUT_REM+1
        lda #16
        sta OUTPUT_QUOT+0
        rts
DU16F_chain_q16_equal_take
        sta OUTPUT_REM+0
        !byte $0b,$00
DU16F_chain_q17_done
        sta OUTPUT_REM+1
        lda #17
        sta OUTPUT_QUOT+0
        rts
DU16F_tree_setup_s0
        jmp DU16F_generic_long_setup
DU16F_divisor_byte_stub
        jmp DU16F_divisor_byte
DU16F_low_d1_lt4
        cpx #1
        bcc DU16F_divisor_byte_stub
        beq DU16F_tree_setup_s0
        ; INPUT_DIV+1=2..3: fall through
DU16F_tree_setup_s1
        lda INPUT_NUM+0
        asl
        sta OUTPUT_QUOT+0
        lda INPUT_NUM+1
        rol
        sta OUTPUT_REM+0
        lda #0
        sta OUTPUT_QUOT+1
        rol
DU16F_tree_linear_s1
        rol OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        cmp INPUT_DIV+1
        bcc DU16F_tree_linear_s2
        beq DU16F_tree_eq_s1_stub
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
        bcs DU16F_tree_linear_s2
DU16F_tree_eq_s1_stub
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcc DU16F_tree_eq_s1_no
        sta OUTPUT_REM+0
        lda #0
        bcs DU16F_tree_linear_s2         ; successful SBC left quotient bit C=1
DU16F_tree_eq_s1_no
        txa
        bcc DU16F_tree_linear_s2         ; failed SBC left quotient bit C=0
DU16F_low_d1
        cpx #4
        bcc DU16F_low_d1_lt4
        cpx #8
        bcs DU16F_tree_setup_s3
        ; INPUT_DIV+1=4..7: fall through
; ----------------------------------------------------------------------------
; WIDTH-SKIPPING RESTORING DIVIDER (small nonzero divisor high bytes)
; Guaranteed leading zero quotient bits are pre-applied in setup.  Each later
; comparison leaves the new quotient bit in C, and ROL OUTPUT_QUOT+0 both shifts the
; source dividend and records that quotient bit.  No generated 256-leaf tree
; is required.
; ----------------------------------------------------------------------------
DU16F_tree_setup_s2
        lda INPUT_NUM+0
        asl
        sta OUTPUT_QUOT+0
        lda INPUT_NUM+1
        rol
        sta OUTPUT_REM+0
        lda #0
        sta OUTPUT_QUOT+1
        rol
        asl OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
DU16F_tree_linear_s2
        rol OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        cmp INPUT_DIV+1
        bcc DU16F_tree_linear_s3
        beq DU16F_tree_eq_s2_stub
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
        bcs DU16F_tree_linear_s3
DU16F_tree_eq_s2_stub
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcc DU16F_tree_eq_s2_no
        sta OUTPUT_REM+0
        lda #0
        bcs DU16F_tree_linear_s3
DU16F_tree_eq_s2_no
        txa
        bcc DU16F_tree_linear_s3
DU16F_tree_eq_s3
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcc DU16F_tree_eq_s3_no
        sta OUTPUT_REM+0
        lda #0
        bcs DU16F_tree_linear_s4
DU16F_tree_eq_s3_no
        txa
        bcc DU16F_tree_linear_s4
DU16F_tree_setup_s3
        lda INPUT_NUM+0
        asl
        sta OUTPUT_QUOT+0
        lda INPUT_NUM+1
        rol
        sta OUTPUT_REM+0
        lda #0
        sta OUTPUT_QUOT+1
        rol
        asl OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        asl OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
DU16F_tree_linear_s3
        rol OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        cmp INPUT_DIV+1
        bcc DU16F_tree_linear_s4
        beq DU16F_tree_eq_s3
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_tree_linear_s4
        rol OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        cmp INPUT_DIV+1
        bcc DU16F_tree_linear_s5
        beq DU16F_tree_eq_s4
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_tree_linear_s5
        rol OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        cmp INPUT_DIV+1
        bcc DU16F_tree_linear_s6
        beq DU16F_tree_eq_s5
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_tree_linear_s6
        rol OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        cmp INPUT_DIV+1
        bcc DU16F_tree_linear_s7
        beq DU16F_tree_eq_s6
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_tree_linear_s7
        rol OUTPUT_QUOT+0
        rol OUTPUT_REM+0
        rol
        cmp INPUT_DIV+1
        bcc DU16F_tree_finish
        beq DU16F_tree_eq_s7
        tay
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        sta OUTPUT_REM+0
        tya
        sbc INPUT_DIV+1
DU16F_tree_finish
        rol OUTPUT_QUOT+0
        sta OUTPUT_REM+1
        rts
DU16F_tree_eq_s4
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcc DU16F_tree_eq_s4_no
        sta OUTPUT_REM+0
        lda #0
        bcs DU16F_tree_linear_s5
DU16F_tree_eq_s4_no
        txa
        bcc DU16F_tree_linear_s5
DU16F_tree_eq_s5
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcc DU16F_tree_eq_s5_no
        sta OUTPUT_REM+0
        lda #0
        bcs DU16F_tree_linear_s6
DU16F_tree_eq_s5_no
        txa
        bcc DU16F_tree_linear_s6
DU16F_tree_eq_s6
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcc DU16F_tree_eq_s6_no
        sta OUTPUT_REM+0
        lda #0
        bcs DU16F_tree_linear_s7
DU16F_tree_eq_s6_no
        txa
        bcc DU16F_tree_linear_s7
DU16F_tree_eq_s7
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        bcc DU16F_tree_eq_s7_no
        sta OUTPUT_REM+0
        lda #0
        bcs DU16F_tree_finish
DU16F_tree_eq_s7_no
        txa
        bcc DU16F_tree_finish
; INPUT_DIV+1=0 enters here to test the low divisor byte. If nonzero, fall directly
; into the shared restoring setup instead of paying a JMP. INPUT_DIV+1=1 callers jump
; straight to DU16F_generic_long_setup and skip this test.
DU16F_divisor_byte
        lda INPUT_DIV+0
        beq DU16F_divide_by_zero

; INPUT_DIV+1=1 uses a compact full restoring divider instead of an 8 KiB estimator.
DU16F_generic_long_setup
        lda INPUT_NUM+0
        sta OUTPUT_QUOT+0
        lda INPUT_NUM+1
        sta OUTPUT_QUOT+1
        lda #0
        ; Prime C=0 for delayed quotient insertion while keeping A=0.
        lsr
        sta OUTPUT_REM+0
        sta OUTPUT_REM+1
        ldy #16
DU16F_generic_long_loop
        rol OUTPUT_QUOT+0
        rol OUTPUT_QUOT+1
        rol OUTPUT_REM+0
        rol OUTPUT_REM+1
        sec
        lda OUTPUT_REM+0
        sbc INPUT_DIV+0
        tax
        lda OUTPUT_REM+1
        sbc INPUT_DIV+1
        bcc DU16F_generic_long_no_sub
        sta OUTPUT_REM+1
        stx OUTPUT_REM+0
DU16F_generic_long_no_sub
        ; C is the current quotient bit. DEY/BNE preserve it for the next ROL.
        dey
        bne DU16F_generic_long_loop
        ; Append the final delayed bit. The placeholder shifted out of OUTPUT_QUOT+1 is 0,
        ; so C also returns clear for the success ABI.
        rol OUTPUT_QUOT+0
        rol OUTPUT_QUOT+1
        rts

; ----------------------------------------------------------------------------
; DIVIDE BY ZERO ABI
; ----------------------------------------------------------------------------
DU16F_divide_by_zero
        ; Reached from DU16F_divisor_byte only when A=INPUT_DIV+0=0.
        sta OUTPUT_QUOT+0
        sta OUTPUT_QUOT+1
        sta OUTPUT_REM+0
        sta OUTPUT_REM+1
        sec
        rts
; ----------------------------------------------------------------------------
; LOW-INPUT_DIV+1 CHAIN/TREE CUTOFFS
; If the high byte of the remainder after the first subtraction is below this
; threshold, repeated subtraction wins; otherwise use the specialized low-INPUT_DIV+1
; path.
;
; IMPORTANT correctness bound for INPUT_DIV+1=1:
;   after the first successful subtraction, chain entry sees remainder r.
;   The unrolled chain can return at most q=17, so we must guarantee
;       floor(r/d) <= 16.
;   With INPUT_DIV+1=1 and only OUTPUT_REM+1 known, OUTPUT_REM+1 < 17 implies r <= $10ff while d >= $0100,
;   hence floor(r/d) <= 16.  A cutoff of 18 would admit OUTPUT_REM+1=17 and can require
;   q=18, which the chain cannot represent.  Therefore 17 is the maximum safe
;   cutoff as well as the fastest valid value in the retune.
;
; The other entries retain the previous benchmark-tuned values because their
; width-skipping paths were not changed by this Firemonger pass.
; ----------------------------------------------------------------------------
DU16F_chain_cut
        !byte 0,17,22,32,36,43,52,61,63,69,77,84,91,98,104
DU16F_cg_code_end:
