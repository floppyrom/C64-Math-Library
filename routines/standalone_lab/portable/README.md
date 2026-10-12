# Relocatable standalone fast math kernels

These are **configurable symbolic-source copies** of the original three [fixed-map standalone donors] plus a newly recovered zero-ZP modulo specialist(../README.md). Unlike the exact donors, the constants at the top of each `.asm` source can be edited to choose code, I/O-buffer and zero-page addresses. All required executable instructions are included. No resident library, REU, private OptiSearch engine, or tables are needed.

| Source | Public entry label | Code reservations | Scratch |
|---|---|---|---|
| [UDIV16 biased](div_u16_biased.asm) | `FAST_UDIV16_BIASED` | `KERNEL_CODE` through +322 | `TEMP_ZP` through +1 |
| [UMOD16 carry-corrected](mod_u16_biased_carry.asm) | `FAST_UMOD16_PUBLIC` (or `FAST_UMOD16_CARRYFIX`) | `KERNEL_CODE` through +243; `KERNEL_ADAPTER` through +17 | `TEMP_ZP` through +1, additional nested JSR |
| [UDIV32 ZP-tail](div_u32_zptail.asm) | `FAST_UDIV32_PUBLIC` | `KERNEL_CODE` through +324; `KERNEL_AUX` through +218 | `TEMP_ZP` through +3, additional nested JSR |
| [UMOD32 zero-ZP aligned specialist](mod_u32_aligned_carry.asm) | `FAST_UMOD32_ALIGNED_PUBLIC` | `KERNEL_CODE` through +249; `KERNEL_AUX` through +224; `KERNEL_ADAPTER` through +20 | **0 zero-page bytes**, 4 bytes `TEMP_RAM`, nested JSR |

**ABI:** `INPUT_NUM` and `INPUT_DIV` point to little-endian N and D (two or four bytes); `OUTPUT_QUOT` and `OUTPUT_REM` are output buffers of that width. For success, carry is clear. For D=0, carry is set and Q/R are zeroed by division; the modulo routine leaves Q unchanged and zeros R. N and D remain unchanged. `CLD` is required. NMOS 6510 undocumented `LAX` and `ANC` are used where present, so these are not 65C02 implementations.

## Example: call the relocatable UMOD16

The shipped example configuration places the core at `$8000`, the adapter at `$8400`, operands at `$C010/$C014`, outputs at `$C018/$C01C`, and 2 bytes of scratch at `$50`. Include `mod_u16_biased_carry.asm` in an ACME-style assembly project, then (from a non-overlapping caller) execute:

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
    jsr FAST_UMOD16_PUBLIC
    ; C=0, 16-bit OUTPUT_REM = 15; OUTPUT_QUOT remains untouched
```

You may change the address constants at the top of a module, provided the RAM memory ranges do not overlap and the machine's bank configuration exposes RAM there. The tested examples use machine-code-owned RAM; do not overwrite BASIC/KERNAL-owned memory while expecting BASIC to keep running. The standalone sources are **not** relocatable object files and do not automatically provide a BASIC loader.

## Verification evidence

Run from repository root:

```sh
python3 routines/standalone_lab/portable/verify.py
python3 routines/standalone_lab/portable/verify_umod32_common.py
```

It assembles each source at **three separate tested address layouts** (including two unaligned code placements) and executes **12,876 calls** total, checking Q, R, carry, untouched operands, stack balance and unchanged code. The published fixed-map donor SHA/cycle benchmark evidence remains [here](../VALIDATION.json) and is **not** replaced by the relocated measurements. Cycle performance varies with page placement; do not advertise the fixed-map record after moving the routine.

An additional native VICE **correctness** campaign on x64sc passed **768 calls**, 96 identical operands per source at both `aligned_8000` and `unaligned_7123`, including zero divisors and small-divisor stress. Run this outside the ordinary CI only when a working native VICE launcher is available:

```sh
VICE_WRAPPER=/absolute/path/to/run-x64sc.sh python3 routines/standalone_lab/portable/native_vice.py
```

The test uses VICE's remote monitor and loads a RAM-backed harness. Native VICE was used for **result/flag** validation; the benchmark cycle numbers remain from the 6502 emulator, not from native VICE timing. The official V1–V5 resident images, public ABI and ranking remain unchanged. Repose / OptiSearch is credited for the donor architectures; the configurable addresses, validation and carry adapter are C64ML work.

## Source cleanup

The original fixed-layout `../div_u32_zptail.asm` had two definitions of `FAST_UDIV32_ZPTAIL_T1`; only the *second*, internal tail label has been renamed `FAST_UDIV32_INTERNAL_TAIL`. The 544 executable bytes, fixed-map entry at `$0600`, and all published measurements are unchanged. This avoids an ambiguous or rejected duplicate symbol in stricter assemblers.

## UMOD32 zero-ZP specialist: important workload distinction

The `mod_u32_aligned_carry.asm` source is the 475-byte aligned OptiSearch remainder engine with a 21-byte carry-correction public adapter. It has **zero zero-page allocation**, but it does require **four bytes of ordinary scratch RAM** (`TEMP_RAM`, default `$C020-$C023`), 8 bytes of input RAM, four remainder output bytes and a two-byte nested JSR frame. `OUTPUT_QUOT` is unchanged. The default symbolic entry is `FAST_UMOD32_ALIGNED_PUBLIC` at `$8400`. The public adapter verifies divisor zero and sets carry accordingly; the donor on its own does not satisfy the full library flag convention.

The official **1,705-pair identical-input** V2-V4 `MATH_UMOD32_32` baseline is **279.620 cycles overall** and **199.833 cycles on its 1,024 random subset**. The new specialist at the default `$8000/$9000/$8400` placement measures **476.938 overall (much worse)** but **190.867 on the random subset (~4.5% faster)**, with correct carry/remainder/inputs. At the tested unaligned placement it measures **477.116 overall** and **191.118 random**. It must be selected *only* when its workload/resource tradeoff fits.

`verify_umod32_common.py` checks the original donor's **two segment SHA-256s and 21-byte carry adapter**, validates the identical-source public benchmark case SHA-256, and runs **3,410 paired-layout 6502 calls**. The new kernel also passed **192 native VICE correctness calls** at the first two portable layouts; native cycle timings are not claimed. None of these new figures change the released V1-V5 benchmark winners.
