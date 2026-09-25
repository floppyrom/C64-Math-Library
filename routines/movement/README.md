# Movement: exact "seek" DDA

These routines move an object from its current position to a target pixel at
a given speed. They are the recommended way to do "move towards (tx,ty)" in a
game; `MATH_VEC2_NORMALIZE_Q8_8` should not be used for this.

The approach follows Repose's review on CSDb. Target seeking needs no unit
vector. Screen coordinates are small integers, so the classic answer is a
Bresenham/DDA line from the start pixel to the target pixel. It is exact, needs
no square root or multiply, and knows exactly when the object has arrived.

| Source | Coordinates | Use it for |
|---|---|---|
| `seek_u8_u8_dda.asm` | x, y 0..255 | the fast version for 8-bit game coordinates (use x/2 for sprite X, as many games do) |
| `seek_u16_u8_dda.asm` | x 0..65535, y 0..255 | full-resolution sprite X (0..319/511), or longer paths |

## What both do

- The path is the Bresenham line from start to target. Each frame's position is
  within 0.5 px of the true line, and the object lands exactly on the target.
- Speed is Q8.8 pixels/frame. The fraction is carried per object, so 0.5 or
  1.25 px/frame work.
- `*_init` measures speed along the major axis (classic Bresenham, so a
  diagonal move is up to 1.41x faster). `*_init_euclid` gives constant speed
  along the path, within 0.7%.
- Several pixels per frame cost the same as one. The k-pixel update is
  precomputed at init as `k*dmin = whole_k*dmaj + rem_k`; then each frame does
  `err -= rem_k` and `minor += whole_k` (+1 on wrap). Every frame is
  bit-identical to k single-pixel Bresenham steps.
- Up to 8 objects run at once (struct-of-arrays, `X` = slot). The steppers use
  no scratch, so objects can be stepped in any order.
- Steppers return C=1 on the arrival frame and on every later call, and the
  position stays on the target. To chain waypoints, call init again: the start
  is always the current position.

## The 8-bit version

With x and y in bytes every delta is at most 255. The error term, the
remaining distance and both positions are then single bytes.

- **No multiply or divide in setup.** For k0 = integer speed, init runs k0+1
  add/compare rounds to get `rem_k` and `whole_k`.
- **One counter for speed and distance.** Instead of a fraction accumulator
  and a pixel countdown, one 16-bit counter `R = dmaj*256 - 1 - speeds so far`
  does both. The borrow out of its low byte decides whether this frame moves
  k0 or k0+1 pixels. The borrow out of its high byte is the arrival test.
- **Carries decided at setup.** Each per-frame path is known to add with C=1,
  so the stored deltas are pre-biased (`VX = vx-1`, `VY = vy-[vx<=0]`) and the
  step has no `clc`/`sec` between adds.
- **One code path per case.** Each stepper indexes only with `X`, with one
  copy per (k0 / k0+1) × (wrap / no wrap) case. No index-register shuffling.
- **`seek8_step1` uses NMOS `DCP`** for the common 1 px/frame case.
  `lda #$FF / dcp RH,x` decrements the distance counter and flags arrival in
  one instruction, and leaves C=1 for the error update. This follows the
  "decrementing 16-bit counter" idiom in *No More Secrets*.

The other unintended opcodes were checked and don't pay off here. `LAX`/`SBX`
overwrite X, which holds the object slot. `ISC`/`RRA`/`SLO`… only
increment, decrement or shift memory, but the work here is "memory ± other
memory" arithmetic.

```asm
        ldx #3                  ; object 3; POS_X+3/POS_Y+3 hold its position
        lda #200
        sta IN_X1
        lda #150
        sta IN_Y1
        lda #$00                ; 1.0 px/frame
        sta IN_SPL
        lda #$01
        sta IN_SPH
        jsr seek8_init          ; C=1 if already there

        ; every frame
        ldx #3
        jsr seek8_step1         ; or seek8_step / seek8_step_int; C=1 on arrival
```

Resources: 642 code bytes + a 32-byte table, a 16-byte IO/scratch block (zero
page recommended), 20 bytes of state per slot (160 for 8 slots). `!cpu 6510`
is needed for `DCP`. Each stepper path is about 30 bytes, so inlining one
into a game's object loop also saves the 12-cycle `JSR`/`RTS`.

## Measured against the normalize pipeline

`benchmark.py` runs everything in the repository's cycle-counting 6502
emulator: 408 random moves at six speeds from 0.5 to 4 px/frame, checking every
frame of every move against a Python Bresenham model. The baseline is what a
caller would build today on the V1 reference build (`baseline_normalize.asm`):

- setup is `MATH_VEC2_NORMALIZE_Q8_8` plus two `MATH_SMUL16_SHR8` for a Q8.8
  velocity;
- each frame adds Q8.8 (or Q16.8) x and Q8.8 y.

A unit-vector mover can't tell when it has arrived. "With arrival" adds the
cheapest fix: `ISQRT32(dx²+dy²)` and `UDIV16_SHL8` for a frame count, a
per-frame countdown, and a snap at the end.

### 8-bit coordinates (256×200), mean cycles

| | Setup | Per frame | Total per move | Path error | Target |
|---|---:|---:|---:|---:|---|
| Normalize mover, 8-bit x, with arrival | 4,412 | 81.7 | 12,356 | ≤3.6 px; left the screen range on 78 frames | snaps from ≤3.4 px |
| **`seek8_init_euclid` + `seek8_step`** | **713** | **84.0** | **8,912** | ≤0.5 px | exact |
| **`seek8_init` + `seek8_step`** | **392** | **84.3** | 7,764 | ≤0.5 px | exact |
| **`seek8_init` + `seek8_step_int`** (integer speeds) | **406** | **68.0** | 4,324 | ≤0.5 px | exact |
| **`seek8_init` + `seek8_step1`** (1 px/frame) | **375** | **63.0** | 7,312 | ≤0.5 px | exact |
| Normalize mover at 1 px/frame, for comparison | 4,286 | 81.7 | 14,306 | ≤2.2 px | snaps |

The Euclidean row is the like-for-like comparison: same speed meaning, 97.6
vs 97.3 frames per move. The major-axis rows take fewer frames on diagonals.

What this shows:

- **Setup:** 6–12x cheaper than a normalize mover that knows when it has
  arrived.
- **Per frame:** integer and 1 px/frame speeds beat the fixed-point mover;
  fractional speed is within 3 cycles of it.
- **End to end:** 1.4x cheaper at the same Euclidean speed, 2x at 1 px/frame.
- **Accuracy:** exact arrival and ≤0.5 px path error. The 8-bit fixed-point
  mover drifts by up to 3.6 px and can wrap at the screen edge.
- **Memory:** 674 bytes of code and table, against 3,441 for the stock
  normalizer alone.

### 16-bit x (320×200), mean cycles

| | Setup | Per frame | Total per move |
|---|---:|---:|---:|
| Normalize mover, with arrival | 4,412 | 93.7 | 14,741 |
| `seek_init_euclid` + `seek_step` | 967 | 126.6 | 14,960 |
| `seek_init` + `seek_step` | 630 | 125.7 | 13,173 |
| `seek_init` + `seek_step_int` | 651 | 109.3 | 7,839 |

The 16-bit version keeps a 16-bit error term and a separate pixel countdown.
It still has the exactness and setup advantages, but per frame it is behind
the fixed-point mover. Most games can use the 8-bit version with half-
resolution X.

`MATH_VEC2_NORMALIZE_Q8_8` remains the right tool for true direction vectors:
thrust from a joystick angle, reflections, physics, lighting.

## Files

| File | Purpose |
|---|---|
| `seek_u8_u8_dda.asm` | 8-bit routine (ACME syntax, `!cpu 6510`; set `ORG`, `IO`, `ST`) |
| `seek_u16_u8_dda.asm` | 16-bit-x routine (set `ORG`, `IO`, `ST`) |
| `seek_model.py` | Python Bresenham reference model and emulator loaders |
| `baseline_normalize.asm` | the normalize-based baseline, linked against the V1 build |
| `benchmark.py` | validation and benchmark |

To reproduce:

```sh
make reference                                          # V1 PRG for the baseline
python3 routines/movement/benchmark.py                  # -> validation/movement/SEEK_DDA_BENCHMARK.json
python3 routines/movement/benchmark.py --variant u8     # -> validation/movement/SEEK8_DDA_BENCHMARK.json
```

Each run checks every frame of every move for every entry combination. It also
runs eight objects at once, stepped round-robin: 103,600 slot-frames for the
8-bit version and 129,440 for the 16-bit one.

The emulator's unintended-opcode support (`tools/mini6502.py`) is tested
against the worked examples in *No More Secrets* by
`tools/test_mini6502_illegal.py`. ACME was not available in this environment,
so the sources have not been cross-assembled with it.
