; Issue #144 V4 REU ISQRT32 all-input rotate6 peephole
; Same 6 executable bytes in each of the two existing code sites.
; Source: original V4 signed image and independent CPU/VICE qualification.
; MUST disable IRQ/NMI math callers while enabling/disabling non-atomically.
; Assumes original $C90B..$C910 and $C924..$C929 contain six ASL A each.
; Profile V4 only, original 16-MiB REU image and MATH_INIT required.
!cpu 6510
* = $0D00

ISQRT32_V4_REU_ROT6_BEGIN:
    lda #$4A
    sta $C90B
    sta $C924
    lda #$6A
    sta $C90C
    sta $C925
    lda #$6A
    sta $C90D
    sta $C926
    lda #$90
    sta $C90E
    sta $C927
    lda #$01
    sta $C90F
    sta $C928
    lda #$EA
    sta $C910
    sta $C929
    rts

ISQRT32_V4_REU_ROT6_END:
    lda #$0A
    sta $C90B
    sta $C90C
    sta $C90D
    sta $C90E
    sta $C90F
    sta $C910
    sta $C924
    sta $C925
    sta $C926
    sta $C927
    sta $C928
    sta $C929
    rts

