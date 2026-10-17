; Standalone unsigned 32-bit integer square root (floor), 16-bit output.
; Full-domain, zero-ZP, no REU/tables/SMC; CLD expected.
; Preserves input N32, X, Y and SP; output Z16, clears carry.
; Private reusable 10-byte RAM scratch; radix-4 restoring.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
OUTPUT_Z = $C008
TEMP_RAM = $C020
SQ_N0 = TEMP_RAM+0
SQ_N1 = TEMP_RAM+1
SQ_N2 = TEMP_RAM+2
SQ_N3 = TEMP_RAM+3
SQ_R0 = TEMP_RAM+4
SQ_R1 = TEMP_RAM+5
SQ_R2 = TEMP_RAM+6
SQ_T0 = TEMP_RAM+7
SQ_T1 = TEMP_RAM+8
SQ_T2 = TEMP_RAM+9
* = KERNEL_CODE
FAST_ISQRT32_RESTORING:
    txa
    pha
    tya
    pha
    lda INPUT_NUM
    sta SQ_N0
    lda INPUT_NUM+1
    sta SQ_N1
    lda INPUT_NUM+2
    sta SQ_N2
    lda INPUT_NUM+3
    sta SQ_N3
    lda #0
    sta SQ_R0
    sta SQ_R1
    sta SQ_R2
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    ldx #16
SQ_LOOP:
    asl SQ_N0
    rol SQ_N1
    rol SQ_N2
    rol SQ_N3
    rol SQ_R0
    rol SQ_R1
    rol SQ_R2
    asl SQ_N0
    rol SQ_N1
    rol SQ_N2
    rol SQ_N3
    rol SQ_R0
    rol SQ_R1
    rol SQ_R2
    lda OUTPUT_Z
    sta SQ_T0
    lda OUTPUT_Z+1
    sta SQ_T1
    lda #0
    sta SQ_T2
    asl SQ_T0
    rol SQ_T1
    rol SQ_T2
    asl SQ_T0
    rol SQ_T1
    rol SQ_T2
    inc SQ_T0
    asl OUTPUT_Z
    rol OUTPUT_Z+1
    lda SQ_R2
    cmp SQ_T2
    bcc SQ_SKIP
    bne SQ_TAKE
    lda SQ_R1
    cmp SQ_T1
    bcc SQ_SKIP
    bne SQ_TAKE
    lda SQ_R0
    cmp SQ_T0
    bcc SQ_SKIP
SQ_TAKE:
    sec
    lda SQ_R0
    sbc SQ_T0
    sta SQ_R0
    lda SQ_R1
    sbc SQ_T1
    sta SQ_R1
    lda SQ_R2
    sbc SQ_T2
    sta SQ_R2
    inc OUTPUT_Z
SQ_SKIP:
    dex
    beq SQ_DONE
    jmp SQ_LOOP
SQ_DONE:
    pla
    tay
    pla
    tax
    clc
    rts
