; Direct CPU UDIV8; faster than the prior public adapter (and faster than REU quotient fetch).
; Direct stable-memory ABI: inputs remain in MATH_N/MATH_D and q/r are written directly.
; NMOS 6510 target; decimal mode must be clear.
* = MATH_UDIV8
    jmp DU8_div_u8

* = REG_KERNEL
DU8_cg_code_start:
DU8_zero:
 sta MATH_Q
 sta MATH_R
 sec
 rts
DU8_div_u8:
 lda MATH_D
 beq DU8_zero
 lda MATH_N
 cmp MATH_D
 bcs DU8_cont0
 sta MATH_R
 lda #0
 sta MATH_Q
 rts
DU8_cont0:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont1
 sta MATH_R
 lda #1
 sta MATH_Q
 rts
DU8_cont1:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont2
 sta MATH_R
 lda #2
 sta MATH_Q
 rts
DU8_cont2:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont3
 sta MATH_R
 lda #3
 sta MATH_Q
 rts
DU8_cont3:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont4
 sta MATH_R
 lda #4
 sta MATH_Q
 rts
DU8_cont4:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont5
 sta MATH_R
 lda #5
 sta MATH_Q
 rts
DU8_cont5:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont6
 sta MATH_R
 lda #6
 sta MATH_Q
 rts
DU8_cont6:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont7
 sta MATH_R
 lda #7
 sta MATH_Q
 rts
DU8_cont7:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont8
 sta MATH_R
 lda #8
 sta MATH_Q
 rts
DU8_cont8:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont9
 sta MATH_R
 lda #9
 sta MATH_Q
 rts
DU8_cont9:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont10
 sta MATH_R
 lda #10
 sta MATH_Q
 rts
DU8_cont10:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont11
 sta MATH_R
 lda #11
 sta MATH_Q
 rts
DU8_cont11:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont12
 sta MATH_R
 lda #12
 sta MATH_Q
 rts
DU8_cont12:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont13
 sta MATH_R
 lda #13
 sta MATH_Q
 rts
DU8_cont13:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont14
 sta MATH_R
 lda #14
 sta MATH_Q
 rts
DU8_cont14:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont15
 sta MATH_R
 lda #15
 sta MATH_Q
 rts
DU8_cont15:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont16
 sta MATH_R
 lda #16
 sta MATH_Q
 rts
DU8_cont16:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont17
 sta MATH_R
 lda #17
 sta MATH_Q
 rts
DU8_cont17:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont18
 sta MATH_R
 lda #18
 sta MATH_Q
 rts
DU8_cont18:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_cont19
 sta MATH_R
 lda #19
 sta MATH_Q
 rts
DU8_cont19:
 sbc MATH_D
 cmp MATH_D
 bcs DU8_tail
 sta MATH_R
 lda #20
 sta MATH_Q
 rts
DU8_tail:
 sta MATH_R
 lda MATH_D
 sta ZP_MAIN+$0E
 ldx #0
 stx MATH_Q
DU8_align:
 lda ZP_MAIN+$0E
 asl
 bcs DU8_aligned
 cmp MATH_R
 bcc DU8_take
 beq DU8_take
DU8_aligned:
 lda MATH_R
DU8_bits:
 cmp ZP_MAIN+$0E
 bcc DU8_no_sub
 sbc ZP_MAIN+$0E
DU8_no_sub:
 rol MATH_Q
 lsr ZP_MAIN+$0E
 dex
 bpl DU8_bits
 sta MATH_R
 lda MATH_Q
 clc
 adc #20
 sta MATH_Q
 rts
DU8_take:
 sta ZP_MAIN+$0E
 inx
 bne DU8_align
DU8_cg_code_end:
