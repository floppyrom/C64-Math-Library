; V1 direct UDIV16/UMOD16, 256-class q=2-specialized speed/size knee.
; Direct stable-memory ABI: inputs remain in MATH_N/MATH_D and q/r are written directly.
; NMOS 6510 target; decimal mode must be clear.
* = MATH_UDIV16
    jmp DU16B_div_u16
* = MATH_UMOD16
    jmp DU16B_div_u16

* = REG_KERNEL+$0200
DU16B_cg_code_start:

DU16B_div_u16
        ; A=X=MATH_N+1.  High-byte comparison gives the cheapest possible q=0 gate.
        !byte $AF,<MATH_N+1,>MATH_N+1 ; LAX abs              ; LAX MATH_N+1
        cmp MATH_D+1
        bcs DU16B_high_ge

DU16B_qzero
        lda #0
        sta MATH_Q+0
        sta MATH_Q+1
        lda MATH_N+0
        sta MATH_R+0
        stx MATH_R+1
        rts                       ; C=0 from compare/subtraction

DU16B_high_ge
        bne DU16B_high_gt

        ; Equal high bytes.  If MATH_N+0<MATH_D+0, q=0.  Otherwise the first subtraction
        ; has succeeded.  For MATH_D+1>=1 that immediately proves q=1, because the
        ; remainder high byte becomes zero while d>=256.
        lda MATH_N+0
        sbc MATH_D+0                    ; entry C=1 from equal CMP MATH_D+1
        bcc DU16B_qzero

        ; Store the low remainder once, then test original MATH_N+1 in X. TXA keeps
        ; the successful subtraction carry live, so pure 16/8 needs no SEC.
        sta MATH_R+0
        txa
        bne DU16B_equal_q1

        ; Here MATH_N+1=MATH_D+1=0: pure 16/8, with one subtraction already complete.
        lda MATH_D+0
        beq DU16B_div_zero
        stx MATH_R+1                    ; X=0 is the correct remainder high byte
        ldx #$fc                  ; q-K = 1-5
        bcs DU16B_small_chain

DU16B_div_zero
        stx MATH_Q+0                    ; X=0 on every divide-by-zero entry
        stx MATH_Q+1
        stx MATH_R+0
        stx MATH_R+1
        sec
        rts

DU16B_equal_q1
        !byte $0b,$00             ; ANC #0: A=0 and C=0 together
        sta MATH_R+1
        sta MATH_Q+1
        lda #1
        sta MATH_Q+0
        rts

DU16B_high_gt
        ; Perform the first subtraction, then test whether a second divisor can
        ; fit.  q=1 is common, so its return remains short.
        lda MATH_N+0
        sbc MATH_D+0                    ; C=1 from MATH_N+1>MATH_D+1 CMP
        sta MATH_R+0
        txa                       ; X still holds original MATH_N+1
        sbc MATH_D+1
        cmp MATH_D+1
        bcc DU16B_qone
        bne DU16B_qge2

        ; Equal high bytes need a low-byte comparison to distinguish q=1/2+.
        tax                       ; save remainder high byte
        lda MATH_R+0
        cmp MATH_D+0
        bcs DU16B_qge2_x
        txa

DU16B_qone
        sta MATH_R+1
        lda #0
        sta MATH_Q+1
        lda #1
        sta MATH_Q+0
        rts

DU16B_small_done
        ; X carries q-K in two's-complement form and C=0 on every entry here.
        ; ADC #K decodes q directly. ANC #0 then clears both MATH_Q+1 and success C.
        txa
        adc #5
        sta MATH_Q+0
        !byte $0b,$00             ; ANC #0: A=0, C=0
        sta MATH_Q+1
        rts

DU16B_qge2_x
        txa                       ; restore high remainder in A
DU16B_qge2
        ; A:MATH_R+0 is remainder after the first subtraction, and q>=2 is proved.
        ; Check d=0 only on the MATH_D+1=0 path.  LDX does not disturb carry.
        ldx MATH_D+1
        bne DU16B_qge2_nonzero
        ldx MATH_D+0
        beq DU16B_div_zero

DU16B_qge2_nonzero
        ; The second subtraction MUST succeed.
        tay
        lda MATH_R+0
        sbc MATH_D+0
        sta MATH_R+0                    ; guaranteed second subtraction: store directly
        tya
        sbc MATH_D+1
        sta MATH_R+1

        ; q=2 is common enough to warrant a dedicated return.  CMP supplies
        ; C=1 for the first q>=3 trial; moving LDX below the branch makes that
        ; specialization free on every q>=3 path.
        cmp MATH_D+1
        bcs DU16B___r0
        jmp DU16B_qtwo
