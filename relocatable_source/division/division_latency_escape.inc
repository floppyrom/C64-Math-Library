; Division tail-latency escape overlay.
; Requires the Repose UDIV24 source, direct split-tail UDIV32/16 source and
; four-ZP UDIV32/32 live-high source to have been included earlier.
;
; Goals:
;   * preserve the UDIV24 q=0 and low-quotient paths;
;   * preserve the UDIV32/32 wide-divisor hot path exactly;
;   * route only proven pathological narrow tails through UDIV32/16.
; Carry returned by UDIV32/16 is preserved by all cleanup instructions below.

; UDIV24 reaches this point only for D2=0 and N>=D.  The Repose shifted-divisor
; tail is cheaper for small quotients, so escape only when N >= D<<8, i.e.
; quotient >= 256.  This removes the earlier low-quotient regressions while
; retaining the large bounded-latency win.
* = DU24F_low_tail0
    lda MATH_N+2
    cmp MATH_D+1
    bcc DIVLAT_DU24_OLD_STUB
    bne DIVLAT_DU24_NEW_STUB
    lda MATH_N+1
    cmp MATH_D+0
    bcc DIVLAT_DU24_OLD_STUB
DIVLAT_DU24_NEW_STUB:
    jmp DIVLAT_DU24_NARROW
DIVLAT_DU24_OLD_STUB:
    jmp DIVLAT_DU24_OLD

; UDIV32/32: retain the exact D3/D2 width test. Wide divisors branch to the
; existing live-high path with identical instructions/cycles.  For narrow
; divisors preserve the legacy divide-by-zero exit, then use UDIV32/16.
* = UD32_L064F
    lda MATH_D+3
    ora MATH_D+2
    bne UD32_L0662
    jmp DIVLAT_UD32_NARROW

; The narrow dispatch above makes the legacy internal 32/8 block unreachable.
; Reuse its beginning for the helpers, avoiding any new resident allocation.
* = UD32_OLD_C23D
DIVLAT_DU24_NARROW:
    ; UDIV24 owns N[0..2]; preserve adjacent N[3] while zero-extending.
    lda MATH_N+3
    pha
    lda #0
    sta MATH_N+3
    jsr MATH_UDIV32_16
    pla
    sta MATH_N+3
    lda #0
    sta MATH_R+2
    rts

DIVLAT_UD32_NARROW:
    ; Preserve the original zero-divisor exit without lengthening the live-high
    ; width dispatch (the legacy zero handler is too far for a relative branch).
    lda MATH_D+1
    ora MATH_D+0
    bne DIVLAT_UD32_NONZERO
    jmp UD32_L072A
DIVLAT_UD32_NONZERO:
    jsr MATH_UDIV32_16
    lda #0
    sta MATH_R+2
    sta MATH_R+3
    rts

; Exact original UDIV24 low-tail setup, used when quotient <256.
DIVLAT_DU24_OLD:
    lda MATH_N+0
    sta MATH_R+0
    lda MATH_N+1
    sta MATH_R+1
    lda MATH_N+2
    sta MATH_R+2
    lda #0
    sta DU24F_tail_bias+1
    jmp DU24F_tail_setup
DIVLAT_END:
