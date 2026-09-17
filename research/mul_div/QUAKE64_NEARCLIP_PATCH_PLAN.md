# Quake64 near-clip prepared-ratio patch plan

**Target snapshot:** `Kweepa/Quake64 @ 7c84654946a60314568b709e7e7b97467fed69df`

**Purpose:** turn the standalone Quake-native prepared-fraction evidence into a real-build experiment without changing the C64 Math Library stable API.

The patch should remain a Quake64 experiment until the real GAME build, heap gate and emulator/runtime tests pass.

## 1. Source facts the patch relies on

Current Quake64 near clipping in `src/cube.asm` does:

```text
.near0 / .near1
    form dynamic n,d
    save n,d on stack
    interpolate X through .nlrun
    restore n,d
    interpolate Y through .nlrun
    clamp Z to ZCLIP
```

`.nlrun` currently executes:

```text
scale_nd
lerp16
```

so the ratio is reduced to signed-byte numerator/denominator separately for X and Y.

The proposed replacement prepares the strict fraction once:

```text
0 < n < d
m = Q0.16 approximation of n/d
```

then applies the same prepared `m` to both signed 16-bit component deltas.

The game already owns the required 2 KiB quarter-square bank:

```text
$F000-$F1FF  sqlo
$F200-$F3FF  sqhi
$F400-$F5FF  negsqlo
$F600-$F7FF  negsqhi
```

and the prototype reuses existing Quake math scratch instead of allocating new ZP.

## 2. Add the prepared-fraction source to GAME

The source include should be placed **after `loader.asm` and before `end_game = *`** in `src/quake64.asm`:

```asm
!source "enemy.asm"
!source "loader.asm"
!source "prepared_fraction_smc.asm"

end_game = *
```

This is preferable to a fixed `$9000/$9800` research origin. Quake64's GAME image is ordinary writable RAM and the SMC operands must remain writable. Appending before `end_game` also lets the existing heap check account for the exact code size automatically.

The research generator that supplies the algorithm is:

```text
research/mul_div/generate_quake64_prepared_fraction_smc.py
```

For the first game patch, use the **nearest-Q0.16** form. The floor form remains a speed-biased comparison tier.

The integration version should be emitted as ordinary sequential source with no fixed `.org`, retaining these Quake-native labels:

```text
qfrac_prep
qfrac_apply_s16
```

## 3. Patch `.near0`

Replace the current ratio save/restore sequence:

```asm
.near0
    jsr .nd01
    lda nlo
    pha
    lda nhi
    pha
    lda dlo
    pha
    lda dhi
    pha
    jsr .nlx0
    pla
    sta dhi
    pla
    sta dlo
    pla
    sta nhi
    pla
    sta nlo
    jsr .nly0
    lda #<ZCLIP
    sta e0z
    lda #>ZCLIP
    sta e0zh
    rts
```

with:

```asm
.near0
    jsr .nd01
    jsr qfrac_prep
    jsr .nlx0
    jsr .nly0
    lda #<ZCLIP
    sta e0z
    lda #>ZCLIP
    sta e0zh
    rts
```

`qfrac_prep` consumes/clobbers `nlo:nhi/dlo:dhi`; this is intentional. After PREP, the ratio is represented by patched fixed multipliers and the original n/d values are no longer needed for X or Y.

## 4. Patch `.near1` symmetrically

Replace the stack save/restore block after `.nd10` with:

```asm
.near1
    jsr .nd10
    jsr qfrac_prep
    jsr .nlx1
    jsr .nly1
    lda #<ZCLIP
    sta e1z
    lda #>ZCLIP
    sta e1zh
    rts
```

The same strict-fraction invariant holds because `.nd10` orients the ratio from the behind endpoint toward the front endpoint.

## 5. Replace `.nlrun`

The old helper:

```asm
.nlrun
    jsr scale_nd
    lda dlo
    ora dhi
    bne +
    lda #0
    sta rot0
    sta rot1
    rts
+
    jmp lerp16
```

becomes:

```asm
.nlrun
    jmp qfrac_apply_s16
```

The prepared APPLY returns its signed result in `rot0:rot1`.

Unlike the old `lerp16` contract, the current prepared prototype does **not** promise `A=rot0` on return. Therefore add an explicit `lda rot0` after `jsr .nlrun` in all four component helpers before their accumulation carry chain.

For example:

```asm
.nlx0
    sec
    lda e1x
    sbc e0x
    sta ylo
    lda e1xh
    sbc e0xh
    sta yhi
    jsr .nlrun
    lda rot0
    clc
    adc e0x
    sta e0x
    lda rot1
    adc e0xh
    sta e0xh
    rts
```

Apply the same one-instruction change to:

```text
.nlx0
.nly0
.nlx1
.nly1
```

This is the arithmetic shape already represented by `benchmark_quake64_nearclip_smc_integration.py`.

## 6. Build and heap gates

Quake64's own build already provides the correct release gate:

```text
ACME builds game-krill and game
mkreloc.py regenerates relocation data
checkheap.py validates map/pose heap coexistence
mkdisk.py rebuilds both disks
```

The unmodified snapshot reports:

```text
GAME next free      $9546
heap ceiling        $C000
heap available      10938 B
E1M2 tightest need   7958 B
current E1M2 slack   2980 B
```

The Quake-native candidate is roughly 1 KiB, so it appears feasible, but the real `checkheap.py` result after assembly is authoritative.

The C64 Math Library research-side assembler check is:

```text
research/mul_div/quake64_smc_placement.py
```

It relocates PREP/APPLY contiguously from the old GAME end and reports the new tightest-level slack before a real Quake build is attempted.

## 7. Correctness gate

For a patched Quake build, validate at least:

```text
near0 crossings
near1 crossings
positive X/Y deltas
negative X/Y deltas
zero X/Y deltas
ratios very close to 0
ratios very close to 1
large valid 8.8 deltas
room transitions with heap pressure
```

The arithmetic promise for the nearest tier is:

```text
prepared result differs from exact trunc(component*n/d) by at most 1
```

The 5,000-edge standalone integration benchmark has already shown zero prepared-contract failures and max endpoint error 1. The full game test must additionally establish that no SMC/table/banking interaction is introduced.

## 8. Performance gate

Standalone near-clip integration evidence on 5,000 valid crossings:

```text
Quake64 current             3703.0204 cycles mean
Quake-native nearest        1373.5418 cycles mean
Quake-native floor          1347.9062 cycles mean
```

Nearest is **62.91% lower** and floor **63.60% lower** in the isolated near-clip region.

A real game benchmark should time the same near-clipping work with normal IRQ/VIC/SID activity. The target is not to reproduce the exact isolated percentage; it is to show that the saved arithmetic time survives in the scene and buys useful frame budget.

## 9. Promotion rule

If the patched Quake64 build passes correctness, heap and scene timing gates, then M2 has a concrete demonstrated capability:

> dynamic two-component interpolation can replace a reduced-ratio approximation with a <=1-error prepared ratio while cutting the expensive clipping arithmetic substantially.

At that point the C64 Math Library can design the stable checked `FRAC16_PREP` / `FRAC16_APPLY_S16` ABI from evidence.

If the real build fails the memory or scene-wide gate, keep the game-native implementation as research evidence and do **not** force the stable API merely because the isolated arithmetic benchmark is strong.
