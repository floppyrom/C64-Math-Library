; V1 Balanced direct-output SDIV16/SMOD16 from q2-special native Pareto core.
; Direct stable-memory signed ABI; executable-disjoint private magnitude engine.
; Six transient ZP bytes, all inside the common 31-byte window.
D16B_sn0 = MATH_N+0
D16B_sn1 = MATH_N+1
D16B_sd_in0 = MATH_D+0
D16B_sd_in1 = MATH_D+1
D16B_sdin0 = MATH_D+0
D16B_sdin1 = MATH_D+1
D16B_q0 = MATH_Q+0
D16B_q1 = MATH_Q+1
D16B_r0 = MATH_R+0
D16B_r1 = MATH_R+1
D16B_n0 = ZP_MAIN+$0E
D16B_n1 = ZP_MAIN+$0F
D16B_d0 = ZP_MAIN+$10
D16B_d1 = ZP_MAIN+$11
D16B_sd0 = ZP_MAIN+$12
D16B_sd1 = ZP_MAIN+$13

* = MATH_SDIV16
    jmp D16B_div_s16
* = MATH_SMOD16
    jmp D16B_div_s16

;ABI
;CPU: mos6502
;Operation: sdiv
;Entry: D16B_div_s16
;Input n: int16 = D16B_sn0, D16B_sn1
;Input d: int16 = D16B_sd_in0, D16B_sd_in1
;Output q: int16 = D16B_q0, D16B_q1
;Remainder r: int16 = D16B_r0, D16B_r1
;Region ZP: sg_zp_start..sg_zp_end, cg_zp_start..cg_zp_end
;Region Code: D16B_sg_code_start..D16B_sg_code_end, D16B_cg_code_start..D16B_cg_code_end
;End ABI
; ============================================================================
; FIREMONGER C64 DIVISION REFERENCE — PUBLICATION COPY
; Family       : sdiv16
; Tier         : q2-special
; Target       : NMOS 6502/6510, decimal mode clear
; Measurement  : canonical 2,097,152-case SplitMix64 corpus; seed $C0FFEE where random
; Timing       : entry instruction through final RTS; caller JSR excluded
; Avg cycles   : 152.570305
; Min / Max    : 36 / 1427
; Stddev       : 136.540434
; Resident     : 442 bytes (Code 442 + Data 0); ZP 14 bytes separate
; Validation   : 2097152 cases, 0 errors
; Edge suite   : 10276 cases in canonical run, 0 errors
; Architecture : Signed front end feeding the q=2-specialized unsigned /256 core.
;
; NOTE: this publication block is comments only and does not alter the exact
; assembled image that produced the result. Raw canonical JSON is supplied
; beside the source when available. See TECHNICAL_ASSESSMENT.md for caveats.
; ============================================================================

