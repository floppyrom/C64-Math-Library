; Experimental Turbo16 REU SWAP lifecycle for modular operation-first source.
; This is NOT a public installer backend. BEGIN/CALL/END source proof only.
; All constants bound by the host's placement/safety checker.
; $92 = REU SWAP, exchanges exact 122 C64 ZP bytes with REU bank payload.
; First SWAP saves caller ZP in REU, loads executable overlay into ZP.
; Second SWAP restores both caller ZP and original overlay REU payload.
; No ordinary math/IRQ accesses to overlaid ZP are safe during active mode.

* = REU_CTRL_BASE
T16_SWAP_BEGIN:
        lda T16_STATE
        beq T16_BEGIN_GO
        sec
        rts
T16_BEGIN_GO:
        php
        sei
        jsr T16_DMA_SWAP
        lda #$01
        sta T16_STATE
        plp
        clc
        rts

T16_SWAP_END:
        lda T16_STATE
        bne T16_END_GO
        sec
        rts
T16_END_GO:
        php
        sei
        jsr T16_DMA_SWAP
        lda #$00
        sta T16_STATE
        plp
        clc
        rts

T16_SWAP_CALL:
        lda T16_STATE
        bne T16_CALL_GO
        sec
        rts
T16_CALL_GO:
        jmp T16_PUBLIC_CALL

T16_DMA_SWAP:
        lda #<TURBO16_ZP_BASE
        sta $DF02
        lda #>TURBO16_ZP_BASE
        sta $DF03
        lda #$00
        sta $DF04
        sta $DF05
        lda #REU_TURBO16_BANK
        sta $DF06
        lda #$7A
        sta $DF07
        lda #$00
        sta $DF08
        sta $DF0A
        lda #$92
        sta $DF01
        rts
