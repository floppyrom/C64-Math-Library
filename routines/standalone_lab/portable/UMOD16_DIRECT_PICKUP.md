# UMOD16 direct-chain with zero ZP (memory-saving standalone)

This OptiSearch/Repose-generated 16/16 modulo candidate is preserved as an **isolated resource-budget alternative**, not as a general-purpose fastest result. The donor is adapted by C64ML to correct carry on successful division and prevent writes to the quotient buffer. It requires no OptiSearch engine or C64ML resident to assemble or call.

**Memory:** 945 bytes of donor code, 16 lookup bytes and 15-byte public carry adapter (**976 bytes total**); **0 zero-page bytes**; 2 bytes ordinary RAM scratch; 2 additional hardware stack bytes. Uses NMOS 6510 opcodes and requires CLD. N and D are preserved; Q untouched; R=N%D and C=0 on success; D=0 sets C=1 and clears R.

**Standalone source:** [mod_u16_direct_zerozp.asm](mod_u16_direct_zerozp.asm). Edit its KERNEL_CODE, KERNEL_TABLE, KERNEL_ADAPTER, INPUT_NUM, INPUT_DIV, OUTPUT_QUOT, OUTPUT_REM and TEMP_RAM address definitions for your memory map. Default code at $8000-$83B0, table $8400-$840F, adapter $8800-$880E, N=$C010, D=$C014, Q=$C018, R=$C01C, TEMP_RAM=$C020-$C021. Reserve all these bytes and avoid overlapping your machine-code program.

```asm
    cld
    lda #200
    sta INPUT_NUM
    lda #0
    sta INPUT_NUM+1
    lda #37
    sta INPUT_DIV
    lda #0
    sta INPUT_DIV+1
    jsr FAST_UMOD16_DIRECT_PUBLIC
    ; C clear; OUTPUT_REM = 15; OUTPUT_QUOT unchanged
```

**Same-input performance (1,705 cases):** 209.868035 cycles at aligned $8000/$8400/$8800; 209.920821 at $7123/$752F/$7955; 209.867449 at $830F/$8755/$8B15. Published full-corpus UMOD16 residents: V1 189.128 cycles, V2–V5 198.601. This routine is *slower*, offered for its zero-ZP contract only. CPU instruction cycles measured from routine entry through RTS, not native-VICE cycle timings; placement changes branch penalties.

**Reproduction:** `python3 routines/standalone_lab/portable/verify_umod16_direct_zerozp.py` assembles and checks 5,115 independent same-input runs over three placements, including Q/R/C/N/D/stack and source-code immutability. An earlier native x64sc campaign passed 192 correctness calls across two layouts (96 each). Run again with `VICE_WRAPPER=/absolute/path/to/x64sc-launcher python3 routines/standalone_lab/portable/native_umod16_direct.py` on systems with VICE. No native cycle measurements are claimed.

Credit Repose / OptiSearch for the donor direct-chain architecture; C64ML for the carry adapter, scratch-buffer rewrite, relocation and tests.
