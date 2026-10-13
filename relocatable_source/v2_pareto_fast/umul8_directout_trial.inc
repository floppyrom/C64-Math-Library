; Issue #39 V2 UMUL8 direct-public-output research integration.
; Signed/internal callers must not enter old $5300; source-built ABI tests
; enforce all public operations and mixed UMUL8 -> UMUL16 interactions.
; The native core is shifted TWO bytes back into existing padding, retaining
; its original final byte at REG_KERNEL+$1322 (no resident growth).
; Independently derived from V2's already published quarter-square routine.
; PRIVATE trial; do not merge without full 65,536 pair, relocation and VICE.

* = MATH_UMUL8
UMUL8_DIRECT_PUBLIC_ENTRY:
    ldx MATH_IO+$00
    ldy MATH_IO+$04
    jsr UMUL8_DIRECT_PRIVATE
    sta MATH_IO+$09
    clc
    rts
    !byte $EA, $EA, $EA, $EA, $EA

* = REG_KERNEL+$12FE
UMUL8_DIRECT_PRIVATE:
    sec
    stx ZP_MAIN+$37
    stx ZP_MAIN+$39
    tya
    sbc ZP_MAIN+$37
    tax
    lda (ZP_MAIN+$37),y
    bcc UMUL8_DIRECT_NEG
    sbc REG_TABLE+$0800,x
    sta MATH_IO+$08
    lda (ZP_MAIN+$39),y
    sbc REG_TABLE+$0A00,x
    rts
UMUL8_DIRECT_NEG:
    sbc REG_TABLE+$0C00,x
    sta MATH_IO+$08
    lda (ZP_MAIN+$39),y
    sbc REG_TABLE+$0D00,x
    rts
UMUL8_DIRECT_PRIVATE_END:
