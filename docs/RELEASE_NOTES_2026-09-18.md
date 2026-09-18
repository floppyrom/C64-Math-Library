# Release notes — 2026-09-18 — 46-entry vector-normalization update

This update promotes `MATH_VEC2_NORMALIZE_Q8_8` to the common stable API and increases the public surface from **45 to 46 entries** across V1–V5 and generated Custom Pareto builds.

## New stable routine

`MATH_VEC2_NORMALIZE_Q8_8` accepts signed Q8.8 X/Y components and returns a signed Q1.15 normalized direction in `Z[0..3]`.

- reference entry: `$5E39`;
- inputs preserved;
- `C=0` on non-zero input;
- `C=1` on `(0,0)`, with zero output;
- common public precision contract: **<=0.3621 degrees / <=202 Q1.15 LSB**;
- corrected full-domain proof: **<=0.360856382 degrees / <=200 LSB** over 723,073 reduced-domain cells.

## Profile timings

| Profile | Mean | Min | Max | Reachable code |
|---|---:|---:|---:|---:|
| V1 Balanced | **198.770271** | 129 | 333 | 392 B |
| V2 Pareto-Fast | **189.260317** | 127 | 323 | 383 B |
| V3 REU 512K | **170.058633** | 133 | 306 | 346 B |
| V4 REU 16M | **170.058633** | 133 | 306 | 346 B |
| V5 Hybrid Low-ZP | **198.770271** | 129 | 333 | 392 B |

V1 and V5 preserve the 31-byte low-ZP integration contract. V2 uses the faster stock-C64 backend. V3/V4 use a generated 32 KiB direct ratio-index table at `$8000-$FFFF` in the configured `REU_TURBO16_BANK`; no additional REU bank is required.

## Source/build integration

- `PUBLIC_API_COMPLETE.csv` contains the 46th entry.
- Every canonical `math_relocatable.asm` exports `MATH_VEC2_NORMALIZE_Q8_8 = REG_GAME_API+$0039`.
- V1-V4 canonical relocatable sources now include profile-local `resident/vector/native/vec2_normalize_q8_8.asm` files directly; V5 publishes the byte-identical V1/V5 backend in its own native directory for standalone reuse.
- Each native directory includes extraction notes covering scratch bytes, table pages and REU requirements.
- `tools/validate_normalize_native_sources.py` independently assembles each native kernel on both maps and byte-compares it with the integrated build.
- Every shipped profile `resident/math_api.inc` now exports the routine.
- V3/V4 source regeneration keeps the normalization REU selector symbolic as `REU_TURBO16_BANK`.
- `tools/assemble_sources.py` generates the 32 KiB REU ratio-index table for the selected Turbo16 bank.
- V5 and Custom Pareto builds retain the same 46-entry API without a runtime dispatcher.

## Validation

Fresh canonical source builds pass **46/46 entries and 4,589 machine calls per map** for V1–V4 reference and alternate configurations. V5 passes the same 46-entry common validator on reference and alternate maps. The Custom Pareto matrix covers 12 builds and **55,068 common-API calls**.

The dedicated normalization corpus executes 107,396 vectors per profile/map with zero output, Carry/status, input-preservation or relocation cycle-vector mismatches. V3/V4 reference and alternate maps reproduce **170.058633 cycles mean** exactly.

See `VEC2_NORMALIZE_Q8_8.md` and `validation/normalize/` for the routine-level contract and evidence.
