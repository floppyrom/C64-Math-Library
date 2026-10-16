; Source-linked unsigned 32/16 public DIV/MOD shared reference producer.
; Correct reference kernel (not the faster historical V1-V5 source).
; N32/D16 inputs preserved; Q32/R16 always written by either entry.
; On zero divisor, Q32=R16=0 and C=1; success returns C=0.
; No tables, no REU, no illegal opcodes, no SMC. CLD required.
; 3 bytes private RAM scratch store the 17-bit interim remainder.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020
R0 = TEMP_RAM
R1 = TEMP_RAM+1
R2 = TEMP_RAM+2
* = KERNEL_CODE
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
