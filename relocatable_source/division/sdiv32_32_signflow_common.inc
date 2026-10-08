; SDIV32/32 sign-flow optimization.
; Public N/D inputs are preserved, so quotient/remainder signs are rediscovered
; after the private magnitude core instead of being saved in two ZP flag bytes.
; Profile wrapper must define SD3232_ZERO and SD3232_MAG before sourcing this file.

* = REG_GAME+$002C
SD3232_ENTRY:
    lda MATH_D+0
    ora MATH_D+1
    ora MATH_D+2
    ora MATH_D+3
    bne SD3232_DNZ
    jsr SD3232_ZERO
    rts

SD3232_DNZ:
    lda MATH_N+0
    sta ZP_MAIN+$51
    lda MATH_N+1
    sta ZP_MAIN+$52
    lda MATH_N+2
    sta ZP_MAIN+$53
    lda MATH_N+3
    sta ZP_MAIN+$54
    bpl SD3232_N_READY
    sec
    lda #0
    sbc ZP_MAIN+$51
    sta ZP_MAIN+$51
    lda #0
    sbc ZP_MAIN+$52
    sta ZP_MAIN+$52
    lda #0
    sbc ZP_MAIN+$53
    sta ZP_MAIN+$53
    lda #0
    sbc ZP_MAIN+$54
    sta ZP_MAIN+$54
SD3232_N_READY:
    lda MATH_D+0
    sta ZP_MAIN+$55
    lda MATH_D+1
    sta ZP_MAIN+$56
    lda MATH_D+2
    sta ZP_MAIN+$57
    lda MATH_D+3
    sta ZP_MAIN+$58
    bpl SD3232_D_READY
    sec
    lda #0
    sbc ZP_MAIN+$55
    sta ZP_MAIN+$55
    lda #0
    sbc ZP_MAIN+$56
    sta ZP_MAIN+$56
    lda #0
    sbc ZP_MAIN+$57
    sta ZP_MAIN+$57
    lda #0
    sbc ZP_MAIN+$58
    sta ZP_MAIN+$58
SD3232_D_READY:
    jsr SD3232_MAG
    bcs SD3232_RET

    ; Quotient sign = original sign(N) XOR original sign(D).
    lda MATH_N+3
    eor MATH_D+3
    bpl SD3232_Q_DONE
    sec
    lda #0
    sbc MATH_Q+0
    sta MATH_Q+0
    lda #0
    sbc MATH_Q+1
    sta MATH_Q+1
    lda #0
    sbc MATH_Q+2
    sta MATH_Q+2
    lda #0
    sbc MATH_Q+3
    sta MATH_Q+3
SD3232_Q_DONE:
    ; Remainder sign follows the original dividend.
    lda MATH_N+3
    bpl SD3232_SUCCESS
    sec
    lda #0
    sbc MATH_R+0
    sta MATH_R+0
    lda #0
    sbc MATH_R+1
    sta MATH_R+1
    lda #0
    sbc MATH_R+2
    sta MATH_R+2
    lda #0
    sbc MATH_R+3
    sta MATH_R+3
SD3232_SUCCESS:
    clc
SD3232_RET:
    rts
SD3232_END:
