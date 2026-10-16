; Zero-ZP shared public 32/16 DIV/MOD using A as remainder high byte.
; Independent RAM-only candidate, NOT the historical resident speed producer.
; 32/16 unsigned N/D preserved. Both entries write Q32 and R16.
; On D=0: Q32=R16=0, C=1. Otherwise C=0. D=0 (CLD) required.
; One byte TEMP_RAM stores low remainder; high is kept live in A.
; Does not use tables, REU, undocumented opcodes or self-modifying code.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020
R0 = TEMP_RAM
* = KERNEL_CODE
FAST_UDIV32_16_ACCUM:
FAST_UMOD32_16_ACCUM:
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
    ldx #32
DIV_LOOP:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE
    cmp INPUT_DIV+1
    bcc DIV_SKIP
    bne DIV_TAKE
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP
DIV_TAKE:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP:
    dex
    bne DIV_LOOP
    sta OUTPUT_REM+1
    lda R0
    sta OUTPUT_REM+0
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
