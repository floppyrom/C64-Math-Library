; SMUL32 compact126 record — native signed 32x32 -> 64.
; Validated 2026-10-05; derived from the Turbo32 quarter-square producer.
; Resource contract:
;   - 136 bytes page zero reserved: $0a..$1f plus $8e..$ff
;   - 126 bytes persistent hardware-stack-page code ($0100..$017d)
;   - 302 bytes ordinary-RAM code: signed wrapper $1200..$12f2 + cold helpers $1300..$133a
;   - 2044 bytes quarter-square data
; Native benchmark ABI: x0..x3 are prebound SMC bytes, y0..y2 are memory bytes,
; CPU Y=y3 and A=x0 on entry; result is r0..r3,Y,X,A,r7.
; Caller input stores are excluded from the published timing, as with the other native record points.
!cpu 6510
TABLE_BIAS_AFTER_DIV = 0
RESULT_YX = 1
REG_LOW = $1000
TURBO32_ZP_BASE = $0a
sqr_lo = $7000
sqr_hi = $7200
neg_lo = $7400
neg_hi = $7600
summation = $00ff

z00=TURBO32_ZP_BASE+$00
z10=TURBO32_ZP_BASE+$01
z20=TURBO32_ZP_BASE+$02
z30=TURBO32_ZP_BASE+$03
z01=TURBO32_ZP_BASE+$04
z11=TURBO32_ZP_BASE+$05
z21=TURBO32_ZP_BASE+$06
z31=TURBO32_ZP_BASE+$07
z02=TURBO32_ZP_BASE+$08
z12=TURBO32_ZP_BASE+$09
z22=TURBO32_ZP_BASE+$0a
z32=TURBO32_ZP_BASE+$0b
z03=TURBO32_ZP_BASE+$0c
z13=TURBO32_ZP_BASE+$0d
z23=TURBO32_ZP_BASE+$0e
z33=TURBO32_ZP_BASE+$0f
z14=TURBO32_ZP_BASE+$10
z24=TURBO32_ZP_BASE+$11
z34=TURBO32_ZP_BASE+$12
y0=$1d
y1=$1e
y2=$1f
r0=TURBO32_ZP_BASE+$00
r1=TURBO32_ZP_BASE+$01
r2=TURBO32_ZP_BASE+$02
r3=TURBO32_ZP_BASE+$03
r7=TURBO32_ZP_BASE+$12

; ---------------------------------------------------------------------------
; Column summation begins at $00ff so the final producer BEQ reaches it
; directly.  Bytes $0100..$017d are persistent code and must be reserved.
; ---------------------------------------------------------------------------
*=$00ff
summation:
        tay
        clc
        lda z01
        adc z10
        sta r1
        ; Compact X-state encoding of the first possible column-2 carry.
        ; X=0 on producer exit.  INX remembers the first carry while C
        ; carries the second addition directly into column 3.
        lda z20
        adc z11
        bcc hy_c2_first_done
        inx
        clc
hy_c2_first_done:
        adc z02
        sta r2

        lda z03
        adc z12
        bcc hy_c3_path0
        iny
        cpx #1
        adc z30
        bcc hy_c3_done
        clc
        iny
        bne hy_c3_done
        jmp hy_c3_over_imp
hy_c3_path0:
        adc z30
        bcc hy_c3_path0_noinc
        iny
hy_c3_path0_noinc:
        cpx #1
hy_c3_done:
        adc z21
        sta r3

        ; Rejoin the faster bounded late-column machinery.
        tya
        adc z22
        bcs bc_c4a_k1
        adc z31
        bcs bc_c4b_k1
bc_c4_k0_common:
        adc z13
        tay
        lda z14
        adc z32
        bcs bc_c5b_k1_m0
        adc z23
        tax
        lda z24
        adc z33
        bcs bc_final_carry
        rts
bc_c5b_k1_m0:
        clc
bc_c5b_k1_m1:
        adc z23
        tax
        lda z24
        adc z33
        bcs bc_c6_done
        adc #1
        bcs bc_final_carry
        rts
bc_c6_done:
        adc #0
bc_final_carry:
        inc r7
        rts
bc_c4a_k1:
        clc
        adc z31
        bcc bc_c4b_one_clear
bc_c4b_k2:
        inc z14
bc_c4b_k1:
        clc
bc_c4b_one_clear:
        adc z13
        tay
        lda z14
        adc z32
        bcs bc_c5b_k1_m1
bc_c5b_k0_m1_alt:
        sec
bc_c5b_k0_m0_alt:
        adc z23
        tax
        lda z24
        adc z33
        bcs bc_final_carry
        rts

; ---------------------------------------------------------------------------
; 136-byte page-zero reservation:
; $0a..$1c row/result overlay, $1d..$1f preserved Y inputs, and
; $8e..$ff producer code + the first summation instruction at $00ff.
; ---------------------------------------------------------------------------
*=TURBO32_ZP_BASE
!byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
*=$8e
cg_zp_code_start:
p1_carry:
        clc
        adc (NL1),y
        sta z01-1,x
        lda #1
        adc (SH1),y
        adc (NH1),y
        adc (SL2),y
        bcc p2_hot
p2_carry:
        clc
        adc (NL2),y
        sta z02-1,x
        lda #1
        adc (SH2),y
        adc (NH2),y
        adc (SL3),y
        bcc p3_hot
p3_carry:
        clc
        adc (NL3),y
        sta z03-1,x
        lda #1
        adc (SH3),y
        adc (NH3),y
        dex
        beq summation
loop:
        sta z14-1,x
        ldy y0-1,x

umult32x8_same_x:
x0=*+1
        lda sqr_lo,y
