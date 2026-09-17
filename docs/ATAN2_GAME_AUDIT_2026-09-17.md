# ATAN2 optimization and game-source audit — 2026-09-17

## Release result

`MATH_ATAN2_8` keeps the stable public contract:

```text
x0 = dx, signed 8-bit
y0 = dy, signed 8-bit
z0 = 8-bit phase
$00 = +X, $40 = +Y, $80 = -X, $C0 = -Y
(0,0) -> 0
```

The stock-C64 implementations use a compressed signed-magnitude logarithm and generated final-angle tables. All 65,536 signed-byte input vectors are checked against rounded mathematical `atan2`; V1–V3/V5 have maximum error one phase unit.

| Profile | Mean cycles | Min | Max | ATAN2 tables | Extra ATAN2 ZP | Accuracy |
|---|---:|---:|---:|---:|---:|---|
| V1 Balanced | **50.441345** | 30 | 53 | 512 B | 0 | <=1 phase unit |
| V2 Pareto-Fast | **46.953064** | 30 | 48 | 1280 B | 0 | <=1 phase unit |
| V3 REU 512K | **46.953064** | 30 | 48 | 1280 B | 0 | <=1 phase unit |
| V4 REU 16M | **48.000000** | 48 | 48 | 64 KiB REU exact plane | 0 | exact |
| V5 Hybrid Low-ZP | **46.953064** | 30 | 48 | V1 base pages + 768 B fast upgrade | 0 | <=1 phase unit |

The V2/V3 fast tier resolves the quadrant in the table selection rather than performing a shared post-lookup correction. V5 imports that fast body but remaps the third added page away from V1-owned data. The reference V2/V3 pages are `$5500`, `$5F00`, and `$4700`; V5 keeps `$5500`/`$5F00` and remaps the donor `$4700` page to its free `$5700` page.

## Why keep more than one stock-C64 point?

The fast tier saves about 3.49 cycles on average versus the compact V1 implementation but spends three more 256-byte pages. That is a real game integration trade-off, so the release keeps both points:

- V1: compact, zero-ZP, 512-byte table footprint;
- V2/V3/V5: speed-first, zero-ZP, 1280-byte table footprint;
- V4: exact REU plane when 16 MiB REU storage is already part of the target.

The Custom Pareto Builder exposes the fast upgrade separately as `atan2_fast` (0 ZP, 768 B extra private RAM) rather than hiding it inside the other V5 zero-ZP imports.

## Real-game audit principle

A faster general routine is not automatically a better game implementation. This audit asks whether each game actually has a dynamic vector-to-angle problem. If an engine already owns the angle directly or deliberately quantizes direction, retaining that representation is cheaper than calling `atan2`.

### Steel Ranger

Source checked: `cadaver/steelranger-demo`, tree/commit `fa99196cb94be80df12bd295adcce7567e860e44`.

The current weapon code defines five vertical aiming classes:

```text
AIM_UP = 0
AIM_DIAGONALUP = 1
AIM_HORIZONTAL = 2
AIM_DIAGONALDOWN = 3
AIM_DOWN = 4
AIM_NUMDIRS = 5
```

`weapon.s` turns that discrete direction into projectile X/Y speeds through direction/speed tables, while `bullet.s` carries the corresponding direction frame. That is exactly the kind of game-specific representation the library should **not** replace merely because a fast general ATAN2 now exists.

**Audit result:** keep the existing five-way lookup for the shipped player firing path. `MATH_ATAN2_8` becomes interesting only for a new mechanic that needs continuous runtime direction from a live displacement vector, for example free-angle homing, steering, or an enemy that must face an arbitrary target rather than one of the existing discrete aim classes.

### Wolf64

Source checked: `Kweepa/Wolf64`, main tree `d606a14bbfb9fb17059c24824e0d921f23fd6860`.

Wolf64 already uses an 8-bit angular state: `playera` is documented as a `0..255` angle. The DDA computes each ray by adding a per-column angle offset to `playera`. Enemy facing is intentionally quantized to eight directions through `enemy_face_ang`:

```text
64, 32, 0, 224, 192, 160, 128, 96
```

The source therefore already has the right representation for its hot raycaster path: angle in, trig/secant lookup out. Reconstructing that angle from a vector each frame would add work rather than remove it.

**Audit result:** do not put ATAN2 in the raycaster or replace the current 8-way facing table. The library routine is directly compatible with the engine's 8-bit phase scale and is useful if future AI gains free-angle steering or must convert a freshly computed target displacement into a non-quantized facing.

### Quake64

Source checked: `Kweepa/Quake64`, main tree `143daa59be6f2073c6f125e6c6d5accab231fafd`.

Quake64 likewise carries orientation directly: `ent_rot` is an 8-bit facing yaw (`0..255`, documented as `0=+Z`). Rendering combines camera yaw and entity yaw directly and then uses fast multiply/trig machinery. The active math source is dominated by signed multiply, log/antilog perspective and transform helpers; the current rendering path has no need to recover yaw with a general ATAN2.

**Audit result:** retain direct yaw state in rendering. ATAN2 is a candidate for a dynamic `face-target`/steering operation where AI starts from `(dx,dz)` and needs yaw. Because the library convention is `$00=+X` while Quake64 documents yaw zero as `+Z`, integration should swap/negate the horizontal components or add a quarter-turn as appropriate for the engine's handedness, and verify the four cardinal vectors before use.

## Practical integration rule

Use `MATH_ATAN2_8` when all of the following are true:

1. the direction is genuinely dynamic at runtime;
2. the inputs naturally exist as signed byte deltas or can be cheaply scaled to them;
3. downstream code benefits from a full 8-bit phase;
4. a smaller discrete-direction table or an already-maintained angle state is not sufficient.

Prefer the game's existing representation when direction is already stored as an angle, when only 4/5/8/16 directions are needed, or when the candidate vectors are static enough to precompute.

## Validation hooks

- `tools/upgrade_atan2.py` builds and exhaustively checks the V1–V3 stock implementations.
- `validation/ATAN2_UPGRADE_VALIDATION.json` records all 65,536-vector timing/error distributions.
- `tools/validate_hybrid.py` exhaustively checks V5 result **and cycle-vector** parity against V2 and independently verifies the <=1-unit error bound.
- `tools/validate_pareto.py` includes exhaustive ATAN2 V2-parity checking in the deep all-pack configuration.

The result is therefore both a faster general-purpose primitive and a deliberately scoped one: it is available when a game really needs vector-to-angle conversion, without implying that existing game-specific direction tricks should be replaced.
