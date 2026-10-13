; Canonical zero-growth V1/V5 UMUL8 direct public result.
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
