; V2/V3/V4 unsigned MULDIV16 candidate fast handoff.
; Common candidate source leaves the composed baseline core at REG_API+$03E0.
; This override redirects only the unsigned public candidate to a direct
; UMUL16 producer -> UDIV32/16 handoff. It reuses the selected 16-ZP UMUL16
; core and does not add a resource class.
;
; Placement: REG_API+$03F8..+$041F, exactly the 40-byte hole before the
; existing out-of-line UMUL32 adapter at REG_API+$0420.

* = MATH_UMULDIV16_CANDIDATE
    jmp MULDIV16_U_FAST

* = REG_API+$03F8
MULDIV16_U_FAST:
    ; Inline the public UMUL16 binder, but send its returned product bytes
    ; straight to N instead of materializing Z1/Z2/Z3 and copying Z->N.
    lda MATH_X
    sta U16_X0
    lda MATH_Y+$01
    sta U16_Y1
    ldy MATH_Y
    lda MATH_X+$01
    sta U16_X1
    jsr U16_UMULT_AX1

    ; UMUL16 direct-output core returns:
    ;   MATH_Z = product byte 0, X=byte1, A=byte2, Y=byte3.
    sta MATH_N+$02
    stx MATH_N+$01
    sty MATH_N+$03
    lda MATH_Z
    sta MATH_N
    jmp MATH_UDIV32_16
