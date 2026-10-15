; Issue144 A - FOUR signed/unsigned 32x32 full/SHR16 narrow16 domain.
; PRECONDITION both 32-bit operands have zero high 16 bits.
; Both signed 32-bit values are then nonnegative, though their low 16 bits
; may exceed $7FFF; use unsigned UMUL16, never signed SMUL16.
; Result: full=8 bytes, SHR16=6 bytes; C=0, X/Y operands untouched.
; Uses resident MATH_UMUL16, original MATH_INIT and existing ZP/tables;
; code RAM $0E60 is caller-owned opt-in example, not default resident.
!cpu 6510
* = $0E60
MATH_UMUL32_U16DOMAIN:
    jsr $3020
    lda #$00
    sta $C00C
    sta $C00D
    sta $C00E
    sta $C00F
    clc
    rts
MATH_SMUL32_U16DOMAIN:
    jmp MATH_UMUL32_U16DOMAIN
MATH_UMUL32_SHR16_U16DOMAIN:
    jsr $3020
    lda $C00A
    sta $C008
    lda $C00B
    sta $C009
    lda #$00
    sta $C00A
    sta $C00B
    sta $C00C
    sta $C00D
    clc
    rts
MATH_SMUL32_SHR16_U16DOMAIN:
    jmp MATH_UMUL32_SHR16_U16DOMAIN
