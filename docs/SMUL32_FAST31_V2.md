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

## Public-ABI candidate

The same ideas were also applied to the 31-ZP public-path research implementation. On the same local cycle-accurate harness it measures:

- **736.188510 cycles**, 100,000 C0FFEE pairs, 0 errors
- **736.128620 cycles**, independent 100,000-pair seed, 0 errors
- **1,849 structured edge cases, 0 errors**

This is materially below the currently shipped public SMUL32 means (~743–744 cycles). It is **not yet selected into V1–V5** in this change because public-profile replacement must pass the canonical source build, alternate relocation map, mixed-call, native-signed ownership and release-audit gates.

## Relation to compact126

`compact126` remains the absolute native speed point at 646.354530 cycles, trading 136 ZP and 126 persistent page-$01 bytes for speed. FAST31 v2 is the low-resource record point: substantially slower, but it preserves the library's 31-ZP / stack-free practical contract.
