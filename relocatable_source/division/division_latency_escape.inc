; Division tail-latency escape overlay.
; Requires the Repose UDIV24 source, direct split-tail UDIV32/16 source and
; four-ZP UDIV32/32 live-high source to have been included earlier.
;
; Goals:
;   * preserve the UDIV24 q=0 hot exit exactly;
;   * preserve the UDIV32/32 wide-divisor hot path exactly;
;   * route only already-detected narrow pathological tails through UDIV32/16.
; Carry returned by UDIV32/16 is preserved by all cleanup instructions below.

; UDIV24: D2=0 and N>=D has already passed the cheap q=0 checks.
; Replace only the slow shifted-divisor setup with a zero-extended UDIV32/16.
* = DU24F_low_tail0
    jmp DIVLAT_DU24_NARROW

; UDIV32/32: retain the exact D3/D2 width test. Wide divisors branch to the
; existing live-high path with identical instructions/cycles; narrow divisors
; use the new 32/16 engine instead of the legacy 32/16 and 32/8 loops.
* = UD32_L064F
    lda MATH_D+3
    ora MATH_D+2
    bne UD32_L0662
    jmp DIVLAT_UD32_NARROW

; The narrow dispatch above makes the legacy internal 32/8 block unreachable.
; Reuse the beginning of that already-owned block for both helpers, avoiding
; any new resident allocation.
* = UD32_OLD_C23D
DIVLAT_DU24_NARROW:
    ; UDIV24 owns N[0..2]; preserve the adjacent N[3] byte while zero-extending.
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
    jsr MATH_UDIV32_16
    lda #0
    sta MATH_R+2
    sta MATH_R+3
    rts
DIVLAT_END:
