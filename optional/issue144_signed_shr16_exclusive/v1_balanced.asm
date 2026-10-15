; C64ML Issue144 signed SHR16 direct-slice EXCLUSIVE overlay: v1_balanced
; Exact stock resident required; 49 shared producer bytes modified.
; BEGIN/END must not be interrupted by code calling signed math.
; NO ordinary SMUL32, READY or overlapping IRQ/NMI math while enabled.
; Requires MATH_INIT; no additional normal zero page or data tables.
; User must verify example $0900 installer RAM actually available.
; Overlay conflicts with any other optional $0900 batch installer.
; Normal SHR16 public address $5E15 unchanged, all signed inputs valid.
!cpu 6510
* = $0900

SMUL32_SHR16_EXCLUSIVE_BEGIN:
    lda #$08
    sta $65B0
    sta $677F
    sta $697F
    sta $6BFB
    lda #$09
    sta $65C5
    sta $6794
    sta $6994
    sta $6C10
    lda #$0A
    sta $65D9
    sta $67C3
    sta $69A8
    sta $6C3F
    lda #$0B
    sta $65E6
    sta $67CA
    sta $69B5
    sta $6C45
    lda #$0C
    sta $65ED
    sta $67D2
    sta $69BC
    sta $6C4C
    lda #$0D
    sta $65F4
    sta $67DA
    sta $69C3
    sta $6C53
    lda #$4C
    sta $C575
    lda #$EA
    sta $659F
    sta $65A0
    sta $65A1
    sta $65F8
    sta $65F9
    sta $65FA
    sta $676E
    sta $676F
    sta $6770
    sta $67DE
    sta $67DF
    sta $67E0
    sta $696E
    sta $696F
    sta $6970
    sta $69C7
    sta $69C8
    sta $69C9
    sta $6BEA
    sta $6BEB
    sta $6BEC
    sta $6C57
    sta $6C58
    sta $6C59
    rts

SMUL32_SHR16_EXCLUSIVE_END:
    lda #$08
    sta $65F9
    sta $67DF
    sta $69C8
    sta $6C58
    lda #$09
    sta $65A0
    sta $676F
    sta $696F
    sta $6BEB
    lda #$0A
    sta $65B0
    sta $677F
    sta $697F
    sta $6BFB
    lda #$0B
    sta $65C5
    sta $6794
    sta $6994
    sta $6C10
    lda #$0C
    sta $65D9
    sta $67C3
    sta $69A8
    sta $6C3F
    lda #$0D
    sta $65E6
    sta $67CA
    sta $69B5
    sta $6C45
    lda #$0E
    sta $65ED
    sta $67D2
    sta $69BC
    sta $6C4C
    lda #$0F
    sta $65F4
    sta $67DA
    sta $69C3
    sta $6C53
    lda #$20
    sta $C575
    lda #$8D
    sta $659F
    sta $65F8
    sta $676E
    sta $67DE
    sta $696E
    sta $69C7
    sta $6BEA
    sta $6C57
    lda #$C0
    sta $65A1
    sta $65FA
    sta $6770
    sta $67E0
    sta $6970
    sta $69C9
    sta $6BEC
    sta $6C59
    rts
