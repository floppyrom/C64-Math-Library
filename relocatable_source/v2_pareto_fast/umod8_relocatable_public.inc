; Issue39 V2 Pareto Fast guarded remainder-only UMOD8.
; Public entry keeps old wrapper bytes from +3 onward for D<32 fallback.
; D>=32 implies quotient<=7; 7 accumulator-only CMP/SBC steps.
; No ZP growth; MATH_Q, MATH_N, MATH_D and high result sentinels preserved.
* = MATH_UMOD8
    jmp V2_UMOD8_GUARD
    sta ZP_MAIN+$0E
    lda MATH_D
    sta ZP_MAIN+$0F
    jsr REG_KERNEL+$1212
    sta MATH_R
    rts

* = REG_LOW+$0E00
V2_UMOD8_GUARD:
    lda MATH_D
    cmp #$20
    bcs V2_UMOD8_FAST
    lda MATH_N
    jmp MATH_UMOD8+3
V2_UMOD8_FAST:
    lda MATH_N
V2_UMOD8_TRY_0:
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_TRY_1:
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_TRY_2:
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_TRY_3:
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_TRY_4:
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_TRY_5:
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_TRY_6:
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_DONE:
    sta MATH_R
    clc
    rts
