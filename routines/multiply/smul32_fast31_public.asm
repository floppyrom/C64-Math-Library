; Signed full-width FAST31 public ABI using the certified V2 unsigned producer.
; Uses the exact 277-byte unsigned native producer, wrapped in
; a public signed X32/Y32 -> two's-complement Z64 ABI shim. No profiles.
; Immutable 511-byte quarter-square tables are emitted by a separate module.
; C=0 on return, X/Y public inputs intact, D=0 required, A/X/Y volatile.
; Self-modifying; safe for sequential calls after reinitializing pointer highs.
!cpu 6510
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_ZP = $0050
sqr_lo = $8300
sqr_hi = $8500
neg_sqr_lo = $8700
neg_sqr_hi = $8900

neg_lo_1 = TEMP_ZP
sqr_hi_1 = TEMP_ZP+2
neg_lo_2 = TEMP_ZP+4
sqr_hi_2 = TEMP_ZP+6
neg_lo_3 = TEMP_ZP+8
sqr_hi_3 = TEMP_ZP+10
z00 = TEMP_ZP+12
z10 = TEMP_ZP+13
z20 = TEMP_ZP+14
z30 = TEMP_ZP+15
z02 = TEMP_ZP+16
z12 = TEMP_ZP+17
z22 = TEMP_ZP+18
z32 = TEMP_ZP+19
z03 = TEMP_ZP+20
z13 = TEMP_ZP+21
z23 = TEMP_ZP+22
z33 = TEMP_ZP+23
z14 = TEMP_ZP+24
z24 = TEMP_ZP+25
z34 = TEMP_ZP+26
z01 = TEMP_ZP+27
z11 = TEMP_ZP+28
z21 = TEMP_ZP+29
z31 = TEMP_ZP+30
x1 = sqr_hi_1
x2 = sqr_hi_2
x3 = sqr_hi_3
y0 = z00
y1 = z10
y2 = z20
r0 = z00
r1 = z10
r2 = z20
r3 = z30
r7 = z34

* = KERNEL_CODE
FAST_SMUL32_FAST31:
    ; Reinstall six table-pointer highs for mixed-call safety. No MATH_INIT.
    lda #>neg_sqr_lo
    sta neg_lo_1+1
    sta neg_lo_2+1
    sta neg_lo_3+1
    lda #>sqr_hi
    sta sqr_hi_1+1
    sta sqr_hi_2+1
    sta sqr_hi_3+1

    lda INPUT_X+1
    sta x1
    lda INPUT_X+2
    sta x2
    lda INPUT_X+3
    sta x3
    lda INPUT_Y
    sta y0
    lda INPUT_Y+1
    sta y1
    lda INPUT_Y+2
    sta y2
    ldy INPUT_Y+3
    lda INPUT_X
    jsr umult32x32
    ; Source-native result geometry: r0,r1,r2,r3,X,Y,A,r7.
    sta OUTPUT_Z+6
    stx OUTPUT_Z+4
    sty OUTPUT_Z+5
    lda r0
    sta OUTPUT_Z
    lda r1
    sta OUTPUT_Z+1
    lda r2
    sta OUTPUT_Z+2
    lda r3
    sta OUTPUT_Z+3
    lda r7
    sta OUTPUT_Z+7
    ; Signed 64-bit full product = unsigned full product, minus Y<<32
    ; when X is negative, and minus X<<32 when Y is negative.
    ; Full-width public operands are preserved in INPUT_X/INPUT_Y.
    lda INPUT_X+3
    bpl fast31_signed_x_positive
    sec
    lda OUTPUT_Z+4
    sbc INPUT_Y
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_Y+1
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    sbc INPUT_Y+2
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    sbc INPUT_Y+3
    sta OUTPUT_Z+7
fast31_signed_x_positive:
    lda INPUT_Y+3
    bpl fast31_signed_y_positive
    sec
    lda OUTPUT_Z+4
    sbc INPUT_X
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_X+1
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    sbc INPUT_X+2
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    sbc INPUT_X+3
    sta OUTPUT_Z+7
fast31_signed_y_positive:
    clc
    rts

