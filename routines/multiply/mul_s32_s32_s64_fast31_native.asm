; Experimental practical signed 32x32->64 composition.
; Base: C64-Math-Library v2 pareto_umul32.a (31 ZP, 649.822007 cycles native).
; Signed strategy learned from Repose OptiSearch:
;   PP: unsigned core
;   NP/PN: unsigned core + upper-half correction
;   NN: negate both operands, fuse X negation into binder, same-X core
; This source keeps the base 31-byte ZP allocation and reserves no stack page.
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

*=$5800
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
        sec
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
; Signed composition. BIT x3 and CPY #$80 preserve entry A=x0.
; ---------------------------------------------------------------------------
*=$5a00
smul32_composed:
        bit x3
        bmi smul32_xneg
        cpy #$80
        bcs smul32_yneg_only
        jmp umult32x32

smul32_xneg:
        cpy #$80
        bcs smul32_nn

        ldx y0
        stx q2_saved_y0+1
        ldx y1
        stx q2_saved_y1+1
        ldx y2
        stx q2_saved_y2+1
        sty q2_saved_y3+1
        jmp q2_umult32x32

smul32_yneg_only:
        jmp q1_umult32x32

smul32_nn:
        ; Negate X while simultaneously installing all bindings.
        ; CPY #$80 left C=1 because y is negative, exactly the +1 needed
        ; for two's-complement negation of the low X byte.
        eor #$ff
        adc #0
        sta _sqr_lo_0+1
        sta _sqr_hi_0+1
        eor #$ff
        sta _neg_lo_0+1
        sta _neg_hi_0+1

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

        ; Negate Y in place.  Start a fresh +1 chain.
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
        jmp umult32x32_same_x
smul32_composed_end:

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
        sec
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
        sec
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

; ---------------------------------------------------------------------------
; Optimized stable-library ABI path. Inputs MATH_X=$C000, MATH_Y=$C004;
; output MATH_Z=$C008. Sign dispatch precedes staging. q0/q2 share a public-X
; direct binder helper; q1 has a direct binder for its specialized core; NN
; constructs magnitudes and bindings directly from the public input.
; ---------------------------------------------------------------------------
*=$6200
api_smul32_fast:
        ldy $c007
        lda $c003
        bmi api_f_xneg
        cpy #$80
        bcs api_f_q1
api_f_q0:
        jsr api_f_bind_base
        jmp api_f_output
api_f_q1:
        jsr api_f_bind_q1
        jmp api_f_output
api_f_xneg:
        cpy #$80
        bcs api_f_nn
api_f_q2:
        jsr api_f_bind_base
        ; Subtract original public Y from the upper half in registers.
        sta api_f_q2_orig_a+1
        txa
        sec
        sbc $c004
        tax
        tya
        sbc $c005
        tay
api_f_q2_orig_a:
        lda #0
        sbc $c006
        sta api_f_q2_restore_a+1
        lda r7
        sbc $c007
        sta r7
api_f_q2_restore_a:
        lda #0
        jmp api_f_output

api_f_nn:
        ; CPY #$80 left C=1. Directly form |X| and bind it.
        lda #0
        sbc $c000
        sta _sqr_lo_0+1
        sta _sqr_hi_0+1
        eor #$ff
        sta _neg_lo_0+1
        sta _neg_hi_0+1
        lda #0
        sbc $c001
        sta x1
        sta _sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta _neg_hi_1+1
        lda #0
        sbc $c002
        sta x2
        sta _sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta _neg_hi_2+1
        lda #0
        sbc $c003
        sta x3
        sta _sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta _neg_hi_3+1
        sec
        lda #0
        sbc $c004
        sta y0
        lda #0
        sbc $c005
        sta y1
        lda #0
        sbc $c006
        sta y2
        lda #0
        sbc $c007
        tay
        jsr umult32x32_same_x

api_f_output:
        sta $c00e
        stx $c00c
        sty $c00d
        lda r0
        sta $c008
        lda r1
        sta $c009
        lda r2
        sta $c00a
        lda r3
        sta $c00b
        lda r7
        sta $c00f
        clc
        rts

; q0/q2 shared base binding helper. JSR return address becomes the continuation;
; tail-JMP into same_x means the producer RTS returns directly to the caller.
api_f_bind_base:
        ; Entry A is original x3 from sign dispatch: bind it before clobbering A.
        sta x3
        sta _sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta _neg_hi_3+1
        lda $c000
        sta _sqr_lo_0+1
        sta _sqr_hi_0+1
        eor #$ff
        sta _neg_lo_0+1
        sta _neg_hi_0+1
        lda $c001
        sta x1
        sta _sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta _neg_hi_1+1
        lda $c002
        sta x2
        sta _sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta _neg_hi_2+1
        lda $c004
        sta y0
        lda $c005
        sta y1
        lda $c006
        sta y2
        jmp umult32x32_same_x

; q1 binder targets the q1-special producer's SMC operands.
api_f_bind_q1:
        ; Entry A is original x3 from sign dispatch.
        sta x3
        sta q1__sqr_lo_3+1
        eor #$ff
        sta neg_lo_3
        sta q1__neg_hi_3+1
        lda $c000
        sta q1__sqr_lo_0+1
        sta q1__sqr_hi_0+1
        eor #$ff
        sta q1__neg_lo_0+1
        sta q1__neg_hi_0+1
        lda $c001
        sta x1
        sta q1__sqr_lo_1+1
        eor #$ff
        sta neg_lo_1
        sta q1__neg_hi_1+1
        lda $c002
        sta x2
        sta q1__sqr_lo_2+1
        eor #$ff
        sta neg_lo_2
        sta q1__neg_hi_2+1
        lda $c004
        sta y0
        lda $c005
        sta y1
        lda $c006
        sta y2
        jmp q1_umult32x32_same_x

; Reconstructed current stable API for matched-corpus differential validation.
*=$6500
api_smul32_current_reconstructed:
        lda $c001
        sta x1
        lda $c002
        sta x2
        lda $c003
        sta x3
        lda $c004
        sta y0
        lda $c005
        sta y1
        lda $c006
        sta y2
        ldy $c007
        lda $c000
        jsr umult32x32
        sta $c00e
        stx $c00c
        sty $c00d
        lda r0
        sta $c008
        lda r1
        sta $c009
        lda r2
        sta $c00a
        lda r3
        sta $c00b
        lda r7
        sta $c00f
        lda $c003
        bpl api_cur_x_done
        sec
        lda $c00c
        sbc $c004
        sta $c00c
        lda $c00d
        sbc $c005
        sta $c00d
        lda $c00e
        sbc $c006
        sta $c00e
        lda $c00f
        sbc $c007
        sta $c00f
api_cur_x_done:
        lda $c007
        bpl api_cur_y_done
        sec
        lda $c00c
        sbc $c000
        sta $c00c
        lda $c00d
        sbc $c001
        sta $c00d
        lda $c00e
        sbc $c002
        sta $c00e
        lda $c00f
        sbc $c003
        sta $c00f
api_cur_y_done:
        clc
        rts
