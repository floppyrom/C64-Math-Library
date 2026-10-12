#!/usr/bin/env python3
"""Issue39 V5 UMOD32 high-byte-only quotient-zero shortcut, full ABI.

Reuse the side-by-side public-entry comparison and all test cases from the
previous 127-byte strict frontend. Only N3<D3 is intercepted; 0/0, all
near-equal and all quotient-positive cases go to the unchanged original gate.
No shipped byte is changed.
"""
import screen_issue39_v5_umod32_qpreserving as audit
audit.SRC=f"""* = ${audit.DST:04X}
V5_RM32H_ENTRY:
    lda ${audit.N+3:04X}
    cmp ${audit.D+3:04X}
    bcs V5_RM32H_OLD
    ; N3 < D3 proves N<D and divisor nonzero, no 32-bit OR needed.
    ldx #0
    stx ${audit.Q:04X}
    stx ${audit.Q+1:04X}
    stx ${audit.Q+2:04X}
    stx ${audit.Q+3:04X}
    lda ${audit.N:04X}
    sta ${audit.R:04X}
    lda ${audit.N+1:04X}
    sta ${audit.R+1:04X}
    lda ${audit.N+2:04X}
    sta ${audit.R+2:04X}
    lda ${audit.N+3:04X}
    sta ${audit.R+3:04X}
    clc
    rts
V5_RM32H_OLD:
    jmp ${audit.GATE:04X}
"""
audit.OUT=audit.ROOT/'validation/review/ISSUE39_V5_UMOD3232_HIGHBYTE_QZERO_SCREEN.json'
if __name__=='__main__':
 audit.main()
