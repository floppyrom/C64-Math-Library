; Signed 24/24 quotient-zero fast-path research alternative, 0 ZP/7 RAM.
; Q24 truncates toward zero; R24 follows N sign; divisor zero Q/R=0,C=1.
; Overflow -8388608 / -1 wraps Q24. N/D & high Q/R bytes preserved.
; Legal NMOS 6502, no tables/REU/writable code; CLD required.
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
D0 = TEMP_RAM+4
D1 = TEMP_RAM+5
D2 = TEMP_RAM+6
* = KERNEL_CODE
FAST_SDIV24_QZERO:
FAST_SMOD24_QZERO:
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
    bpl SIGN24_N_ABS_DONE
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
SIGN24_N_ABS_DONE:
    lda INPUT_DIV
    sta D0
    lda INPUT_DIV+1
    sta D1
    lda INPUT_DIV+2
    sta D2
    bpl SIGN24_D_ABS_DONE
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
SIGN24_D_ABS_DONE:
    ; Short-circuit the quotient-zero domain before the 24-round loop.
    ; Both Q and D hold unsigned magnitudes here; no sign assumption.
    lda OUTPUT_QUOT+2
    cmp D2
    bcc SIGN24_QZERO_BRANCH
    bne SIGN24_QGE
    lda OUTPUT_QUOT+1
    cmp D1
    bcc SIGN24_QZERO_BRANCH
    bne SIGN24_QGE
    lda OUTPUT_QUOT
    cmp D0
    bcs SIGN24_QGE
SIGN24_QZERO_BRANCH:
    jmp SIGN24_QZERO_FAST
SIGN24_QGE:
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
    cmp D2
    bcc SKIP
    bne TAKE
    lda R1
    cmp D1
    bcc SKIP
    bne TAKE
    lda R0
    cmp D0
    bcc SKIP
TAKE:
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
    lda INPUT_NUM+2
    eor INPUT_DIV+2
    bpl SIGN24_Q_DONE
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
SIGN24_Q_DONE:
    lda INPUT_NUM+2
    bpl SIGN24_R_DONE
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
SIGN24_R_DONE:
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

; Q=0 and R=N for |N|<|D|. Preserve high public Q/R sentinel bytes.
SIGN24_QZERO_FAST:
    lda #0
    sta OUTPUT_QUOT
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    lda INPUT_NUM
    sta OUTPUT_REM
    lda INPUT_NUM+1
    sta OUTPUT_REM+1
    lda INPUT_NUM+2
    sta OUTPUT_REM+2
    clc
    rts
