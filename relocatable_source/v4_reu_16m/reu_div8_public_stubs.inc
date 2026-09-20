; Relocation-safe public stubs for the V3/V4 REU-backed 8-bit divider/modulo.
; The resident REU cores remain in the profile API block at REG_API+$0A00/$0A40.
; Keep the profile-specific REU implementation rather than importing the slower
; stock-CPU UDIV8 path selected for V1/V2/V5.
* = MATH_UDIV8
    jmp REG_API+$0A00

* = MATH_UMOD8
    jmp REG_API+$0A40
