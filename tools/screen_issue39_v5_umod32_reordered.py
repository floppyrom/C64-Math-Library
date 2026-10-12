#!/usr/bin/env python3
"""Issue39 V5 32/32: direct gate reordered to omit D==0 test on qzero.

This changes only an *ephemeral* V5 in-memory 32-bit UMOD public frontend.
Full Q32/R32/C and nonvolatile N/D are validated against the current
shipped image. N>D fallback retains A/C by PHA/PLA: V5's $6810 high-qone
helper consumes A from the first mismatching numerator byte, so forgetting
that detail would silently corrupt its arithmetic.
"""
import screen_issue39_v5_umod32_qpreserving as a
a.SRC=f"""* = ${a.DST:04X}
V5_RM32R_ENTRY:
    lda ${a.N+3:04X}
    cmp ${a.D+3:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    lda ${a.N+2:04X}
    cmp ${a.D+2:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    lda ${a.N+1:04X}
    cmp ${a.D+1:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    lda ${a.N:04X}
    cmp ${a.D:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    ; N=D: only 0/0 needs the original divide-zero handler.
    lda ${a.D:04X}
    ora ${a.D+1:04X}
    ora ${a.D+2:04X}
    ora ${a.D+3:04X}
    beq V5_RM32R_DIVZERO
    ldx #0
    lda #1
    sta ${a.Q:04X}
    stx ${a.Q+1:04X}
    stx ${a.Q+2:04X}
    stx ${a.Q+3:04X}
    stx ${a.R:04X}
    stx ${a.R+1:04X}
    stx ${a.R+2:04X}
    stx ${a.R+3:04X}
    clc
    rts
V5_RM32R_QZERO:
    ldx #0
    stx ${a.Q:04X}
    stx ${a.Q+1:04X}
    stx ${a.Q+2:04X}
    stx ${a.Q+3:04X}
    lda ${a.N:04X}
    sta ${a.R:04X}
    lda ${a.N+1:04X}
    sta ${a.R+1:04X}
    lda ${a.N+2:04X}
    sta ${a.R+2:04X}
    lda ${a.N+3:04X}
    sta ${a.R+3:04X}
    clc
    rts
V5_RM32R_GREATER:
    ; The original V5 high-qone helper at $6810 stores incoming A
    ; immediately, so preserve the compare-stage A across the D==0 guard.
    pha
    lda ${a.D:04X}
    ora ${a.D+1:04X}
    ora ${a.D+2:04X}
    ora ${a.D+3:04X}
    beq V5_RM32R_ZEROPOP
    pla
    jmp $6810
V5_RM32R_ZEROPOP:
    pla
V5_RM32R_DIVZERO:
    jmp $C222
"""
a.OUT=a.ROOT/'validation/review/ISSUE39_V5_UMOD3232_REORDERED_SHARED_GATE_SCREEN.json'
if __name__=='__main__':a.main()
