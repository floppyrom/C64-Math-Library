; Issue #39 opt-in unsigned 32/16 POWER-OF-TWO division AND modulo.
; Preconditions: 1 <= D <= 32768 and exactly one divisor bit set.
; Outputs: full Q32 = floor(N32 / D16), low R16 = N32 % D16, C=0.
; Preserves N32, D16, high remainder bytes, stack and sentinel memory.
; No extra zero-page bytes, no nested JSR. X/A and CPU flags clobbered.
; This helper is NOT an unconditional public-entry replacement and does
; NOT validate the divisor precondition. Caller must own the code RAM.
; Default origin is sample-only and may conflict with BASIC/game state.
!cpu 6510
* = $0800
U3216_POW2_OPTIN:
    lda $C014
    sec
    sbc #1
    and $C010
    sta $C01C
    lda $C015
    sbc #0
    and $C011
    sta $C01D
    lda $C010
    sta $C018
    lda $C011
    sta $C019
    lda $C012
    sta $C01A
    lda $C013
    sta $C01B
    lda $C014
    bne LOW_BYTE
    ; Divisor >=256: quotient gets a full byte shift, not 8 LSR loops.
    lda $C019
    sta $C018
    lda $C01A
    sta $C019
    lda $C01B
    sta $C01A
    lda #0
    sta $C01B
    lda $C015
    ldx #0
    jmp SCAN
LOW_BYTE:
    ldx #0
SCAN:
    cmp #1
    beq DONE_SCAN
    lsr
    inx
    bne SCAN
DONE_SCAN:
    cpx #0
    beq FINISH
SHR_LOOP:
    lsr $C01B
    ror $C01A
    ror $C019
    ror $C018
    dex
    bne SHR_LOOP
FINISH:
    clc
    rts
