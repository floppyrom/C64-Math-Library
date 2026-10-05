; SMUL32 FAST31 native v2 — signed 32x32 -> 64, 31-ZP / stack-free record.
; Improved 2026-10-05 from FAST31 native using two compact126 ideas:
;   1. common/rare NN negation after the x0 borrow;
;   2. CPY #$00 sign dispatch to seed C=1 and remove producer-entry SEC.
; Entry: A=x0, x1..x3 in ZP aliases, y0..y2 in ZP, CPU Y=y3.
; Return byte order: r0,r1,r2,r3,X,Y,A,r7.
; Timing includes RTS; caller JSR/input staging excluded. D=0 required.
; Self-modifying/non-reentrant. No persistent page-$01 reservation.
;
;ABI
;Entry: smul32_composed
;CPU: mos6502
;Operation: smul
;Input x: int32 = reg:A, x1, x2, x3
;Input y: int32 = y0, y1, y2, reg:Y
;Output z: int64 = r0, r1, r2, r3, reg:X, reg:Y, reg:A, r7
;Region ZP: cg_zp_start..cg_zp_end
;Region Code: cg_code_start..cg_code_end plus signed/q1/q2 executable islands
;Region Data: cg_sqr_lo_start..cg_neg_hi_end
;End ABI
;Results
;Status: validated research standalone
;Validation cases: 100000
;Validation errors: 0
;Independent cases: 100000
;Independent errors: 0
;Edge cases: 1849
;Edge errors: 0
;Min cycles: 590
;Max cycles: 808
;Avg cycles: 692.825100
;Independent avg cycles: 692.678520
;ZP bytes: 31
;Stack-page reserved bytes: 0
;Code bytes: 1133
;Data bytes: 2044
;Total bytes: 3177
;Occupied bytes incl ZP: 3208
;End Results
!cpu 6510

neg_lo_1 = $02
sqr_hi_1 = $04
neg_lo_2 = $06
sqr_hi_2 = $08
neg_lo_3 = $0a
sqr_hi_3 = $0c

z00 = $0e
z10 = $0f
z20 = $10
z30 = $11
z02 = $12
z12 = $13
z22 = $14
z32 = $15
z03 = $16
z13 = $17
z23 = $18
z33 = $19
z14 = $1a
z24 = $1b
z34 = $1c
z01 = $1d
z11 = $1e
z21 = $1f
z31 = $20

x1 = sqr_hi_1
x2 = sqr_hi_2
x3 = sqr_hi_3
y0 = $0e
y1 = $0f
y2 = $10
r0 = $0e
r1 = $0f
r2 = $10
r3 = $11
r7 = $1c

*=$02
cg_zp_start:
!byte 0, >neg_sqr_lo
!byte 0, >sqr_hi
!byte 0, >neg_sqr_lo
!byte 0, >sqr_hi
!byte 0, >neg_sqr_lo
!byte 0, >sqr_hi
!fill 19,0
cg_zp_end:

*=$5839
cg_code_start:
umult32x32:
        sta _sqr_lo_0+1
        sta _sqr_hi_0+1
        eor #$ff
        sta _neg_lo_0+1
        sta _neg_hi_0+1

        lda x1
        sta _sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta _neg_hi_1+1

        lda x2
        sta _sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta _neg_hi_2+1

        lda x3
        sta _sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta _neg_hi_3+1

umult32x32_same_x:
        ldx #3
        bcs kernel

H10:
        clc
        adc (neg_lo_1),y
        sta z01,x
        lda #1
        adc (sqr_hi_1),y
        bcc p10_tail
H20:
        clc
        adc (neg_lo_2),y
        sta z02,x
        lda #1
        adc (sqr_hi_2),y
        bcc p20_tail
H30:
        clc
        adc (neg_lo_3),y
        sta z03,x
        lda #1
        adc (sqr_hi_3),y
        bcc p30_tail

row_loop:
        sta z14,x
        ldy y0,x

