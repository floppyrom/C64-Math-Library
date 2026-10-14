; Issue144 B all-input 32/16 quotient+remainder pow2 guard.
; Requires preexisting independently qualified 114-byte Issue39 pow2 helper
; assembled at $0800 (user-owned RAM, not necessarily available).
; Original MATH_UMOD32_16 $3226 remains unmodified; that path handles
; every non-power-of-two divisor, including D=0 with C=1.
; Checked fast path returns complete Q32 and R16, C=0. No additional ZP.
; Only use as an optional profile-specific dispatcher after workload audit:
; uniformly random D16 has an approx 28-cycle regression per call.
!cpu 6510
* = $0900
MATH_UMOD32_16_POW2_GUARDED:
    lda $C014
    ora $C015
    beq fallback
    lda $C014
    sec
    sbc #1
    and $C014
    bne fallback
    lda $C015
    sbc #0
    and $C015
    bne fallback
    jmp $0800
fallback:
    jmp $3226
