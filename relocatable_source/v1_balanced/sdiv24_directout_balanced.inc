; V1 Balanced direct-output SDIV24/SMOD24 from deep-practical native Pareto core.
; Direct stable-memory signed ABI; executable-disjoint private magnitude engine.
; At most nine transient ZP bytes, all inside the common 31-byte window.
D24B_sn0 = MATH_N+0
D24B_sn1 = MATH_N+1
D24B_sn2 = MATH_N+2
D24B_sdin0 = MATH_D+0
D24B_sdin1 = MATH_D+1
D24B_sdin2 = MATH_D+2
D24B_q0 = MATH_Q+0
D24B_q1 = MATH_Q+1
D24B_q2 = MATH_Q+2
D24B_r0 = MATH_R+0
D24B_r1 = MATH_R+1
D24B_r2 = MATH_R+2
D24B_n0 = ZP_MAIN+$0E
D24B_n1 = ZP_MAIN+$0F
D24B_n2 = ZP_MAIN+$10
D24B_d0 = ZP_MAIN+$11
D24B_d1 = ZP_MAIN+$12
D24B_d2 = ZP_MAIN+$13
D24B_sd0 = ZP_MAIN+$14
D24B_sd1 = ZP_MAIN+$15
D24B_sd2 = ZP_MAIN+$16

* = MATH_SDIV24
    jmp D24B_div_s24
* = MATH_SMOD24
    jmp D24B_div_s24

;ABI
;CPU: mos6502
;Operation: sdiv
;Entry: D24B_div_s24
;Input n: int24 = D24B_sn0, D24B_sn1, D24B_sn2
;Input d: int24 = D24B_sdin0, D24B_sdin1, D24B_sdin2
;Output q: int24 = D24B_q0, D24B_q1, D24B_q2
;Remainder r: int24 = D24B_r0, D24B_r1, D24B_r2
;Region ZP: sg_zp_start..sg_zp_end, cg_zp_start..cg_zp_end
;Region Code: D24B_sg_code_start..D24B_sg_code_end, D24B_cg_code_start..D24B_cg_code_end
;End ABI
; ============================================================================
; FIREMONGER C64 DIVISION REFERENCE — PUBLICATION COPY
; Family       : sdiv24
; Tier         : deep-practical
; Target       : NMOS 6502/6510, decimal mode clear
; Measurement  : canonical 2,097,152-case SplitMix64 corpus; seed $C0FFEE where random
; Timing       : entry instruction through final RTS; caller JSR excluded
; Avg cycles   : 238.764977
; Min / Max    : 110 / 5475
; Stddev       : 284.201967
; Resident     : 373 bytes (Code 373 + Data 0); ZP 18 bytes separate
; Validation   : 2097152 cases, 0 errors
; Edge suite   : 19950 cases in canonical run, 0 errors
; Architecture : Proved |n|>=|d| enters practical unsigned subtraction state directly.
;
; NOTE: this publication block is comments only and does not alter the exact
; assembled image that produced the result. Raw canonical JSON is supplied
; beside the source when available. See TECHNICAL_ASSESSMENT.md for caveats.
; ============================================================================

* = REG_KERNEL+$1600
D24B_sg_code_start:
D24B_div_s24:
        ; Signed divide-by-D24B_zero check before magnitude formation.
        lda D24B_sdin0
        ora D24B_sdin1
        ora D24B_sdin2
        bne D24B_s_dnz
D24B_s_zero:
        lda #0
        sta D24B_q0
        sta D24B_q1
        sta D24B_q2
        sta D24B_r0
        sta D24B_r1
        sta D24B_r2
        sec
        rts
D24B_s_dnz:
        lda D24B_sdin2
        bmi D24B_s_dneg
D24B_s_dpos:
        lda D24B_sdin0
        sta D24B_d0
        lda D24B_sdin1
        sta D24B_d1
        lda D24B_sdin2
        sta D24B_d2
        bpl D24B_s_nmake
D24B_s_dneg:
        lda #0
        sec
        sbc D24B_sdin0
        sta D24B_d0
        lda #0
        sbc D24B_sdin1
        sta D24B_d1
        lda #0
        sbc D24B_sdin2
        sta D24B_d2
D24B_s_nmake:
        lda D24B_sn2
        bmi D24B_s_nneg
D24B_s_npos:
        lda D24B_sn0
        sta D24B_n0
        lda D24B_sn1
        sta D24B_n1
        lda D24B_sn2
        sta D24B_n2
        bpl D24B_s_call
D24B_s_nneg:
        lda #0
        sec
        sbc D24B_sn0
        sta D24B_n0
        lda #0
        sbc D24B_sn1
        sta D24B_n1
        lda #0
        sbc D24B_sn2
        sta D24B_n2
D24B_s_call:
        ; Magnitudes are now available: resolve q=0 before the unsigned core.
        lda D24B_n2
        cmp D24B_d2
        bcc D24B_s_qzero
        bne D24B_s_do_unsigned
        lda D24B_n1
        cmp D24B_d1
        bcc D24B_s_qzero
        bne D24B_s_do_unsigned
        lda D24B_n0
        cmp D24B_d0
        bcc D24B_s_qzero
D24B_s_do_unsigned:
        lda D24B_d2
        beq D24B_s_u146_low
        sec
        lda D24B_n0
        sbc D24B_d0
        sta D24B_r0
        lda D24B_n1
        sbc D24B_d1
        sta D24B_r1
        lda D24B_n2
        sbc D24B_d2
        sta D24B_r2
        ldx #1
        sec
        jsr D24B_chain
        jmp D24B_s_after_unsigned
D24B_s_u146_low:
        jsr D24B_div_u24
D24B_s_after_unsigned:

        ; Remainder has the sign of the original dividend.
        lda D24B_sn2
        bpl D24B_s_rdone
        lda #0
        sec
        sbc D24B_r0
        sta D24B_r0
        lda #0
        sbc D24B_r1
        sta D24B_r1
        lda #0
        sbc D24B_r2
        sta D24B_r2
D24B_s_rdone:
        ; Quotient sign = sign(n) XOR sign(d).
        lda D24B_sn2
        eor D24B_sdin2
        bpl D24B_s_success
        lda #0
        sec
        sbc D24B_q0
        sta D24B_q0
        lda #0
        sbc D24B_q1
        sta D24B_q1
        lda #0
        sbc D24B_q2
        sta D24B_q2
D24B_s_success:
        clc
        rts
D24B_s_qzero:
        lda #0
        sta D24B_q0
        sta D24B_q1
        sta D24B_q2
        lda D24B_sn0
        sta D24B_r0
        lda D24B_sn1
        sta D24B_r1
        lda D24B_sn2
        sta D24B_r2
        clc
        rts
D24B_sg_code_end:

* = REG_KERNEL+$1800
D24B_cg_code_start:
D24B_div_u24:
 lda D24B_d2
 beq D24B_lowd
 lda D24B_n0
 sta D24B_r0
 lda D24B_n1
 sta D24B_r1
 lda D24B_n2
 sta D24B_r2
 ldx #0
 sec
D24B_chain:
 lda D24B_r0
 sbc D24B_d0
 tay
 lda D24B_r1
 sbc D24B_d1
 sta D24B_q1
 lda D24B_r2
 sbc D24B_d2
 bcc D24B_chain_done
 sta D24B_r2
 sty D24B_r0
 lda D24B_q1
 sta D24B_r1
 inx
 bne D24B_chain
D24B_chain_done:
 stx D24B_q0
 !byte $0b,$00
 sta D24B_q1
 sta D24B_q2
 rts
D24B_lowd:
 lda D24B_d0
 ora D24B_d1
 beq D24B_zero
 lda D24B_n0
 sta D24B_q0
 lda D24B_n1
 sta D24B_q1
 lda D24B_n2
 sta D24B_q2
 lda #0
 sta D24B_r0
 sta D24B_r1
 sta D24B_r2
 ldx #24
D24B_loop:
 asl D24B_q0
 rol D24B_q1
 rol D24B_q2
 rol D24B_r0
 rol D24B_r1
 bcs D24B_over
 sec
 lda D24B_r0
 sbc D24B_d0
 tay
 lda D24B_r1
 sbc D24B_d1
 bcc D24B_no
 sta D24B_r1
 sty D24B_r0
 inc D24B_q0
 clc
D24B_no:
 dex
 bne D24B_loop
 rts
D24B_over:
 sec
 lda D24B_r0
 sbc D24B_d0
 sta D24B_r0
 lda D24B_r1
 sbc D24B_d1
 sta D24B_r1
 inc D24B_q0
 clc
 bcc D24B_no
D24B_zero:
 ldx #5
D24B_zloop:
 sta D24B_q0,x
 dex
 bpl D24B_zloop
 sec
 rts
D24B_cg_code_end:
