; Research-only 26-byte library-dependent 32/16 N16 delegate.
; CPU-model overlay at E100 under default KERNAL ROM; not deployable without
; bank-state design. Patch public $31B0 LDA N to JMP $E100 only in an owned
; live RAM placement; original 32/16 code resumes at $31B3.
; This is not independent standalone arithmetic, and uses a nested JSR.
* = $E100
N16_GATE:
    lda $C012
    ora $C013
    bne OLD
    jsr $3140
    lda #0
    sta $C01A
    sta $C01B
    rts
OLD:
    lda $C010
    jmp $31B3
