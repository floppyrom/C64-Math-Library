# Machine-audited profile-retirement evidence gate

The operation-first **stock C64** builder already links 56/56 stable public
operations and declares public-call CPU-model speed evidence for all 56.
This is not equivalent to proof that every historical V1–V5 fastest donor
has been transplanted or that V3/V4 REU services can disappear.

Run:

```sh
python3 tools/profile_retirement_audit.py --out build/retirement-evidence.json
python3 tools/profile_retirement_audit.py --require-retirement-ready
```

The first command generates a machine-readable source/ABI/resource catalog.
The second deliberately exits **2** while the cutover is unqualified. No
workflow should automatically delete V1–V5 release artifacts or advertise
full historical performance/hardware parity.

## Current strictly separate scopes

- **56 stock-C64 APIs**: 41 have two or more selectable source variants,
  15 retain one exact historical source. Stock linker resource constraints,
  shared producer, scratch/ZP/state and writable-code flags are inventoried.
  A single original-source variant does not imply a slower routine.
- **13 stock non-operation symbols**: MATH_INIT, seven shared I/O aliases
  (X/Y/Z/N/D/Q/R), and five SEEK8/SEEK16 position-field aliases. These
  are public ABI symbols but **not** standalone callable math operations or
  REU backend services; the audit protects them separately on all V1–V5.
- **Nine extra REU lifecycle exports**: V3/V4 each provide six
  `MATH_REU_UMUL16/UMUL32_{BEGIN,CALL,END}` entry points; V4 additionally
  provides three `MATH_REU_QS16_{BEGIN,CALL,END}` entries. Their public
  symbol presence and historical ownership are independently checked
  against the actual V3/V4 generated `math_api.inc` files.
- **Resource protection**: the legacy Turbo16 direct-output overlay
  owns 122 ZP bytes while active, Turbo32 owns 135, and V4 QS16 owns 16.
  These are mode-exclusive lifetimes with BEGIN→CALL→END, not free
  zero-page storage for concurrent math.
- **Planned drive backends**: 1541/1571/1581 have no selectable executable
  binary backend. Drive support is separate from stock C64 parity and
  must not be inferred from planning-only targets.

The report counts source *declarations*, historical resident records and
standalone alternatives. It does not execute new matched-input timing or
independently prove fastest donors; the 56 full-public source-cycle models
were already qualified via #327 and native VICE. Use the
[full parity policy](PERFORMANCE_PARITY_GATE.md) and
[REU family hardware review](ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md)
for actual evidence.

## Gates still blocking profile retirement

1. Per-operation historical V1–V5/OptiSearch fastest-variant parity on
   identical complete public-call corpora, mean/p95/maximum and frame tail.
2. Native 50Hz application-level worst-frame proof with VIC-II, IRQ/SID,
   bus contention, REU DMA and init amortization accounted for when relevant.
3. A qualified separate REU/Turbo/QS16 service implementation or a
   permanently maintained, obvious V3/V4 compatibility package.

The report will fail if a profile export disappears, source is unlinked,
or an unqualified stock speed model is removed. It does **not** use the
false implication that simply obtaining 56/56 linkable APIs makes all
historical profiles safely obsolete.