; ============================================================================
; DIV_U16 / 256-BYTE CLASS — Q=2-SPECIALIZED RECORD
; Fast unsigned 16/16 division for NMOS 6502/6510
;
; Hard target:
;       executable code <= 256 bytes
;
; Final source:
;       executable code = 255 bytes ($1000-$10fe)
;       ZP ABI           =   8 bytes ($10-$17)
;       ZP scratch       =   2 bytes ($18-$19)
;       tables           =   0 bytes
;
; ABI:
;       D16B_n1:D16B_n0  unsigned 16-bit dividend       (preserved)
;       D16B_d1:D16B_d0  unsigned 16-bit divisor        (preserved)
;       D16B_q1:D16B_q0  unsigned 16-bit quotient
;       D16B_r1:D16B_r0  unsigned 16-bit remainder
;       C=0    success
;       C=1    divide by zero, q=r=0
;
;       A/X/Y clobbered.
;       Decimal mode MUST be clear on entry (D=0).
;
; CPU note:
;       Uses stable NMOS undocumented LAX zp ($a7) and ANC #imm ($0b).
;       Intended for NMOS 6502/6510 machines such as the C64.
;
; Design summary
; --------------
; The 256-byte budget is large enough for a genuinely different tail rather
; than a larger version of the 128-byte subtraction/restoring hybrid.
;
;   1. Resolve q=0 and q=1 immediately.  These dominate uniformly random
;      unsigned operand pairs.
;
;   2. Once q>=2 is proved, the SECOND subtraction is mathematically
;      guaranteed to succeed, so it is unrolled with no failure test.
;
;   3. Continue cheap repeated subtraction up to K=5 using X=q-K. Successful
;      subtraction leaves C=1 for the next SBC; INX preserves it. Because X is
;      negative before K and zero at K, BMI is the complete loop/cutoff test.
;
;   4. At K=5 keep the residual
;
;            r = n - 5*d
;
;      and divide only that residual with a shifted-divisor binary tail.
;      If t=floor(r/d), the final quotient is q=5+t.
;
; The shifted tail scales with the bit length of t rather than running a fixed
; 16 restoring iterations.  Its successful/failed trial subtraction leaves
; the quotient bit directly in C; ROL D16B_q0 / ROL D16B_q1 consumes that carry, avoiding
; a separate INC/OR instruction.
;
; D16B_sd1:D16B_sd0 is a destructively shifted COPY of the divisor.  The original D16B_d1:D16B_d0
; therefore remains preserved with no SMC or stack restore traffic.
;
; Physical layout still matters.  The enhanced routine occupies 255 bytes and,
; at the supplied $1000 origin, remains wholly within one page.
; The common alignment-overshoot path shares its low-byte ROR with the normal
; descending loop, and the rare bit-15 alignment exit uses a guaranteed BPL.
;
; Additional state specialization:
;   q=2 is the largest remaining single quotient class (about 1/12 of uniform
;   input pairs).  The guaranteed second subtraction already leaves the final
;   remainder in D16B_r1:D16B_r0, so a dedicated nine-byte q=2 return avoids both loading
;   X=q-K and decoding that biased state.  Moving LDX after the q=2 branch is
;   cycle-neutral for q>=3.
;
; Validation of this exact release image in the local NMOS instruction model:
;   - code size: 255 bytes ($1000-$10fe)
;   - 576 structured edge pairs: 0 errors, inputs preserved
;   - 1,000,000 random pairs, seed $C0FFEE: 84.493770 average
;   - 5,000,000 random pairs, seed $C0FFEE: 84.546491 average
;   - RTS included; caller JSR excluded; min/max on 1M: 31 / 1364
;   - all relative branches assemble in range
; ============================================================================

; ---- zero-page ABI + scratch ------------------------------------------------

; ---- code -------------------------------------------------------------------

* = REG_KERNEL+$1200
D16B_sg_code_start:
D16B_div_s16:
        ; Normalize divisor into the proven unsigned core's D16B_d1:D16B_d0.
        ; Low-byte zero testing is deferred to the rare d.high==0 class.
        !byte $AF,<MATH_D+1,>MATH_D+1          ; LAX signed divisor high
        beq D16B_s_d_high_zero
        bmi D16B_s_d_negative
D16B_s_d_positive:
        lda D16B_sd_in0
        sta D16B_d0
        stx D16B_d1
        jmp D16B_s_make_n
D16B_s_d_high_zero:
        lda D16B_sd_in0
        bne D16B_s_d_low_nonzero
        jmp D16B_s_zero
D16B_s_d_low_nonzero:
        sta D16B_d0
        stx D16B_d1                   ; X=0
        jmp D16B_s_make_n
D16B_s_d_negative:
        lda #0
        sec
        sbc D16B_sd_in0
        sta D16B_d0
        lda #0
        sbc D16B_sd_in1
        sta D16B_d1
D16B_s_make_n:
        !byte $AF,<MATH_N+1,>MATH_N+1            ; LAX signed dividend high
        bmi D16B_s_n_negative
        lda D16B_sn0
        sta D16B_n0
        stx D16B_n1
        jmp D16B_s_q0_test
D16B_s_n_negative:
        lda #0
        sec
        sbc D16B_sn0
        sta D16B_n0
        lda #0
        sbc D16B_sn1
        sta D16B_n1

        ; Resolve |q|=0 and |q|=1 before entering the unsigned core.
D16B_s_q0_test:
        !byte $a7,D16B_n1             ; A=X=|n| high
        cmp D16B_d1
        bcc D16B_s_qzero
        bne D16B_s_first_sub
        lda D16B_n0
        cmp D16B_d0
        bcc D16B_s_qzero
D16B_s_first_sub:
        lda D16B_n0                   ; compare above guarantees C=1
        sbc D16B_d0
        sta D16B_r0
        txa
        sbc D16B_d1
        sta D16B_r1
        cmp D16B_d1
        bcc D16B_s_qone
        bne D16B_s_qge2
        lda D16B_r0
        cmp D16B_d0
        bcc D16B_s_qone
D16B_s_qge2:
        ; Exact state expected by the q>=2 continuation: A:D16B_r0=|n|-|d|, C=1.
        lda D16B_r1
        jsr D16B_qge2
        jmp D16B_s_sign_outputs

