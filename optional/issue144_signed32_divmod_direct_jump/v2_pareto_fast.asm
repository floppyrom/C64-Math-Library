; Issue144 signed S32/16 public alias JMP-chain opt-in, v2_pareto_fast
; Only JMP OPERAND BYTES are changed; no normal 6510 register or ZP budget.
; Invalid during live/concurrent divmod calls or when code is not RAM writable.
; Example loader-owned installer RAM $0C80; move if occupied.
; Source qualifies with the exactly matching stock resident binary.
!cpu 6510
* = $0C80
DIRECT_S32_16_ENABLE:
  lda #$00
  sta $3EE1
  lda #$92
  sta $3EE2
  lda #$00
  sta $3FDE
  lda #$92
  sta $3FDF
  rts
DIRECT_S32_16_DISABLE:
  lda #$90
  sta $3EE1
  lda #$25
  sta $3EE2
  lda #$E0
  sta $3FDE
  lda #$3E
  sta $3FDF
  rts