; The native arithmetic core below is copied from the certified profile
; source, with only its output/zero-page/table labels rebound above.
umult32x32
        sta SMC_sqr_lo_0+1
        sta SMC_sqr_hi_0+1
        eor #$ff
        sta SMC_neg_lo_0+1
        sta SMC_neg_hi_0+1

        lda x1
        sta SMC_sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta SMC_neg_hi_1+1

        lda x2
        sta SMC_sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta SMC_neg_hi_2+1

        lda x3
        sta SMC_sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta SMC_neg_hi_3+1

umult32x32_same_x
        ldx #3
        sec
        bcs kernel

H10
        clc
        adc (neg_lo_1),y
        sta z01,x
        lda #1
        adc (sqr_hi_1),y
        bcc p10_tail
H20
        clc
        adc (neg_lo_2),y
        sta z02,x
        lda #1
        adc (sqr_hi_2),y
        bcc p20_tail
H30
        clc
        adc (neg_lo_3),y
        sta z03,x
        lda #1
        adc (sqr_hi_3),y
        bcc p30_tail

row_loop
        sta z14,x
        ldy y0,x

kernel
SMC_sqr_lo_0
        lda sqr_lo,y
SMC_neg_lo_0
        adc neg_sqr_lo,y
        sta z00,x
SMC_sqr_hi_0
        lda sqr_hi,y
SMC_neg_hi_0
        adc neg_sqr_hi,y

SMC_sqr_lo_1
        adc sqr_lo,y
        bcs H10
        adc (neg_lo_1),y
        sta z01,x
        lda (sqr_hi_1),y
p10_tail
SMC_neg_hi_1
        adc neg_sqr_hi,y

SMC_sqr_lo_2
        adc sqr_lo,y
        bcs H20
        adc (neg_lo_2),y
        sta z02,x
        lda (sqr_hi_2),y
p20_tail
SMC_neg_hi_2
        adc neg_sqr_hi,y

SMC_sqr_lo_3
        adc sqr_lo,y
        bcs H30
        adc (neg_lo_3),y
        sta z03,x
        lda (sqr_hi_3),y
p30_tail
SMC_neg_hi_3
        adc neg_sqr_hi,y

        dex
        bpl row_loop

; Direct column summation.  Each intermediate carry is materialized by
; incrementing a byte in the next column, then C is cleared before continuing.
summation
        tax
        ldy z14
        clc

        lda z01
        adc z10
        sta r1

        lda z11
        adc z20
        bcc c2a_done
        inc z30
        beq c2a_overflow
        clc
c2a_done
        adc z02
        sta r2

        lda z12
        adc z03
        bcc c3a_done
        inx
        clc
c3a_done
        adc z30
        bcc c3b_done
        inx
        beq c3b_overflow
        clc
c3b_done
        adc z21
        sta r3

        txa
        adc z13
        bcc c4a_done
        iny
        clc
c4a_done
        adc z31
        bcc c4b_done
        iny
        beq c4b_overflow
        clc
c4b_done
        adc z22
        tax

        tya
        adc z32
        bcc c5a_done
        inc z24
        clc
c5a_done
        adc z23
        tay

        lda z33
        adc z24
        bcs final_carry
        rts
final_carry
        inc r7
        rts

; Rare ripple when materializing the first column-2 carry into a $ff z30.
; Follow row 3 upward so every possible wrap remains exact.
c2a_overflow
        inc z31
        bne c2a_overflow_done
        inc z32
        bne c2a_overflow_done
        inc z33
        bne c2a_overflow_done
        inc z34
c2a_overflow_done
        clc
        jmp c2a_done

; z04 and z14 are top bytes of 32x8 rows, hence at most $fe before
; summation.  They remain in X and Y until consumed, so their carry bumps
; use two-cycle INX/INY.  Only the second possible increment can wrap.  The
; c3 carry enters z32 (column 5); the c4 carry enters z33 (column 6), with
; each path rippling upward through row 3 as required.
c3b_overflow
        inc z32
        bne c3b_overflow_done
        inc z33
        bne c3b_overflow_done
        inc z34
c3b_overflow_done
        clc
        jmp c3b_done
c4b_overflow
        inc z33
        bne c4b_overflow_done
        inc z34
c4b_overflow_done
        clc
        jmp c4b_done
