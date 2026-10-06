; Optimized low-resource V1/V5 UMUL16 public producer.
; Preserves V1's per-call pointer-high setup and post-call repair because the
; low-ZP profile shares these bytes with other resident paths.
; The public adapter keeps x0 live in A and enters after the old LDA x0.
; The core writes Z0 directly to MATH_Z, removing the private result staging.
!cpu 6510

L16_P0 = ZP_MAIN+$07   ; ref $09-$0A
L16_P1 = L16_P0+$02    ; ref $0B-$0C
L16_P2 = L16_P0+$04    ; ref $0D-$0E
L16_P3 = L16_P0+$06    ; ref $0F-$10
L16_P4 = L16_P0+$08    ; ref $11-$12
L16_P5 = L16_P0+$0A    ; ref $13-$14
L16_P6 = L16_P0+$0C    ; ref $15-$16
L16_P7 = L16_P0+$0E    ; ref $17-$18
L16_X0 = L16_P0
L16_X1 = L16_P4

L16_SL = REG_TABLE+$2400
L16_SH = REG_TABLE+$2600
L16_NL = REG_TABLE+$2800
L16_NH = REG_TABLE+$2A00

* = MATH_UMUL16
L16_PUBLIC:
        ; Preserve the existing V1/V5 mixed-call-safe high-byte contract.
        lda #>L16_SL
        sta L16_P0+$01
        sta L16_P4+$01
        lda #>L16_NL
        sta L16_P1+$01
        sta L16_P5+$01
        lda #>L16_SH
        sta L16_P2+$01
        sta L16_P6+$01
        lda #>L16_NH
        sta L16_P3+$01
        sta L16_P7+$01

        lda MATH_X+$01
        sta L16_X1
        lda MATH_Y+$01
        sta L16_Y1
        ldy MATH_Y
        lda MATH_X
        sta L16_X0
        jsr L16_UMULT_AX0
        sta MATH_Z+$02
        stx MATH_Z+$01
        sty MATH_Z+$03
        jmp L16_REPAIR

* = REG_KERNEL+$07EC
L16_UMULT:
        lda L16_X0
L16_UMULT_AX0:
        sta L16_P2
        eor #$FF
        sta L16_P1
        sta L16_P3
        lda L16_X1
        sta L16_P6
        eor #$FF
        sta L16_P5
        sta L16_P7
        sec
        lda (L16_P0),y
        adc (L16_P1),y
        sta MATH_Z
        lda (L16_P2),y
        adc (L16_P3),y
        adc (L16_P4),y
        bcs L16_CARRY0
        adc (L16_P5),y
        tax
        lda (L16_P6),y
L16_TAIL0:
        adc (L16_P7),y
        sta L16_HIGH0+$01
L16_Y1=*+$01
        ldy #$00
        lda (L16_P0),y
        adc (L16_P1),y
        sta L16_LOW1+$01
        lda (L16_P2),y
        adc (L16_P3),y
        adc (L16_P4),y
        bcs L16_CARRY1
        adc (L16_P5),y
        sta L16_HIGH1+$01
        lda (L16_P6),y
L16_TAIL1:
        adc (L16_P7),y
        tay
        clc
        txa
L16_LOW1:
        adc #$00
        tax
L16_HIGH0:
        lda #$00
L16_HIGH1:
        adc #$00
        bcs L16_FINAL
        rts
L16_FINAL:
        iny
        rts

L16_CARRY0:
        clc
        adc (L16_P5),y
        tax
        lda #$01
        adc (L16_P6),y
        bcc L16_TAIL0

L16_CARRY1:
        clc
        adc (L16_P5),y
        sta L16_HIGH1+$01
        lda #$01
        adc (L16_P6),y
        bcc L16_TAIL1

; Restore the low-byte state expected by other V1/V5 resident users.
L16_REPAIR:
        lda #<(REG_TABLE+$2E00)
        sta L16_P0
        sta L16_P2
        lda #<(REG_TABLE+$3000)
        sta L16_P1
        clc
        rts
