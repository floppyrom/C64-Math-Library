# Issue39 normalize logarithmic branch collapse

V1, V2 and V5: eight two-branch lookup decisions replaced with one BEQ each. Code 881 to 865 bytes. CPU-model mean 160.150080 to 159.128794 cycles; same exact signed output bytes on 1,073,960 reference/alternate input calls, 320 real native VICE old/new public calls. Existing certified 723073-cell signed precision envelope, public ABI, 4 ZP scratch and REU unchanged. Native VICE cycle timing not measured. PR/main CI pending.
