# Stock-C64 user-configurable builder: release acceptance

**Release target:** users choose the mathematical operations needed by their
own program, resource limits and optimization goal. The operation-first
installer builds only the selected independently linkable operations and
publishes correct physical memory usage, source lineage and public exports.

These acceptance checks are **about the user's library**, not a demonstration
that a particular SID player, game, REU driver or VIC-II effect fits one PAL
frame. All experimental application workloads are optional.

## Acceptance scenarios

Run with:

```sh
python3 -m unittest discover -s tools -p 'test_user_builder_release.py' -v
```


| User need | Requested operations | Optimization | ZP limit | Total RAM limit |
|---|---|---|---|---|
| General-purpose calculation | UMUL16, UDIV16, ISQRT16 | balanced | 8 B | 4096 B |
| Tight code+data | UMUL8, UDIV16 | size | 0 B | 4096 B |
| No available zero page | UMUL16, ISQRT16 | zp | 0 B | 4096 B |
| 1000:1 mixed workload | UMUL8, UMUL16 | speed | 4 B | 1400 B |
| Game memory reserved | UMUL8, UDIV16 | size + explicit pin | 0 B | 4096 B |

For each scenario, the acceptance test runs the **real
`tools/configure_math.py` CLI**, writes an editable JSON config, emits
`math_selective.prg` and `math_api.inc`, and compares the
SHA-256 identity, exports, selected variants, physical RAM/ZP consumption
and memory map with a second byte-for-byte rebuild by the original
`tools/math_builder.py --config ... --build` command.

Speed mode requires explicit per-operation positive workload call counts
and authentic same-input CPU-model cycle evidence; no assumptions are
made about the user's game loop or hardware-exact native PAL latency.
The custom memory case reserves game code at `$8000..$9FFF` and
low zero page for the IRQ, relocates the library code to `$7123`
and its I/O to `$C040`, and pins one certified UMUL8 variant.
A deliberate code-reservation collision must fail without leaving any
configuration or partial binary.

## Exit criteria

1. All 56 public APIs are independently linkable (already merged) and
   have individually qualified source alternatives where published.
2. The guided interactive setup and CLI produce user-owned JSON + a
   real binary, include and manifest. Normal installation never asks for
   V1–V5 as a package choice.
3. All four user objectives and a pinned custom memory map rebuild
   reproducibly; impossible budgets or collisions fail closed.
4. The existing complete native VICE all-56 image and historical
   reference/REU checksum regressions remain green.
5. A release notes summary makes clear that stock-C64 is the only
   current selective hardware backend; drive-side and REU Turbo/QS16
   services remain separate historical compatibility exports.

**Preservation:** all V1–V5 profiles, source snapshots, reference PRGs,
V3/V4 REU compatibility images, source hashes and specialized research
remain untouched by these release acceptance tests.

The tests prove that the user-driven configuration and produced binary are
reproducible and satisfy declared budgets. They do not prove that the
selected source is the fastest imaginable source for future algorithms, or
that CPU-model weighted cycles are exact hardware-frame deadlines.
