; Optimized fixed-profile V2/V3/V4 UMUL16 public producer.
; Keeps the qualified 16-byte pointer layout and existing quarter-square tables.
; Public wrapper supplies A=x1 to the specialized binder entry and the core writes
; the low product byte directly to MATH_Z.  No new resource class is introduced.
;
; Reference geometry:
;   pointers $21-$30 (16 bytes), code $53EC..., tables $6000/$6200/$6400/$6600.
; Alternate/custom source builds relocate through ZP_MAIN/REG_KERNEL/REG_TABLE.

U16_P0 = ZP_MAIN+$1F
U16_P1 = U16_P0+$02
U16_P2 = U16_P0+$04
U16_P3 = U16_P0+$06
U16_P4 = U16_P0+$08
U16_P5 = U16_P0+$0A
U16_P6 = U16_P0+$0C
U16_P7 = U16_P0+$0E
U16_X0 = U16_P0
U16_X1 = U16_P4

U16_SL = REG_TABLE
U16_SH = REG_TABLE+$0200
U16_NL = REG_TABLE+$0400
U16_NH = REG_TABLE+$0600

* = MATH_UMUL16
U16_PUBLIC:
        lda MATH_X
        sta U16_X0
        lda MATH_Y+$01
        sta U16_Y1
        ldy MATH_Y
        lda MATH_X+$01
        sta U16_X1
        jsr U16_UMULT_AX1
        sta MATH_Z+$02
        stx MATH_Z+$01
        sty MATH_Z+$03
        clc
        rts

* = REG_KERNEL+$13EC
U16_UMULT:
        lda U16_X1
U16_UMULT_AX1:
        ; Bind x1 first so the public wrapper can enter with A=x1.
        sta U16_P6
        eor #$FF
        sta U16_P5
        sta U16_P7

        lda U16_X0
        sta U16_P2
        eor #$FF
        sta U16_P1
        sta U16_P3

U16_SAME_X:
        sec
        lda (U16_P0),y
        adc (U16_P1),y
        ; The low product byte is final immediately; avoid the old ZP staging.
        sta MATH_Z
        lda (U16_P2),y
        adc (U16_P3),y
        adc (U16_P4),y
        bcs U16_CARRY0
        adc (U16_P5),y
        tax
        lda (U16_P6),y
U16_TAIL0:
        adc (U16_P7),y
        sta U16_HIGH0+$01
U16_Y1 = *+$01
        ldy #$00
        lda (U16_P0),y
        adc (U16_P1),y
        sta U16_LOW1+$01
        lda (U16_P2),y
        adc (U16_P3),y
        adc (U16_P4),y
        bcs U16_CARRY1
U16_HOT1:
        adc (U16_P5),y
        sta U16_HIGH1+$01
        lda (U16_P6),y
U16_TAIL1:
        adc (U16_P7),y
        tay
        clc
        txa
U16_LOW1:
        adc #$00
        tax
U16_HIGH0:
        lda #$00
U16_HIGH1:
        adc #$00
        bcs U16_FINAL
        rts
U16_FINAL:
        iny
        rts

U16_CARRY0:
        clc
        adc (U16_P5),y
        tax
        lda #$01
        adc (U16_P6),y
        bcc U16_TAIL0

U16_CARRY1:
        clc
        adc (U16_P5),y
        sta U16_HIGH1+$01
        lda #$01
        adc (U16_P6),y
        bcc U16_TAIL1

; Preserve the qualified record candidate's pointer-high repair helper directly
; after the core. It is not part of the public fast path.
U16_INIT:
        lda #>U16_SL
        sta U16_P0+$01
        sta U16_P4+$01
        lda #>U16_NL
        sta U16_P1+$01
        sta U16_P5+$01
        lda #>U16_SH
        sta U16_P2+$01
        sta U16_P6+$01
        lda #>U16_NH
        sta U16_P3+$01
        sta U16_P7+$01
        rts
