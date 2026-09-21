# `MATH_VEC2_NORMALIZE_Q8_8`

`MATH_VEC2_NORMALIZE_Q8_8` is the 46th stable C64 Math Library entry. It normalizes an arbitrary signed two-dimensional Q8.8 vector and returns a signed Q1.15 unit direction.

## Public contract

```text
input:
    MATH_X+0..1 = signed Q8.8 x
    MATH_Y+0..1 = signed Q8.8 y

output:
    MATH_Z+0..1 = signed Q1.15 normalized x
    MATH_Z+2..3 = signed Q1.15 normalized y

status:
    C=0  non-zero vector normalized successfully
    C=1  input vector is (0,0); all four output bytes are zero

preservation:
    MATH_X+0..1 and MATH_Y+0..1 are preserved
    A/X/Y are volatile
    decimal mode must be clear, as for the rest of the library
```

The reference-map entry is `$5E39`. Relocatable callers should use `MATH_VEC2_NORMALIZE_Q8_8` from the generated/profile `math_api.inc` rather than hardcoding the address.

Q1.15 output uses signed 16-bit two's-complement values. The positive unit endpoint is represented by `$7FFF` (32767).

## Example

```asm
        ; x = +3.0, y = +4.0 in Q8.8
        lda #$00
        sta MATH_X+0
        lda #$03
        sta MATH_X+1
        lda #$00
        sta MATH_Y+0
        lda #$04
        sta MATH_Y+1

        jsr MATH_VEC2_NORMALIZE_Q8_8
        bcs .zero_vector

        ; MATH_Z+0..1 ~= +0.6 in Q1.15
        ; MATH_Z+2..3 ~= +0.8 in Q1.15
        rts

.zero_vector:
        ; Z[0..3] are all zero
        rts
```

## Precision contract

The public error limits remain profile-independent: **<=0.3621 degrees** angular error and **<=202 Q1.15 LSB** component error, measured against a unit vector scaled by 32767.

The full signed-16-bit input domain is covered by interval bounds over **723,073 reduction cells**:

| Backend | Profiles | Certified angular bound | Certified component bound | Sampled angle / component maximum |
|---|---|---:|---:|---:|
| Logarithmic ratio | V1, V2, V5 | 0.356152275 degrees | 200 LSB | 0.347974118 degrees / 199 LSB |
| Existing REU ratio index | V3, V4 | 0.360856382 degrees | 200 LSB | 0.351573687 degrees / 196 LSB |

Stock outputs change from the previous implementation while retaining the contract. V1/V2/V5 now produce identical outputs. V3/V4 retain the previous component tables and ratio mapping; all 107,396 benchmark outputs are byte-identical to the baseline.

## Profile implementations

The sign quadrant is selected once at entry. Each path performs magnitude reduction and writes signed components directly. Stock profiles replace the reciprocal multiply with a logarithmic ratio lookup; REU profiles retain their direct ratio-index lookup.

| Profile | Previous mean | New mean cycles | Reduction | Min–max | Code bytes | Table bytes in C64 RAM |
|---|---:|---:|---:|---:|---:|---:|
| V1 Balanced | 198.770271 | **161.332256** | 18.83% | 90–302 | 915 | 2,816 |
| V2 Pareto-Fast | 189.260317 | **161.332256** | 14.76% | 90–302 | 915 | 2,816 |
| V3 REU 512K | 170.058633 | **157.552684** | 7.35% | 90–298 | 867 | 1,024 |
| V4 REU 16M | 170.058633 | **157.552684** | 7.35% | 90–298 | 867 | 1,024 |
| V5 Hybrid Low-ZP | 198.770271 | **161.332256** | 18.83% | 90–302 | 915 | 2,816 |

These are emulator public-call cycles over the unchanged deterministic 107,396-vector corpus, including the entry JMP and RTS, excluding caller JSR/input stores and video/IRQ contention. Reference and alternate maps have identical output and cycle vectors. Code counts include the three-byte public JMP; table counts exclude the existing 32 KiB REU ratio table.

### RAM and integration tradeoff

The faster routines are larger. V1/V5 add 523 code bytes, V2 adds 532, and V3/V4 add 521. Stock tables total 2,816 bytes, replacing 1,152 bytes of normalizer-specific component/reciprocal data (1,664 additional active table bytes). The old stock reciprocal multiply's shared quarter-square tables remain available to other routines.