kernel:
_sqr_lo_0:
        lda sqr_lo,y
_neg_lo_0:
        adc neg_sqr_lo,y
        sta z00,x
_sqr_hi_0:
        lda sqr_hi,y
_neg_hi_0:
        adc neg_sqr_hi,y

_sqr_lo_1:
        adc sqr_lo,y
        bcs H10
        adc (neg_lo_1),y
        sta z01,x
        lda (sqr_hi_1),y
p10_tail:
_neg_hi_1:
        adc neg_sqr_hi,y

_sqr_lo_2:
        adc sqr_lo,y
        bcs H20
        adc (neg_lo_2),y
        sta z02,x
        lda (sqr_hi_2),y
p20_tail:
_neg_hi_2:
        adc neg_sqr_hi,y

_sqr_lo_3:
        adc sqr_lo,y
        bcs H30
        adc (neg_lo_3),y
        sta z03,x
        lda (sqr_hi_3),y
p30_tail:
_neg_hi_3:
        adc neg_sqr_hi,y

        dex
        bpl row_loop

summation:
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
c2a_done:
        adc z02
        sta r2

        lda z12
        adc z03
        bcc c3a_done
        inx
        clc
c3a_done:
        adc z30
        bcc c3b_done
        inx
        beq c3b_overflow
        clc
c3b_done:
        adc z21
        sta r3

        txa
        adc z13
        bcc c4a_done
        iny
        clc
c4a_done:
        adc z31
        bcc c4b_done
        iny
        beq c4b_overflow
        clc
c4b_done:
        adc z22
        tax

        tya
        adc z32
        bcc c5a_done
        inc z24
        clc
c5a_done:
        adc z23
        tay

        lda z33
        adc z24
        bcs final_carry
        rts
final_carry:
        inc r7
        rts

c2a_overflow:
        inc z31
        bne c2a_overflow_done
        inc z32
        bne c2a_overflow_done
        inc z33
        bne c2a_overflow_done
        inc z34
c2a_overflow_done:
        clc
        jmp c2a_done

c3b_overflow:
        inc z32
        bne c3b_overflow_done
        inc z33
        bne c3b_overflow_done
        inc z34
c3b_overflow_done:
        clc
        jmp c3b_done
c4b_overflow:
        inc z33
        bne c4b_overflow_done
        inc z34
c4b_overflow_done:
        clc
        jmp c4b_done
cg_code_end:

init:
        lda #>neg_sqr_lo
        sta neg_lo_1+1
        sta neg_lo_2+1
        sta neg_lo_3+1
        lda #>sqr_hi
        sta sqr_hi_1+1
        sta sqr_hi_2+1
        sta sqr_hi_3+1
        rts

; ---------------------------------------------------------------------------
; Signed composition. BIT x3 preserves entry A=x0; CPY #$00 tests Y sign
; while leaving C=1 for PP/PN/NP producer entry.
; ---------------------------------------------------------------------------
*=$5a00
; Far rare handler for NN when X0==0. This is reached through the near
; trampoline below in only 1/256 of random NN inputs.
smul32_nn_xcarry_far:
        lda #0
        sbc x1
        sta x1
        sta _sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta _neg_hi_1+1
        lda #0
        sbc x2
        sta x2
        sta _sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta _neg_hi_2+1
        lda #0
        sbc x3
        sta x3
        sta _sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta _neg_hi_3+1
        jmp smul32_nn_y_near

; Pack the common signed dispatcher/NN path below the unsigned binder.
*=$5760
smul32_nn_xcarry_tramp:
        jmp smul32_nn_xcarry_far

