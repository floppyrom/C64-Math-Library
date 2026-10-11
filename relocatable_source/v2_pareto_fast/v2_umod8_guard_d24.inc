; Issue #39 - candidate V2-only guarded remainder UMOD8 (D >= 24).
; The original V2 UMOD8 public wrapper/core remain live as D<24 fallback.
; Private helper: REG_KERNEL+$1323 (reference $5323..$5387, 101 bytes).
; This is a source-level overlay, not a standalone loadable plug-in.
; Preserve N/D, all Q bytes, upper R, and C=1 iff D=0.
* = MATH_UMOD8
    jmp V2_UMOD8_GUARD

* = REG_KERNEL+$1323
V2_UMOD8_GUARD:
    lda MATH_D
    cmp #$18
    bcs V2_UMOD8_FAST
    lda MATH_N
    jmp MATH_UMOD8+3
V2_UMOD8_FAST:
    lda MATH_N
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
    cmp MATH_D
    bcc V2_UMOD8_DONE
    sbc MATH_D
V2_UMOD8_DONE:
    sta MATH_R
    clc
    rts
