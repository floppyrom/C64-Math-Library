; Issue144 B: signed 32/16 remainder-only for POSITIVE power-of-two D16.
; N is arbitrary signed 32-bit. D signed16 must be +1,+2,...,+16384.
; Output signed R16 at $C01C-$C01D, carry clear. Q32 untouched, NOT produced.
; Not a drop-in replacement for MATH_SMOD32_16, which also returns quotient.
; No extra ZP or lookup; caller-owned example executable RAM $0C80.
!cpu 6510
* = $0C80
MATH_SMOD32_16_POSPOW2_RONLY:
    lda $C014
    sec
    sbc #1
    and $C010
    sta $C01C
    lda $C015
    sbc #0
    and $C011
    sta $C01D
    lda $C013
    bpl done
    lda $C01C
    ora $C01D
    beq done
    sec
    lda $C01C
    sbc $C014
    sta $C01C
    lda $C01D
    sbc $C015
    sta $C01D
done:
    clc
    rts
