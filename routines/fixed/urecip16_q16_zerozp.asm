; 16-bit unsigned divisor -> unsigned Q16 reciprocal Q24 = floor(65536/D16).
; Independent source-linked 24-step divide reference, NOT historical V2/V4 fast.
; D16 preserved; Q0..Q2 written; Q3 and R0..R3 untouched.
; D=0: Q24=0 and C=1. D!=0: exact Q24, C=0. Requires CLD.
; Only 1 exclusive ordinary RAM scratch byte, zero ZP, no tables/REU/SMC.
!cpu 6510
KERNEL_CODE = $8000
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
TEMP_RAM = $C020
R0 = TEMP_RAM
* = KERNEL_CODE
FAST_URECIP16_Q16_ZEROZP:
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne RECIP_NONZERO
    jmp RECIP_ZERO
RECIP_NONZERO:
    lda #0
    sta OUTPUT_QUOT+0
    sta OUTPUT_QUOT+1
    sta R0
    lda #1
    sta OUTPUT_QUOT+2
    lda #0
    ldx #24
RECIP_LOOP:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol R0
    rol a
    bcs RECIP_TAKE
    cmp INPUT_DIV+1
    bcc RECIP_SKIP
    bne RECIP_TAKE
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc RECIP_SKIP
RECIP_TAKE:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
RECIP_SKIP:
    dex
    bne RECIP_LOOP
    clc
    rts
RECIP_ZERO:
    lda #0
    sta OUTPUT_QUOT+0
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sec
    rts
