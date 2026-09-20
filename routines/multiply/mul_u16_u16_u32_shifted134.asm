; UMUL16: 134 ZP bytes, 0 ordinary code bytes, 3066 table bytes.
; Exact uniform average: 154.297827851260 cycles, fresh-X entry through RTS.
; Input: x0,x1,y1 at labels, y0 in Y. Output low-first: z0,X,A,Y.
; D=0 required. Writable ZP SMC, nonreentrant. NMOS AXS/SBX $CB required.
; Identity for each byte b: (x0*b+256)+256*(x1*b-1) = x*b.
; The strictly negative prefix -(x0*b+256) removes the zero-prefix branch.
; New planes: square-high+1 and plain-difference-low+1. The latter never
; wraps with bias 202, so its high plane can be shared with plain difference.
; No extra runtime bindings: generic binder 28 cycles, unchanged.
; umult_ax1: also A=x1, saves 3. same_x: installed X, saves 28.
; same_x_ready: installed X and C=1, saves 30. Always supply new Y/y1.
; gmec qualified the unchanged instructions below; original Results retained.
; See UMUL16_SHIFTED_ROWS_TECHNICAL_NOTES.md for derivation and limitations.
; Lineage: Firemonger, the retained negative-row/AXS work, and the carry
; sharing work prompted by Repose. No worldwide priority claim is made.
; Padded PRG is for the harness. Integrate the source sections on the C64.
;
; Experimental adjacent-product redistribution; fresh-X generic ABI.
;ABI
;CPU: mos6502
;Operation: umul
;Entry: umult
;Input x: uint16 = x0, x1
;Input y: uint16 = reg:Y, y1
;Output z: uint32 = z0, reg:X, reg:A, reg:Y
;Region ZP: cg_zp_start..cg_zp_end
;Region Code: cg_code_start..cg_code_end
;Region Data: cg_data0_start..cg_data0_end, cg_data1_start..cg_data1_end, cg_data2_start..cg_data2_end, cg_data3_start..cg_data3_end, cg_data4_start..cg_data4_end, cg_data5_start..cg_data5_end
;End ABI
;Results
;Status: validated
;Validation level: validate
;Validation cases: 8388608
;Validation errors: 0
;Validation complete: yes
;Edge cases: 262430
;Edge errors: 0
;Edge complete: yes
;Profile distribution: uniform
;Profile cases: 8388608
;Profile errors: 0
;Profile complete: yes
;Min cycles: 142
;Max cycles: 177
;Avg cycles: 154.293260
;Stddev cycles: 7.392763
;ZP bytes: 134
;Code bytes: 0
;Data bytes: 3066
;Total bytes: 3066
;End Results

!cpu 6502
PARITY_BIAS = $ca

* = $0002
cg_zp_start:

; Install x1 and x0 into the existing address operands.
umult:
        lda+1 x1
umult_ax1:
        sta+1 _sqr_hi_1+1
        eor #$ff
        sta+1 _neg_lo_1+1
        sta+1 _neg_hi_1+1

        lda+1 x0
        sta+1 _sqr_hi_0+1
        eor #$ff
        sta+1 _neg_lo_0+1
        sta+1 _neg_hi_0+1

umult_same_x:
        sec

umult_same_x_ready:

; P00 is x0*y0+256; z0 is unchanged by this high-byte offset.
x0 = *+1
_sqr_lo_0:
        lda sqr_lo,y
_neg_lo_0:
        sbc neg_sqr_lo,y
        sta+1 z0
_sqr_hi_0:
        lda sqr_hi_plus1,y
_neg_hi_0:
        sbc neg_sqr_hi,y

; P10 is x1*y0-1. Its shifted -1 cancels P00's +256.
x1 = *+1
_sqr_lo_1:
        adc sqr_lo,y
        bcs _p10_carry
_neg_lo_1:
        sbc neg_sqr_lo_plus1,y
        tax
_sqr_hi_1:
        lda sqr_hi,y