smul32_nn_near:
        ; Entry A=x0 and C=1 from CPY #$00 in the X-negative dispatcher.
        ; If x0 is non-zero, the low-byte negation has already borrowed and
        ; every upper byte of |X| is simply the complement of the source byte.
        eor #$ff
        adc #0
        sta _sqr_lo_0+1
        sta _sqr_hi_0+1
        eor #$ff
        sta _neg_lo_0+1
        sta _neg_hi_0+1
        bcs smul32_nn_xcarry_tramp
        lda x1
        sta neg_lo_1
        sta _neg_hi_1+1
        eor #$ff
        sta x1
        sta _sqr_lo_1+1
        lda x2
        sta neg_lo_2
        sta _neg_hi_2+1
        eor #$ff
        sta x2
        sta _sqr_lo_2+1
        lda x3
        sta neg_lo_3
        sta _neg_hi_3+1
        eor #$ff
        sta x3
        sta _sqr_lo_3+1
smul32_nn_y_near:
        sec
        lda #0
        sbc y0
        sta y0
        lda #0
        sbc y1
        sta y1
        lda #0
        sbc y2
        sta y2
        tya
        eor #$ff
        adc #0
        tay
        ldx #3
        sec
        jmp kernel

*=$57d0
smul32_xneg_near:
        cpy #$00
        bmi smul32_nn_near
        ldx y0
        stx q2_saved_y0+1
        ldx y1
        stx q2_saved_y1+1
        ldx y2
        stx q2_saved_y2+1
        sty q2_saved_y3+1
        jmp q2_umult32x32

*=$57f8
smul32_composed:
        bit x3
        bmi smul32_xneg_near
        cpy #$00
        bpl umult32x32
        ; PN falls through to the bridge at $5800.
smul32_composed_end:

*=$5800
smul32_yneg_bridge:
        sta q1__sqr_lo_0+1
        sta q1__sqr_hi_0+1
        eor #$ff
        sta q1__neg_lo_0+1
        sta q1__neg_hi_0+1

        lda x1
        sta q1__sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta q1__neg_hi_1+1

        lda x2
        sta q1__sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta q1__neg_hi_2+1

        lda x3
        sta q1__sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta q1__neg_hi_3+1

        ldx #3
        jmp q1_kernel

; ---------------------------------------------------------------------------
; Speed-max mixed-sign producer copies. Both share the original 31-byte ZP
; state and table planes. Their normal exit falls into the required signed
; correction, avoiding the JSR + producer RTS round-trip.
; ---------------------------------------------------------------------------
*=$5c00
q2_cg_code_start:
q2_umult32x32:
        sta q2__sqr_lo_0+1
        sta q2__sqr_hi_0+1
        eor #$ff
        sta q2__neg_lo_0+1
        sta q2__neg_hi_0+1

        lda x1
        sta q2__sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta q2__neg_hi_1+1

        lda x2
        sta q2__sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta q2__neg_hi_2+1

        lda x3
        sta q2__sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta q2__neg_hi_3+1

q2_umult32x32_same_x:
        ldx #3
        bcs q2_kernel

q2_H10:
        clc
        adc (neg_lo_1),y
        sta z01,x
        lda #1
        adc (sqr_hi_1),y
        bcc q2_p10_tail
q2_H20:
        clc
        adc (neg_lo_2),y
        sta z02,x
        lda #1
        adc (sqr_hi_2),y
        bcc q2_p20_tail
q2_H30:
        clc
        adc (neg_lo_3),y
        sta z03,x
        lda #1
        adc (sqr_hi_3),y
        bcc q2_p30_tail

q2_row_loop:
        sta z14,x
        ldy y0,x

q2_kernel:
q2__sqr_lo_0:
        lda sqr_lo,y
q2__neg_lo_0:
        adc neg_sqr_lo,y
        sta z00,x
q2__sqr_hi_0:
        lda sqr_hi,y
q2__neg_hi_0:
        adc neg_sqr_hi,y

q2__sqr_lo_1:
        adc sqr_lo,y
        bcs q2_H10
        adc (neg_lo_1),y
        sta z01,x
        lda (sqr_hi_1),y
q2_p10_tail:
q2__neg_hi_1:
        adc neg_sqr_hi,y

q2__sqr_lo_2:
        adc sqr_lo,y
        bcs q2_H20
        adc (neg_lo_2),y
        sta z02,x
        lda (sqr_hi_2),y
