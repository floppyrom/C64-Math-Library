; Issue #39 — V1/V5 public UMOD8 remainder-only guarded fast path.
; Exact guard D>=32 implies floor(255/D)<=7: no tail, no scratch.
; Small divisors retain the existing original modulo implementation. Public
; quotient bytes, inputs, carry conventions and unowned ZP remain unchanged.
; This is a genuine source-relocatable V1 overlay and reused V5 hybrid donor.
; The original public wrapper after its first 3-byte LDA MATH_N remains
; reachable from the fallback at MATH_UMOD8+3.
* = MATH_UMOD8
    jmp V1_UMOD8_GUARD

* = REG_LOW+$0E00
V1_UMOD8_GUARD:
    lda MATH_D
    cmp #$20
    bcs V1_UMOD8_FAST
    lda MATH_N
    jmp MATH_UMOD8+3
V1_UMOD8_FAST:
    lda MATH_N
V1_UMOD8_TRY_0:
    cmp MATH_D
    bcc V1_UMOD8_DONE
    sbc MATH_D
V1_UMOD8_TRY_1:
    cmp MATH_D
    bcc V1_UMOD8_DONE
    sbc MATH_D
V1_UMOD8_TRY_2:
    cmp MATH_D
    bcc V1_UMOD8_DONE
    sbc MATH_D
V1_UMOD8_TRY_3:
    cmp MATH_D
    bcc V1_UMOD8_DONE
    sbc MATH_D
V1_UMOD8_TRY_4:
    cmp MATH_D
    bcc V1_UMOD8_DONE
    sbc MATH_D
V1_UMOD8_TRY_5:
    cmp MATH_D
    bcc V1_UMOD8_DONE
    sbc MATH_D
V1_UMOD8_TRY_6:
    cmp MATH_D
    bcc V1_UMOD8_DONE
    sbc MATH_D
V1_UMOD8_DONE:
    sta MATH_R
    clc
    rts
