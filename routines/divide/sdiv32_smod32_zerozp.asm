; Shared source-linked signed 32/32 divide and modulo (one machine-code image).
; Truncated signed quotient Q32, numerator-signed remainder R32; full N/D preserved.
; D=0 => Q32=R32=0, C=1; otherwise C=0. -2^31/-1 wraps to $80000000.
; 9 ordinary call-exclusive RAM scratch bytes, zero ZP. CLD required.
; Legal NMOS 6502, no tables, REU, undocumented opcodes, SMC or initialization.
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
R3 = TEMP_RAM+3
R4 = TEMP_RAM+4
D0 = TEMP_RAM+5
D1 = TEMP_RAM+6
D2 = TEMP_RAM+7
D3 = TEMP_RAM+8
* = KERNEL_CODE
FAST_SDIV32_32_ZEROZP:
FAST_SMOD32_32_ZEROZP:
    lda INPUT_DIV
    ora INPUT_DIV+1
    ora INPUT_DIV+2
    ora INPUT_DIV+3
    bne SDIV32_NONZERO
    jmp SDIV32_ZERO
SDIV32_NONZERO:
    lda INPUT_NUM
    sta OUTPUT_QUOT
    lda INPUT_NUM+1
    sta OUTPUT_QUOT+1
    lda INPUT_NUM+2
    sta OUTPUT_QUOT+2
    lda INPUT_NUM+3
    sta OUTPUT_QUOT+3
    bpl SDIV32_N_ABS_DONE
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
SDIV32_N_ABS_DONE:
    lda INPUT_DIV
    sta D0
    lda INPUT_DIV+1
    sta D1
    lda INPUT_DIV+2
    sta D2
    lda INPUT_DIV+3
    sta D3
    bpl SDIV32_D_ABS_DONE
    lda #0
    sec
    sbc D0
    sta D0
    lda #0
    sbc D1
    sta D1
    lda #0
    sbc D2
    sta D2
    lda #0
    sbc D3
    sta D3
SDIV32_D_ABS_DONE:
    lda #0
    sta R0
    sta R1
    sta R2
    sta R3
    sta R4
    ldx #32
SDIV32_LOOP:
    clc
    rol OUTPUT_QUOT
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol R1
    rol R2
    rol R3
    rol R4
    lda R4
    bne SDIV32_TAKE
    lda R3
    cmp D3
    bcc SDIV32_SKIP
    bne SDIV32_TAKE
    lda R2
    cmp D2
    bcc SDIV32_SKIP
    bne SDIV32_TAKE
    lda R1
    cmp D1
    bcc SDIV32_SKIP
    bne SDIV32_TAKE
    lda R0
    cmp D0
    bcc SDIV32_SKIP
SDIV32_TAKE:
    sec
    lda R0
    sbc D0
    sta R0
    lda R1
    sbc D1
    sta R1
    lda R2
    sbc D2
    sta R2
    lda R3
    sbc D3
    sta R3
    lda R4
    sbc #0
    sta R4
    inc OUTPUT_QUOT
SDIV32_SKIP:
    dex
    beq SDIV32_DONE
    jmp SDIV32_LOOP
SDIV32_DONE:
    lda R0
    sta OUTPUT_REM
    lda R1
    sta OUTPUT_REM+1
    lda R2
    sta OUTPUT_REM+2
    lda R3
    sta OUTPUT_REM+3
    lda INPUT_NUM+3
    eor INPUT_DIV+3
    bpl SDIV32_Q_SIGN_DONE
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
SDIV32_Q_SIGN_DONE:
    lda INPUT_NUM+3
    bpl SDIV32_R_SIGN_DONE
    lda #0
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    lda #0
    sbc OUTPUT_REM+1
    sta OUTPUT_REM+1
    lda #0
    sbc OUTPUT_REM+2
    sta OUTPUT_REM+2
    lda #0
    sbc OUTPUT_REM+3
    sta OUTPUT_REM+3
SDIV32_R_SIGN_DONE:
    clc
    rts
SDIV32_ZERO:
    lda #0
    sta OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_QUOT+3
    sta OUTPUT_REM
    sta OUTPUT_REM+1
    sta OUTPUT_REM+2
    sta OUTPUT_REM+3
    sec
    rts
