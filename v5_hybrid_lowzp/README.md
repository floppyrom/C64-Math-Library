# V5 Hybrid Low-ZP — stock C64 game/demo profile

V5 keeps the **V1 31-byte normal zero-page footprint** while selectively importing V2 implementations that are faster without requiring additional ZP.

The stable **46-entry public API is unchanged**. `MATH_INIT` remains optional, as in V1.

## Refreshed selected paths

V5 now combines V1’s 31-byte normal-ZP contract with the current division refresh. Selected/repacked paths include:

- direct CPU `MATH_UDIV8`;
- refreshed `MATH_UDIV16` / `MATH_UDIV24`;
- V2-selected `MATH_UDIV32_16`;
- compatible `UMOD8/16/24/32_16` paths;
- direct-output native `MATH_SDIV16` / `MATH_SDIV24` and their `SMOD` aliases;
- refreshed low-ZP signed 32/16 and signed 32/32 paths;
- `MATH_COS8`, `MATH_SINCOS8`, and `MATH_ATAN2_8`.

`MATH_UDIV16_SHL8`, `MATH_SDIV16_SHL8`, and `MATH_URECIP16_Q16` inherit the selected inner division paths. The complete selection is validated as one fixed V5 image; there is no runtime dispatcher.

## Memory requirement

Reference build:

```text
normal ZP      $02-$20        31 bytes
hybrid code    $A000-$BDFF    7680 bytes
ATAN2 pages    $6D00-$70FF          1024 bytes total
```

The refresh also places selected signed-division private islands in otherwise free profile regions. The exact current private-RAM increase versus V1, measured by the Pareto endpoint that reproduces V5 byte-for-byte, is **9,633 bytes**. `$A000-$BFFF` is RAM under BASIC ROM, so the CPU must see RAM while executing code in the reference hybrid block. If that does not fit your map, relocate `HYBRID_CODE` and rebuild.

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

- 46/46 stable entries on the reference map: 4,589 machine calls;
- 46/46 stable entries on the alternate map: 4,589 machine calls;
- **144,246 direct-import correctness/parity cases**, including exhaustive 65,536-vector `ATAN2_8` result/cycle parity and <=1 phase-unit error;
- exhaustive 65,536-case `UMOD8` correctness;
- exhaustive 256-phase `COS8` and `SINCOS8` checks;
- exhaustive 65,536-vector `ATAN2_8` result/cycle parity with V2 and maximum error <=1 phase unit;
- thousands of 16/24/32-bit division cases with exact V2 cycle-vector parity;
- dynamic reference/alternate ZP confinement checks: all 225 bytes outside the 31-byte window unchanged;
- mixed V1/V2 state stress;
- 2,000 reference/alternate cold-load calls without `MATH_INIT`, covering imported paths and an untouched V1 safe routine;
- deterministic rebuild identity on both maps;
- rejected invalid hybrid maps for overlap, I/O, alignment and overflow.

See `../docs/HYBRID_PROFILE.md` and `../validation/hybrid/`.
