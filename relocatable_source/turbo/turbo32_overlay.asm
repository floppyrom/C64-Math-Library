; Build-time relocatable Turbo32 zero-page overlay.
; Arithmetic body is the validated exact Turbo32 source retained in the complete
; developer archive. Only the ZP origin is parameterized; the affine indexed
; store bases remain deliberately fixed because X carries the translated row coordinate.

sqr_lo=REG_TABLE+$1000
sqr_hi=REG_TABLE+$1200
neg_sqr_lo=REG_TABLE+$1400
neg_sqr_hi=REG_TABLE+$1600

* = TURBO32_ZP_BASE
cg_zp_start
muly0tail
        sta+1 z04

y2 = * + 1
        ldy #0
        ldx #<muly2tail
        bne umult32x8_same_x       ; X=$5b, therefore unconditional

* = TURBO32_ZP_BASE+$08
muly1tail
        sta+1 z14
muly1_after_high_store

y3 = * + 1
        ldy #0
        ldx #<summation
        ; FALL THROUGH: branch-free fourth-row entry

; ----------------------------------------------------------------------------
; Shared 32x8 -> 40 kernel, $18-$5a inclusive (67 bytes).
;
; X simultaneously selects:
;   - the four ZP indexed destinations; and
;   - the low byte of the final self-modified absolute JMP return.
;
; Store bases $6b/$71/$77/$7d produce the four affine row vectors:
;   row0 X=$0a -> $75 $7b $81 $87
;   row1 X=$12 -> $7d $83 $89 $8f
;   row2 X=$5b -> $c6 $cc $d2 $d8
;   row3 X=$78 -> $e3 $e9 $ef $f5
; ----------------------------------------------------------------------------

* = TURBO32_ZP_BASE+$0E
umult32x8_same_x
        stx+1 return_jmp + 1

; P00 = x0*y
x0 = * + 1
_sqr_lo_0
        lda sqr_lo,y
_neg_lo_0
        adc neg_sqr_lo,y
        sta $6b,x
_sqr_hi_0
        lda sqr_hi,y
_neg_hi_0
        adc neg_sqr_hi,y

; P10 = x1*y, fused into the previous high byte
x1 = * + 1
_sqr_lo_1
        adc sqr_lo,y
        bcs H10
_p10_hot
_neg_lo_1
        adc neg_sqr_lo,y
        sta $71,x
_sqr_hi_1
        lda sqr_hi,y
_p10_tail
_neg_hi_1
        adc neg_sqr_hi,y

; P20
x2 = * + 1
_sqr_lo_2
        adc sqr_lo,y
        bcs H20
_p20_hot
_neg_lo_2
        adc neg_sqr_lo,y
        sta $77,x
_sqr_hi_2
        lda sqr_hi,y
_p20_tail
_neg_hi_2
        adc neg_sqr_hi,y

; P30
x3 = * + 1
_sqr_lo_3
        adc sqr_lo,y
        bcs H30
_p30_hot
_neg_lo_3
        adc neg_sqr_lo,y
        sta $7d,x
_sqr_hi_3
        lda sqr_hi,y
_p30_tail
_neg_hi_3
        adc neg_sqr_hi,y

return_jmp
        jmp muly0tail              ; low operand is patched from X each row

; ----------------------------------------------------------------------------
; Row-2 return and zero-row shortcut.
; Reordering LDX/LDY makes the existing BNE test y1 at no nonzero-path cost.
; If y1=0, Y already contains zero and five STY zp stores synthesize the whole
; 32x8 row.  STY preserves Z, so BEQ is an unconditional return to the R1 tail
; after its normal high-byte STA.
; ----------------------------------------------------------------------------

* = TURBO32_ZP_BASE+$51
muly2tail
        sta+1 z24
        ldx #<muly1tail

y1 = * + 1
        ldy #0
        bne umult32x8_same_x

zero_y1_row
        sty+1 z10
        sty+1 z11
        sty+1 z12
        sty+1 z13
        sty+1 z14
        beq muly1_after_high_store

; ----------------------------------------------------------------------------
; Result bytes.  The layout is intentionally non-contiguous for speed.
; ----------------------------------------------------------------------------

