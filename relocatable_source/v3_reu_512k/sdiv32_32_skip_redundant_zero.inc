; SDIV32/32 private-magnitude entry optimization — 2026-09-20
; Public signed front-end has already rejected d=0 before magnitude formation.
; Skip the duplicated zero-divisor check at the private native magnitude core.
* = REG_GAME+$00AD
LC1AD:
    jsr REG_LOW+$0852