D16B_s_qzero:
        lda #0
        sta D16B_q0
        sta D16B_q1
        lda D16B_sn0
        sta D16B_r0
        lda D16B_sn1
        sta D16B_r1
        clc
        rts

D16B_s_qone:
        lda #1
        sta D16B_q0
        lda #0
        sta D16B_q1
        ; D16B_r1:D16B_r0 already holds |n|-|d|.

D16B_s_sign_outputs:
        ; Remainder sign follows original n.
        lda D16B_sn1
        bpl D16B_s_r_done
        lda #0
        sec
        sbc D16B_r0
        sta D16B_r0
        lda #0
        sbc D16B_r1
        sta D16B_r1
D16B_s_r_done:
        ; Quotient sign = sign(n) XOR sign(d).
        lda D16B_sn1
        eor D16B_sd_in1
        bpl D16B_s_success
        lda #0
        sec
        sbc D16B_q0
        sta D16B_q0
        lda #0
        sbc D16B_q1
        sta D16B_q1
D16B_s_success:
        clc
        rts

D16B_s_zero:
        lda #0
        sta D16B_q0
        sta D16B_q1
        sta D16B_r0
        sta D16B_r1
        sec
        rts
D16B_sg_code_end:

* = REG_KERNEL+$1400
D16B_cg_code_start:

D16B_div_u16
        ; A=X=D16B_n1.  High-byte comparison gives the cheapest possible q=0 gate.
        !byte $a7,D16B_n1              ; LAX D16B_n1
        cmp D16B_d1
        bcs D16B_high_ge

D16B_qzero
        lda #0
        sta D16B_q0
        sta D16B_q1
        lda D16B_n0
        sta D16B_r0
        stx D16B_r1
        rts                       ; C=0 from compare/subtraction

D16B_high_ge
        bne D16B_high_gt

        ; Equal high bytes.  If D16B_n0<D16B_d0, q=0.  Otherwise the first subtraction
        ; has succeeded.  For D16B_d1>=1 that immediately proves q=1, because the
        ; remainder high byte becomes zero while d>=256.
        lda D16B_n0
        sbc D16B_d0                    ; entry C=1 from equal CMP D16B_d1
        bcc D16B_qzero

        ; Store the low remainder once, then test original D16B_n1 in X. TXA keeps
        ; the successful subtraction carry live, so pure 16/8 needs no SEC.
        sta D16B_r0
        txa
        bne D16B_equal_q1

        ; Here D16B_n1=D16B_d1=0: pure 16/8, with one subtraction already complete.
        lda D16B_d0
        beq D16B_div_zero
        stx D16B_r1                    ; X=0 is the correct remainder high byte
        ldx #$fc                  ; q-K = 1-5
        bcs D16B_small_chain

D16B_div_zero
        stx D16B_q0                    ; X=0 on every divide-by-zero entry
        stx D16B_q1
        stx D16B_r0
        stx D16B_r1
        sec
        rts

D16B_equal_q1
        !byte $0b,$00             ; ANC #0: A=0 and C=0 together
        sta D16B_r1
        sta D16B_q1
        lda #1
        sta D16B_q0
        rts

D16B_high_gt
        ; Perform the first subtraction, then test whether a second divisor can
        ; fit.  q=1 is common, so its return remains short.
        lda D16B_n0
        sbc D16B_d0                    ; C=1 from D16B_n1>D16B_d1 CMP
        sta D16B_r0
        txa                       ; X still holds original D16B_n1
        sbc D16B_d1
        cmp D16B_d1
        bcc D16B_qone
        bne D16B_qge2

        ; Equal high bytes need a low-byte comparison to distinguish q=1/2+.
        tax                       ; save remainder high byte
        lda D16B_r0
        cmp D16B_d0
        bcs D16B_qge2_x
        txa

D16B_qone
        sta D16B_r1
        lda #0
        sta D16B_q1
        lda #1
        sta D16B_q0
        rts

D16B_small_done
        ; X carries q-K in two's-complement form and C=0 on every entry here.
        ; ADC #K decodes q directly. ANC #0 then clears both D16B_q1 and success C.
        txa
        adc #5
        sta D16B_q0
        !byte $0b,$00             ; ANC #0: A=0, C=0
        sta D16B_q1
        rts

D16B_qge2_x
        txa                       ; restore high remainder in A
D16B_qge2
        ; A:D16B_r0 is remainder after the first subtraction, and q>=2 is proved.
        ; Check d=0 only on the D16B_d1=0 path.  LDX does not disturb carry.
        ldx D16B_d1
        bne D16B_qge2_nonzero
        ldx D16B_d0
        beq D16B_div_zero

