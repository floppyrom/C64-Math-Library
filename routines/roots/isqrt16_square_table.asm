; Relocatable extraction of the shipped V1/V2/V5 16-bit lookup-square root.
; The three tables are regenerated from integer arithmetic; no resident bytes copied.
; Original algorithm: v1_balanced/standalone/isqrt_u16_u16.asm (entry trampoline omitted).
; Input MATH_N low two bytes, output MATH_Z low two bytes, C=0.
; Preconditions: CLD. Input preserved, ZP=0, no RAM scratch or init.
KERNEL_CODE = $8000
INPUT_NUM = $C010
OUTPUT_Z = $C008
SQ_LO = $8100
SQ_HI = $8200
SEED = $8300

* = KERNEL_CODE
FAST_ISQRT16_TABLE:
    ldx INPUT_NUM+1
    ldy SEED,x
ISQRT_COMPARE:
    lda INPUT_NUM+1
    cmp SQ_HI,y
    bcc ISQRT_DECREMENT
    bne ISQRT_FOUND
    lda INPUT_NUM
    cmp SQ_LO,y
    bcc ISQRT_DECREMENT
ISQRT_FOUND:
    sty OUTPUT_Z
    lda #$00
    sta OUTPUT_Z+1
    clc
    rts
ISQRT_DECREMENT:
    dey
    jmp ISQRT_COMPARE
