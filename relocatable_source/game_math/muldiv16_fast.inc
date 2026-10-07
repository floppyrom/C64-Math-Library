; V2/V3/V4 MULDIV16 stable fast handoffs.
; The common source keeps V1/V5 on composition. V2/V3/V4 overwrite the
; now-dead unsigned composed baseline area for the direct unsigned handoff.
; The larger signed-quadrant fusion lives in the certified free REG_LOW+$0BCD island;
; the existing UMUL32 adapter at REG_API+$0420 remains untouched.

* = MATH_SMULDIV16
    jmp MULDIV16_S_FUSED
* = MATH_UMULDIV16
    jmp MULDIV16_U_FAST

; OptiSearch-style signed-quadrant fusion. Normalize X/Y/D once, run the
; unsigned quarter-square producer and the private unsigned 32/16 divider, then
; apply quotient/remainder signs once. This removes the signed-product
; correction + signed-divider magnitude reconstruction pair.
* = REG_LOW+$0BCD
MULDIV16_S_FUSED:
    ; Divisor zero can return before paying for the multiply.
    lda MATH_D+$01
    ora MATH_D
    bne MULDIV16_S_DNZ
    jmp U3216_ZERO

MULDIV16_S_DNZ:
    ; |D| -> private divider state. Public D remains untouched.
    lda MATH_D+$01
    bpl MULDIV16_S_DPOS
    lda #$00
    sec
    sbc MATH_D
    sta U3216_D0
    lda #$00
    sbc MATH_D+$01
    sta U3216_D1
    jmp MULDIV16_S_X
MULDIV16_S_DPOS:
    lda MATH_D
    sta U3216_D0
    lda MATH_D+$01
    sta U3216_D1

MULDIV16_S_X:
    ; |X| -> unsigned producer X state.
    lda MATH_X+$01
    bpl MULDIV16_S_XPOS
    lda #$00
    sec
    sbc MATH_X
    sta U16_X0
    lda #$00
    sbc MATH_X+$01
    sta U16_X1
    jmp MULDIV16_S_Y
MULDIV16_S_XPOS:
    lda MATH_X
    sta U16_X0
    lda MATH_X+$01
    sta U16_X1

MULDIV16_S_Y:
    ; |Y|; low byte stays in Y as required by U16_UMULT_AX1.
    lda MATH_Y+$01
    bpl MULDIV16_S_YPOS
    lda #$00
    sec
    sbc MATH_Y
    tay
    lda #$00
    sbc MATH_Y+$01
    sta U16_Y1
    jmp MULDIV16_S_MUL
MULDIV16_S_YPOS:
    ldy MATH_Y
    lda MATH_Y+$01
    sta U16_Y1

MULDIV16_S_MUL:
    lda U16_X1
    jsr U16_UMULT_AX1
    ; Magnitude product -> private 32/16 divider state, no MATH_N round-trip.
    sta U3216_N0
    stx U3216_LN1
    sty U3216_N1
    lda MATH_Z
    sta U3216_LN0
    jsr U3216_ENTRY
    bcs MULDIV16_S_RET

    ; Quotient sign = sign(X) xor sign(Y) xor sign(D).
    lda MATH_X+$01
    eor MATH_Y+$01
    eor MATH_D+$01
    bpl MULDIV16_S_RSIGN
    lda #$00
    sec
    sbc MATH_Q
    sta MATH_Q
    lda #$00
    sbc MATH_Q+$01
    sta MATH_Q+$01
    lda #$00
    sbc MATH_Q+$02
    sta MATH_Q+$02
    lda #$00
    sbc MATH_Q+$03
    sta MATH_Q+$03

MULDIV16_S_RSIGN:
    ; Remainder sign follows the signed product.
    lda MATH_X+$01
    eor MATH_Y+$01
    bpl MULDIV16_S_OK
    lda #$00
    sec
    sbc MATH_R
    sta MATH_R
    lda #$00
    sbc MATH_R+$01
    sta MATH_R+$01
MULDIV16_S_OK:
    clc
MULDIV16_S_RET:
    rts

; Inline the V2-V4 public UMUL16 binder, then feed its returned product bytes
; directly into the private UDIV32/16 state without a public N/Z round-trip.
* = REG_API+$03C9
MULDIV16_U_FAST:
    lda MATH_X
    sta U16_X0
    lda MATH_Y+$01
    sta U16_Y1
    ldy MATH_Y
    lda MATH_X+$01
    sta U16_X1
    jsr U16_UMULT_AX1
    ; OptiSearch-style producer/consumer fusion: do not materialize the
    ; canonical 32-bit product in MATH_N and then make the public divider copy
    ; it again.  Feed the product registers directly into the private
    ; UDIV32/16 state and enter after its public marshalling wrapper.
    ; UMUL16 returns MATH_Z=byte0, X=byte1, A=byte2, Y=byte3.
    sta U3216_N0
    stx U3216_LN1
    sty U3216_N1
    lda MATH_Z
    sta U3216_LN0
    lda MATH_D
    sta U3216_D0
    lda MATH_D+$01
    sta U3216_D1
    jmp U3216_ENTRY
