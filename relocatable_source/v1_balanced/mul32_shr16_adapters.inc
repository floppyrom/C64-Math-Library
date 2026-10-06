; V1/V5 32-bit fixed-point multiply adapters.
; Base MATH_UMUL32/MATH_SMUL32 guarantee C=0. The six LDA/STA copies below
; do not modify carry, so the historical final CLC is redundant.
!cpu 6510

* = REG_GAME+$044C
MUL32_U_SHR16_ADAPTER:
        jsr MATH_UMUL32
        lda MATH_Z+$02
        sta MATH_Z
        lda MATH_Z+$03
        sta MATH_Z+$01
        lda MATH_Z+$04
        sta MATH_Z+$02
        lda MATH_Z+$05
        sta MATH_Z+$03
        lda MATH_Z+$06
        sta MATH_Z+$04
        lda MATH_Z+$07
        sta MATH_Z+$05
        rts

* = REG_GAME+$0475
MUL32_S_SHR16_ADAPTER:
        jsr MATH_SMUL32
        lda MATH_Z+$02
        sta MATH_Z
        lda MATH_Z+$03
        sta MATH_Z+$01
        lda MATH_Z+$04
        sta MATH_Z+$02
        lda MATH_Z+$05
        sta MATH_Z+$03
        lda MATH_Z+$06
        sta MATH_Z+$04
        lda MATH_Z+$07
        sta MATH_Z+$05
        rts

* = MATH_UMUL32_SHR16
        jmp MUL32_U_SHR16_ADAPTER

* = MATH_SMUL32_SHR16
        jmp MUL32_S_SHR16_ADAPTER