DU16B___r0:
        ldx #$fd                  ; q-K = 2-5 for the q>=3 chain

DU16B_small_chain
        ; C=1 is carried directly from the preceding successful compare/trial.
        lda MATH_R+0
        sbc MATH_D+0
        tay
        lda MATH_R+1
        sbc MATH_D+1
        bcc DU16B_small_done

        sta MATH_R+1
        sty MATH_R+0
        inx                       ; q increased by one, so X=q-K increases too
        bmi DU16B_small_chain           ; still negative => q<K; C=1 is preserved

DU16B_small_cutoff
        ; At q=K, avoid the tail when r<d.  Check both bytes exactly.
        cmp MATH_D+1
        bcc DU16B_small_done
        bne DU16B_shift_setup
        lda MATH_R+0
        cmp MATH_D+0
        bcc DU16B_small_done

DU16B_shift_setup
        ; r = n - 5*d here.  Preserve d by copying it into two scratch bytes.
        lda MATH_D+0
        sta ZP_MAIN+$0E
        lda MATH_D+1
        sta ZP_MAIN+$0F

        ; X is exactly zero at the K cutoff: reuse that live zero for t=0.
        stx MATH_Q+0
        stx MATH_Q+1                    ; X simultaneously remains alignment depth 0
        ldy MATH_R+1              ; LDY MATH_R+1: cache residual high byte in Y

DU16B_align_loop
        ; Try 2*shifted_divisor. Y remains MATH_R+1 throughout alignment.
        asl ZP_MAIN+$0E
        rol ZP_MAIN+$0F

        ; Compare residual.high (cached Y) against shifted-divisor.high.
        !byte $c4,ZP_MAIN+$0F             ; CPY ZP_MAIN+$0F
        bcc DU16B_align_undo            ; MATH_R+1 < ZP_MAIN+$0F => overshot
        bne DU16B_align_ok              ; MATH_R+1 > ZP_MAIN+$0F => definitely fits
        lda MATH_R+0
        cmp ZP_MAIN+$0E
        bcc DU16B_align_undo            ; equal high, low too small => overshot

DU16B_align_ok
        inx
        ; BIT tests ZP_MAIN+$0F bit 7 without disturbing cached Y=MATH_R+1.
        !byte $24,ZP_MAIN+$0F             ; BIT ZP_MAIN+$0F
        bpl DU16B_align_loop
        inx
        bpl DU16B_div_bits              ; X is small positive: guaranteed branch

DU16B_align_undo
        ; Common termination: undo the high byte first. INX preserves C, so the
        ; low-byte ROR can be shared with the descending-loop back edge.
        lsr ZP_MAIN+$0F
        inx                       ; number of descending bit positions

DU16B_shift_low
        ror ZP_MAIN+$0E

DU16B_div_bits
        ; Trial r -= shifted divisor.  The final SBC carry is exactly the next
        ; quotient bit: C=1 if subtraction fits, C=0 otherwise.
        sec
        lda MATH_R+0
        sbc ZP_MAIN+$0E
        tay
        lda MATH_R+1
        sbc ZP_MAIN+$0F
        bcc DU16B_no_take
        sta MATH_R+1
        sty MATH_R+0

DU16B_no_take
        rol MATH_Q+0                    ; consume subtraction carry as quotient bit
        rol MATH_Q+1

        ; Preserve the quotient pipeline's C=0 on the final bit by skipping the
        ; now-useless final divisor shift. Nonfinal iterations pay a short
        ; guarded back-edge; the bias addition can then consume C directly.
        dex
        beq DU16B_bits_done
        lsr ZP_MAIN+$0F
        bpl DU16B_shift_low             ; guaranteed: LSR always clears N

DU16B_bits_done
        ; q = t + K. C is provably zero after the final ROL MATH_Q+1.
        lda #5
        adc MATH_Q+0
        sta MATH_Q+0
        bcc DU16B_bias_done             ; taken path already guarantees C=0
        inc MATH_Q+1
        clc                       ; only rare carry path needs normalization

DU16B_bias_done
        rts

DU16B_qtwo
        ; The guaranteed second subtraction already committed the remainder.
        lda #2
        sta MATH_Q+0
        !byte $0b,$00             ; ANC #0: A=0 and success C=0
        sta MATH_Q+1
        rts
DU16B_cg_code_end:

