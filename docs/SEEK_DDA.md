# Seek: exact "move toward target" (`MATH_SEEK8_*`, `MATH_SEEK16_*`)

API entries 47–54 move an object from its current position to a target pixel
at a given speed. The object follows the exact Bresenham line and lands
exactly on the target. This is the library's answer to the most common
direction-vector job in games, and it needs no unit vector, no square root and
no multiply. The approach follows Repose's review on CSDb: screen coordinates
are small integers, so the classic Bresenham/DDA line is exact and far
cheaper to set up than normalize + scale + arrival bookkeeping.

Use `MATH_VEC2_NORMALIZE_Q8_8` for real direction vectors instead: steering
that turns every frame, reflections, physics, lighting.

| Family | Coordinates | Typical use |
|---|---|---|
| `MATH_SEEK8_*` | x, y unsigned bytes (0..255) | 8-bit game coordinates; sprite X/2 |
| `MATH_SEEK16_*` | x unsigned 16-bit (\|dx\| <= 32767), y unsigned byte | full sprite X (0..319/511), scrolling world coordinates |

## Calling convention

Each family manages **eight objects** (slots 0..7, one per hardware sprite).
`X` selects the slot for every entry and is preserved; `A`/`Y` are volatile;
`D=0` is required. The object's position lives in the library and is what you
draw:

| Symbol (from `math_api.inc`) | Contents |
|---|---|
| `MATH_SEEK8_POS_X`, `MATH_SEEK8_POS_Y` | 8-byte arrays, one byte per slot |
| `MATH_SEEK16_POS_XL`, `MATH_SEEK16_POS_XH`, `MATH_SEEK16_POS_Y` | 8-byte arrays, one byte per slot |

The start of a move is whatever the position arrays hold, so write them once
when the object appears. To chain waypoints, call `*_INIT` again with the next
target on arrival.

**`*_INIT`** (once per move). Inputs are preserved:

| Input | Meaning |
|---|---|
| `MATH_X+0` (`MATH_X+1` for SEEK16) | target x |
| `MATH_Y+0` | target y |
| `MATH_N+0` | speed fraction (1/256 px per frame) |
| `MATH_N+1` bits 0–6 | speed integer part, 0..126 |
| `MATH_N+1` bit 7 | 0 = speed along the major axis (classic Bresenham: diagonals move up to 1.41x faster); 1 = speed along the path (constant Euclidean speed, within 0.7%) |

Returns C=1 if the object is already on the target, else C=0.

**Per frame**, call one stepper per object (use the same stepper for the whole move):

| Entry | Use | Returns |
|---|---|---|
| `*_STEP` | any speed, including fractions and the Euclidean mode | C=1 on the arrival frame and every later call, else C=0 |
| `*_STEP_INT` | whole-pixel major-axis speed (bit 7 clear, integer part >= 1); ignores the fraction | same |
| `*_STEP1` | exactly 1 px/frame (init with `$0100`); uses the NMOS `DCP` opcode | same |

After arrival the position stays on the target. The steppers use no scratch,
so any number of objects can be stepped in any order. Like the rest of the
library they must not be interrupted by another library call from an IRQ.

```asm
        ; spawn: object 3 at (40,180)
        lda #40
        sta MATH_SEEK8_POS_X+3
        lda #180
        sta MATH_SEEK8_POS_Y+3
        ; go to (200,20) at 1.5 px/frame along the path
        lda #200
        sta MATH_X
        lda #20
        sta MATH_Y
        lda #$80
        sta MATH_N
        lda #$81                ; integer 1, bit 7 = Euclidean speed
        sta MATH_N+1
        ldx #3
        jsr MATH_SEEK8_INIT

        ; every frame
        ldx #3
        jsr MATH_SEEK8_STEP
        bcs arrived
        lda MATH_SEEK8_POS_X+3  ; draw
```

## How it works

- **The path is Bresenham's line** from start to target: every frame's position
  is within 0.5 px of the true line and the last one is the target pixel.
- **k pixels per frame cost the same as one.** The frame moves the major axis by
  k = floor or ceil of the speed. Init precomputes `k*dmin = whole_k*dmaj + rem_k`
  for k0 and k0+1 using k0+1 add/compare rounds, with no multiply or divide.
  Each frame then does `err -= rem_k` and `minor += whole_k`, plus one more minor
  step on wrap. Every frame is bit-identical to k single-pixel Bresenham steps.