q2_p20_tail:
q2__neg_hi_2:
        adc neg_sqr_hi,y

q2__sqr_lo_3:
        adc sqr_lo,y
        bcs q2_H30
        adc (neg_lo_3),y
        sta z03,x
        lda (sqr_hi_3),y
q2_p30_tail:
q2__neg_hi_3:
        adc neg_sqr_hi,y

        dex
        bpl q2_row_loop

q2_summation:
        tax
        ldy z14
        clc

        lda z01
        adc z10
        sta r1

        lda z11
        adc z20
        bcc q2_c2a_done
        inc z30
        beq q2_c2a_overflow
        clc
q2_c2a_done:
        adc z02
        sta r2

        lda z12
        adc z03
        bcc q2_c3a_done
        inx
        clc
q2_c3a_done:
        adc z30
        bcc q2_c3b_done
        inx
        beq q2_c3b_overflow
        clc
q2_c3b_done:
        adc z21
        sta r3

        txa
        adc z13
        bcc q2_c4a_done
        iny
        clc
q2_c4a_done:
        adc z31
        bcc q2_c4b_done
        iny
        beq q2_c4b_overflow
        clc
q2_c4b_done:
        adc z22
        tax

        tya
        adc z32
        bcc q2_c5a_done
        inc z24
        clc
q2_c5a_done:
        adc z23
        tay

        lda z33
        adc z24
        bcc q2_signed_correction
        inc r7
q2_signed_correction:
        sta q2_xneg_orig_a+1
        txa
        sec
q2_saved_y0:
        sbc #0
        tax
        tya
q2_saved_y1:
        sbc #0
        tay
q2_xneg_orig_a:
        lda #0
q2_saved_y2:
        sbc #0
        sta q2_xneg_restore_a+1
        lda r7
q2_saved_y3:
        sbc #0
        sta r7
q2_xneg_restore_a:
        lda #0
        rts

q2_c2a_overflow:
        inc z31
        bne q2_c2a_overflow_done
        inc z32
        bne q2_c2a_overflow_done
        inc z33
        bne q2_c2a_overflow_done
        inc z34
q2_c2a_overflow_done:
        clc
        jmp q2_c2a_done

q2_c3b_overflow:
        inc z32
        bne q2_c3b_overflow_done
        inc z33
        bne q2_c3b_overflow_done
        inc z34
q2_c3b_overflow_done:
        clc
        jmp q2_c3b_done
q2_c4b_overflow:
        inc z33
        bne q2_c4b_overflow_done
        inc z34
q2_c4b_overflow_done:
        clc
        jmp q2_c4b_done
q2_cg_code_end:

*=$5e00
q1_cg_code_start:
q1_umult32x32:
        sta q1__sqr_lo_0+1
        sta q1__sqr_hi_0+1
        eor #$ff
        sta q1__neg_lo_0+1
        sta q1__neg_hi_0+1

        lda x1
        sta q1__sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta q1__neg_hi_1+1

        lda x2
        sta q1__sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta q1__neg_hi_2+1

        lda x3
        sta q1__sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta q1__neg_hi_3+1

q1_umult32x32_same_x:
        ldx #3
        bcs q1_kernel

q1_H10:
        clc
        adc (neg_lo_1),y
        sta z01,x
        lda #1
        adc (sqr_hi_1),y
        bcc q1_p10_tail
q1_H20:
        clc
        adc (neg_lo_2),y
        sta z02,x
        lda #1
        adc (sqr_hi_2),y
        bcc q1_p20_tail
q1_H30:
        clc
        adc (neg_lo_3),y
        sta z03,x
        lda #1
        adc (sqr_hi_3),y
        bcc q1_p30_tail

q1_row_loop:
        sta z14,x
        ldy y0,x

q1_kernel:
q1__sqr_lo_0:
        lda sqr_lo,y
q1__neg_lo_0:
        adc neg_sqr_lo,y
        sta z00,x
