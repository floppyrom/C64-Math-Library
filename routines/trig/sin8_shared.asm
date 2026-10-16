; Exact public V1-V5 8-bit trig lookup kernel with a shared immutable table.
; Uses shipped PRG SINE8 table bytes; never re-compute via floating point.
; CLD required; input MATH_X[0] retained, C clear on return; no private RAM/ZP.
KERNEL_CODE = $8000
SINE_TAB = $8100
INPUT_X = $C000
OUTPUT_Z = $C008

* = KERNEL_CODE
FAST_SIN8:
    ldx INPUT_X
    lda SINE_TAB,x
    sta OUTPUT_Z
    clc
    rts
