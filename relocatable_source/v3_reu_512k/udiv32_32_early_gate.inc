; UDIV32/UMOD32 early q=0/q=1 gate — 2026-09-20
; Applies the Repose early-quotient idea before the legacy public path copies
; all eight operand bytes into private scratch. Inputs are preserved.
;
; d=0 or n>d: fall through to the existing profile-selected divider at REG_GAME.
; n<d: q=0, r=n directly.
; n=d: q=1, r=0 directly.

* = MATH_UDIV32_32
    jmp D3232_EARLY_GATE
* = MATH_UMOD32_32
    jmp D3232_EARLY_GATE

* = REG_KERNEL+$1957
D3232_EARLY_GATE:
    ; Preserve legacy divide-by-zero handling.
    lda MATH_IO+$14
    ora MATH_IO+$15
    ora MATH_IO+$16
    ora MATH_IO+$17
    beq D3232_LEGACY

    ; Unsigned n ? d, most-significant byte first.
    lda MATH_IO+$13
    cmp MATH_IO+$17
    bcc D3232_QZERO
    bne D3232_LEGACY
    lda MATH_IO+$12
    cmp MATH_IO+$16
    bcc D3232_QZERO
    bne D3232_LEGACY
    lda MATH_IO+$11
    cmp MATH_IO+$15
    bcc D3232_QZERO
    bne D3232_LEGACY
    lda MATH_IO+$10
    cmp MATH_IO+$14
    bcc D3232_QZERO
    bne D3232_LEGACY

    ; n == d -> q=1, r=0.
    ldx #$00
    lda #$01
    sta MATH_IO+$18
    stx MATH_IO+$19
    stx MATH_IO+$1A
    stx MATH_IO+$1B
    stx MATH_IO+$1C
    stx MATH_IO+$1D
    stx MATH_IO+$1E
    stx MATH_IO+$1F
    clc
    rts

D3232_QZERO:
    ; n < d -> q=0, r=n.
    ldx #$00
    stx MATH_IO+$18
    stx MATH_IO+$19
    stx MATH_IO+$1A
    stx MATH_IO+$1B
    lda MATH_IO+$10
    sta MATH_IO+$1C
    lda MATH_IO+$11
    sta MATH_IO+$1D
    lda MATH_IO+$12
    sta MATH_IO+$1E
    lda MATH_IO+$13
    sta MATH_IO+$1F
    clc
    rts

D3232_LEGACY:
    jmp REG_GAME
