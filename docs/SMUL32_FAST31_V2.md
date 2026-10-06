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

The low-resource work is now integrated into V2–V4 using a profile-native mixed-call-safe pointer layout. **All six** FAST31 table-pointer pairs live in holes already covered by the normal profile ZP ownership map, so ordinary calls no longer need the old pointer-high repair at all. `MATH_INIT` installs the persistent high bytes.

The persistent-pointer integration first removed 25 cycles from ordinary signed `MATH_SMUL32`/`MATH_SMUL32_SHR16`. A follow-up then removed the redundant 3-cycle stable-entry self-redirect, for a total **−28 cycles** versus the pre-integration signed public path. Unsigned `MATH_UMUL32`/`MATH_UMUL32_SHR16` remain **−22 cycles** from the persistent-pointer change.

A further summation pass now exploits bounds that are already guaranteed by the signed quadrant dispatcher. In the NN/q0/q1 positive-magnitude producers, the relevant row-top bytes cannot wrap at several late-column carry sites. The hot no-carry paths were therefore made fall-through and the impossible wrap checks removed, while the actual carry work moved to cold helpers. The four-row quarter-square producer, the 31-byte ZP contract, the public ABI and the persistent-pointer layout are unchanged.

On an exact 20,324-case A/B corpus, shipped V2 improves from **722.867792** to **720.762498 cycles mean** (**−2.105294 cycles/call**), with the minimum improving **632 → 630** and the maximum remaining **845**. The canonical 2,409-case signed-corpus means are now:

- **V2: 712.403902 cycles**
- **V3: 712.856787 cycles**
- **V4: 712.948941 cycles**


A subsequent **q2-only bounded-carry pass** replaces the late-column summation only for the X<0, Y>=0 quadrant. It reuses the compact126/validated UMUL32 bounded carry-state encoding after the existing four-row producer. The q0, q1 and NN paths remain on the previous optimized summation. On the shared 20,324-case corpus this reduces the overall mean from **721.297825 to 720.566375 cycles** (−0.731451), while q2 itself falls from **730.300079 to 727.363295 cycles**. The worst case improves from **845 to 841 cycles** with no change to the 31-ZP, stack-free resource contract.

A further **q2 tail-placement follow-up** moves the shared signed upper-half correction after the alternate bounded-carry continuation. This removes the hot alternate-path jump and converts its final carry test into a same-page fall-through without changing the producer or correction arithmetic. On the same shared 20,324-case corpus the mean falls from **720.566375 to 720.223332 cycles** (−0.343043), with identical cycle vectors in V2/V3/V4 and worst case **841 → 838**. A focused 20,070-case q2 corpus improves from **727.560538 to 726.469507 cycles** (−1.091031). The block remains 291 bytes and the 31-ZP / zero-persistent-stack contract is unchanged.

A further **q1 bounded-carry + correction-tail follow-up** replaces only the X>=0,Y<0 late-column summation with the compact bounded-carry state machine and tail-places its signed correction. On an identical 6,361-case shared corpus V2/V3/V4 remain cycle-identical and improve from **717.780538 to 717.448043 cycles** (−0.332495). A focused 20,070-case q1 corpus improves from **734.268012 to 732.785800 cycles** (−1.482212), with worst case **839 → 830**. The producer, ABI, 31-ZP footprint, and zero persistent stack-page contract are unchanged.

The fixed-point derivative `MATH_SMUL32_SHR16` is now **781.620041 cycles mean (695–903)** in V2/V3/V4. Current READY means are **724.873047 / 725.296875 / 723.177734** on their profile-specific 1,024-case corpora.

V2 remains comfortably inside its documented **221-byte total ZP commitment**; the regenerated stable-API union touches **207 bytes**. V3/V4 touch 202/201 bytes respectively. V3/V4 Turbo BEGIN may temporarily overlay the persistent bytes, and END restores their previous values exactly. V1/V5 retain the original all-in-`$02-$20` 31-ZP public layout because those profiles promise a 31-byte normal-ZP contract.

The earlier 736.188510 public-path research point remains useful historical evidence, but it is superseded for V2–V4 by this faster profile-integrated form.

## Relation to compact126

### Public-ABI v2 arithmetic transplant check

The remaining FAST31 v2 arithmetic ideas were tested against the persistent-pointer public core. The NN common/rare `x0` borrow optimization was already present. The literal `CPY #$00` carry-seeded sign dispatch assembled and passed the full signed/public/Turbo gates, but measured **exactly the same** 2,409-case means as the non-carry-seeded form: the public ABI must load Y from memory, so the added 2-cycle compare only replaces an existing 2-cycle `SEC`. It was therefore discarded. The retained follow-up optimization is the fixed-entry fallthrough, which saves a constant 3 cycles without changing the arithmetic or resource contract.

Evidence: `validation/review/SMUL32_FAST31_V2_TRANSPLANT.json`.

### V2/V3/V4 timing comparability

The small difference between the profile-specific canonical means above is **benchmark-corpus noise, not a real V3/V4 slowdown**. The signed validator intentionally uses a different deterministic random seed for each profile. A dedicated same-input check now runs all three optimized profiles on one shared **20,324-case** edge+random corpus and obtains **720.223332 cycles in V2, V3 and V4**, with zero errors. The relocated implementations therefore remain cycle-identical when the inputs are identical; the canonical spread (**712.403902 / 712.856787 / 712.948941**) comes from corpus variation, not a relocation or page-cross penalty.

`compact126` remains the absolute native speed point at 646.354530 cycles, trading 136 ZP and 126 persistent page-$01 bytes for speed. FAST31 v2 is the low-resource record point: substantially slower, but it preserves the library's 31-ZP / stack-free practical contract.