q1__sqr_hi_0:
        lda sqr_hi,y
q1__neg_hi_0:
        adc neg_sqr_hi,y

q1__sqr_lo_1:
        adc sqr_lo,y
        bcs q1_H10
        adc (neg_lo_1),y
        sta z01,x
        lda (sqr_hi_1),y
q1_p10_tail:
q1__neg_hi_1:
        adc neg_sqr_hi,y

q1__sqr_lo_2:
        adc sqr_lo,y
        bcs q1_H20
        adc (neg_lo_2),y
        sta z02,x
        lda (sqr_hi_2),y
q1_p20_tail:
q1__neg_hi_2:
        adc neg_sqr_hi,y

q1__sqr_lo_3:
        adc sqr_lo,y
        bcs q1_H30
        adc (neg_lo_3),y
        sta z03,x
        lda (sqr_hi_3),y
q1_p30_tail:
q1__neg_hi_3:
        adc neg_sqr_hi,y

        dex
        bpl q1_row_loop

q1_summation:
        tax
        ldy z14
        clc

        lda z01
        adc z10
        sta r1

        lda z11
        adc z20
        bcc q1_c2a_done
        inc z30
        beq q1_c2a_overflow
        clc
q1_c2a_done:
        adc z02
        sta r2

        lda z12
        adc z03
        bcc q1_c3a_done
        inx
        clc
q1_c3a_done:
        adc z30
        bcc q1_c3b_done
        inx
        beq q1_c3b_overflow
        clc
q1_c3b_done:
        adc z21
        sta r3

        txa
        adc z13
        bcc q1_c4a_done
        iny
        clc
q1_c4a_done:
        adc z31
        bcc q1_c4b_done
        iny
        beq q1_c4b_overflow
        clc
q1_c4b_done:
        adc z22
        tax

        tya
        adc z32
        bcc q1_c5a_done
        inc z24
        clc
q1_c5a_done:
        adc z23
        tay

        lda z33
        adc z24
        bcc q1_signed_correction
        inc r7
q1_signed_correction:
        sta q1_yneg_orig_a+1
        txa
        sec
        sbc q1__sqr_lo_0+1
        tax
        tya
        sbc x1
        tay
q1_yneg_orig_a:
        lda #0
        sbc x2
        sta q1_yneg_restore_a+1
        lda r7
        sbc x3
        sta r7
q1_yneg_restore_a:
        lda #0
        rts

q1_c2a_overflow:
        inc z31
        bne q1_c2a_overflow_done
        inc z32
        bne q1_c2a_overflow_done
        inc z33
        bne q1_c2a_overflow_done
        inc z34
q1_c2a_overflow_done:
        clc
        jmp q1_c2a_done

q1_c3b_overflow:
        inc z32
        bne q1_c3b_overflow_done
        inc z33
        bne q1_c3b_overflow_done
        inc z34
q1_c3b_overflow_done:
        clc
        jmp q1_c3b_done
q1_c4b_overflow:
        inc z33
        bne q1_c4b_overflow_done
        inc z34
q1_c4b_overflow_done:
        clc
        jmp q1_c4b_done
q1_cg_code_end:

*=$7000
cg_sqr_lo_start:
sqr_lo:
!for i,0,510 { !byte <((i*i + 202*(i&1))/4) }
cg_sqr_lo_end:
!align 255,0,0
cg_sqr_hi_start:
sqr_hi:
!for i,0,510 { !byte >((i*i + 202*(i&1))/4) }
cg_sqr_hi_end:
!align 255,0,0
cg_neg_lo_start:
neg_sqr_lo:
!for i,0,510 { !byte 255-(<(((255-i)*(255-i)+202*((255-i)&1))/4)) }
cg_neg_lo_end:
!align 255,0,0
cg_neg_hi_start:
neg_sqr_hi:
!for i,0,510 { !byte 255-(>(((255-i)*(255-i)+202*((255-i)&1))/4)) }
cg_neg_hi_end:
