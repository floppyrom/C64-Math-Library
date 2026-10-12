; Issue39 V1 Balanced 24/8 shared-subtraction screen (not yet shipped).
; 69 bytes vs shipped 84 at $1D00. Identical N/D/Q/R/C semantics.
!cpu 6510
MATH_N = $c010
MATH_D = $c014
MATH_Q = $c018
MATH_R = $c01c
* = $1d00
V1LAT_24_BY_8:
    lda MATH_N+0
    sta MATH_Q+0
    lda MATH_N+1
    sta MATH_Q+1
    lda MATH_N+2
    sta MATH_Q+2
    lda #0
    sta MATH_R+0
    ldx #24
V1LAT_8_LOOP:
    asl MATH_Q+0
    rol MATH_Q+1
    rol MATH_Q+2
    rol MATH_R+0
    lda MATH_R+0
    bcs V1LAT_8_SUB
    cmp MATH_D+0
    bcc V1LAT_8_NEXT
V1LAT_8_SUB:
    sbc MATH_D+0
    sta MATH_R+0
    inc MATH_Q+0
V1LAT_8_NEXT:
    dex
    bne V1LAT_8_LOOP
    lda #0
    sta MATH_R+1
    sta MATH_R+2
    clc
    rts
