; Relocation-safe public UMOD8 wrapper.
; Keeps the certified V2 dedicated UMOD8 magnitude core, but expresses the
; public I/O, scratch and core call symbolically so alternate maps cannot retain
; reference-map $C000/$52xx operands.
* = MATH_UMOD8
    lda MATH_N
    sta ZP_MAIN+$0E
    lda MATH_D
    sta ZP_MAIN+$0F
    jsr REG_KERNEL+$1212
    sta MATH_R
    rts
