; Original V1–V5 46-byte signed SMUL8 quarter-square producer.
; Relocatable; requires writable C64 RAM because operand bytes are modified.
; Exactly four STA abs updates to indexed-lookup *operand low bytes*.
; Non-reentrant, no zero-page usage or temporary scratch. CLD required.
; Signed X/Y low bytes preserved; signed 16-bit product in Z low two bytes.
; Carry clear; higher Z bytes untouched. No REU, MATH_INIT or helper needed.
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
SMUL_LOW_SUM = $8100
SMUL_HIGH_SUM = $8300
SMUL_LOW_COMP = $8500
SMUL_HIGH_COMP = $8700

* = KERNEL_CODE
FAST_SMUL8_V1:
    lda INPUT_X
    eor #$80
    sta SMUL_OP_LOW_SUM+1
    sta SMUL_OP_HIGH_SUM+1
    eor #$ff
    sta SMUL_OP_LOW_COMP+1
    sta SMUL_OP_HIGH_COMP+1
    lda INPUT_Y
    eor #$80
    tax
    sec
SMUL_OP_LOW_SUM:
    lda SMUL_LOW_SUM,x
SMUL_OP_LOW_COMP:
    adc SMUL_LOW_COMP,x
    sta OUTPUT_Z
SMUL_OP_HIGH_SUM:
    lda SMUL_HIGH_SUM,x
SMUL_OP_HIGH_COMP:
    adc SMUL_HIGH_COMP,x
    sta OUTPUT_Z+1
    clc
    rts
