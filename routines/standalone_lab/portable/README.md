# Relocatable standalone fast math kernels

These are **configurable symbolic-source copies** of the original [fixed-map donor collection](../README.md), plus standalone zero-ZP alternatives. Unlike the exact donors, the constants at the top of each `.asm` source can be edited to choose code, I/O-buffer and zero-page addresses. All required executable instructions are included. No resident library, REU, private OptiSearch engine, or tables are needed.

| Source | Public entry label | Code reservations | Scratch |
|---|---|---|---|
| [UDIV16 biased](div_u16_biased.asm) | `FAST_UDIV16_BIASED` | `KERNEL_CODE` through +322 | `TEMP_ZP` through +1 |
| [UMOD16 carry-corrected](mod_u16_biased_carry.asm) | `FAST_UMOD16_PUBLIC` (or `FAST_UMOD16_CARRYFIX`) | `KERNEL_CODE` through +243; `KERNEL_ADAPTER` through +17 | `TEMP_ZP` through +1, additional nested JSR |
| [UDIV32 ZP-tail](div_u32_zptail.asm) | `FAST_UDIV32_PUBLIC` | `KERNEL_CODE` through +324; `KERNEL_AUX` through +218 | `TEMP_ZP` through +3, additional nested JSR |
| [UDIV32 zero-ZP aligned](div_u32_aligned_nozp.asm) | `FAST_UDIV32_PUBLIC` | `KERNEL_CODE` through +324; `KERNEL_AUX` through +250 | **0 ZP bytes**; four bytes `TEMP_RAM` (ordinary RAM); nested JSR |
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
python3 routines/standalone_lab/portable/verify_aligned_udiv32_common.py
```

It assembles each source at **three separate tested address layouts** (including two unaligned code placements) and executes **16,095 calls** total, checking Q, R, carry, untouched operands, stack balance and unchanged code. The published fixed-map donor SHA/cycle benchmark evidence remains [here](../VALIDATION.json) and is **not** replaced by the relocated measurements. Cycle performance varies with page placement; do not advertise the fixed-map record after moving the routine.

An additional native VICE **correctness** campaign on x64sc passed **960 calls**, 96 identical operands per source at both `aligned_8000` and `unaligned_7123`, including zero divisors and small-divisor stress. Run this outside the ordinary CI only when a working native VICE launcher is available:

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

## UDIV32 zero-ZP aligned: memory saving, not a speed winner

The [aligned division source](div_u32_aligned_nozp.asm) reconstructs Repose's complete 325-byte live-high-quotient entry and 251-byte aligned tail: **576 total executable bytes, zero zero-page bytes**, and four ordinary scratch RAM bytes (`TEMP_RAM`; default `$C020-$C023`). It returns quotient **and** remainder and preserves N/D, the documented carry flag, and stack balance. Inputs, outputs and both code origins are configurable. The nested tail JSR consumes a return address on the hardware stack; it needs neither REU nor tables.

On the exact 2,729-pair current-library UDIV32_32 corpus:

| Program placement | Full mean cycles | 2,048 random-operand mean |
|---|---:|---:|
| Aligned `$8000/$9000` | 408.012 | 196.890 |
| Unaligned `$7123/$9507` | 408.224 | 197.150 |
| Unaligned `$830F/$9900` | 408.012 | 196.890 |
| Published C64ML V2–V4 resident | **242.549** | **193.660** |
| Published standalone 4-ZP ZP-tail donor | 380.698 | **188.398** |

This is **not the fastest standalone UDIV32**; it trades cycles for zero-page savings. On small divisors/high quotients its cost can be thousands of cycles (full-corpus maximum **5,677**). `verify_aligned_udiv32_common.py` independently reassembles both original donor segments, checks their SHA-256 values and the frozen public corpus hash, and verifies **8,187 paired-layout arithmetic calls**. Native x64sc correctness was also checked over **192 calls** at the first two address layouts; native cycle timing has not been measured. The existing integrated V1–V5 routines and their performance records are unchanged.

## UMOD16 direct-chain: zero-ZP memory-saving alternative

[Pick up the configurable UMOD16 direct-chain source](UMOD16_DIRECT_PICKUP.md) or [open the ACME assembly](mod_u16_direct_zerozp.asm). This completes recovery of the remaining unique 16-bit modulo implementation in Repose's October 11 comparison bundle. C64ML adapted the generated direct-chain donor to normalize carry, route internal quotient writes to two regular scratch-RAM bytes and preserve the caller's quotient buffer. **0 ZP, 976 bytes code+data, 2 ordinary scratch RAM, nested JSR.** It is **not** a speed winner: 209.868 mean versus V2-V5 198.601 on the same 1,705-input corpus. The independent verifier confirms 5,115 Q/R/C/N/D/stack-preserving emulator calls over three layouts, and native x64sc correctness evidence covers another 192 calls. Run `python3 routines/standalone_lab/portable/verify_umod16_direct_zerozp.py` in CI; optional native VICE script `native_umod16_direct.py` requires `VICE_WRAPPER`. No native cycle figures are claimed.
