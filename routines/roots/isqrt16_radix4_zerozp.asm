; Tableless restoring unsigned ISQRT16: exact floor sqrt in Z16, C=0.
; Requires 6 bytes caller RAM scratch, no ZP, no SMC, CLD on entry.
; Preserves N16, X, Y, stack; independent of original aligned square tables.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
OUTPUT_Z = $C008
TEMP_RAM = $C020
N0 = TEMP_RAM+0
N1 = TEMP_RAM+1
R0 = TEMP_RAM+2
R1 = TEMP_RAM+3
T0 = TEMP_RAM+4
T1 = TEMP_RAM+5
* = KERNEL_CODE
FAST_ISQRT16_RESTORING:
    txa
    pha
    tya
    pha
    lda INPUT_NUM
    sta N0
    lda INPUT_NUM+1
    sta N1
    lda #0
    sta R0
    sta R1
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    ldx #8
ISQRT_LOOP:
    asl N0
    rol N1
    rol R0
    rol R1
    asl N0
    rol N1
    rol R0
    rol R1
    lda OUTPUT_Z
    sta T0
    lda #0
    sta T1
    asl T0
    rol T1
    asl T0
    rol T1
    inc T0
    asl OUTPUT_Z
    lda R1
    cmp T1
    bcc ISQRT_SKIP
    bne ISQRT_TAKE
    lda R0
    cmp T0
    bcc ISQRT_SKIP
ISQRT_TAKE:
    sec
    lda R0
    sbc T0
    sta R0
    lda R1
    sbc T1
    sta R1
    inc OUTPUT_Z
ISQRT_SKIP:
    dex
    beq ISQRT_DONE
    jmp ISQRT_LOOP
ISQRT_DONE:
    pla
    tay
    pla
    tax
    clc
    rts
