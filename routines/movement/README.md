# Movement: exact "seek" DDA

Standalone copies of the kernels the library installs as `MATH_SEEK8_*` and
`MATH_SEEK16_*` (API entries 47–54). Each one moves up to eight objects to a
target pixel at a Q8.8 speed along the exact Bresenham line and lands exactly
on the target. The full description (calling convention, how it works,
per-profile timings and the comparison with normalize) is in
[`docs/SEEK_DDA.md`](../../docs/SEEK_DDA.md).

The approach follows Repose's review on CSDb: target seeking needs no unit
vector, and small screen coordinates make the classic Bresenham/DDA line exact
and cheap.

| Source | Coordinates | Entries |
|---|---|---|
| `seek_u8_u8_dda.asm` | x, y 0..255 | `seek8_init`, `seek8_step`, `seek8_step_int`, `seek8_step1` |
| `seek_u16_u8_dda.asm` | x 0..65535 (\|dx\| <= 32767), y 0..255 | `seek16_init`, `seek16_step`, `seek16_step_int`, `seek16_step1` |

Both files are generated from `tools/seek_kernel.py` by
`tools/generate_seek_sources.py`, the same template as the library installs.
They assemble byte-identically with ACME 0.97 (`!cpu 6510`) and the bundled
assembler.

## Standalone interface

Configure `ORG`, `IO` (24 bytes, zero page recommended) and `ST` (state,
8-byte aligned) at the top of the file.

- Inputs, all preserved:
  - `IO+0`/`IO+1` target x (the high byte is SEEK16 only);
  - `IO+2` target y;
  - `IO+3` speed fraction;
  - `IO+4` speed integer part, 0..126. Bit 7 set means the speed is along the path (Euclidean) instead of along the major axis.
- `X` = slot 0..7 for every entry and is preserved. The position arrays are `S8_POS_X`/`S8_POS_Y` or `S16_POS_XL`/`S16_POS_XH`/`S16_POS_Y`; the start of a move is whatever they hold.
- `*_init` returns C=1 if the object is already on the target. The steppers return C=1 on the arrival frame and on every later call.
- Steppers:
  - `*_step`: any speed;
  - `*_step_int`: whole-pixel major-axis speed, bit 7 clear;
  - `*_step1`: speed `$0100`, uses NMOS `DCP`.

Sizes: `seek_u8_u8_dda.asm` 582 bytes, `seek_u16_u8_dda.asm` 800 bytes; each
includes the 32-byte Euclidean table. State: 160 or 248 bytes.

## Measured against the normalize pipeline

`benchmark.py` runs both kernels and a normalize-based mover
(`baseline_normalize.asm`, linked against the V1 build) in the repository's
cycle-counting 6502 emulator. It uses 408 random moves at six speeds from 0.5
to 4 px/frame and checks every frame of every move. Mean cycles per move;
standalone kernels have no JMP slot:

| 256×200, 8-bit x | Setup | Per frame | Total | Arrival |
|---|---:|---:|---:|---|
| normalize + scale + ISQRT/divide arrival | 4,412 | 81.7 | 12,356 | snaps from ≤3.4 px; 78 frames wrapped past the screen edge |
| `seek8`, same (Euclidean) speed | 741 | 84.0 | 8,940 | exact |
| `seek8`, integer speed | 304 | 68.0 | 4,222 | exact |
| `seek8` at 1 px/frame (normalize: 4,286 / 81.7 / 14,306) | 273 | 63.0 | 7,210 | exact |

| 320×200, 16-bit x | Setup | Per frame | Total | Arrival |
|---|---:|---:|---:|---|
| normalize + scale + ISQRT/divide arrival | 4,412 | 93.7 | 14,741 | snaps from ≤4.0 px |
| `seek16`, same (Euclidean) speed | 914 | 115.1 | 13,639 | exact |
| `seek16`, integer speed | 449 | 100.7 | 7,068 | exact |
| `seek16` at 1 px/frame (normalize: 4,285 / 93.7 / 17,314) | 375 | 95.2 | 12,348 | exact |

The seek path stays within 0.5 px of the true line. The normalize path drifts
up to 3.6 px. Reproduce with:

```sh
make reference                                          # V1 PRG for the baseline
python3 routines/movement/benchmark.py --variant u8     # -> validation/movement/SEEK8_DDA_BENCHMARK.json
python3 routines/movement/benchmark.py --variant u16    # -> validation/movement/SEEK_DDA_BENCHMARK.json
```

Each run also steps eight objects at once, round-robin, and checks every
frame of those moves too.

## Files

| File | Purpose |
|---|---|
| `seek_u8_u8_dda.asm`, `seek_u16_u8_dda.asm` | generated standalone kernels |
| `seek_model.py` | Python Bresenham reference model and emulator loader |
| `baseline_normalize.asm` | the normalize-based baseline |
| `benchmark.py` | validation and benchmark |
