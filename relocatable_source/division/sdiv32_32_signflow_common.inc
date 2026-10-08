; SDIV32/32 public-unsigned reuse wrapper.
; Profile wrapper defines SD3232_BASE before sourcing this file.
;
; Public N/D are preserved at the API boundary. For nonzero divisors, original
; sign bytes are held transiently on the CPU stack while negative operands are
; converted in place to magnitudes. The selected public MATH_UDIV32_32 is then
; called directly; because it preserves its inputs, negative operands can be
; restored in place afterward. Result signs are finally rediscovered from the
; restored public inputs. This keeps signed division automatically coupled to
; the profile's fastest qualified unsigned 32/32 core with no permanent ZP.

* = SD3232_BASE
SD3232_ENTRY:
        ; Preserve canonical divide-by-zero behavior without touching N/D.
        lda MATH_D+0
        ora MATH_D+1
        ora MATH_D+2
        ora MATH_D+3
        bne SD3232_DNZ
        jmp MATH_UDIV32_32

SD3232_DNZ:
        ; Save only the original sign bytes. Nested JSR use is safe: the
        ; unsigned divider returns with its own stack balanced before these PLAs.
        lda MATH_N+3
        pha
        lda MATH_D+3
        pha

        ; Temporarily normalize N32 in place only when negative.
        lda MATH_N+3
        bpl SD3232_N_READY
        lda #0
        sec
        sbc MATH_N+0
        sta MATH_N+0
        lda #0
        sbc MATH_N+1
        sta MATH_N+1
        lda #0
        sbc MATH_N+2
        sta MATH_N+2
        lda #0
        sbc MATH_N+3
        sta MATH_N+3
SD3232_N_READY:

        ; Temporarily normalize D32 in place only when negative.
        lda MATH_D+3
        bpl SD3232_D_READY
        lda #0
        sec
        sbc MATH_D+0
        sta MATH_D+0
        lda #0
        sbc MATH_D+1
        sta MATH_D+1
        lda #0
        sbc MATH_D+2
        sta MATH_D+2
        lda #0
        sbc MATH_D+3
        sta MATH_D+3
SD3232_D_READY:
        jsr MATH_UDIV32_32

        ; Restore D first (its sign byte was pushed last).
        pla
        bpl SD3232_D_RESTORED
        lda #0
        sec
        sbc MATH_D+0
        sta MATH_D+0
        lda #0
        sbc MATH_D+1
        sta MATH_D+1
        lda #0
        sbc MATH_D+2
        sta MATH_D+2
        lda #0
        sbc MATH_D+3
        sta MATH_D+3
SD3232_D_RESTORED:

        ; Restore N from its magnitude when the original numerator was negative.
        pla
        bpl SD3232_N_RESTORED
        lda #0
        sec
        sbc MATH_N+0
        sta MATH_N+0
        lda #0
        sbc MATH_N+1
        sta MATH_N+1
        lda #0
        sbc MATH_N+2
        sta MATH_N+2
        lda #0
        sbc MATH_N+3
        sta MATH_N+3
SD3232_N_RESTORED:

        ; Quotient sign = sign(N) XOR sign(D).
        lda MATH_N+3
        eor MATH_D+3
        bpl SD3232_Q_DONE
        lda #0
        sec
        sbc MATH_Q+0
        sta MATH_Q+0
        lda #0
        sbc MATH_Q+1
        sta MATH_Q+1
        lda #0
        sbc MATH_Q+2
        sta MATH_Q+2
        lda #0
        sbc MATH_Q+3
        sta MATH_Q+3
SD3232_Q_DONE:

        ; Remainder sign follows the original numerator.
        lda MATH_N+3
        bpl SD3232_SUCCESS
        lda #0
        sec
        sbc MATH_R+0
        sta MATH_R+0
        lda #0
        sbc MATH_R+1
        sta MATH_R+1
        lda #0
        sbc MATH_R+2
        sta MATH_R+2
        lda #0
        sbc MATH_R+3
        sta MATH_R+3
SD3232_SUCCESS:
        clc
        rts
SD3232_END:
