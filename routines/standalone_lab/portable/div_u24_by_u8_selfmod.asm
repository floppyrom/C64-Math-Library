; Standalone C64ML RAM-only self-modifying 24-bit/8-bit division kernel.
; Manual C64ML optimization after Repose-derived V1 short-divisor engine.
; Precondition: N2>0, D1=D2=0, D0>0. NOT generic unsigned 24/24!
; Caller owns writable executable RAM (self-modifying immediate operands),
; inputs and outputs; CLD required. NOT ROM-safe or re-entrant.
; Q24, R24 and clear carry are produced under the exact precondition.
; Zero-divisor behavior is outside this kernel: caller must guard.
!cpu 6510
KERNEL_CODE = $8000
MATH_N = $c010
MATH_D = $c014
MATH_Q = $c018
MATH_R = $c01c
* = KERNEL_CODE
FAST_UDIV24_BY8_RAM_SMC:
V1LAT_24_BY_8:
    lda MATH_N+0
    sta MATH_Q+0
    lda MATH_N+1
    sta MATH_Q+1
    lda MATH_N+2
    sta MATH_Q+2
    lda MATH_D+0
    sta CPAT+1
    sta SPAT+1
    lda #0
    ldx #24
V1LAT_8_LOOP:
    asl MATH_Q+0
    rol MATH_Q+1
    rol MATH_Q+2
    rol a                   ; A carries the eight-bit partial remainder.
    bcs V1LAT_8_SUB        ; Carry = ninth remainder bit.
CPAT:
    cmp #$00           ; If A >= D0, CMP also sets C for SBC.
    bcc V1LAT_8_NEXT
V1LAT_8_SUB:
SPAT:
    sbc #$00           ; New A = (2*remainder + nextbit) - D0.
    inc MATH_Q+0           ; Set the quotient's bit zero.
V1LAT_8_NEXT:
    dex
    bne V1LAT_8_LOOP
    sta MATH_R+0           ; Only one R0 store, after all 24 bits.
    lda #0
    sta MATH_R+1
    sta MATH_R+2
    clc
    rts
