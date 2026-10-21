; Optional source-built Turbo16 REU preflight and payload loader.
; All C64/REU physical addresses are supplied by the standalone packager.
; REQUIREMENT: selected REU bank exclusive; higher-bank alias probe also owns
; one byte at offset $ffff in the lower alias bank. I/O2 must be REU-only.
; Carry=0 success, Carry=1 failure. Never BEGIN before INSTALL succeeds.
* = T16_LOADER_BASE

T16_REU_INSTALL:
        lda T16_STATE
        beq T16_CHECK_READY
T16_INSTALL_FAIL:
        sec
        rts
T16_CHECK_READY:
        lda T16_READY
        bne T16_INSTALL_FAIL
        lda $01
        and #$04
        beq T16_INSTALL_FAIL
        lda $01
        and #$03
        beq T16_INSTALL_FAIL
        php
        sei
        lda #$00
        sta $DF09
        sta $DF0A
        ; Real DMA round trip, not open-bus or status-register guesswork.
        lda #$6b
        sta T16_PROBE
        ldx #REU_TURBO16_BANK
        lda #$90
        jsr T16_ONE_BYTE
        lda #$24
        sta T16_PROBE
        ldx #REU_TURBO16_BANK
        lda #$91
        jsr T16_ONE_BYTE
        lda T16_PROBE
        cmp #$6b
        bne T16_INSTALL_BAD
        ; 16MiB bank numbering can alias on a physically smaller REU.
        ; Caller reserves the lower mirror location before permitting probe.
        lda #REU_HIGH_BANK
        beq T16_INSTALL_UPLOAD
        lda #$a5
        sta T16_PROBE
        ldx #REU_ALIAS_BANK
        lda #$90
        jsr T16_ONE_BYTE
        lda #$24
        sta T16_PROBE
        ldx #REU_TURBO16_BANK
        lda #$91
        jsr T16_ONE_BYTE
        lda T16_PROBE
        cmp #$6b
        bne T16_INSTALL_BAD
T16_INSTALL_UPLOAD:
        lda #<T16_OVERLAY_STAGE
        sta $DF02
        lda #>T16_OVERLAY_STAGE
        sta $DF03
        lda #$00
        sta $DF04
        sta $DF05
        lda #REU_TURBO16_BANK
        sta $DF06
        lda #$7a
        sta $DF07
        lda #$00
        sta $DF08
        sta $DF09
        sta $DF0A
        lda #$90
        sta $DF01
        lda #$01
        sta T16_READY
        plp
        clc
        rts
T16_INSTALL_BAD:
        plp
        sec
        rts

; Transfer one test byte at REU bank:$ffff to/from owned C64 scratch.
; A=$90 store or $91 fetch, X=bank. Leaves caller IRQ state unchanged.
T16_ONE_BYTE:
        pha
        lda #<T16_PROBE
        sta $DF02
        lda #>T16_PROBE
        sta $DF03
        lda #$ff
        sta $DF04
        sta $DF05
        stx $DF06
        lda #$01
        sta $DF07
        lda #$00
        sta $DF08
        sta $DF09
        sta $DF0A
        pla
        sta $DF01
        rts

; Only these lifecycle gates are public to a caller.
T16_REU_BEGIN:
        lda T16_READY
        beq T16_PUBLIC_REJECT
        jmp T16_SWAP_BEGIN
T16_REU_CALL:
        lda T16_READY
        beq T16_PUBLIC_REJECT
        jmp T16_SWAP_CALL
T16_REU_END:
        lda T16_READY
        beq T16_PUBLIC_REJECT
        jmp T16_SWAP_END
T16_PUBLIC_REJECT:
        sec
        rts
