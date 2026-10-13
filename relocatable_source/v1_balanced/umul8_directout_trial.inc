; Research-only source overlay. NOT included in normal source generation.
; Candidate direct low-byte write (V1 source; V5 inherits when staged).
* = MATH_UMUL8+$0014
U8V1_DIRECT_PUBLIC_TAIL:
    clc
    rts

* = REG_KERNEL+$0714
U8V1_DIRECT_PRODUCT_LOW:
    sta MATH_Z
    lda (ZP_MAIN+$10),y
    sbc REG_TABLE+$2200,x
    rts
