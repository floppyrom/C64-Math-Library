; Original V1 unsigned UMUL8 quarter-square producer: 22-byte entry and
; 29-byte helper concatenated (original $3000 + $4700).
; Only absolute code/data/ZP references are relocated. Requires CLD; X,Y input
; bytes retained, 16-bit product at OUTPUT_Z, success carry clear.
; Q_LO and Q_HI are the original 511-byte quarter-square pages, each starting
; on a 256-byte boundary, with a one-byte unused gap after each page.
; Four exclusive zero-page bytes (two 16-bit pointers), no writable code, REU
; or initialization. The pointers are overwritten on every call (nonreentrant).
!cpu 6510
KERNEL_CODE = $8000
Q_LO = $8100
Q_HI = $8300
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_ZP = $0050
TEMP_ZP2 = $0052

* = KERNEL_CODE
FAST_UMUL8_V1:
    lda #>Q_LO
    sta TEMP_ZP+1
    lda #>Q_HI
    sta TEMP_ZP2+1
    ldx INPUT_X
    ldy INPUT_Y
    jsr UMUL8_V1_CORE
    sta OUTPUT_Z+1
    clc
    rts

UMUL8_V1_CORE:
    sec
    stx TEMP_ZP
    stx TEMP_ZP2
    tya
    sbc TEMP_ZP
    bcs UMUL8_V1_POS
    sbc #$00
    eor #$FF
UMUL8_V1_POS:
    tax
    lda (TEMP_ZP),y
    sbc Q_LO,x
    sta OUTPUT_Z
    lda (TEMP_ZP2),y
    sbc Q_HI,x
    rts
