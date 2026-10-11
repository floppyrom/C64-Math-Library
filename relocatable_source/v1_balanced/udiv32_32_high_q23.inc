; Issue39 V1/V5 proven quotient-two/three bounded high-divisor fast path.
; From high-qone reject: N>D, D!=0. D3 in [$40,$7F] and
; N3>2*D3+1 => N>=2D (allowing low-byte doubling carry), while D>=2^30 => Q<=3.
; Preserve N,D and normal ZP. Use only public R/Q as output scratch.
* = REG_TABLE+$0860
D3232_HIGH_Q23:
    lda MATH_D+3
    cmp #$40
    bcc D3232_HIGH_Q23_LEGACY
    asl
    adc #1
    cmp MATH_N+3
    bcs D3232_HIGH_Q23_LEGACY
    ; N>=2D guaranteed. R=N-2D.
    sec
    ldx #0
    ldy #4
D3232_HIGH_Q23_SUB1:
    lda MATH_N,x
    sbc MATH_D,x
    sta MATH_R,x
    inx
    dey
    bne D3232_HIGH_Q23_SUB1
    ldx #0
    ldy #4
D3232_HIGH_Q23_SUB2:
    lda MATH_R,x
    sbc MATH_D,x
    sta MATH_R,x
    inx
    dey
    bne D3232_HIGH_Q23_SUB2
    ; Quotient is 2 unless R>=D, in which case quotient is 3.
    ldy #2
    lda MATH_R+3
    cmp MATH_D+3
    bcc D3232_HIGH_Q23_FINISH
    bne D3232_HIGH_Q23_THREE
    lda MATH_R+2
    cmp MATH_D+2
    bcc D3232_HIGH_Q23_FINISH
    bne D3232_HIGH_Q23_THREE
    lda MATH_R+1
    cmp MATH_D+1
    bcc D3232_HIGH_Q23_FINISH
    bne D3232_HIGH_Q23_THREE
    lda MATH_R+0
    cmp MATH_D+0
    bcc D3232_HIGH_Q23_FINISH
D3232_HIGH_Q23_THREE:
    ldx #0
    ldy #4
    sec
D3232_HIGH_Q23_SUB3:
    lda MATH_R,x
    sbc MATH_D,x
    sta MATH_R,x
    inx
    dey
    bne D3232_HIGH_Q23_SUB3
    ldy #3
D3232_HIGH_Q23_FINISH:
    tya
    sta MATH_Q+0
    lda #0
    sta MATH_Q+1
    sta MATH_Q+2
    sta MATH_Q+3
    clc
    rts
D3232_HIGH_Q23_LEGACY:
    jmp REG_GAME
