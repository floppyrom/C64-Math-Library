# Movement: exact "seek" DDA

`seek_u16_u8_dda.asm` moves an object from its current position to a target
pixel at a given speed. It is the recommended way to do "move towards (tx,ty)"
in a game. `MATH_VEC2_NORMALIZE_Q8_8` should not be used for this.

The approach follows Repose's review on CSDb. For target seeking you don't need
a unit vector. Screen coordinates are small integers, so the classic answer is
a Bresenham/DDA line from the start pixel to the target pixel. That line is
exact, needs no square root or multiply, and says precisely when the object has
arrived.

## What it does

- The path is the Bresenham line from start to target. Each frame's position is
  within 0.5 px of the true line, and the object lands exactly on the target.
- Speed is Q8.8 pixels/frame. The fraction is accumulated per object, so 0.5 or
  1.25 px/frame work.
- `seek_init` measures speed along the major axis (classic Bresenham, so a
  diagonal move is up to 1.41x faster). `seek_init_euclid` gives constant
  speed along the path, within 0.7%.
- Several pixels per frame cost the same as one. The k-pixel Bresenham update
  is precomputed at init: `err -= rem_k`, `minor += whole_k` (+1 on wrap),
  where `k*dmin = whole_k*dmaj + rem_k`. Every frame is bit-identical to
  running k single-pixel Bresenham steps.
- Up to 8 objects run at once (struct-of-arrays, `X` = slot). The steppers use
  no scratch, so objects can be stepped in any order.

x is unsigned 16-bit (sprite X), y is unsigned 8-bit, |dx| <= 32767, and the
speed's integer part is <= 126.

## Calling

```asm
        ; object 3 starts where it is: POS_XL/POS_XH/POS_Y+3 already hold it
        ldx #3
        lda #<300
        sta IN_X1L
        lda #>300
        sta IN_X1H
        lda #150
        sta IN_Y1
        lda #$80                ; 1.5 px/frame
        sta IN_SPL
        lda #$01
        sta IN_SPH
        jsr seek_init_euclid    ; C=1 if already there

        ; every frame
        ldx #3
        jsr seek_step           ; C=1 on arrival (and after)
        ; draw at POS_XL,x / POS_XH,x / POS_Y,x
```

`seek_step_int` skips the fraction accumulator. Use it with `seek_init` and a
whole-pixel speed; it is about 16 cycles cheaper per frame.

The steppers return C=1 on the arrival frame and on every later call, and the
position stays on the target. To chain waypoints, call `seek_init` again with
the next target: the start is always the current position.

Resources: 722 code bytes + a 32-byte table, a 16-byte IO/scratch block (zero
page recommended), and 32 bytes of state per slot (256 bytes for 8 slots).
Code and state must be in RAM (no self-modifying code). D=0 is required. Init is
not reentrant because it uses the IO block.

## Measured against the normalize pipeline

`benchmark.py` runs both in the repository's cycle-counting 6502 emulator on
408 random screen moves (x 0..319, y 0..199) at six speeds from 0.5 to 4
px/frame. The baseline is what a caller would build today on the V1 reference
build (`baseline_normalize.asm`):

- setup is `MATH_VEC2_NORMALIZE_Q8_8` plus two `MATH_SMUL16_SHR8` calls for a
  Q8.8 velocity;
- each frame adds a Q16.8 x and a Q8.8 y.

A unit-vector mover can't tell when it has arrived. "With arrival" adds the
cheapest honest fix: len = `ISQRT32(dx²+dy²)`, frames = len/speed, a per-frame
countdown, and a snap at the end.

| | Setup (mean cycles) | Per frame | Total per move | Path error | Lands on target |
|---|---:|---:|---:|---:|---|
| Normalize, bare | 1,122 | 77.0 | 9,611 | ≤3.21 px | no, never stops |
| Normalize, with arrival | 4,412 | 93.7 | 14,741 | ≤3.21 px | snaps; ≤4.03 px jump |
| **`seek_init_euclid` + `seek_step`** | **967** | **126.6** | **14,960** | **≤0.5 px** | **exact** |
| **`seek_init` + `seek_step`** | **630** | **125.7** | 13,173 | ≤0.5 px | exact |
| **`seek_init` + `seek_step_int`** (integer speeds) | **651** | **109.3** | 7,839 | ≤0.5 px | exact |

Totals are means per move. The two `seek_init` rows are not directly
comparable with the Euclidean-speed rows: diagonal moves take fewer frames.
Memory: seek is 754 bytes of code and table. The stock normalizer alone is
3,441 bytes (881 code + 2,560 tables), before the multiply, square-root and
divide routines it needs here.

What this shows:

- **Setup** is 4.6x cheaper than a normalize mover that knows when it has
  arrived (967 vs 4,412). Even against the bare mover it is cheaper, and the
  bare mover never stops.
- **Accuracy:** the normalize path drifts up to 3.2 px off the line and misses
  the target by up to 4 px. seek is exact.
- **Memory** is about 4.5x smaller than the normalizer alone.
- **Per frame**, seek costs about 33 cycles more than the Q8.8 countdown
  mover. That is the price of the exact Bresenham error term, which works mod
  dmaj instead of mod 256. For long, uninterrupted moves the totals end up
  about even (+1.5%). The DDA wins clearly when moves are short or targets
  change often (homing), because then setup dominates.

`MATH_VEC2_NORMALIZE_Q8_8` remains the right tool for true direction vectors:
thrust from a joystick angle, reflections, physics, and lighting.

## Files

| File | Purpose |
|---|---|
| `seek_u16_u8_dda.asm` | the routine (ACME syntax; set `ORG`, `IO`, `ST`) |
| `seek_model.py` | Python Bresenham reference model and emulator loader |
| `baseline_normalize.asm` | the normalize-based baseline, linked against the V1 build |
| `benchmark.py` | validation and benchmark; writes `validation/movement/SEEK_DDA_BENCHMARK.json` |

To reproduce:

```sh
make reference          # builds the V1 PRG used by the baseline
python3 routines/movement/benchmark.py
```

The benchmark checks every frame of every move against the reference model,
for all three entry combinations. It also runs 129,440 slot-frames with eight
objects moving at once and stepped round-robin.