* = TURBO32_ZP_BASE+$68
r3: !byte 0
r4: !byte 0
r5: !byte 0
z00:
r0: !byte 0
r1: !byte 0
r2: !byte 0

; ----------------------------------------------------------------------------
; Summation stage 1: row0 + row1.
; $78-$98 inclusive.  The carry-only branch at $97 jumps across the handler
; region to sum2.  X caches row3's fifth byte (z34) for the final carry.
; ----------------------------------------------------------------------------

* = TURBO32_ZP_BASE+$6E
summation
        tax                         ; X = z34 = future r7
        clc

z01 = * + 1
        lda #$01
z10 = * + 1
        adc #10
        sta+1 r1

z02 = * + 1
        lda #$02
z11 = * + 1
        adc #11
        sta+1 t0

z03 = * + 1
        lda #$03
z12 = * + 1
        adc #12
        sta+1 t1

z04 = * + 1
        lda #$04
z13 = * + 1
        adc #13
        sta+1 t2

        bcc sum2
        clc
        inc+1 z14
        bcc sum2                    ; C was cleared; taken only on carry path

; ----------------------------------------------------------------------------
; 41-byte dual indirect cascade in the old 42-byte handler hole.
;
; Why indirect is faster here than a flat +1-cycle accounting suggests:
; the duplicated absolute,Y accesses frequently page-cross.  (zp),Y is always
; 5 cycles, so on those events it is cycle-neutral while also removing JMP/BCS
; control-flow work.  Exact corpus accounting is in validate_sub615.py.
; ----------------------------------------------------------------------------

* = TURBO32_ZP_BASE+$8F
H10
        clc
        adc (_neg_lo_1 + 1),y
        sta $71,x
        lda #1
        adc (_sqr_hi_1 + 1),y

        ; duplicate P10 tail + begin P20 using existing ZP operand pointers
        adc (_neg_hi_1 + 1),y
        adc (_sqr_lo_2 + 1),y
        bcc _p20_hot
        ; P20 is cold too: fall through H20

H20
        clc
        adc (_neg_lo_2 + 1),y
        sta $77,x
        lda #1
        adc (_sqr_hi_2 + 1),y

        ; duplicate P20 tail + begin P30
        adc (_neg_hi_2 + 1),y
        adc (_sqr_lo_3 + 1),y
        bcc _p30_hot
        ; P30 is cold too: fall through H30

H30
        clc
        adc (_neg_lo_3 + 1),y
        sta $7d,x
        lda #1
        adc (_sqr_hi_3 + 1),y

        ; The only sqr_hi=$fe endpoint is index 510.  On a genuine cold
        ; entry at that endpoint the preceding repaired-low ADC cannot carry,
        ; so 1+sqr_hi+C <= $ff.  The validator checks this local invariant.
        bcc _p30_tail

        ; one unreachable byte keeps sum2 at the validated $c3 coordinate
        !byte $ea

; ----------------------------------------------------------------------------
; Summation stages 2 + 3, $c3-$fa.
; ----------------------------------------------------------------------------

* = TURBO32_ZP_BASE+$B9
sum2

t0 = * + 1
        lda #0
z20 = * + 1
        adc #20
        sta+1 r2

t1 = * + 1
        lda #1
z21 = * + 1
        adc #21
        sta+1 s0

t2 = * + 1
        lda #2
z22 = * + 1
        adc #22
        sta+1 s1

z14 = * + 1
        lda #3
z23 = * + 1
        adc #23
        sta+1 s2

        bcc sum3
        clc
        inc+1 z24

sum3
s0 = * + 1
        lda #0
z30 = * + 1
        adc #30
        sta+1 r3

s1 = * + 1
        lda #1
z31 = * + 1
        adc #31
        sta+1 r4

s2 = * + 1
        lda #2
z32 = * + 1
        adc #32
        sta+1 r5

z24 = * + 1
        lda #3
z33 = * + 1
        adc #33                    ; A = r6
        bcs sum3_final_carry
        rts
sum3_final_carry
        inx                        ; X = r7
        rts
cg_zp_end
