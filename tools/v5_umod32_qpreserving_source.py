"""V5 32-bit source-relative quotient-preserving remainder frontend.

MATH_UMOD32_32 retains both Q32 and R32 side effects; the high-quotient
dispatcher receives the original compare A/C, restored around the late D0
test. Normal ZP and resident file size are unchanged.
"""

def source(entry:int,io:int,high_qone:int,divzero:int)->str:
    n,d,q,r=io+0x10,io+0x14,io+0x18,io+0x1c
    return f"""* = ${entry:04X}
V5_RM32R_ENTRY:
    lda ${n+3:04X}
    cmp ${d+3:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    lda ${n+2:04X}
    cmp ${d+2:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    lda ${n+1:04X}
    cmp ${d+1:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    lda ${n:04X}
    cmp ${d:04X}
    bcc V5_RM32R_QZERO
    bne V5_RM32R_GREATER
    ; N=D: only 0/0 needs the original divide-zero handler.
    lda ${d:04X}
    ora ${d+1:04X}
    ora ${d+2:04X}
    ora ${d+3:04X}
    beq V5_RM32R_DIVZERO
    ldx #0
    lda #1
    sta ${q:04X}
    stx ${q+1:04X}
    stx ${q+2:04X}
    stx ${q+3:04X}
    stx ${r:04X}
    stx ${r+1:04X}
    stx ${r+2:04X}
    stx ${r+3:04X}
    clc
    rts
V5_RM32R_QZERO:
    ldx #0
    stx ${q:04X}
    stx ${q+1:04X}
    stx ${q+2:04X}
    stx ${q+3:04X}
    lda ${n:04X}
    sta ${r:04X}
    lda ${n+1:04X}
    sta ${r+1:04X}
    lda ${n+2:04X}
    sta ${r+2:04X}
    lda ${n+3:04X}
    sta ${r+3:04X}
    clc
    rts
V5_RM32R_GREATER:
    ; The original V5 high-qone helper at $6810 stores incoming A
    ; immediately, so preserve the compare-stage A across the D==0 guard.
    pha
    lda ${d:04X}
    ora ${d+1:04X}
    ora ${d+2:04X}
    ora ${d+3:04X}
    beq V5_RM32R_ZEROPOP
    pla
    jmp ${high_qone:04X}
V5_RM32R_ZEROPOP:
    pla
V5_RM32R_DIVZERO:
    jmp ${divzero:04X}
"""
