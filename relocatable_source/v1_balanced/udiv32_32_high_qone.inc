; Issue39 source-backed bounded q=1 shortcut for V1/V5 32/32 DIV/MOD.
; Entry from D3232_EARLY_GATE is proven N>D and D!=0. High-byte bounds:
; D3 >= 128 => 2D >= 2^32 > N; alternatively D3>0 and N3<2*D3
; prove N < 2D; therefore the only possible quotient is exactly one.
; Worst unqualified paths fall through to the unchanged legacy divider.
; Stable inputs, no new zero-page allocations, relocatable table island.
* = REG_TABLE+$0810
D3232_HIGH_QONE:
    lda MATH_D+3
    beq D3232_HIGH_ZERO
    bmi D3232_HIGH_ONE
    asl
    cmp MATH_N+3
    bcc D3232_HIGH_OLD
    beq D3232_HIGH_OLD
D3232_HIGH_ONE:
    sec
    lda MATH_N+0
    sbc MATH_D+0
    sta MATH_R+0
    lda MATH_N+1
    sbc MATH_D+1
    sta MATH_R+1
    lda MATH_N+2
    sbc MATH_D+2
    sta MATH_R+2
    lda MATH_N+3
    sbc MATH_D+3
    sta MATH_R+3
    lda #$01
    sta MATH_Q+0
    lda #$00
    sta MATH_Q+1
    sta MATH_Q+2
    sta MATH_Q+3
    clc
    rts
D3232_HIGH_OLD:
    jmp D3232_HIGH_Q23
D3232_HIGH_ZERO:
    jmp V1_D3232_D8_GATE
