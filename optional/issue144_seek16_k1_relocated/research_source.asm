!cpu 6510
; ---- executable island $18E2 ----
* = $0D00
L18E2:
    lda #$FF                           ; @18E2 A9 FF
    sta $9118,x                        ; @18E4 9D 18 91
    ldy #$00                           ; @18E7 A0 00
    lda $C004                          ; @18E9 AD 04 C0
    sta $9110,x                        ; @18EC 9D 10 91
    sec                                ; @18EF 38
    sbc $90F8,x                        ; @18F0 FD F8 90
    bcs L18FA                          ; @18F3 B0 05
    eor #$FF                           ; @18F5 49 FF
    adc #$01                           ; @18F7 69 01
    dey                                ; @18F9 88
L18FA:
    sta $62                            ; @18FA 85 62
    sty $59                            ; @18FC 84 59
    ldy #$00                           ; @18FE A0 00
    lda $C000                          ; @1900 AD 00 C0
    sta $9100,x                        ; @1903 9D 00 91
    sec                                ; @1906 38
    sbc $90E8,x                        ; @1907 FD E8 90
    sta $60                            ; @190A 85 60
    lda $C001                          ; @190C AD 01 C0
    sta $9108,x                        ; @190F 9D 08 91
    sbc $90F0,x                        ; @1912 FD F0 90
    bcs L192A                          ; @1915 B0 13
    eor #$FF                           ; @1917 49 FF
    sta $61                            ; @1919 85 61
    lda $60                            ; @191B A5 60
    eor #$FF                           ; @191D 49 FF
    adc #$01                           ; @191F 69 01
    sta $60                            ; @1921 85 60
    bcc L1927                          ; @1923 90 02
    inc $61                            ; @1925 E6 61
L1927:
    dey                                ; @1927 88
    lda $61                            ; @1928 A5 61
L192A:
    sta $61                            ; @192A 85 61
    sty $58                            ; @192C 84 58
    bne L1946                          ; @192E D0 16
    lda $60                            ; @1930 A5 60
    cmp $62                            ; @1932 C5 62
    bcs L1946                          ; @1934 B0 10
    ldy $62                            ; @1936 A4 62
    sta $62                            ; @1938 85 62
    sty $60                            ; @193A 84 60
    lda $58                            ; @193C A5 58
    ora #$01                           ; @193E 09 01
    sta $5C                            ; @1940 85 5C
    lda #$80                           ; @1942 A9 80
    bne L194E                          ; @1944 D0 08
L1946:
    lda $59                            ; @1946 A5 59
    ora #$01                           ; @1948 09 01
    sta $5C                            ; @194A 85 5C
    lda #$00                           ; @194C A9 00
L194E:
    sta $5A                            ; @194E 85 5A
    lda $61                            ; @1950 A5 61
    sta $9148,x                        ; @1952 9D 48 91
    lsr a                              ; @1955 4A
    sta $9138,x                        ; @1956 9D 38 91
    lda $60                            ; @1959 A5 60
    sta $9140,x                        ; @195B 9D 40 91
    ror a                              ; @195E 6A
    sta $9130,x                        ; @195F 9D 30 91
    lda $60                            ; @1962 A5 60
    sec                                ; @1964 38
    sbc #$01                           ; @1965 E9 01
    sta $9120,x                        ; @1967 9D 20 91
    lda $61                            ; @196A A5 61
    sbc #$00                           ; @196C E9 00
    sta $9128,x                        ; @196E 9D 28 91
    bcc L19C7                          ; @1971 90 54
    lda $C011                          ; @1973 AD 11 C0
    bmi L19CA                          ; @1976 30 52
    sta $9158,x                        ; @1978 9D 58 91
    lda $C010                          ; @197B AD 10 C0
    sta $9150,x                        ; @197E 9D 50 91
L1981:
    lda #$00                           ; @1981 A9 00
    sta $63                            ; @1983 85 63
    sta $64                            ; @1985 85 64
    sta $5B                            ; @1987 85 5B
    ldy $9158,x
    beq L1994
    cpy #$01
    bne L198E
    lda $61
    bne k1fast
    lda $62
    cmp $60
    bcs L198E
k1fast:
    lda $62
    sta $63
    jmp L1994
L198E:
    jsr $3EE3                          ; @198E 20 E3 3E
    dey                                ; @1991 88
    bne L198E                          ; @1992 D0 FA
L1994:
    lda $63                            ; @1994 A5 63
    sta $9160,x                        ; @1996 9D 60 91
    lda $64                            ; @1999 A5 64
    sta $9170,x                        ; @199B 9D 70 91
    txa                                ; @199E 8A
    tay                                ; @199F A8
    lda $9158,x                        ; @19A0 BD 58 91
    jsr $3F01                          ; @19A3 20 01 3F
    lda $9150,x                        ; @19A6 BD 50 91
    beq L19C5                          ; @19A9 F0 1A
    jsr $3EE3                          ; @19AB 20 E3 3E
    lda $63                            ; @19AE A5 63
    sta $9168,x                        ; @19B0 9D 68 91
    lda $64                            ; @19B3 A5 64
    sta $9178,x                        ; @19B5 9D 78 91
    txa                                ; @19B8 8A
    ora #$08                           ; @19B9 09 08
    tay                                ; @19BB A8
    lda $9158,x                        ; @19BC BD 58 91
    sec                                ; @19BF 38
    adc #$00                           ; @19C0 69 00
    jsr $3F01                          ; @19C2 20 01 3F
L19C5:
    clc                                ; @19C5 18
    rts                                ; @19C6 60
L19C7:
    jmp $5E72                          ; @19C7 4C 72 5E
L19CA:
    lda $61                            ; @19CA A5 61
    sta $5F                            ; @19CC 85 5F
    lda $62                            ; @19CE A5 62
    sta $54                            ; @19D0 85 54
    lda $60                            ; @19D2 A5 60
    ldy $5F                            ; @19D4 A4 5F
    beq L19E1                          ; @19D6 F0 09
L19D8:
    lsr $5F                            ; @19D8 46 5F
    ror a                              ; @19DA 6A
    lsr $54                            ; @19DB 46 54
    ldy $5F                            ; @19DD A4 5F
    bne L19D8                          ; @19DF D0 F7
L19E1:
    sta $53                            ; @19E1 85 53
    jsr $3D23                          ; @19E3 20 23 3D
    sta $9158,x                        ; @19E6 9D 58 91
    tya                                ; @19E9 98
    sta $9150,x                        ; @19EA 9D 50 91
    jmp L1981                          ; @19ED 4C 81 19
