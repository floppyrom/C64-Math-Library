# V5 Hybrid Low-ZP — stock C64 game/demo profile

V5 keeps the **V1 31-byte normal zero-page footprint** while selectively importing V2 implementations that are faster without requiring additional ZP.

The stable **45-entry public API is unchanged**. `MATH_INIT` remains optional, as in V1.

## Imported V2 paths

- `MATH_UDIV16`
- `MATH_UDIV24`
- `MATH_UDIV32_16`
- `MATH_UMOD8`
- `MATH_UMOD16`, `MATH_UMOD24`, `MATH_UMOD32_16` through their normal UDIV aliases
- `MATH_COS8`
- `MATH_SINCOS8`

Everything else remains V1.

The imported division paths also accelerate V1 helpers that call those stable entries, notably `MATH_UDIV16_SHL8` and `MATH_URECIP16_Q16`, although the published direct-import parity guarantees apply to the entries listed above.

## Memory requirement

Reference build:

```text
normal ZP      $02-$20   31 bytes
hybrid code    $A000-$B1FF   4608 bytes
```

`$A000-$BFFF` is RAM under BASIC ROM. The reference build therefore requires BASIC ROM to be banked out while an imported V5 path executes. In most machine-code games/demos BASIC is already disabled. If that does not fit your memory map, relocate `HYBRID_CODE` and rebuild.

The PRG file is the **same length as V1** because V5 fills a hole already inside the V1 PRG's load span; it does, however, consume 4608 bytes of RAM that V1 leaves unused.

## Build

```sh
python3 tools/build_hybrid.py --config-kind reference
python3 tools/build_hybrid.py --config-kind alternate
python3 tools/validate_hybrid.py
python3 tools/test_hybrid_config.py
python3 tools/verify_hybrid_deterministic.py
```

For a custom map, copy `relocatable_source/v5_hybrid_lowzp/math_config_reference.inc`, change `HYBRID_CODE` and the normal V1 map symbols, then pass it with `--config`.

## Validation

The shipped validation includes:

- 45/45 stable entries on the reference map: 4,172 machine calls;
- 45/45 stable entries on the alternate map: 4,172 machine calls;
- 78,710 direct-import correctness/parity cases;
- exhaustive 65,536-case `UMOD8` correctness;
- exhaustive 256-phase `COS8` and `SINCOS8` checks;
- thousands of 16/24/32-bit division cases with exact V2 cycle-vector parity;
- dynamic reference/alternate ZP confinement checks: all 225 bytes outside the 31-byte window unchanged;
- mixed V1/V2 state stress;
- 2,000 reference/alternate cold-load calls without `MATH_INIT`, covering imported paths and an untouched V1 safe routine;
- deterministic rebuild identity on both maps;
- rejected invalid hybrid maps for overlap, I/O, alignment and overflow.

See `../docs/HYBRID_PROFILE.md` and `../validation/hybrid/`.