_p10_tail:
_neg_hi_1:
        sbc neg_sqr_hi,y
        sta+1 _z2_part1+1

; Start N=-x*y1. The first prefix is always strictly negative.
y1 = *+1
        ldy #0

        lda (_neg_lo_0+1),y
        sbc (_sqr_lo_0+1),y
        sta+1 _z1_part2+1
        lda (_neg_hi_0+1),y
        sbc (_sqr_hi_0+1),y

; Prefix carry is always clear; no zero-input handler is needed.
negative_prefix_ready:
        sbc (_sqr_lo_1+1),y
        bcc _p11_carry
p11_hot:
        adc (_neg_lo_1+1),y
negative_mid_ready:
        sta+1 _z2_part2+1
        lda (_neg_hi_1+1),y
        sbc (_sqr_hi_1+1),y
; Finish R0-256*N. AXS supplies the low merge and its no-borrow carry.
negative_high_ready:
        eor #$ff
        tay

        lda #$ff
_z1_part2:
        !byte $cb, 0             ; AXS #negative_low: X = (A & X) - operand
_z2_part1:
        lda #0
_z2_part2:
        sbc #0
        bcs _final_carry
        rts
_final_carry:
        iny
        rts

_p10_carry:
        clc
        sbc (_neg_lo_1+1),y
        tax
        lda #1
        adc (_sqr_hi_1+1),y
        sbc (_neg_hi_1+1),y
        sta+1 _z2_part1+1
        ldy+1 y1
        lda (_neg_lo_0+1),y
        sbc (_sqr_lo_0+1),y
        sta+1 _z1_part2+1
        lda (_neg_hi_0+1),y
        sbc (_sqr_hi_0+1),y
        sbc (_sqr_lo_1+1),y
        bcs p11_hot

_p11_carry:
        sec
        adc (_neg_lo_1+1),y
        sta+1 _z2_part2+1
        lda #$fe
        sbc (_sqr_hi_1+1),y
        adc (_neg_hi_1+1),y
        bcc negative_high_ready

z0:    !byte 0
cg_zp_end:

bind_sqr_hi_0 = _sqr_hi_0+1
bind_neg_lo_0 = _neg_lo_0+1
bind_neg_hi_0 = _neg_hi_0+1
bind_sqr_hi_1 = _sqr_hi_1+1
bind_neg_lo_1 = _neg_lo_1+1
bind_neg_hi_1 = _neg_hi_1+1

* = $1000
cg_code_start:
cg_code_end:

; Original plain quarter-square planes; bias is AFTER division by 4.
* = $2000
cg_data0_start:
sqr_lo:
!for i,0,510 { !byte <(((i*i)/4) + PARITY_BIAS*(i&1)) }
cg_data0_end:

* = $2200
cg_data1_start:
sqr_hi:
!for i,0,510 { !byte >(((i*i)/4) + PARITY_BIAS*(i&1)) }
cg_data1_end:

* = $2400
cg_data2_start:
neg_sqr_lo:
!for i,0,510 { !byte <(((((255-i)*(255-i))/4)+PARITY_BIAS*((255-i)&1))) }
cg_data2_end:

* = $2600
cg_data3_start:
neg_sqr_hi:
!for i,0,510 { !byte >(((((255-i)*(255-i))/4)+PARITY_BIAS*((255-i)&1))) }
cg_data3_end:

; Offset the first byte product by +256 without runtime instructions.
* = $2800
cg_data4_start:
sqr_hi_plus1:
!for i,0,510 { !byte >(((i*i)/4) + PARITY_BIAS*(i&1) + 256) }
cg_data4_end:

; Offset the second byte product by -1; no low-byte wrap is possible.
* = $2a00
cg_data5_start:
neg_sqr_lo_plus1:
!for i,0,510 { !byte <(((((255-i)*(255-i))/4)+PARITY_BIAS*((255-i)&1)+1)) }
cg_data5_end:
