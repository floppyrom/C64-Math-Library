; Division tail-latency escape overlay.
; Requires the Repose UDIV24 source, direct split-tail UDIV32/16 source and
; four-ZP UDIV32/32 live-high source to have been included earlier.
;
; Goals:
;   * preserve the UDIV24 q=0 and low-quotient paths;
;   * route pathological UDIV24 narrow tails through UDIV32/16;
;   * route 16-bit UDIV32/32 divisors through UDIV32/16;
;   * handle the 17-bit divisor band ($00010000-$0001FFFF) with a dedicated
;     16-step divider, because its quotient is provably <=16 bits.
; Carry returned by UDIV32/16 is preserved by cleanup LDA/STA instructions.

; UDIV24 reaches this point only for D2=0 and N>=D.  The Repose shifted-divisor
; tail is cheaper for small quotients, so escape only when N >= D<<8, i.e.
; quotient >= 256.
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

; UDIV32/32 width dispatch, exactly filling the original $064F-$0661 window.
; D3!=0 is ordinary wide division.  With D3=0, LSR distinguishes D2=0
; (16-bit divisor), D2=1 (17-bit divisor), and D2>=2 (ordinary wide).
; For the overwhelmingly common D3!=0 wide case this is four cycles faster than
; the previous LDA/ORA/BNE sequence; no new hot-path tax is introduced.
* = UD32_L064F
    lda MATH_D+3
    bne UD32_L0662
    lda MATH_D+2
    beq DIVLAT_UD32_NARROW_STUB
    lsr
    bne UD32_L0662
    jmp DIVLAT_UD32_D17_PREP
DIVLAT_UD32_NARROW_STUB:
    jmp DIVLAT_UD32_NARROW

; Reuse the now-unreachable legacy 32/8 block for the shared latency helpers.
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
    ; UDIV32/16 already owns the exact divide-by-zero ABI: C=1 and zero Q/R.
    ; Removing the duplicate zero guard frees the preamble space for D17.
    jsr MATH_UDIV32_16
    lda #0
    sta MATH_R+2
    sta MATH_R+3
    rts

DIVLAT_UD32_D17_PREP:
    ; Only use the 16-step D17 engine once N>=2^24.  For D17 this implies a
    ; quotient >=128; smaller quotients stay on the existing live-high q1/q2
    ; path.  A is already zero here: D2 was exactly 1 and LSR produced 0.
    ; LDX preserves that zero for the output clears.
    ldx MATH_N+3
    bne DIVLAT_UD32_D17_USE
    jmp UD32_L0662
DIVLAT_UD32_D17_USE:
    sta MATH_Q+2
    sta MATH_Q+3
    sta MATH_R+3
    jmp DIVLAT_UD32_D17

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

; The legacy 32/16 restoring fallback is unreachable now that D2=0 routes to
; MATH_UDIV32_16.  Its 100-byte island ($C433-$C496 reference) is therefore
; repurposed for an exact 32/17 divider.  For D in $10000-$1FFFF the high
; 16-bit numerator is already a valid initial remainder (<D), so only the low
; 16 numerator bits need to be consumed.
;
; UD32_SHIFT+0/+1 hold the low 16 remainder bits. Y holds bit 16.  Each
; iteration shifts one source bit from Q0:Q1 into the remainder and, when the
; remainder reaches D, subtracts D and sets the newly generated quotient bit.
; X is the 16-step loop counter. Inputs N/D remain untouched.
* = UD32_OLD_C28A
DIVLAT_UD32_D17:
    ; A=0 from the width classifier / helper; use the island's final spare byte
    ; to establish the 17th remainder bit in Y.
    tay
    lda MATH_N+0
    sta MATH_Q+0
    lda MATH_N+1
    sta MATH_Q+1
    lda MATH_N+2
    sta UD32_SHIFT+0
    lda MATH_N+3
    sta UD32_SHIFT+1
    ldx #16
DIVLAT_D17_LOOP:
    asl MATH_Q+0
    rol MATH_Q+1
    rol UD32_SHIFT+0
    rol UD32_SHIFT+1
    tya
    rol
    tay
    cpy #1
    bcc DIVLAT_D17_NEXT
    bne DIVLAT_D17_SUB
    lda UD32_SHIFT+1
    cmp MATH_D+1
    bcc DIVLAT_D17_NEXT
    bne DIVLAT_D17_SUB
    lda UD32_SHIFT+0
    cmp MATH_D+0
    bcc DIVLAT_D17_NEXT
DIVLAT_D17_SUB:
    sec
    lda UD32_SHIFT+0
    sbc MATH_D+0
    sta UD32_SHIFT+0
    lda UD32_SHIFT+1
    sbc MATH_D+1
    sta UD32_SHIFT+1
    tya
    sbc #1
    tay
    inc MATH_Q+0
DIVLAT_D17_NEXT:
    dex
    bne DIVLAT_D17_LOOP
    lda UD32_SHIFT+0
    sta MATH_R+0
    lda UD32_SHIFT+1
    sta MATH_R+1
    sty MATH_R+2
    clc
    rts
DIVLAT_D17_END:
