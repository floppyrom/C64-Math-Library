; Direct public SDIV8/SMOD8. Exhaustive 65,536-pair candidate: zero errors.
; Only the magnitude divisor uses transient ZP; public signed inputs are preserved.
* = MATH_SDIV8
    jmp DS8_div_s8
* = MATH_SMOD8
    jmp DS8_div_s8

* = MATH_IO-$0220
DS8_cg_code_start:
DS8_zero:
 sta MATH_Q
 sta MATH_R
 sec
 rts
DS8_div_s8:
 lda MATH_D
 beq DS8_zero
 bpl DS8_dpos
 eor #$ff
 clc
 adc #1
DS8_dpos:
 sta ZP_MAIN+$0E
 lda MATH_N
 bpl DS8_npos_mag
 eor #$ff
 clc
 adc #1
DS8_npos_mag:
 cmp ZP_MAIN+$0E
 bcs DS8_cont0
 sta MATH_R
 lda #0
 sta MATH_Q
 bit MATH_N
 bmi DS8_q0_neg
 clc
 rts
DS8_q0_neg:
 sec
 sbc MATH_R
 sta MATH_R
 clc
 rts
DS8_cont0:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont1
 sta MATH_R
 lda #1
 sta MATH_Q
 bit MATH_N
 bmi DS8_q1_nneg
 bit MATH_D
 bmi DS8_q1_negpos
 clc
 rts
DS8_q1_negpos:
 lda #$ff
 sta MATH_Q
 clc
 rts
DS8_q1_nneg:
 lda #0
 sec
 sbc MATH_R
 sta MATH_R
 bit MATH_D
 bpl DS8_q1_negneg
 clc
 rts
DS8_q1_negneg:
 lda #$ff
 sta MATH_Q
 clc
 rts
DS8_cont1:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont2
 sta MATH_R
 lda #2
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont2:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont3
 sta MATH_R
 lda #3
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont3:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont4
 sta MATH_R
 lda #4
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont4:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont5
 sta MATH_R
 lda #5
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont5:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont6
 sta MATH_R
 lda #6
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont6:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont7
 sta MATH_R
 lda #7
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont7:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont8
 sta MATH_R
 lda #8
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont8:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont9
 sta MATH_R
 lda #9
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont9:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont10
 sta MATH_R
 lda #10
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont10:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont11
 sta MATH_R
 lda #11
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont11:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont12
 sta MATH_R
 lda #12
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont12:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont13
 sta MATH_R
 lda #13
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont13:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont14
 sta MATH_R
 lda #14
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont14:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont15
 sta MATH_R
 lda #15
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont15:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont16
 sta MATH_R
 lda #16
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont16:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont17
 sta MATH_R
 lda #17
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont17:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont18
 sta MATH_R
 lda #18
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont18:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_cont19
 sta MATH_R
 lda #19
 sta MATH_Q
 jmp DS8_signed_finish
DS8_cont19:
 sbc ZP_MAIN+$0E
 cmp ZP_MAIN+$0E
 bcs DS8_tail
 sta MATH_R
 lda #20
 sta MATH_Q
 jmp DS8_signed_finish
DS8_tail:
 sta MATH_R
 ldx #0
 stx MATH_Q
DS8_align:
 lda ZP_MAIN+$0E
 asl
 bcs DS8_aligned
 cmp MATH_R
 bcc DS8_take
 beq DS8_take
DS8_aligned:
 lda MATH_R
DS8_bits:
 cmp ZP_MAIN+$0E
 bcc DS8_no_sub
 sbc ZP_MAIN+$0E
DS8_no_sub:
 rol MATH_Q
 lsr ZP_MAIN+$0E
 dex
 bpl DS8_bits
 sta MATH_R
 lda MATH_Q
 clc
 adc #20
 sta MATH_Q
DS8_signed_finish:
 lda MATH_N
 bmi DS8_nneg
 eor MATH_D
 bmi DS8_negq
 rts
DS8_nneg:
 lda #0
 sec
 sbc MATH_R
 sta MATH_R
 lda MATH_D
 bmi DS8_done
DS8_negq:
 lda #0
 sec
 sbc MATH_Q
 sta MATH_Q
DS8_done:
 clc
 rts
DS8_take:
 sta ZP_MAIN+$0E
 inx
 bne DS8_align
DS8_cg_code_end:
