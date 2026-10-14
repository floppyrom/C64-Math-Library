; Issue #39 DIST8 shared magnitude-ordering swap, source-backed overlay.
; Original BCC skip still targets the following original RTS.
; TAX/LDA/STA/STX costs fewer cycles than PHA/PLA and preserves all
; public outputs, carry and hardware stack; A/X/Y are volatile.
; Absolute C040 scratch resource class, no new storage.
* = REG_GAME+$09ED
    tax
    lda V1_SCRATCH+$0A
    sta V1_SCRATCH+$0B
    stx V1_SCRATCH+$0A
    rts
    nop
    nop
    nop
