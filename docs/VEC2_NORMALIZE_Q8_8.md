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

The implementation is approximate but the public error contract is profile-independent:

- full reduced-domain angular error: **<= 0.3621 degrees**;
- full reduced-domain component error: **<= 202 Q1.15 LSB**;
- deterministic 107,396-vector corpus: sampled maximum angular error **0.351573687 degrees** and sampled maximum component error **196 LSB**;
- zero output/status/input-preservation failures in the reference and alternate relocation maps.

The current full-domain proof is tighter than the public contract: **<= 0.360856382 degrees** and **<= 200 LSB** over 723,073 reduced-domain cells. See `validation/normalize/`.

## Profile implementations

All fixed profiles expose the same entry and semantics, but use profile-appropriate internal backends.

| Profile | Mean cycles | Min | Max | Reachable code | Normal ZP policy | Backend |
|---|---:|---:|---:|---:|---|---|
| V1 Balanced | **198.770271** | 129 | 333 | 392 B | keeps V1 31-byte contract | stock-C64 low-ZP/self-modifying ratio backend |
| V2 Pareto-Fast | **189.260317** | 127 | 323 | 383 B | V2 resident ZP | Pareto-fast stock-C64 ratio backend |
| V3 REU 512K | **170.058633** | 133 | 306 | 346 B | no additional normal ZP | direct REU ratio-index lookup |
| V4 REU 16M | **170.058633** | 133 | 306 | 346 B | no additional normal ZP | direct REU ratio-index lookup |
| V5 Hybrid Low-ZP | **198.770271** | 129 | 333 | 392 B | keeps V1 31-byte contract | V1-compatible low-ZP backend |

The cycle figures use the deterministic 107,396-vector normalization corpus and include the public entry path.

### V3/V4 REU layout

For V3/V4 the final ratio index is precomputed for every normalized major/minor byte pair. The table is 128 x 256 = 32 KiB and occupies `$8000-$FFFF` inside the configured `REU_TURBO16_BANK`.

The Turbo16 executable overlay occupies only the low beginning of that bank, so normalization does **not** require another REU bank, including on V3's 512 KiB image. `tools/assemble_sources.py` generates the table for the selected `REU_TURBO16_BANK`; alternate/custom bank maps therefore remain relocatable.

Normal math calls, including normalization, remain forbidden while a Turbo `BEGIN`/`END` lifecycle is active.

## Validation and regeneration

The principal files are:

- `validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json`
- `validation/normalize/V2_FULL_DOMAIN_PRECISION_CERTIFICATE.json`
- `validation/normalize/EXACT_RATIO_FULL_DOMAIN_PRECISION_CERTIFICATE.json`
- `validation/normalize/COMPONENT_TABLE_DESIGN.json`
- `tools/benchmark_normalize_profile_parity.py`
- `tools/certify_normalize_exact_ratio.py`

The common source validator executes the normalizer as part of the 46-entry suite. A complete profile validation now executes **4,589 machine calls** per map.
