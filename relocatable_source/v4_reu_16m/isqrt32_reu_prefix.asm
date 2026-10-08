; V4 exact ISQRT32 prefix accelerator.
; A 4 MiB REU table consumes the high 16 radicand bits plus the next four
; bits and returns the exact partial root/residual after two base-4 steps.
; The remaining 12 radicand bits are resolved by six ordinary restoring steps.
; Input N is preserved; output Z0:Z1 is floor(sqrt(N)); C=0.

IS32_RES0   = ZP_MAIN+$52
IS32_RES1   = ZP_MAIN+$53
IS32_RES2   = ZP_MAIN+$54
IS32_ROOT0  = ZP_MAIN+$55
IS32_ROOT1  = ZP_MAIN+$56
IS32_TRIAL0 = ZP_MAIN+$57
IS32_TRIAL1 = ZP_MAIN+$58
IS32_TRIAL2 = ZP_MAIN+$59

* = MATH_ISQRT32
    jmp IS32P_ENTRY

* = REG_GAME+$07FC
IS32P_ENTRY:
    ; Four-byte table record address:
    ; offset = (((N3:N2) << 4) | (N1 >> 4)) << 2
    ;        = high_word*64 + high_nibble(N1)*4.
    ; The configured base is 64-bank aligned, so its upper two address bits
    ; can be ORed with high_word>>10.
    lda MATH_N+3
    lsr
    lsr
    ora #REU_ISQRT32_PREFIX_BASE_BANK
    sta $DF06

    lda MATH_N+3
    and #$03
    asl
    asl
    asl
    asl
    asl
    asl
    sta REU_SCRATCH+3
    lda MATH_N+2
    lsr
    lsr
    ora REU_SCRATCH+3
    sta $DF05

    lda MATH_N+2
    and #$03
    asl
    asl
    asl
    asl
    asl
    asl
    sta REU_SCRATCH+3
    lda MATH_N+1
    and #$F0
    lsr
    lsr
    ora REU_SCRATCH+3
    sta $DF04

    ; One four-byte REU -> C64 transfer.
    lda #<REU_SCRATCH
    sta $DF02
    lda #>REU_SCRATCH
    sta $DF03
    lda #$04
    sta $DF07
    lda #$00
    sta $DF08
    sta $DF0A
    lda #$81
    sta $DF01

    ; Record = partial root (16-bit), residual (16-bit).
    lda REU_SCRATCH+0
    sta IS32_ROOT0
    lda REU_SCRATCH+1
    sta IS32_ROOT1
    lda REU_SCRATCH+2
    sta IS32_RES0
    lda REU_SCRATCH+3
    sta IS32_RES1
    lda #$00
    sta IS32_RES2

    ; The table consumed N1 bits 7..4.  Align bits 3..0 to the top of X
    ; for two steps, then process all eight bits of N0 in four more steps.
    lda MATH_N+1
    and #$0F
    asl
    asl
    asl
    asl
    tax
    ldy #$02
    jsr IS32P_REFINE

    ldx MATH_N+0
    ldy #$04
    jsr IS32P_REFINE

    lda IS32_ROOT0
    sta MATH_Z+0
    lda IS32_ROOT1
    sta MATH_Z+1
    clc
    rts

; Y restoring square-root steps, two radicand bits per step from X.
IS32P_REFINE:
IS32P_LOOP:
    txa
    asl
    rol IS32_RES0
    rol IS32_RES1
    rol IS32_RES2
    asl
    rol IS32_RES0
    rol IS32_RES1
    rol IS32_RES2
    tax

    asl IS32_ROOT0
    rol IS32_ROOT1
    lda IS32_ROOT0
    asl
    ora #$01
    sta IS32_TRIAL0
    lda IS32_ROOT1
    rol
    sta IS32_TRIAL1
    lda #$00
    rol
    sta IS32_TRIAL2

    ; Compare the full 17-bit trial against the 17-bit residual.  The top
    ; trial bit becomes live on the final large-root steps, so it must also
    ; participate in the subtraction (not merely in the comparison).
    lda IS32_RES2
    cmp IS32_TRIAL2
    bcc IS32P_SKIP
    bne IS32P_TAKE
    lda IS32_RES1
    cmp IS32_TRIAL1
    bcc IS32P_SKIP
    bne IS32P_TAKE
    lda IS32_RES0
    cmp IS32_TRIAL0
    bcc IS32P_SKIP

IS32P_TAKE:
    sec
    lda IS32_RES0
    sbc IS32_TRIAL0
    sta IS32_RES0
    lda IS32_RES1
    sbc IS32_TRIAL1
    sta IS32_RES1
    lda IS32_RES2
    sbc IS32_TRIAL2
    sta IS32_RES2
    inc IS32_ROOT0

IS32P_SKIP:
    dey
    bne IS32P_LOOP
    rts
