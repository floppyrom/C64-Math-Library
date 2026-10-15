; Issue144 B — all-domain UDIV32_16/UMOD32_16 full-Q32/R16 guarded helper
; When N32 high word is zero, use original resident UDIV16;
; zero upper quotient bytes beforehand to preserve FULL Q32 output.
; Any other numerator, including division by zero, uses stock UDIV32_16.
; Inputs N32 $C010..13, D16 $C014..15; outputs Q32 $C018..1B,
; R16 $C01C..1D; carry=1 on D=0 (original divide-by-zero contract).
; A, X, Y and N/Z/V are volatile under published math-library ABI.
; Original public routine and normal resident untouched. No added ZP.
; NOT a general performance improvement: full-width operands pay +14 cycles.
; Example caller-owned $0C80..$0C95 MUST be checked free / relocated.
!cpu 6510
* = $0C80
MATH_UDIV32_16_NARROW_GUARDED:
    lda $C012
    ora $C013
    bne full32
    lda #$00
    sta $C01A
    sta $C01B
    jmp $3140
full32:
    jmp $31B0
