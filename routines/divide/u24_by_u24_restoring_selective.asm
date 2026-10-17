; Portable 24/24 restoring shared unsigned divide/modulo public alias.
; Exact Q24/R24, N/D unchanged; division zero Q=R=0 and C=1.
; Zero ZP, 4 reusable RAM scratch, no tables, REU or SMC; CLD required.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020
R0 = TEMP_RAM+0
R1 = TEMP_RAM+1
R2 = TEMP_RAM+2
R3 = TEMP_RAM+3
* = KERNEL_CODE
FAST_UDIV24_RESTORING:
FAST_UMOD24_RESTORING:
    lda INPUT_DIV
    ora INPUT_DIV+1
    ora INPUT_DIV+2
    bne NONZERO
    jmp ZERO
NONZERO:
    lda INPUT_NUM
    sta OUTPUT_QUOT
    lda INPUT_NUM+1
    sta OUTPUT_QUOT+1
    lda INPUT_NUM+2
    sta OUTPUT_QUOT+2
    lda #0
    sta R0
    sta R1
    sta R2
    sta R3
    ldx #24
LOOP:
    clc
    rol OUTPUT_QUOT
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol R0
    rol R1
    rol R2
    rol R3
    lda R3
    bne TAKE
    lda R2
    cmp INPUT_DIV+2
    bcc SKIP
    bne TAKE
    lda R1
    cmp INPUT_DIV+1
    bcc SKIP
    bne TAKE
    lda R0
    cmp INPUT_DIV
    bcc SKIP
TAKE:
    sec
    lda R0
    sbc INPUT_DIV
    sta R0
    lda R1
    sbc INPUT_DIV+1
    sta R1
    lda R2
    sbc INPUT_DIV+2
    sta R2
    lda R3
    sbc #0
    sta R3
    inc OUTPUT_QUOT
SKIP:
    dex
    beq DONE
    jmp LOOP
DONE:
    lda R0
    sta OUTPUT_REM
    lda R1
    sta OUTPUT_REM+1
    lda R2
    sta OUTPUT_REM+2
    clc
    rts
ZERO:
    lda #0
    sta OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_REM
    sta OUTPUT_REM+1
    sta OUTPUT_REM+2
    sec
    rts
