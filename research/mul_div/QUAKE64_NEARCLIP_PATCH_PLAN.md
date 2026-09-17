# Quake64 near-clip prepared-ratio patch plan

**Target snapshot:** `Kweepa/Quake64 @ 7c84654946a60314568b709e7e7b97467fed69df`

**Purpose:** turn the standalone Quake-native prepared-fraction evidence into a real-build experiment without changing the C64 Math Library stable API.

The patch remains a Quake64 experiment until the real GAME build, heap gate and emulator/runtime tests pass.

> **Safety correction:** the shared `.nlrun` helper must **not** be replaced globally. It is also used by Cohen-Sutherland side/top/bottom clipping paths that do not call `qfrac_prep`. Only the four dedicated near-plane helpers `.nlx0`, `.nly0`, `.nlx1`, and `.nly1` should call the prepared APPLY routine.

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

For these crossings:

```text
n = ZCLIP - z_behind
d = z_front - z_behind
0 < n < d
```

The proposed replacement prepares the strict fraction once:

```text
m = round(n * 65536 / d)
```

then applies the same prepared `m` to both signed 16-bit component deltas.

Quake64 already owns the required 2 KiB quarter-square bank:

```text
$F000-$F1FF  sqlo
$F200-$F3FF  sqhi
$F400-$F5FF  negsqlo
$F600-$F7FF  negsqhi
```

The prototype also reuses existing Quake math scratch, so it does not allocate new zero page.

## 2. Add the prepared-fraction source to GAME

Insert the generated source after `loader.asm`:

```asm
!source "enemy.asm"
!source "loader.asm"
!source "prepared_fraction_smc.asm"

!source "map_bss.asm"
```

The source is emitted without fixed `.org` directives so it follows the GAME image in writable RAM and is counted by the existing `end_game` / heap checks.

Generator/exporter:

```text
research/mul_div/generate_quake64_prepared_fraction_smc.py
research/mul_div/export_quake64_prepared_fraction.py
```

Use the **nearest-Q0.16** tier for the first real-game experiment. The floor tier remains a speed-biased comparison point.

The integration source exposes:

```text
qfrac_prep
qfrac_apply_s16
```

## 3. Patch `.near0`

Replace the ratio save/restore sequence with one PREP:

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

After PREP, the original `nlo:nhi/dlo:dhi` values are no longer required by the two near-plane component applications.

## 4. Patch `.near1` symmetrically

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

`.nd10` establishes the same behind-to-front strict-fraction invariant.

## 5. Patch only the four near-plane component helpers

**Do not change `.nlrun`.** It remains the generic `scale_nd + lerp16` helper for the other clipping paths.

Change each of:

```text
.nlx0
.nly0
.nlx1
.nly1
```

from:

```asm
    jsr .nlrun
    clc
```

to:

```asm
    jsr qfrac_apply_s16
    lda rot0
    clc
```

The explicit `lda rot0` is required because the prepared APPLY promises the signed result in `rot0:rot1` but does not promise the old `lerp16` return convention `A=rot0`.

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
    jsr qfrac_apply_s16
    lda rot0
    clc
    adc e0x
    sta e0x
    lda rot1
    adc e0xh
    sta e0xh
    rts
```

The audited patcher enforces this narrow scope:

```text
research/mul_div/apply_quake64_nearclip_experiment.py
```

It fails unless there are exactly two PREP calls, exactly four prepared APPLY calls, and the original `.nlrun -> scale_nd` helper remains present.

## 6. Build and heap gates

Quake64's build chain provides the authoritative integration gate:

```text
ACME GAME build
mkreloc.py
second ACME GAME build
checkheap.py
```

The unmodified snapshot reports approximately:

```text
GAME next free      $9546
heap ceiling        $C000
heap available      10938 B
E1M2 tightest need   7958 B
current E1M2 slack   2980 B
```

The Quake-native candidate is about 1 KiB. Placement modeling suggests it should fit, but only the actual assembled GAME and `checkheap.py` result count as evidence.

The automated real-build gate is:

```text
research/mul_div/build_quake64_experiment.sh
.github/workflows/quake64-nearclip-integration.yml
```

It checks out the exact audited Quake snapshot, exports the origin-free nearest kernel, applies the narrow patch, assembles GAME, regenerates relocation data, assembles again, runs the heap gate, and archives build evidence.

## 7. Correctness gate

The arithmetic promise for the nearest tier is:

```text
prepared result differs from exact trunc(component*n/d) by at most 1
```

Standalone 5,000-edge integration testing already produced zero prepared-contract failures and maximum endpoint error 1. The real game experiment must additionally cover:

```text
near0 crossings
near1 crossings
positive / negative / zero X and Y deltas
ratios near 0 and near 1
large valid 8.8 deltas
room transitions under heap pressure
SMC/table/banking interactions
```

## 8. Performance gate

Standalone near-clip integration evidence on 5,000 valid crossings:

```text
Quake64 current             3703.0204 cycles mean
Quake-native nearest        1373.5418 cycles mean
Quake-native floor          1347.9062 cycles mean
```

Nearest is about **62.91% lower** and floor about **63.60% lower** in the isolated near-clip region.

A real-game benchmark should time the same work with normal IRQ/VIC/SID activity. The requirement is not to reproduce the isolated percentage exactly; it is to show that the saving survives at scene level and buys useful frame budget.

## 9. Promotion rule

If the patched Quake64 build passes correctness, heap, and scene-timing gates, M2 has a concrete demonstrated capability:

> Dynamic two-component interpolation can replace a reduced-ratio approximation with a <=1-error prepared ratio while substantially reducing clipping arithmetic.

Only then should the library freeze a checked `FRAC16_PREP` / `FRAC16_APPLY_S16` ABI or a higher-level interpolation form.

If the real build or scene-wide gate fails, keep the game-native implementation as research evidence and do **not** promote the stable API merely because isolated arithmetic benchmarks are strong.
