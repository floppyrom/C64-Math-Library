; V3_REU_512K SDIV32/16 shared-magnitude front-end.
; Normalize signed N32/D16 directly into the selected U3216 private state,
; execute the same UDIV32/16 substrate as MATH_UDIV32_16, then reuse the
; already-qualified MULDIV16 signed result tails. Public N/D are preserved.
; This deliberately replaces the older executable-disjoint D32F magnitude core.

* = REG_LOW+$1690
D32F_PUBLIC:
        jmp D32F_DIV_S32_16

* = REG_TABLE+$3200
D32F_DIV_S32_16:
        ; |D| -> U3216 divisor state. Keep public D untouched so its sign can
        ; select the quotient correction after the magnitude divide.
        lda MATH_D+1
        bmi D32F_DNEG
        sta U3216_D1
        ; STA preserves Z from the high-byte load. Positive divisors with a
        ; nonzero high byte can skip the redundant low-byte zero classification.
        beq D32F_DHI_ZERO
        lda MATH_D+0
        sta U3216_D0
        jmp D32F_NSET
D32F_DHI_ZERO:
        lda MATH_D+0
        sta U3216_D0
        bne D32F_NSET
        ; D=0: the unsigned core owns the canonical Q/R/C zero-divisor result.
        jmp U3216_ENTRY

D32F_DNEG:
        lda #0
        sec
        sbc MATH_D+0
        sta U3216_D0
        lda #0
        sbc MATH_D+1
        sta U3216_D1

D32F_NSET:
        lda MATH_N+3
        bmi D32F_NNEG

        ; Positive numerator: copy N32 directly into private magnitude state.
        lda MATH_N+0
        sta U3216_LN0
        lda MATH_N+1
        sta U3216_LN1
        lda MATH_N+2
        sta U3216_N0
        lda MATH_N+3
        sta U3216_N1
        lda MATH_D+1
        bmi D32F_PN
        ; ++ : magnitude result already has final quotient/remainder signs.
        jmp U3216_ENTRY

D32F_PN:
        ; +- : quotient negative, remainder follows positive numerator.
        jsr U3216_ENTRY
        jmp MULDIV16_S_NEG_Q

D32F_NNEG:
        ; |N32| -> U3216 state, low to high so carry propagates naturally.
        lda #0
        sec
        sbc MATH_N+0
        sta U3216_LN0
        lda #0
        sbc MATH_N+1
        sta U3216_LN1
        lda #0
        sbc MATH_N+2
        sta U3216_N0
        lda #0
        sbc MATH_N+3
        sta U3216_N1
        lda MATH_D+1
        bmi D32F_NN

        ; -+ : quotient and remainder both negative.
        jsr U3216_ENTRY
        jsr MULDIV16_S_NEG_R
        jmp MULDIV16_S_NEG_Q

D32F_NN:
        ; -- : quotient positive, remainder follows negative numerator.
        jsr U3216_ENTRY
        jmp MULDIV16_S_NEG_R
