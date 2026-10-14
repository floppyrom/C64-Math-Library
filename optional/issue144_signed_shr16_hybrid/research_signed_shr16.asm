; Issue #144 signed 32x32 SHR16 non-default experimentation: V2/V3/V4.
; Requires separately loaded unsigned clone at $0D05..$0E49 (entry $0E03),
; all ordinary math resident tables and MATH_INIT, plus free $0E50..$0F30.
; This is a research build, NOT reentrant or concurrent IRQ/NMI safe.
; The optional public $5E15 JMP redirects here without changing stock producer.
; Signed correction in bits 32..63: unsigned product - sign(x)*y*2^32
;                                          - sign(y)*x*2^32.
!cpu 6510

* = $0E50
MATH_SMUL32_SHR16_CORRECT_ALL:
    jsr $0E03
    lda $C003
    bpl ALL_X_DONE
    sec
    lda $C00A
    sbc $C004
    sta $C00A
    lda $C00B
    sbc $C005
    sta $C00B
    lda $C00C
    sbc $C006
    sta $C00C
    lda $C00D
    sbc $C007
    sta $C00D
    clc
ALL_X_DONE:
    lda $C007
    bpl ALL_Y_DONE
    sec
    lda $C00A
    sbc $C000
    sta $C00A
    lda $C00B
    sbc $C001
    sta $C00B
    lda $C00C
    sbc $C002
    sta $C00C
    lda $C00D
    sbc $C003
    sta $C00D
    clc
ALL_Y_DONE:
    clc
    rts

; Select the faster unsigned clone for positive-positive and single-negative
; inputs, preserve old signed implementation for both-negative inputs.
* = $0EB0
MATH_SMUL32_SHR16_HYBRID:
    lda $C003
    bmi HYBRID_X_NEG
    lda $C007
    bmi HYBRID_Y_NEG
    jmp $0E03
HYBRID_X_NEG:
    lda $C007
    bmi HYBRID_BOTH_NEG
    jsr $0E03
    sec
    lda $C00A
    sbc $C004
    sta $C00A
    lda $C00B
    sbc $C005
    sta $C00B
    lda $C00C
    sbc $C006
    sta $C00C
    lda $C00D
    sbc $C007
    sta $C00D
    clc
    rts
HYBRID_Y_NEG:
    jsr $0E03
    sec
    lda $C00A
    sbc $C000
    sta $C00A
    lda $C00B
    sbc $C001
    sta $C00B
    lda $C00C
    sbc $C002
    sta $C00C
    lda $C00D
    sbc $C003
    sta $C00D
    clc
    rts
HYBRID_BOTH_NEG:
    jmp $C50C
