# SMUL32 compact126 record

`mul_s32_s32_s64_compact126.asm` is the current native signed 32×32 → 64 speed/stack Pareto point in the repository.

## Validated result

| Corpus | Cases | Errors | Mean | Min | Max |
|---|---:|---:|---:|---:|---:|
| C0FFEE deterministic native corpus | 100,000 | 0 | **646.354530** | 548 | 757 |
| independent seed 0x5EED1234 | 100,000 | 0 | **646.281100** | 548 | 767 |
| structured signed edge suite | 1,849 | 0 | 614.909681 | 548 | 769 |

The primary mean is a narrow measured improvement over the reported Repose 646.37 result on this benchmark basis. Treat it as a record point rather than a large performance separation.

## Resource contract

The standalone kernel owns **136 ZP bytes**, reserves **126 bytes of page $01** (`$0100-$017d`) as persistent executable storage, uses **302 bytes of ordinary RAM code**, and shares **2,044 bytes of quarter-square tables**. Under the repository's standalone accounting convention, `code_bytes` is **428** (302 ordinary-RAM executable bytes + 126 page-$01 executable bytes), while executable ZP remains counted inside the 136-byte ZP claim; total occupied bytes are therefore **2,608**. Its native ABI prebinds the four X bytes into SMC operands and passes Y as three memory bytes plus CPU Y; caller input stores are excluded from the published timing.

## Fixed-profile applicability

This kernel is intentionally **not selected as the stable `MATH_SMUL32` implementation** in V1–V5.

| Profile | Applicability | Reason |
|---|---|---|
| V1 Balanced | no | the fixed profile promises a 31-byte normal-ZP footprint |
| V2 Pareto-Fast | opt-in only | its `$80-$F3` executable-ZP window is already occupied by the faster native SMUL16 kernel |
| V3 REU 512K | opt-in / overlay only | same executable-ZP conflict as V2; Turbo ownership rules can host alternate overlays, but not simultaneously |
| V4 REU 16M | opt-in / overlay only | same executable-ZP conflict as V2/V3 |
| V5 Hybrid Low-ZP | no | preserves the V1 31-byte normal-ZP contract |

A direct standard-ABI transplant was also tested: marshalling ordinary `MATH_X/MATH_Y` inputs into the compact kernel removes the native-ABI advantage and measures about **757.7 cycles** on the 10,000-pair probe. It remains slower than every fixed-profile public SMUL32 path; current V2/V3/V4 means are **712.623495 / 713.107929 / 713.133250 cycles**, while V1/V5 retain their low-ZP public implementations. Compact126 therefore remains an opt-in ownership mode rather than a fixed-profile substitution.

## Profile-local exposure

The exact record source is also exposed in the fixed-profile trees where an **exclusive overlay** is technically viable:

- **V2:** [`v2_pareto_fast/optional/smul32_compact126/`](../v2_pareto_fast/optional/smul32_compact126/) — manual save/restore mode.
- **V3:** [`v3_reu_512k/optional/smul32_compact126/`](../v3_reu_512k/optional/smul32_compact126/) — Turbo-style exclusive host.
- **V4:** [`v4_reu_16m/optional/smul32_compact126/`](../v4_reu_16m/optional/smul32_compact126/) — Turbo-style exclusive host.

These aliases include the exact validated canonical source; they do **not** replace the resident `MATH_SMUL32`. The overlay owns ZP `$0A-$1F` and `$8E-$FF`, page $01 `$0100-$017D`, and ordinary RAM `$1200-$12F2` plus `$1300-$133A`. V2–V4 must preserve and restore those ranges around the exclusive interval. The quarter-square data at `$7000/$7200/$7400/$7600` can be shared.

See [`SMUL32_COMPACT126_PROFILE_FIT.csv`](SMUL32_COMPACT126_PROFILE_FIT.csv) for the machine-readable compatibility matrix.

## What made 126 stack bytes viable

The compact summation uses X to encode the first deferred column-2 carry, reducing page-$01 code. The timing lost to that compact encoding is recovered in the NN quadrant: after negating x0, the common x0≠0 case has already propagated the borrow, so the upper bytes of -X are simply `~x1`, `~x2`, and `~x3`. Only the rare x0=0 case uses the cold SBC propagation helper.

The two independent 100,000-pair records and the edge record are under `validation/records/`.

## Low-resource counterpart

For applications that cannot reserve page $01 or 136 ZP bytes, [`fast31_native_v2`](SMUL32_FAST31_V2.md) is the current **31-ZP / stack-free** signed 32×32 record at **692.825100 cycles**.
