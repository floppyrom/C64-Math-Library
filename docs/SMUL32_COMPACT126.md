# SMUL32 compact126

`mul_s32_s32_s64_compact126` is the current source-backed signed 32x32 -> 64 speed/stack record point in this repository.

## Measured point

| Corpus | Cases | Errors | Mean | Min | Max |
|---|---:|---:|---:|---:|---:|
| Random(0xC0FFEE) | 100,000 | 0 | **646.354530** | 548 | 757 |
| Random(0x5EED1234) | 100,000 | 0 | **646.281100** | 548 | 767 |
| Structured edges | 1,849 | 0 | 614.909681 | 548 | 769 |

The primary-corpus result is a narrow measured win over the reported 646.37-cycle Repose point. It should be described as a narrow timing lead, not a large separation.

## Resource contract

- 136 bytes of zero page: `$0A-$1F` and `$8E-$FF`.
- 126 bytes of persistent page-$01 executable storage: `$0100-$017D`.
- 302 bytes ordinary-RAM executable code.
- 2,044 bytes of quarter-square data.
- NMOS 6502/6510, binary mode, self-modifying and non-reentrant.

The stack-page reservation is a hard ownership requirement. While the kernel is installed, normal hardware-stack use must not descend into `$0100-$017D`, and IRQ/NMI/caller nesting must respect the remaining stack headroom.

## Fixed-profile compatibility

| Profile | Select as normal resident `MATH_SMUL32`? | Reason |
|---|---|---|
| V1 Balanced | No | The normal profile contract is 31 ZP bytes. |
| V2 Pareto-Fast | No | The aggregate ZP budget is large enough, but `$80-$F3` is already the MATH_INIT-installed native SMUL16 executable-ZP image. A permanent compact126 install would break SMUL16. |
| V3 REU 512K | **Optional exclusive overlay** | The profile already has explicit Turbo ownership semantics and the same quarter-square table geometry. The compact126 overlay must be installed/restored as an exclusive mode; it is not a drop-in resident replacement. |
| V4 REU 16M | **Optional exclusive overlay** | Same as V3. |
| V5 Hybrid Low-ZP | No | The normal profile contract is 31 ZP bytes. |

This distinction is intentional. The fixed `PUBLIC_PROFILE_RESULTS.csv` rows continue to describe the always-resident 54-entry API and therefore are not replaced with the standalone 646-cycle number.

## V3/V4 profile exposure

Profile-local optional entry points are published under:

- `v3_reu_512k/optional/smul32_compact126/`
- `v4_reu_16m/optional/smul32_compact126/`

They point at the exact validated source in `routines/multiply/mul_s32_s32_s64_compact126.asm`. The existing resident tables at `$7000/$7200/$7400/$7600` are algebraically identical to the record-family planes, so an integrated loader may reuse them rather than store a second 2,044-byte table set.

The optional mode is deliberately not wired into the existing unsigned Turbo32 BEGIN/CALL/END surface in this change. Doing that correctly requires the lifecycle to save and restore not only executable ZP but also the 126-byte stack-page interval (and any temporary ordinary-RAM overlay chosen by the integrator). Treating it as an ordinary fixed-profile call would hide that ownership change.

## Why the result improved

The 126-byte stack point uses a compact X-state column-2/3 carry encoding. The timing recovered in the negative/negative quadrant comes from observing that, after negating the low byte, the common original-`x0 != 0` case already propagated the borrow: the upper bytes of `-X` are simply `~x1, ~x2, ~x3`. Only the rare original-`x0 == 0` case goes through the cold SBC propagation helper.

## Evidence

Machine-readable validation: `validation/records/SMUL32_COMPACT126_2026-10-05.json`.

The standalone source retains the record benchmark ABI so its timing remains directly reproducible. Profile public-call marshalling is intentionally accounted separately from this record number.
