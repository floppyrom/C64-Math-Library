; V2/V3/V4 MULDIV16 candidate fast handoffs.
; The common source keeps V1/V5 on composition. Here the 64-byte hole
; REG_API+$03E0..+$041F is packed exactly:
;   +$03E0..+$03F7  signed handoff (24 bytes)
;   +$03F8..+$041F  unsigned handoff (40 bytes)
; The existing UMUL32 adapter begins at REG_API+$0420.

* = MATH_SMULDIV16_CANDIDATE
    jmp MULDIV16_S_FAST
* = MATH_UMULDIV16_CANDIDATE
    jmp MULDIV16_U_FAST

; Public V2-V4 SMUL16 returns A=product byte1 and X=byte2 while Z0/Z3 are
; already materialized. Copy those four bytes directly into N and enter the
; signed 32/16 divider, avoiding the generic four-byte Z->N loop.
* = REG_API+$03E0
MULDIV16_S_FAST:
    jsr MATH_SMUL16
    sta MATH_N+$01
    stx MATH_N+$02
    lda MATH_Z
    sta MATH_N
    lda MATH_Z+$03
    sta MATH_N+$03
    jmp MATH_SDIV32_16

; Inline the V2-V4 public UMUL16 binder, but send its returned product bytes
; straight to N instead of materializing Z1/Z2/Z3 and then copying Z->N.
* = REG_API+$03F8
MULDIV16_U_FAST:
    lda MATH_X
    sta U16_X0
    lda MATH_Y+$01
    sta U16_Y1
    ldy MATH_Y
    lda MATH_X+$01
    sta U16_X1
    jsr U16_UMULT_AX1
    ; UMUL16 direct-output core returns:
    ;   MATH_Z = product byte0, X=byte1, A=byte2, Y=byte3.
    sta MATH_N+$02
    stx MATH_N+$01
    sty MATH_N+$03
    lda MATH_Z
    sta MATH_N
    jmp MATH_UDIV32_16
