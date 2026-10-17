; Independently relocatable signed 16/16 quotient-and-remainder shared kernel.
; Truncates signed quotient toward zero; remainder has numerator's sign.
; Handles -32768 / -1 by two's-complement 16-bit wrapped quotient.
; On D=0 Q16=R16=0, C=1. Otherwise C=0. N/D preserved; Q/R high bytes untouched.
; No ZP, self-modifying code, tables or initialization. Three ordinary RAM scratch.
; Requires decimal clear (CLD); A/X/Y and non-carry flags volatile.
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
FAST_SDIV16_ZEROZP:
FAST_SMOD16_ZEROZP:
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne SDIV16_NONZERO
    jmp SDIV16_ZERO
SDIV16_NONZERO:
    lda INPUT_NUM
    sta OUTPUT_QUOT
    lda INPUT_NUM+1
    sta OUTPUT_QUOT+1
    bpl SDIV16_N_ABS_DONE
    lda #0
    sec
    sbc OUTPUT_QUOT
    sta OUTPUT_QUOT
    lda #0
    sbc OUTPUT_QUOT+1
    sta OUTPUT_QUOT+1
SDIV16_N_ABS_DONE:
    lda INPUT_DIV
    sta D0
    lda INPUT_DIV+1
    sta D1
    bpl SDIV16_D_ABS_DONE
    lda #0
    sec
    sbc D0
    sta D0
    lda #0
    sbc D1
    sta D1
SDIV16_D_ABS_DONE:
    lda #0
    sta R0
    ldx #16
    lda #0
SDIV16_LOOP:
    clc
    rol OUTPUT_QUOT
    rol OUTPUT_QUOT+1
    rol R0
    rol a
    bcs SDIV16_TAKE
    cmp D1
    bcc SDIV16_SKIP
    bne SDIV16_TAKE
    tay
    lda R0
    cmp D0
    tya
    bcc SDIV16_SKIP
SDIV16_TAKE:
    tay
    lda R0
    sbc D0
    sta R0
    tya
    sbc D1
    inc OUTPUT_QUOT
SDIV16_SKIP:
    dex
    bne SDIV16_LOOP
    sta OUTPUT_REM+1
    lda R0
    sta OUTPUT_REM
    lda INPUT_NUM+1
    eor INPUT_DIV+1
    bpl SDIV16_QUOT_SIGN_DONE
    lda #0
    sec
    sbc OUTPUT_QUOT
    sta OUTPUT_QUOT
    lda #0
    sbc OUTPUT_QUOT+1
    sta OUTPUT_QUOT+1
SDIV16_QUOT_SIGN_DONE:
    lda INPUT_NUM+1
    bpl SDIV16_REM_SIGN_DONE
    lda #0
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    lda #0
    sbc OUTPUT_REM+1
    sta OUTPUT_REM+1
SDIV16_REM_SIGN_DONE:
    clc
    rts
SDIV16_ZERO:
    lda #0
    sta OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    sta OUTPUT_REM
    sta OUTPUT_REM+1
    sec
    rts