- **One counter carries speed and distance.**
  `R = dmaj*256 - 1 - (sum of speeds so far)`. The borrow out of its low byte
  decides whether this frame moves k0 or k0+1 pixels; the borrow out of its top
  byte is arrival.
- **No flag instructions in the adds.** Each stepper path is entered with a known
  carry, so the per-frame deltas are stored pre-biased (`VX = vx-1`,
  `VY = vy + sign(VX)`). The x and y adds chain without `clc`/`sec`.
- **One code path per case**, indexed only by `X`. The 1 px/frame stepper uses
  `LDA #$FF / DCP counter,X`, which decrements and tests arrival in one
  instruction and leaves C=1 for the error update.
- **Euclidean speed**: the major-axis speed is `speed*cos(atan(dmin/dmaj))`. A
  5-bit slope index selects a 32-byte table of `256*(1-cos)` and a 16×8 multiply
  applies it.

## Performance (public entry through RTS)

Mean cycles; 408 random moves (256x200 for SEEK8, 320x200 for SEEK16) at 0.5–4 px/frame, every frame verified.

| Entry | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| `MATH_SEEK8_INIT`, major-axis speed | 368.3 | 336.5 | 337.1 | 337.1 | 368.3 |
| `MATH_SEEK8_INIT`, integer speed | 339.5 | 310.6 | 311.0 | 311.0 | 339.5 |
| `MATH_SEEK8_INIT`, speed $0100 | 304.2 | 279.4 | 279.9 | 279.9 | 304.2 |
| `MATH_SEEK8_INIT`, Euclidean speed | 835.2 | 751.4 | 752.3 | 752.3 | 835.2 |
| `MATH_SEEK16_INIT`, major-axis speed | 529.9 | 479.6 | 478.0 | 478.0 | 529.9 |
| `MATH_SEEK16_INIT`, integer speed | 506.8 | 458.1 | 456.2 | 456.2 | 506.8 |
| `MATH_SEEK16_INIT`, speed $0100 | 420.1 | 382.7 | 381.7 | 381.7 | 420.1 |
| `MATH_SEEK16_INIT`, Euclidean speed | 1036.5 | 925.8 | 925.1 | 925.1 | 1036.5 |
| `MATH_SEEK8_STEP` | 87.14 | 87.14 | 87.14 | 87.14 | 87.14 |
| `MATH_SEEK8_STEP_INT` | 70.99 | 70.99 | 70.99 | 70.99 | 70.99 |
| `MATH_SEEK8_STEP1` | 65.95 | 65.95 | 65.95 | 65.95 | 65.95 |
| `MATH_SEEK16_STEP` | 118.28 | 118.69 | 118.28 | 118.28 | 118.28 |
| `MATH_SEEK16_STEP_INT` | 103.65 | 103.65 | 103.65 | 103.65 | 103.65 |
| `MATH_SEEK16_STEP1` | 98.18 | 98.18 | 98.18 | 98.18 | 98.18 |

The per-frame steppers are identical in every profile. V2 pays one extra cycle
on the frames where SEEK16 moves k0+1 pixels, because no V2 free island can
hold the 291-byte stepper without a page-crossing branch.

## Compared with normalize + scale + arrival

Standalone kernels (no JMP slot) against a normalize mover built on the V1 library: `MATH_VEC2_NORMALIZE_Q8_8`, then two `MATH_SMUL16_SHR8` calls for a Q8.8 velocity. To know when it has arrived it also needs `ISQRT32(dx²+dy²)` and `UDIV16_SHL8` for a frame count, a per-frame countdown, and a snap to the target at the end. Mean cycles per move, same 408 moves × 6 speeds (`routines/movement/benchmark.py`). The library entries add 3 cycles per call for their JMP slot.

**8-bit coordinates (256×200)**

