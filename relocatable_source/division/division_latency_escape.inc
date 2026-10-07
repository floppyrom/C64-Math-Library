; Division tail-latency escape helpers.
; Requires the Repose UDIV24 source, direct split-tail UDIV32/16 source and
; four-ZP UDIV32/32 live-high source to have been included earlier.
;
; UDIV24 performs its crossover test at DU24F_overshoot, where X already
; encodes quotient bit length.  q<256 retains the original Repose tail with
; only CPX/BCS overhead; q>=256 comes here.  The 32/32 wide-divisor hot path
; remains byte-for-byte unchanged and only its already-narrow branch is
; redirected through the bounded 32/16 engine.

; UDIV32/32: retain the exact D3/D2 width test. Wide divisors branch to the
; existing live-high path with identical instructions/cycles.
* = UD32_L064F
    lda MATH_D+3
    ora MATH_D+2
    bne UD32_L0662
    jmp DIVLAT_UD32_NARROW

; The redirected narrow path makes the legacy internal 32/8 block unreachable.
; Reuse its beginning for both helpers, avoiding new resident allocation.
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
    ; width dispatch.
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
DIVLAT_END:
