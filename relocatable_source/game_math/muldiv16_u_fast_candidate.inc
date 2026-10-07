; V2/V3/V4 MULDIV16 candidate fast handoffs.
; The common source keeps V1/V5 on composition. V2/V3/V4 overwrite the
; now-dead composed baseline area and pack both fast handoffs below the
; existing UMUL32 adapter at REG_API+$0420:
;   +$03C9... unsigned fused handoff
;   +$03F8... signed fused handoff.

* = MATH_SMULDIV16_CANDIDATE
    jmp MULDIV16_S_FAST
* = MATH_UMULDIV16_CANDIDATE
    jmp MULDIV16_U_FAST

; Public V2-V4 SMUL16 returns A=product byte1 and X=byte2 while Z0/Z3 are
; already materialized. Copy those four bytes directly into N and enter the
; signed 32/16 divider, avoiding the generic four-byte Z->N loop.
* = REG_API+$03F8
MULDIV16_S_FAST:
    jsr MATH_SMUL16
    sta MATH_N+$01
    stx MATH_N+$02
    lda MATH_Z
    sta MATH_N
    lda MATH_Z+$03
    sta MATH_N+$03
    jmp MATH_SDIV32_16
!if * > REG_API+$0420 { !error "MULDIV16 signed fast handoff overflow" }

; Inline the V2-V4 public UMUL16 binder, but send its returned product bytes
; straight to N instead of materializing Z1/Z2/Z3 and then copying Z->N.
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
!if * > REG_API+$03F8 { !error "MULDIV16 unsigned fast handoff overflow" }
