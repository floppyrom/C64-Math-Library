; Shared signed N32/D16 quotient Q32, signed remainder R16; zero ZP.
; Q truncates toward zero, R follows numerator sign; -2^31/-1 wraps Q32.
; D=0 clears Q/R, C=1; otherwise C=0. N/D intact, R[2..3] untouched.
; 3 bytes exclusive ordinary-RAM scratch, no REU/SMC/tables, CLD required.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020
R0 = TEMP_RAM
D0 = TEMP_RAM+1
D1 = TEMP_RAM+2
* = KERNEL_CODE
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
