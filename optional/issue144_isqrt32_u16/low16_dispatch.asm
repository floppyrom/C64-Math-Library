; Issue #144 C - two fixed-reference V1-V5 integer sqrt selectors.
; N32=$C010..13, Z16=$C008..09, C=0, input N preserved.
; Must run original MATH_INIT to initialize the resident lookup tables.
; LOW16_ONLY is valid only if N[3:2]=$0000, no check performed.
; AUTO handles all N32, but adds overhead for full-width inputs and
; is NOT recommended as the default based on the official 4130 corpus.
; Both are separately placed opt-in examples, RAM availability required.
!cpu 6510
* = $0C40
MATH_ISQRT32_LOW16_ONLY:
    jmp $5E2D
MATH_ISQRT32_AUTO:
    lda $C012
    ora $C013
    bne full32
    jmp $5E2D
full32:
    jmp $5E30
