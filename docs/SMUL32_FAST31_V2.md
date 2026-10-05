# SMUL32 FAST31 v2

`mul_s32_s32_s64_fast31_native_v2.asm` is the improved 31-byte-ZP, stack-free native signed 32×32 → 64 record point.

## Native result

| Corpus | Cases | Errors | Mean | Min | Max |
|---|---:|---:|---:|---:|---:|
| C0FFEE deterministic native corpus | 100,000 | 0 | **692.825100** | 590 | 808 |
| independent seed 0x5EED1234 | 100,000 | 0 | **692.678520** | 590 | 815 |
| structured signed edge suite | 1,849 | 0 | 659.812872 | 590 | 832 |

The previous published `fast31_native` point is 697.259440 cycles, so v2 improves the same resource class by **4.434340 cycles/call** on the primary corpus.

## Resource contract

- **31 ZP bytes**
- **0 persistent page-$01 bytes**
- **1,133 executable code bytes**
- **2,044 immutable quarter-square table bytes**
- **3,208 occupied bytes including the 31-byte ZP workspace**

The code-size increase relative to the shared public implementation comes from retaining specialized PN and NP producer copies. This is intentional: the native ABI has no untouched public input buffer to read original operands from after the product.

## Ideas transferred from compact126

### 1. NN common/rare negation

After the low byte of negative X is negated, carry is set only when the original `x0 == 0`. For the overwhelmingly common `x0 != 0` case, the borrow is known to propagate through the remaining bytes, so the upper magnitude bytes are simply `~x1`, `~x2`, and `~x3`.

The rare `x0 == 0` case takes a cold propagation helper using the full SBC chain.

### 2. Carry-seeding sign dispatch

`CPY #$00` identifies Y's sign through N while leaving C=1 for every input byte. PP, PN and NP therefore reach their producer kernels with the required initial carry already set, removing one `SEC` from each of those quadrants.

Together these changes account for the measured reduction from 697.259440 to 692.825100.

## Public-profile integration

The low-resource work is now integrated into V2–V4 using a profile-native mixed-call-safe pointer layout. Five FAST31 table-pointer pairs live in holes already covered by the normal profile ZP ownership map; one shared pair remains in ZP_MAIN and is rebound on an ordinary call. `MATH_INIT` installs the persistent high bytes.

This removes a constant **17 cycles** from ordinary `MATH_SMUL32`, `MATH_UMUL32`, and both 32-bit SHR16 derivatives while leaving READY timings unchanged. The canonical 2,409-case signed-corpus means are:

- **V2: 726.605230 cycles**
- **V3: 727.033209 cycles**
- **V4: 727.090079 cycles**

V2 remains inside its documented **221-byte total ZP commitment**; the current stable API union touches 220 bytes. V3/V4 Turbo BEGIN may temporarily overlay the persistent bytes, and END restores their previous values exactly. V1/V5 retain the original all-in-`$02-$20` 31-ZP public layout because those profiles promise a 31-byte normal-ZP contract.

The earlier 736.188510 public-path research point remains useful historical evidence, but it is superseded for V2–V4 by this faster profile-integrated form.

## Relation to compact126

`compact126` remains the absolute native speed point at 646.354530 cycles, trading 136 ZP and 126 persistent page-$01 bytes for speed. FAST31 v2 is the low-resource record point: substantially slower, but it preserves the library's 31-ZP / stack-free practical contract.
