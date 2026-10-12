; Issue #39: 12-byte fast 32/16 helper for caller-known 16-bit numerators.
; Depends on C64 Math Library UDIV16 at $3140 and IO $C010..$C01F.
; Caller must reserve writable executable RAM at this origin.
; Preconditions N2=N3=0. Prefer D>=256 for V2-V5 performance.
; The public UDIV32_16/UMOD32_16 entrypoints remain unchanged.
!cpu 6510
MATH_UDIV16 = $3140
MATH_Q = $C018
* = $0800
U3216_N16_OPTIN:
    jsr MATH_UDIV16
    lda #0
    sta MATH_Q+2
    sta MATH_Q+3
    rts
