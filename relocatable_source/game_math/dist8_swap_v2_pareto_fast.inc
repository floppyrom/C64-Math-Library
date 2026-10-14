; Issue #39 DIST8 shared magnitude-ordering swap, source-backed overlay.
; Original BCC skip still targets the following original RTS.
; TAX/LDA/STA/STX costs fewer cycles than PHA/PLA and preserves all
; public outputs, carry and hardware stack; A/X/Y are volatile.
; Absolute zero-page scratch resource class, no new storage.
* = REG_GAME+$0906
    tax
    lda ZP_MAIN+$5B
    sta ZP_MAIN+$5C
    stx ZP_MAIN+$5B
    rts
    nop
    nop