V1/V2/V5 reference PRGs now load at **$1000**, previously $2000. Their contiguous file payload spans therefore grow by **4,096 bytes**, including gaps. This is separate from occupied code/table size; loaders must honor the PRG header and reserve the expanded range. V3/V4 PRG spans and REU images are unchanged.

Every normalizer uses only **four volatile bytes at `ZP_MAIN+$18..+$1B`**, retaining V1/V5's 31-byte shared ZP contract and adding no persistent stack-page reservation. The public entry remains `REG_GAME_API+$0039` ($5E39 by default). Stock code modifies lookup operands and must execute from writable RAM; calls share scratch and are non-reentrant, as elsewhere in the library. The stock normalizer itself needs no initialization. V3/V4 retain the normal `MATH_INIT` and preloaded-REU requirements.

Reference code islands are $1600–$198F for stock profiles and $1200–$12EC, $1300–$13CA, $1720–$17FC, $1B00–$1BCA for REU profiles. The REU placement avoids the fixed signed-multiply planes at $9C00–$9FFF after relocation. Adjacent native READMEs list all table locations and include symbols.

### Standalone native sources

The optimized kernels are now first-class source files rather than code buried in the
monolithic relocatable source. V1-V4 include these files directly from their canonical
`math_relocatable.asm`; V5 is built from the V1 base and publishes the byte-identical
V1/V5 backend in its own profile directory for independent reuse.

| Profile | Native source |
|---|---|
| V1 | `v1_balanced/resident/vector/native/vec2_normalize_q8_8.asm` |
| V2 | `v2_pareto_fast/resident/vector/native/vec2_normalize_q8_8.asm` |
| V3 | `v3_reu_512k/resident/vector/native/vec2_normalize_q8_8.asm` |
| V4 | `v4_reu_16m/resident/vector/native/vec2_normalize_q8_8.asm` |
| V5 | `v5_hybrid_lowzp/resident/vector/native/vec2_normalize_q8_8.asm` |

Each adjacent `README.md` documents the exact scratch bytes, table pages, REU resources
and minimal include pattern required to lift the routine into another game or demo.
The native-source validator assembles every file independently on both reference and
alternate maps and byte-compares it with the integrated profile build. V1/V5 and V3/V4
are also checked to remain byte-identical source pairs.

Run:

```sh
make normalize
```

The native-source evidence is written to
`validation/normalize/NATIVE_SOURCE_VALIDATION.json`.

### V3/V4 REU layout

For V3/V4 the final ratio index is precomputed for every normalized major/minor byte pair. The table is 128 x 256 = 32 KiB and occupies `$8000-$FFFF` inside the configured `REU_TURBO16_BANK`.

The Turbo16 executable overlay occupies only the low beginning of that bank, so normalization does **not** require another REU bank, including on V3's 512 KiB image. `tools/assemble_sources.py` generates the table for the selected `REU_TURBO16_BANK`; alternate/custom bank maps therefore remain relocatable.

Normal math calls, including normalization, remain forbidden while a Turbo `BEGIN`/`END` lifecycle is active.

## Validation and regeneration

The principal files are:

- `validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json`
- `validation/normalize/LOG_RATIO_FULL_DOMAIN_PRECISION_CERTIFICATE.json`
- `validation/normalize/LOG_RATIO_TABLE_DESIGN.json`
- `validation/normalize/BASELINE_107396.json`
- `validation/normalize/OPTIMIZED_VALIDATION.json`
- `validation/normalize/EXACT_RATIO_FULL_DOMAIN_PRECISION_CERTIFICATE.json`
- `validation/normalize/COMPONENT_TABLE_DESIGN.json`
- `tools/benchmark_normalize_profile_parity.py`
- `tools/certify_normalize_exact_ratio.py`
- `tools/generate_normalize_tables.py`
- `tools/normalize_model.py`
- `tools/validate_normalize_optimized.py`

The common source validator executes the normalizer as part of the 46-entry suite. A complete profile validation now executes **4,589 machine calls** per map.

`V2_FULL_DOMAIN_PRECISION_CERTIFICATE.json` and the older `certification/` artifacts are historical evidence for the superseded reciprocal backends. Active stock builds use the logarithmic-ratio certificate above.
