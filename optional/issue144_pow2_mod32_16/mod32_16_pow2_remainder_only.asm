; Issue #144 B - 32/16 unsigned remainder-only specialist.
; PRECONDITION: divisor D16 is NONZERO and EXACTLY a power of 2.
; N32=$C010..13, D16=$C014..15, output R16=$C01C..1D, C=0.
; Quotient Q32=$C018..1B is UNMODIFIED, NOT calculated.
; This is NOT a drop-in MATH_UMOD32_16 replacement (public alias also makes Q).
; Needs no ZP, tables or MATH_INIT. X/Y and stack remain unchanged.
; $0C00 is an example RAM location, not library-reserved memory.
!cpu 6510
* = $0C00
MATH_UMOD32_16_POW2_RONLY:
    lda $C014
    sec
    sbc #$01
    and $C010
    sta $C01C
    lda $C015
    sbc #$00
    and $C011
    sta $C01D
    clc
    rts