| | Setup | Per frame | Total per move | Path error | Target |
|---|---:|---:|---:|---:|---|
| normalize mover, 8-bit x | 4,412 | 81.7 | 12,356 | ≤3.6 px; 78 frames wrapped past the screen edge | snaps from ≤3.4 px |
| SEEK8, Euclidean speed (same speed meaning) | 741 | 84.0 | 8,940 | ≤0.5 px | exact |
| SEEK8, major-axis speed | 330 | 84.3 | 7,701 | ≤0.5 px | exact |
| SEEK8, integer speed (`STEP_INT`) | 304 | 68.0 | 4,222 | ≤0.5 px | exact |
| normalize mover at 1 px/frame | 4,286 | 81.7 | 14,306 | ≤2.2 px | snaps from ≤2.0 px |
| SEEK8 at 1 px/frame (`STEP1`) | 273 | 63.0 | 7,210 | ≤0.5 px | exact |

**16-bit x (320×200)**

| | Setup | Per frame | Total per move | Path error | Target |
|---|---:|---:|---:|---:|---|
| normalize mover | 4,412 | 93.7 | 14,741 | ≤3.2 px | snaps from ≤4.0 px |
| SEEK16, Euclidean speed | 914 | 115.1 | 13,639 | ≤0.5 px | exact |
| SEEK16, major-axis speed | 471 | 115.5 | 11,993 | ≤0.5 px | exact |
| SEEK16, integer speed | 449 | 100.7 | 7,068 | ≤0.5 px | exact |
| normalize mover at 1 px/frame | 4,285 | 93.7 | 17,314 | ≤2.1 px | snaps from ≤2.4 px |
| SEEK16 at 1 px/frame | 375 | 95.2 | 12,348 | ≤0.5 px | exact |

End to end, SEEK8 is 1.38x cheaper at the same Euclidean speed and 1.98x at 1 px/frame. SEEK16 is 1.08x and 1.40x cheaper. Setup is 6–16x cheaper for SEEK8. Per frame, SEEK16's 16-bit error term makes it 21 cycles slower than the fixed-point mover at the same Euclidean speed. The setup saving outweighs that for moves of up to about 163 frames, and the integer and 1 px/frame steppers are cheaper outright. The normalizer alone is 3,441 bytes (881 code + 2,560 tables); both seek families together are 1,288 bytes.

## Resources

- **Code:** 1,288 bytes (V2–V4) or 1,423 bytes (V1/V5, absolute-RAM init scratch),
  plus 24 bytes of JMP slots. No lookup table except the 32-byte Euclidean
  correction.
- **Object state:** 408 bytes of runtime RAM (160 for SEEK8, 248 for SEEK16).
- **Zero page:** none added. Init borrows 19 bytes of the existing game scratch
  (`$53-$6A` ZP in V2–V4; `V1_SCRATCH` RAM in V1/V5). The steppers use no scratch.
- **REU:** not used. No `MATH_INIT` dependency.
- **Placement:** code and state occupy islands inside the profiles' existing
  claimed regions. They were proven untouched by every other routine, by
  `MATH_INIT` and by REU DMA on both maps
  (`validation/movement/SEEK_PLACEMENT.json`). Only seek-owned bytes changed
  in any image (`validation/movement/SEEK_BINARY_DELTA.json`), and neither the
  PRG spans nor the REU images changed size. Per-profile islands:
  `<profile>/resident/movement/native/README.md`.

## Sources and validation

| Item | Path |
|---|---|
| kernel template (single source of truth) | `tools/seek_kernel.py`, emitted by `tools/generate_seek_sources.py` |
| library installs | `<profile>/resident/movement/native/seek_dda.asm` |
| standalone kernels | `routines/movement/seek_u8_u8_dda.asm`, `seek_u16_u8_dda.asm` (byte-identical under ACME 0.97) |
| exact executable mirrors | `<profile>/standalone/seek_u8_u8_*.asm`, `seek_u16_u8_*.asm` |
| profile benchmark | `tools/benchmark_seek_profiles.py` → `validation/movement/SEEK_PROFILE_BENCHMARK.json` |
| comparison with normalize | `routines/movement/benchmark.py` → `validation/movement/SEEK8_DDA_BENCHMARK.json`, `SEEK_DDA_BENCHMARK.json` |

The common validator (`tools/validate_source_build.py`) runs every seek entry
in V1–V4, V5 and all Custom Pareto builds on both maps. It checks every frame,
keeps inputs and `X` unchanged, and interleaves other library calls between
frames. `make seek` rebuilds and reruns the seek-specific checks.
