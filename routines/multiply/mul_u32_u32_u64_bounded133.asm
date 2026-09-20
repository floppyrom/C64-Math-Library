; Integration commentary revision 1
; Firemonger kernel; bounded-carry join and page placement refinement.
; Unsigned 32 x 32 -> 64; documented NMOS 6502 instructions, binary mode (D=0).
; Entry: x0..x3 in the named SMC operand bytes, y0..y2 in ZP, CPU Y=y3.
; Return MSB first: r7 A X Y r3 r2 r1 r0. A, X, Y, flags and row data clobbered.
; The core is self-modifying and non-reentrant; keep all bindings writable/private.
; Timing includes the final RTS; excludes caller JSR/input loading and C64 stalls.
; All input X bytes survive. Y bytes overlap outputs and must be supplied each time.
;
; Additional entry contracts (same generic result ABI):
; umult32x32_ax0: x0 operand STILL supplied; A ALSO contains x0. Saves 3 cycles.
; umult32x32_same_x: prior generic binding remains installed. Saves 56 cycles.
; umult32x8_same_x: despite its historical name, with X=4, Y=y3, C=1 and installed
; X bindings it completes all FOUR rows and the 64-bit sum. Saves 63 cycles.
;
; Fixed layout: code reserves the bottom 177 bytes of the hardware stack page.
; Stack writes must never reach $0100..$01b0. Keep interrupt and
; caller nesting headroom above it; see TECHNICAL_NOTE.md for exact reservations.
; Do not use a sparse-layout PRG as a ready-to-RUN C64 executable. Relocate/copy
; the occupied ranges using a loader which preserves the executing stack.
;
;ABI
;Entry: umult32x32
;CPU: mos6502
;Operation: umul
;Input x: uint32 = x0, x1, x2, x3
;Input y: uint32 = y0, y1, y2, reg:Y
;Output z: uint64 = r0, r1, r2, r3, reg:Y, reg:X, reg:A, r7
;Region ZP: cg_zp_start..cg_zp_data_end, cg_zp_code_start..cg_zp_code_end
;Region Code: cg_code_start..cg_code_end, cg_stack_start..cg_stack_end
;Region Data: cg_data0_start..cg_data0_end, cg_data1_start..cg_data1_end, cg_data2_start..cg_data2_end, cg_data3_start..cg_data3_end
;End ABI
;Results
;Status: validated
;Validation level: validate
;Validation cases: 67108864
;Validation errors: 0
;Validation complete: yes
;Edge cases: 1049350
;Edge errors: 0
;Edge complete: yes
;Profile distribution: uniform
;Profile cases: 67108864
;Profile errors: 0
;Profile complete: yes
;Min cycles: 542
;Max cycles: 729
;Avg cycles: 606.337632
;Stddev cycles: 22.533570
;ZP bytes: 133
;Code bytes: 236
;Data bytes: 2044
;Total bytes: 2280
;End Results
!cpu 6502

cg_zp_start = $02
cg_zp_data_end = $15
cg_zp_code_end = $100
cg_stack_start = $100
z00 = $02 : z10 = $03 : z20 = $04 : z30 = $05
z01 = $06 : z11 = $07 : z21 = $08 : z31 = $09
z02 = $0a : z12 = $0b : z22 = $0c : z32 = $0d
z03 = $0e : z13 = $0f : z23 = $10 : z33 = $11
z14 = $12 : z24 = $13 : z34 = $14
y0 = $02 : y1 = $03 : y2 = $04
r0 = $02 : r1 = $03 : r2 = $04 : r3 = $05 : r7 = $14

*=$2000
; Q(i) = floor(i*i/4) + 202*(i&1); the bias is AFTER division.
!align 255, 0, 0
cg_data0_start
sqr_lo: !for i,0,510 { !byte <((i*i)/4 + 202*(i&1)) }
cg_data0_end
!align 255, 0, 0
cg_data1_start
sqr_hi: !for i,0,510 { !byte >((i*i)/4 + 202*(i&1)) }
cg_data1_end
!align 255, 0, 0
cg_data2_start
neg_lo: !for i,0,510 { !byte 255 - (<(((255-i)*(255-i))/4 + 202*((255-i)&1))) }
cg_data2_end
!align 255, 0, 0
cg_data3_start
neg_hi: !for i,0,510 { !byte 255 - (>(((255-i)*(255-i))/4 + 202*((255-i)&1))) }
cg_data3_end

*=$200
cg_code_start
; The four 14-cycle bindings below account for 56 generic-entry cycles.
umult32x32
                lda+1 x0
umult32x32_ax0
                sta+1 SH0
                eor #$FF
                sta+1 NL0
                sta+1 NH0
                lda+1 x1
                sta+1 SH1
                eor #$FF
                sta+1 NL1
                sta+1 NH1
                lda+1 x2
                sta+1 SH2
                eor #$FF
                sta+1 NL2
                sta+1 NH2
                lda+1 x3
                sta+1 SH3
                eor #$FF
                sta+1 NL3
                sta+1 NH3
; Process y3, y2, y1, y0 in descending order, safely reusing Y-input slots.
umult32x32_same_x
                ldx #4
                sec
                jmp umult32x8_same_x

; A second increment of row-0 top byte can wrap. Ripple into row 3.
; The return target supplies the necessary CLC. z14 remains untouched here.
c3_over_imp     inc z32
                bne c3_over_done_tramp
                inc z33
                bne c3_over_done_tramp
                inc r7
