# Public API compatibility — operation-first stock C64

**For new projects, use the operation-first builder, not V1–V5.** Choose
from 56 individually linkable public operations; only selected callable
entries and shared physical dependencies are emitted. Addresses are **not**
fixed historic resident addresses. Always consume the generated
`math_api.inc` and `selective_manifest.json` to obtain the
actual public aliases, operand I/O, initializer and output/Carry contracts,
source variants and relocations.

Normal installation: `make builder-setup`. For source/budget
configuration see [the installer guide](OPERATION_FIRST_USER_SETUP.md) and
[release qualification](BUILDER_RELEASE_ACCEPTANCE.md).

A selected operation's calling convention must match its documented
source-qualified public ABI. Physical shared code/tables or source-aliasing
may change across configurations. The math library is **not reentrant**.

## Historical resident API and compatibility notes (archived)

The following material documents the frozen V1–V5 common API, historical
initialization requirements, fixed-address symbol layouts, V3/V4 REU Turbo
and QS16 lifecycle services and the older Custom Pareto builds. It
is **not** guidance to select a historical resident profile for a new
stock-C64 project. V3/V4 stateful hardware extensions remain available
only through a [separate compatible resident package](REU_COMPAT_EXPORT.md),
which must not be mixed with the selective image.

---

The release retains the authoritative **56-entry stable signed/unsigned/game-math API** in all five resident profiles **and in all generated Custom Pareto builds**. `PUBLIC_API_COMPLETE.csv` remains authoritative for that common surface. Normal operations use the configured public memory geometry and preserve the documented input semantics.

`MATH_VEC2_NORMALIZE_Q8_8` is part of the common surface in every profile at the generated `REG_GAME_API+$39` address. Its signed Q8.8 -> signed Q1.15 contract, zero-vector Carry convention and precision bounds are identical across profiles.

V2–V4 require `MATH_INIT`; V1 and V5 ordinary safe entries retain the optional-init contract. A generated Pareto build states its exact requirement in `selection_manifest.json` / `MATH_PROFILE_INIT_REQUIRED`; `--init-policy optional` preserves the V1/V5-style optional-init contract. V5 preserves the same 46 names/ABI while replacing a certified subset of V1 implementations with faster V2-derived paths. `MATH_UMOD32_32` and `MATH_SMOD32_32` remain ABI aliases because their division kernels already produce quotient and remainder.

## REU Turbo extension

V3/V4 additionally expose six stateful batch lifecycle entries:

- `MATH_REU_UMUL16_BEGIN`
- `MATH_REU_UMUL16`
- `MATH_REU_UMUL16_END`
- `MATH_REU_UMUL32_BEGIN`
- `MATH_REU_UMUL32`
- `MATH_REU_UMUL32_END`

These are intentionally documented separately from the 54 stable calls because `BEGIN` installs an executable ZP overlay and temporarily owns the configured Turbo ZP range until `END`. They are now **source/build-time relocatable** but remain stateful/non-composable while active. No normal/game-math call is permitted between Turbo BEGIN and END.

Generated `math_api.inc` files for V3/V4 contain the six Turbo entry symbols plus the configured Turbo ZP/bank symbols. See `TURBO_API.csv` and `TURBO_RELOCATION.md`.

## V5 Hybrid Low-ZP

V5 is not a second API and does not load V1 and V2 side-by-side. It is one V1-based resident image with the same 56-entry surface. The hybrid builder source-builds both donor profiles, relocates only the certified V2 kernels, and patches the existing V1 public wrapper bodies in place. No runtime profile switch or dispatcher is involved.

The reference V5 normal ZP contract remains `$02-$20` (31 bytes). Sequential calls and repeated game/demo loops are supported; the library remains non-reentrant exactly as the other profiles are.
## Custom Pareto builds

The Custom Pareto Builder does not add API entries. It replaces only certified implementation paths behind the same public names, using one generated memory map and one public I/O block. `selection_manifest.json` is the resource/provenance contract for that build: selected packs, exact ZP ranges, exact private RAM ranges, initialization policy and binary hash.

A 31-ZP/zero-extra-RAM generated build is byte-identical to V1; a 31-ZP optional-init generated build is byte-identical to V5; a 221-ZP build selects complete V2.

