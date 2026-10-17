; Self-contained signed 16x16 full-product then 32/16 divide.
; Inputs signed iff named SMUL; X16/Y16/D16 unchanged, full Q32 and R16.
; D=0 -> Q32=R16=0 and C=1; other inputs return C=0 (CLD required).
; Z[0..3] and N[0..3] are temporary/volatile. R[2..3] preserved.
; Zero ZP, six private ordinary RAM scratch bytes, no SMC or init.
; Correctness-first replacement for independently selective linking.
!cpu 6510
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020
R0 = TEMP_RAM
D0 = TEMP_RAM+1
D1 = TEMP_RAM+2
* = KERNEL_CODE
FAST_UMUL16_COMPACT:
    lda INPUT_X
    sta TEMP_RAM
    lda INPUT_X+1
    sta TEMP_RAM+1
    lda #$00
    sta TEMP_RAM+2
    sta TEMP_RAM+3
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    sta OUTPUT_Z+2
    sta OUTPUT_Z+3
    lda INPUT_Y
    sta TEMP_RAM+4
    lda INPUT_Y+1
    sta TEMP_RAM+5
    ldx #$10
umul16_loop:
    lsr TEMP_RAM+5
    ror TEMP_RAM+4
    bcc umul16_skip_add
    clc
    lda OUTPUT_Z
    adc TEMP_RAM
    sta OUTPUT_Z
    lda OUTPUT_Z+1
    adc TEMP_RAM+1
    sta OUTPUT_Z+1
    lda OUTPUT_Z+2
    adc TEMP_RAM+2
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc TEMP_RAM+3
    sta OUTPUT_Z+3
umul16_skip_add:
    asl TEMP_RAM
    rol TEMP_RAM+1
    rol TEMP_RAM+2
    rol TEMP_RAM+3
    dex
    bne umul16_loop
    clc
    rts

; Two's-complement correction: (x-uX*65536)(y-uY*65536) mod 2^32
; equals (x*y - sign(x)*y*65536 - sign(y)*x*65536) mod 2^32.
; The low product word is unchanged; correct only the high word.
FAST_SMUL16_COMPACT:
    jsr FAST_UMUL16_COMPACT
    lda INPUT_X+1
    bpl smul16_x_done
    sec
    lda OUTPUT_Z+2
    sbc INPUT_Y
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    sbc INPUT_Y+1
    sta OUTPUT_Z+3
smul16_x_done:
    lda INPUT_Y+1
    bpl smul16_y_done
    sec
    lda OUTPUT_Z+2
    sbc INPUT_X
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    sbc INPUT_X+1
    sta OUTPUT_Z+3
smul16_y_done:
    clc
    rts

FAST_SDIV32_16_ZEROZP:
FAST_SMOD32_16_ZEROZP:
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne SDIV32_16_NONZERO
    jmp SDIV32_16_ZERO
SDIV32_16_NONZERO:
    lda INPUT_NUM+0
    sta OUTPUT_QUOT+0
    lda INPUT_NUM+1
    sta OUTPUT_QUOT+1
    lda INPUT_NUM+2
    sta OUTPUT_QUOT+2
    lda INPUT_NUM+3
    sta OUTPUT_QUOT+3
    bpl SDIV32_16_N_ABS_DONE
    lda #0
    sec
    sbc OUTPUT_QUOT
    sta OUTPUT_QUOT
    lda #0
    sbc OUTPUT_QUOT+1
    sta OUTPUT_QUOT+1
    lda #0
    sbc OUTPUT_QUOT+2
    sta OUTPUT_QUOT+2
    lda #0
    sbc OUTPUT_QUOT+3
    sta OUTPUT_QUOT+3
SDIV32_16_N_ABS_DONE:
    lda INPUT_DIV
    sta D0
    lda INPUT_DIV+1
    sta D1
    bpl SDIV32_16_D_ABS_DONE
    lda #0
    sec
    sbc D0
    sta D0
    lda #0
    sbc D1
    sta D1
SDIV32_16_D_ABS_DONE:
    lda #0
    sta R0
    ldx #32
SDIV32_16_LOOP:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs SDIV32_16_TAKE
    cmp D1
    bcc SDIV32_16_SKIP
    bne SDIV32_16_TAKE
    tay
    lda R0
    cmp D0
    tya
    bcc SDIV32_16_SKIP
SDIV32_16_TAKE:
    tay
    lda R0
    sbc D0
    sta R0
    tya
    sbc D1
    inc OUTPUT_QUOT+0
SDIV32_16_SKIP:
    dex
    bne SDIV32_16_LOOP
    sta OUTPUT_REM+1
    lda R0
    sta OUTPUT_REM+0
    lda INPUT_NUM+3
    eor INPUT_DIV+1
    bpl SDIV32_16_Q_DONE
    lda #0
    sec
    sbc OUTPUT_QUOT
    sta OUTPUT_QUOT
    lda #0
    sbc OUTPUT_QUOT+1
    sta OUTPUT_QUOT+1
    lda #0
    sbc OUTPUT_QUOT+2
    sta OUTPUT_QUOT+2
    lda #0
    sbc OUTPUT_QUOT+3
    sta OUTPUT_QUOT+3
SDIV32_16_Q_DONE:
    lda INPUT_NUM+3
    bpl SDIV32_16_R_DONE
    lda #0
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    lda #0
    sbc OUTPUT_REM+1
    sta OUTPUT_REM+1
SDIV32_16_R_DONE:
    clc
    rts
SDIV32_16_ZERO:
    lda #0
    sta OUTPUT_QUOT+0
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_QUOT+3
    sta OUTPUT_REM+0
    sta OUTPUT_REM+1
    sec
    rts

FAST_SMULDIV16_PORTABLE:
    jsr FAST_SMUL16_COMPACT
    ldx #3
MULDIV16_S_COPY:
    lda OUTPUT_Z,x
    sta INPUT_NUM,x
    dex
    bpl MULDIV16_S_COPY
    jsr FAST_SDIV32_16_ZEROZP
    rts
