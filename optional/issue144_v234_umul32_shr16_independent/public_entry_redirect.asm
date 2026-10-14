; Issue144: V2/V3/V4 stable public-entry redirect to independent SHR16 core.
; Research/opt-in only. Requires standalone_clone.asm resident at $0D05,
; MATH_INIT executed, published V2/V3/V4 exact SHA-verified program image.
; No original $5805..$5949 multiply-core instruction bytes are patched.
;
; Two address bytes of ordinary public MATH_UMUL32_SHR16 JMP at $5E12
; change from JMP $C4E3 to JMP $0E03.
; Install/restore only when IRQ/NMI cannot enter the changed public entry
; mid-patch. Other ordinary math calls are supported sequentially; the
; cloned core shares ZP scratch, and is not reentrant.
; Relocate $0C80 if application RAM is occupied; do not overlap clone.
!cpu 6510
* = $0C80

MATH_UMUL32_SHR16_FAST_ENABLE:
    lda $5e12
    cmp #$4c
    bne not_supported
    lda $5e13
    cmp #$e3
    bne not_supported
    lda $5e14
    cmp #$c4
    bne not_supported
    lda #$03
    sta $5e13
    lda #$0e
    sta $5e14
    clc
    rts
not_supported:
    sec
    rts

MATH_UMUL32_SHR16_FAST_DISABLE:
    lda $5e12
    cmp #$4c
    bne restore_failed
    lda $5e13
    cmp #$03
    bne restore_failed
    lda $5e14
    cmp #$0e
    bne restore_failed
    lda #$e3
    sta $5e13
    lda #$c4
    sta $5e14
    clc
    rts
restore_failed:
    sec
    rts
