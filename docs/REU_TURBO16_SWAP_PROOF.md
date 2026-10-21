# Turbo16 source-assembled REU SWAP controller — CPU-model experiment

This is **not native hardware qualification** or a selectable REU backend in the
56-operation installer. It is the next engineering experiment following the
source-assembled Turbo16 fragments merged in PR #377.

The assembled 6510 controller executes the REU command `$92` (C64/REU SWAP),
to exchange exactly 122 bytes between the program's zero page and a REU bank.

**Intended lifecycle:** BEGIN exchanges executable code from the REU into
zero page while storing all the original caller ZP bytes in REU. CALL
executes the pre-qualified public Turbo16 binder. END exchanges the two
regions back again. Repeated batches must restore the original caller's
entire 122-byte ZP state and original REU overlay.

The new sources are:

- `relocatable_source/turbo/turbo16_swap_controller.asm` — guarded BEGIN/CALL/END and SWAP transfer.
- `tools/reu_turbo16_swap_experiment.py` — physical map validation, source assembly and test-only REU CPU-model execution.
- `tools/test_reu_turbo16_swap_experiment.py` — two batches with input/product/Carry/stack and exact overlay restoration checks.

For test inputs the four 512-byte quarter-square tables are read from the
SHA256-locked **original V3 PRG**, rather than independently generated.
The experiment models 512-KiB and 16-MiB REU banks and checks two physical
layouts. It must reject incompatible resource reservations before assembly.

Run:

```sh
python3 -m unittest discover -s tools -p 'test_reu_turbo16_swap_experiment.py' -v
python3 tools/reu_turbo16_swap_experiment.py --out build/turbo16-swap-proof
```

**Not yet delivered:** independent four-table construction, a real linked
PRG/REU pair, certified error handling for missing REU hardware, native
VICE REU DMA/interrupt/bus validation, lifetime-safe global ZP allocation,
and public installer selection. No existing REU compatibility resident,
kernel or installer default has been changed. Never install this test
controller as a production math module until those requirements are met.