c3_over_done_tramp
                jmp c3_over_done
cg_code_end

*= $8e
cg_zp_code_start
; Cold carry cascade: preserve the extra carry in the high partial product.
p1_carry        clc
                adc (NL1),y
                sta+1 z01-1,x
                lda #1
                adc (SH1),y
                adc (NH1),y
                adc (SL2),y
                bcc p2_hot
p2_carry        clc
                adc (NL2),y
                sta+1 z02-1,x
                lda #1
                adc (SH2),y
                adc (NH2),y
                adc (SL3),y
                bcc p3_hot
p3_carry        clc
                adc (NL3),y
                sta+1 z03-1,x
                lda #1
                adc (SH3),y
                adc (NH3),y
                dex
                beq summation
loop            sta+1 z14-1,x
                ldy+1 y0-1,x

; Each pass writes one complete 40-bit row x*yj. The low-byte operands
; also serve as ZP pointers in the cold carry cascade. Keep both pointer bytes
; in page zero. Entry X=4 selects all four rows; the final pass leaves X=0.
umult32x8_same_x
; P0: form the first two product bytes.
x0=*+1:         lda sqr_lo,y
NL0=*+1:        adc neg_lo,y
                sta+1 z00-1,x
SH0=*+1:        lda sqr_hi,y
NH0=*+1:        adc neg_hi,y
; P1: accumulate the preceding high byte into the next 8x8 product.
x1=*+1:         adc sqr_lo,y
                bcs p1_carry
p1_hot:NL1=*+1: adc neg_lo,y
                sta+1 z01-1,x
SH1=*+1:        lda sqr_hi,y
NH1=*+1:        adc neg_hi,y
; P2: accumulate the preceding high byte into the next 8x8 product.
x2=*+1:SL2=*+1: adc sqr_lo,y
                bcs p2_carry
p2_hot:NL2=*+1: adc neg_lo,y
                sta+1 z02-1,x
SH2=*+1:        lda sqr_hi,y
NH2=*+1:        adc neg_hi,y
; P3: accumulate the preceding high byte into the next 8x8 product.
x3=*+1:SL3=*+1: adc sqr_lo,y
                bcs p3_carry
p3_hot:NL3=*+1: adc neg_lo,y
                sta+1 z03-1,x
SH3=*+1:        lda sqr_hi,y
NH3=*+1:        adc neg_hi,y
                dex
                bne loop

; Columnwise accumulation. Pending multi-carries select continuations.
; Row bytes are zjk: row j contributes at output column j+k.
; Row-0 high byte is still in A; save it in Y for the column-3 carry handling.
summation
                tay
                clc
                ; Column 1: two summands, one carry into column 2.
                lda z01
                adc z10
                sta r1
                ; Column 2: its first overflow chooses the column-3 continuation.
                lda z20
                adc z02
                bcs c2_carry_to_c3
c2_done         adc z11
                sta r2
                lda z03
                adc z12
                bcc c3_path0
                iny
                clc
                adc z30
                bcc c3_done
                iny
                beq c3_over
c3_over_done    clc
c3_done         adc z21
                sta r3
                tya
                adc z22
                bcs c4a_k1
                adc z31
                bcs c4b_k1
                adc z13
                tay
                lda z14
                adc z32
                bcs c5b_k1_m0
                adc z23
                tax
                lda z24
                adc z33
                bcs final_carry
                rts
; Inject the carry deferred from column 2 on the appropriate path.
c3_path0_carry  sec
c3_path0        adc z30
                bcc c3_done
                iny
                clc
                adc z21
                sta r3
                tya
                adc z22
                bcs c4a_k1
                adc z31
                bcs c4b_k1
c4_k0_done      adc z13
                tay
                lda z14
                adc z32
                bcs c5b_k1_m0
c5b_k0_m0       adc z23
                tax
                lda z24
                adc z33
                bcs final_carry
                rts
; A pending extra column-3 carry is encoded by entering this code path.
c2_carry_to_c3  clc
                adc z11
                sta r2
                lda z03
                adc z12
                bcc c3_path0_carry
                iny
                adc z30
                bcc c3_done
                iny
                bne c3_over_done
c3_over         jmp c3_over_imp
; One extra carry is pending into column 6. Finish column 5 first.
c5b_k1_m0       clc
c5b_k1_m1       adc z23
                tax
                lda z24
                adc z33
                bcs c6_done
                adc #1
                bcs final_carry
                rts
final_carry     inc r7
                rts
c4a_k1          clc
                adc z31
                bcc c4b_one_clear ; C=0: skip both INC and redundant CLC
; Two carries are pending into column 5. Normalize ONE into z14 and then
; use the one-carry continuation. On entry z14 is the original top byte of
; x*y1, hence 0 <= z14 <= 254. INC cannot wrap and preserves C and A.
c4b_k2          inc z14
c4b_k1          clc
c4b_one_clear
                adc z13
                tay
                lda z14
                adc z32
                bcs c5b_k1_m1
c5b_k0_m1_alt   sec
c5b_k0_m0_alt   adc z23
                tax
                lda z24
                adc z33
                bcs final_carry
                rts
; The preceding high-byte ADC carried; fold in the deferred +1 and
; increment the most significant result byte. The row bounds prevent wrap
; of this extra ADC from requiring a second increment.
c6_done         adc #0
                inc r7
                rts
cg_stack_end
