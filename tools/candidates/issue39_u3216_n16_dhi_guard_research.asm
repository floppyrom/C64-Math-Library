; ISSUE39 research-only $E100 flat-memory overlay.
; 33-byte 32/16 N16 + high divisor filter.
; The immediate divisor high-byte lower bound in DHI_MIN may be
; 1,4,16,64; default C64 memory maps KERNAL ROM over $E100.
; Requires legal writable-executable relocation and full native
; verification before deployment. Hook $31B0 LDA $C010 -> JMP $E100.
DHI_MIN = $01
* = $E100
N16_DHI_GATE:
    lda $C012
    ora $C013
    bne ORIGINAL
    lda $C015
    cmp #DHI_MIN
    bcc ORIGINAL
    jsr $3140
    lda #0
    sta $C01A
    sta $C01B
    rts
ORIGINAL:
    lda $C010
    jmp $31B3
