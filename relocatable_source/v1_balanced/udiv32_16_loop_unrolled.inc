; Issue #39 V1 32/16 dual-loop unroll; source-level symbolic operands.
; Retain first iterations in existing core; unroll remaining 14 low and
; 15 high rounds. Source expresses ALL mutable ZP operands through ZP_MAIN,
; so reference $02 and alternate $07 relocate identically to parent core.
; Low-round code was at $1900-$1B6C and overlapped public SEEK state.
; Move LOW only to $4D80-$4FEC, free in V1 and V5; keep HIGH at $1B6D.
; All public division and movement entry/data addresses remain unchanged.
; Explicit branch labels are local to each copy and retain original widths.

* = REG_KERNEL+$046A
L446A:
D3216_HIGH_REDIRECT:
    jmp D3216_HIGH_ROUNDS

* = REG_KERNEL+$0570
L4570:
D3216_LOW_REDIRECT:
    jmp D3216_LOW_ROUNDS

* = REG_KERNEL+$0D80
D3216_LOW_ROUNDS:
    ; low-word iteration 2/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_2
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_2
    bne D3216_LOW_SIMPLE_2
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_2
D3216_LOW_SIMPLE_2:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_2
D3216_LOW_FULL_2:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_2:
    ; low-word iteration 3/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_3
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_3
    bne D3216_LOW_SIMPLE_3
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_3
D3216_LOW_SIMPLE_3:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_3
D3216_LOW_FULL_3:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_3:
    ; low-word iteration 4/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_4
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_4
    bne D3216_LOW_SIMPLE_4
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_4
D3216_LOW_SIMPLE_4:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_4
D3216_LOW_FULL_4:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_4:
    ; low-word iteration 5/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_5
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_5
    bne D3216_LOW_SIMPLE_5
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_5
D3216_LOW_SIMPLE_5:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_5
D3216_LOW_FULL_5:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_5:
    ; low-word iteration 6/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_6
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_6
    bne D3216_LOW_SIMPLE_6
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_6
D3216_LOW_SIMPLE_6:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_6
D3216_LOW_FULL_6:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_6:
    ; low-word iteration 7/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_7
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_7
    bne D3216_LOW_SIMPLE_7
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_7
D3216_LOW_SIMPLE_7:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_7
D3216_LOW_FULL_7:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_7:
    ; low-word iteration 8/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_8
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_8
    bne D3216_LOW_SIMPLE_8
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_8
D3216_LOW_SIMPLE_8:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_8
D3216_LOW_FULL_8:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_8:
    ; low-word iteration 9/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_9
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_9
    bne D3216_LOW_SIMPLE_9
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_9
D3216_LOW_SIMPLE_9:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_9
D3216_LOW_FULL_9:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_9:
    ; low-word iteration 10/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_10
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_10
    bne D3216_LOW_SIMPLE_10
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_10
D3216_LOW_SIMPLE_10:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_10
D3216_LOW_FULL_10:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_10:
    ; low-word iteration 11/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_11
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_11
    bne D3216_LOW_SIMPLE_11
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_11
D3216_LOW_SIMPLE_11:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_11
D3216_LOW_FULL_11:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_11:
    ; low-word iteration 12/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_12
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_12
    bne D3216_LOW_SIMPLE_12
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_12
D3216_LOW_SIMPLE_12:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_12
D3216_LOW_FULL_12:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_12:
    ; low-word iteration 13/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_13
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_13
    bne D3216_LOW_SIMPLE_13
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_13
D3216_LOW_SIMPLE_13:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_13
D3216_LOW_FULL_13:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_13:
    ; low-word iteration 14/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_14
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_14
    bne D3216_LOW_SIMPLE_14
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_14
D3216_LOW_SIMPLE_14:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_14
D3216_LOW_FULL_14:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_14:
    ; low-word iteration 15/15
    rol ZP_MAIN+$18
    rol ZP_MAIN+$19
    rol ZP_MAIN+$14
    rol a
    bcs D3216_LOW_FULL_15
    cmp ZP_MAIN+$11
    bcc D3216_LOW_NEXT_15
    bne D3216_LOW_SIMPLE_15
    ldy ZP_MAIN+$14
    cpy ZP_MAIN+$10
    bcc D3216_LOW_NEXT_15
D3216_LOW_SIMPLE_15:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    bcs D3216_LOW_NEXT_15
D3216_LOW_FULL_15:
    tay
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    sta ZP_MAIN+$14
    tya
    sbc ZP_MAIN+$11
    sec
D3216_LOW_NEXT_15:
    ldx #$00
    jmp REG_KERNEL+$056C

* = REG_LOW+$0B6D
D3216_HIGH_ROUNDS:
    ; high-word iteration 2/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_2
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_2:
    ; high-word iteration 3/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_3
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_3:
    ; high-word iteration 4/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_4
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_4:
    ; high-word iteration 5/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_5
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_5:
    ; high-word iteration 6/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_6
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_6:
    ; high-word iteration 7/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_7
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_7:
    ; high-word iteration 8/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_8
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_8:
    ; high-word iteration 9/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_9
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_9:
    ; high-word iteration 10/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_10
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_10:
    ; high-word iteration 11/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_11
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_11:
    ; high-word iteration 12/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_12
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_12:
    ; high-word iteration 13/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_13
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_13:
    ; high-word iteration 14/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_14
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_14:
    ; high-word iteration 15/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_15
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_15:
    ; high-word iteration 16/16
    asl ZP_MAIN+$12
    rol ZP_MAIN+$13
    rol ZP_MAIN+$14
    rol ZP_MAIN+$15
    sec
    lda ZP_MAIN+$14
    sbc ZP_MAIN+$10
    tay
    lda ZP_MAIN+$15
    sbc ZP_MAIN+$11
    bcc D3216_HIGH_NEXT_16
    sta ZP_MAIN+$15
    sty ZP_MAIN+$14
    inc ZP_MAIN+$12
D3216_HIGH_NEXT_16:
    ldx #$00
    jmp REG_KERNEL+$046D
