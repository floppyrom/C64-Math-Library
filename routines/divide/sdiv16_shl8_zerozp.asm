; Signed fixed-point (N16<<8) / D16, exact signed Q24 and signed R16.
; Truncates quotient toward zero, remainder sign as N, N/D unchanged.
; D=0: Q24/R16 zero, C=1; otherwise C=0. 3 RAM scratch, 0 ZP, CLD.
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
FAST_SDIV16_SHL8_ZEROZP:
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne SDIV16_SHL8_NONZERO
    jmp SDIV16_SHL8_ZERO
SDIV16_SHL8_NONZERO:
    lda INPUT_NUM
    sta OUTPUT_QUOT
    lda INPUT_NUM+1
    sta OUTPUT_QUOT+1
    bpl SDIV16_SHL8_N_ABS_DONE
    lda #0
    sec
    sbc OUTPUT_QUOT
    sta OUTPUT_QUOT
    lda #0
    sbc OUTPUT_QUOT+1
    sta OUTPUT_QUOT+1
SDIV16_SHL8_N_ABS_DONE:
    lda OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    lda OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    lda #0
    sta OUTPUT_QUOT
    lda INPUT_DIV
    sta D0
    lda INPUT_DIV+1
    sta D1
    bpl SDIV16_SHL8_D_ABS_DONE
    lda #0
    sec
    sbc D0
    sta D0
    lda #0
    sbc D1
    sta D1
SDIV16_SHL8_D_ABS_DONE:
    lda #0
    sta R0
    ldx #24
    lda #0
SDIV16_SHL8_LOOP:
    clc
    rol OUTPUT_QUOT
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol R0
    rol a
    bcs SDIV16_SHL8_TAKE
    cmp D1
    bcc SDIV16_SHL8_SKIP
    bne SDIV16_SHL8_TAKE
    tay
    lda R0
    cmp D0
    tya
    bcc SDIV16_SHL8_SKIP
SDIV16_SHL8_TAKE:
    tay
    lda R0
    sbc D0
    sta R0
    tya
    sbc D1
    inc OUTPUT_QUOT
SDIV16_SHL8_SKIP:
    dex
    bne SDIV16_SHL8_LOOP
    sta OUTPUT_REM+1
    lda R0
    sta OUTPUT_REM
    lda INPUT_NUM+1
    eor INPUT_DIV+1
    bpl SDIV16_SHL8_QUOT_SIGN_DONE
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
SDIV16_SHL8_QUOT_SIGN_DONE:
    lda INPUT_NUM+1
    bpl SDIV16_SHL8_REM_SIGN_DONE
    lda #0
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    lda #0
    sbc OUTPUT_REM+1
    sta OUTPUT_REM+1
SDIV16_SHL8_REM_SIGN_DONE:
    clc
    rts
SDIV16_SHL8_ZERO:
    lda #0
    sta OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_REM
    sta OUTPUT_REM+1
    sec
    rts