D16B_qge2_nonzero
        ; The second subtraction MUST succeed.
        tay
        lda D16B_r0
        sbc D16B_d0
        sta D16B_r0                    ; guaranteed second subtraction: store directly
        tya
        sbc D16B_d1
        sta D16B_r1

        ; q=2 is common enough to warrant a dedicated return.  CMP supplies
        ; C=1 for the first q>=3 trial; moving LDX below the branch makes that
        ; specialization free on every q>=3 path.
        cmp D16B_d1
        bcs D16B___rx0
        jmp D16B_qtwo
D16B___rx0:
        ldx #$fd                  ; q-K = 2-5 for the q>=3 chain

D16B_small_chain
        ; C=1 is carried directly from the preceding successful compare/trial.
        lda D16B_r0
        sbc D16B_d0
        tay
        lda D16B_r1
        sbc D16B_d1
        bcc D16B_small_done

        sta D16B_r1
        sty D16B_r0
        inx                       ; q increased by one, so X=q-K increases too
        bmi D16B_small_chain           ; still negative => q<K; C=1 is preserved

D16B_small_cutoff
        ; At q=K, avoid the tail when r<d.  Check both bytes exactly.
        cmp D16B_d1
        bcc D16B_small_done
        bne D16B_shift_setup
        lda D16B_r0
        cmp D16B_d0
        bcc D16B_small_done

D16B_shift_setup
        ; r = n - 5*d here.  Preserve d by copying it into two scratch bytes.
        lda D16B_d0
        sta D16B_sd0
        lda D16B_d1
        sta D16B_sd1

        ; X is exactly zero at the K cutoff: reuse that live zero for t=0.
        stx D16B_q0
        stx D16B_q1                    ; X simultaneously remains alignment depth 0
        ldy D16B_r1              ; LDY D16B_r1: cache residual high byte in Y

D16B_align_loop
        ; Try 2*shifted_divisor. Y remains D16B_r1 throughout alignment.
        asl D16B_sd0
        rol D16B_sd1

        ; Compare residual.high (cached Y) against shifted-divisor.high.
        !byte $c4,D16B_sd1             ; CPY D16B_sd1
        bcc D16B_align_undo            ; D16B_r1 < D16B_sd1 => overshot
        bne D16B_align_ok              ; D16B_r1 > D16B_sd1 => definitely fits
        lda D16B_r0
        cmp D16B_sd0
        bcc D16B_align_undo            ; equal high, low too small => overshot

D16B_align_ok
        inx
        ; BIT tests D16B_sd1 bit 7 without disturbing cached Y=D16B_r1.
        !byte $24,D16B_sd1             ; BIT D16B_sd1
        bpl D16B_align_loop
        inx
        bpl D16B_div_bits              ; X is small positive: guaranteed branch

D16B_align_undo
        ; Common termination: undo the high byte first. INX preserves C, so the
        ; low-byte ROR can be shared with the descending-loop back edge.
        lsr D16B_sd1
        inx                       ; number of descending bit positions

D16B_shift_low
        ror D16B_sd0

D16B_div_bits
        ; Trial r -= shifted divisor.  The final SBC carry is exactly the next
        ; quotient bit: C=1 if subtraction fits, C=0 otherwise.
        sec
        lda D16B_r0
        sbc D16B_sd0
        tay
        lda D16B_r1
        sbc D16B_sd1
        bcc D16B_no_take
        sta D16B_r1
        sty D16B_r0

D16B_no_take
        rol D16B_q0                    ; consume subtraction carry as quotient bit
        rol D16B_q1

        ; Preserve the quotient pipeline's C=0 on the final bit by skipping the
        ; now-useless final divisor shift. Nonfinal iterations pay a short
        ; guarded back-edge; the bias addition can then consume C directly.
        dex
        beq D16B_bits_done
        lsr D16B_sd1
        bpl D16B_shift_low             ; guaranteed: LSR always clears N

D16B_bits_done
        ; q = t + K. C is provably zero after the final ROL D16B_q1.
        lda #5
        adc D16B_q0
        sta D16B_q0
        bcc D16B_bias_done             ; taken path already guarantees C=0
        inc D16B_q1
        clc                       ; only rare carry path needs normalization

D16B_bias_done
        rts

D16B_qtwo
        ; The guaranteed second subtraction already committed the remainder.
        lda #2
        sta D16B_q0
        !byte $0b,$00             ; ANC #0: A=0 and success C=0
        sta D16B_q1
        rts
D16B_cg_code_end:

