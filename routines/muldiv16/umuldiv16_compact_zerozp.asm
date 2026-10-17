; Self-contained unsigned 16x16 full-product then 32/16 divide.
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
R1 = TEMP_RAM+1
R2 = TEMP_RAM+2
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

FAST_UDIV32_16_PORTABLE:
FAST_UMOD32_16_PORTABLE:
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne DIV_NONZERO
    jmp DIV_ZERO
DIV_NONZERO:
    lda INPUT_NUM+0
    sta OUTPUT_QUOT+0
    lda INPUT_NUM+1
    sta OUTPUT_QUOT+1
    lda INPUT_NUM+2
    sta OUTPUT_QUOT+2
    lda INPUT_NUM+3
    sta OUTPUT_QUOT+3
    lda #0
    sta R0
    sta R1
    sta R2
    ldx #32
DIV_LOOP:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol R1
    rol R2
    lda R2
    bne DIV_TAKE
    lda R1
    cmp INPUT_DIV+1
    bcc DIV_SKIP
    bne DIV_TAKE
    lda R0
    cmp INPUT_DIV
    bcc DIV_SKIP
DIV_TAKE:
    sec
    lda R0
    sbc INPUT_DIV
    sta R0
    lda R1
    sbc INPUT_DIV+1
    sta R1
    lda R2
    sbc #0
    sta R2
    inc OUTPUT_QUOT+0
DIV_SKIP:
    dex
    bne DIV_LOOP
    lda R0
    sta OUTPUT_REM+0
    lda R1
    sta OUTPUT_REM+1
    clc
    rts
DIV_ZERO:
    lda #0
    sta OUTPUT_QUOT+0
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_QUOT+3
    sta OUTPUT_REM+0
    sta OUTPUT_REM+1
    sec
    rts

FAST_UMULDIV16_PORTABLE:
    jsr FAST_UMUL16_COMPACT
    ldx #3
MULDIV16_U_COPY:
    lda OUTPUT_Z,x
    sta INPUT_NUM,x
    dex
    bpl MULDIV16_U_COPY
    jsr FAST_UDIV32_16_PORTABLE
    rts
