; Direct fixed-point divide adapters for V2/V3/V4.
; Feed (N16 << 8) directly into the selected private 32/16 state rather than
; saving/re-writing/restoring the stable public N vector.
;
; The signed adapter deliberately shares the same U3216 magnitude substrate as
; the unsigned adapter. It owns sign/magnitude preparation, enters U3216_ENTRY
; with |N<<8| and |D|, then reuses the already-published MULDIV16 signed result
; tails for quotient/remainder correction. Keeping those tiny tails shared also
; keeps this adapter inside its historical REG_GAME+$0475..+$04BA slot.

* = REG_GAME+$0435
FXDIV_U_SHL8:
        lda #0
        sta U3216_LN0
        sta U3216_N1
        lda MATH_N+0
        sta U3216_LN1
        lda MATH_N+1
        sta U3216_N0
        lda MATH_D+0
        sta U3216_D0
        lda MATH_D+1
        sta U3216_D1
        jmp U3216_ENTRY

FXDIV_S_SHL8:
        ; Bind |D| once. Public D remains untouched for sign rediscovery.
        lda MATH_D+1
        bmi FXDIV_S_DNEG
        sta U3216_D1
        ; STA preserves Z from the high-byte load. Skip the low-byte zero test
        ; on the common positive high-byte-nonzero class.
        beq FXDIV_S_DHI_ZERO
        lda MATH_D+0
        sta U3216_D0
        jmp FXDIV_S_NSET
FXDIV_S_DHI_ZERO:
        lda MATH_D+0
        sta U3216_D0
        bne FXDIV_S_NSET
        ; D=0: U3216 detects zero before consuming numerator state.
        jmp U3216_ENTRY
FXDIV_S_DNEG:
        lda #0
        sec
        sbc MATH_D+0
        sta U3216_D0
        lda #0
        sbc MATH_D+1
        sta U3216_D1

FXDIV_S_NSET:
        lda #0
        sta U3216_LN0
        sta U3216_N1
        lda MATH_N+1
        bmi FXDIV_S_NNEG

        ; positive N: |N<<8| = 00:N1:N0:00
        lda MATH_N+0
        sta U3216_LN1
        lda MATH_N+1
        sta U3216_N0
        lda MATH_D+1
        bmi FXDIV_S_PN
        ; ++ : unsigned magnitude result already has the final signs.
        jmp U3216_ENTRY
FXDIV_S_PN:
        ; +- : positive remainder, negative quotient.
        jsr U3216_ENTRY
        jmp MULDIV16_S_NEG_Q

FXDIV_S_NNEG:
        ; negative N: form abs(N16) directly in the shifted magnitude slots.
        lda #0
        sec
        sbc MATH_N+0
        sta U3216_LN1
        lda #0
        sbc MATH_N+1
        sta U3216_N0
        lda MATH_D+1
        bmi FXDIV_S_NN

        ; -+ : negative remainder and negative quotient.
        jsr U3216_ENTRY
        jsr MULDIV16_S_NEG_R
        jmp MULDIV16_S_NEG_Q
FXDIV_S_NN:
        ; -- : quotient positive, remainder follows negative numerator.
        jsr U3216_ENTRY
        jmp MULDIV16_S_NEG_R


* = MATH_UDIV16_SHL8
        jmp FXDIV_U_SHL8
* = MATH_SDIV16_SHL8
        jmp FXDIV_S_SHL8