NL0=*+1
        adc neg_lo,y
        sta z00-1,x
SH0=*+1
        lda sqr_hi,y
NH0=*+1
        adc neg_hi,y
x1=*+1
        adc sqr_lo,y
        bcs p1_carry
p1_hot:
NL1=*+1
        adc neg_lo,y
        sta z01-1,x
SH1=*+1
        lda sqr_hi,y
NH1=*+1
        adc neg_hi,y
x2=*+1
SL2=*+1
        adc sqr_lo,y
        bcs p2_carry
p2_hot:
NL2=*+1
        adc neg_lo,y
        sta z02-1,x
SH2=*+1
        lda sqr_hi,y
NH2=*+1
        adc neg_hi,y
x3=*+1
SL3=*+1
        adc sqr_lo,y
        bcs p3_carry
p3_hot:
NL3=*+1
        adc neg_lo,y
        sta z03-1,x
SH3=*+1
        lda sqr_hi,y
NH3=*+1
        adc neg_hi,y
        dex
        bne loop
cg_zp_end:

; ---------------------------------------------------------------------------
; Signed composition.  Same quadrant strategy as the 31-ZP candidate.
; ---------------------------------------------------------------------------
*=$1200
; Signed wrapper with quadrant-local binding.
smul32_turbo_composed:
        ldx x3
        bmi smul32_turbo_xneg

; Positive-X common binder. Y is untouched, so its sign test can be deferred
; until after binding and PP/PN share this copy.
smul32_pos_bind:
        sta SH0
        eor #$ff
        sta NL0
        sta NH0
        lda x1
        sta SH1
        eor #$ff
        sta NL1
        sta NH1
        lda x2
        sta SH2
        eor #$ff
        sta NL2
        sta NH2
        txa
        sta SH3
        eor #$ff
        sta NL3
        sta NH3
        cpy #$00
        bmi smul32_turbo_yneg_bound
        ldx #4
        jmp umult32x8_same_x

smul32_turbo_yneg_bound:
        ldx #4
        jsr umult32x8_same_x
        sta smul32_turbo_yneg_orig_a+1
        tya
        sec
        sbc x0
        tay
        txa
        sbc x1
        tax
smul32_turbo_yneg_orig_a:
        lda #0
        sbc x2
        sta smul32_turbo_yneg_restore_a+1
        lda r7
        sbc x3
        sta r7
smul32_turbo_yneg_restore_a:
        lda #0
        rts

smul32_turbo_xneg:
        cpy #$00
        bmi smul32_turbo_nn
        ; Keep Y low bytes separate from the row overlay.  Bind X inline and
        ; JSR only the producer, avoiding JSR binder -> JMP producer.
        sty smul32_turbo_saved_y3+1
        sta SH0
        eor #$ff
        sta NL0
        sta NH0
        lda x1
        sta SH1
        eor #$ff
        sta NL1
        sta NH1
        lda x2
        sta SH2
        eor #$ff
        sta NL2
        sta NH2
        txa
        sta SH3
        eor #$ff
        sta NL3
        sta NH3
        ldx #4
        jsr umult32x8_same_x
        sta smul32_turbo_xneg_orig_a+1
        tya
        sec
        sbc y0
        tay
        txa
        sbc y1
        tax
smul32_turbo_xneg_orig_a:
        lda #0
        sbc y2
        sta smul32_turbo_xneg_restore_a+1
        lda r7
smul32_turbo_saved_y3:
        sbc #0
        sta r7
smul32_turbo_xneg_restore_a:
        lda #0
        rts

smul32_turbo_nn:
        ; CPY #$00 leaves C=1 for every byte; BMI selects negative y and keeps that carry.
        eor #$ff
        adc #0
        sta x0
        sta SH0
        eor #$ff
        sta NL0
        sta NH0
        bcs smul32_turbo_nn_x0zero
        lda x1
        sta NL1
        sta NH1
        eor #$ff
        sta x1
        sta SH1
        lda x2
        sta NL2
        sta NH2
        eor #$ff
        sta x2
        sta SH2
        lda x3
        sta NL3
        sta NH3
        eor #$ff
        sta x3
        sta SH3
smul32_turbo_nn_y:
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
        ldx #4
        sec
        jmp umult32x8_same_x
smul32_turbo_composed_end:


; Cold column-3 overflow helper exported from stack page.
*=$1300
hy_c3_over_imp:
        inc z32
        bne hy_c3_over_done_tramp
        inc z33
        bne hy_c3_over_done_tramp
        inc r7
hy_c3_over_done_tramp:
        clc
        jmp hy_c3_done

smul32_turbo_nn_x0zero:
        lda #0
        sbc x1
        sta x1
        sta SH1
        eor #$ff
        sta NL1
        sta NH1
        lda #0
        sbc x2
        sta x2
        sta SH2
        eor #$ff
        sta NL2
        sta NH2
        lda #0
        sbc x3
        sta x3
        sta SH3
        eor #$ff
        sta NL3
        sta NH3
        jmp smul32_turbo_nn_y

; ---------------------------------------------------------------------------
; Quarter-square planes used by the record family: bias after floor(i*i/4).
; ---------------------------------------------------------------------------
*=$7000
sqr_lo:
!for i,0,510 { !byte <((i*i)/4 + 202*(i&1)) }
!align 255,0,0
sqr_hi:
!for i,0,510 { !byte >((i*i)/4 + 202*(i&1)) }
!align 255,0,0
neg_lo:
!for i,0,510 { !byte 255-(<(((255-i)*(255-i))/4 + 202*((255-i)&1))) }
!align 255,0,0
neg_hi:
!for i,0,510 { !byte 255-(>(((255-i)*(255-i))/4 + 202*((255-i)&1))) }
