# First historical speed parity replay: whole-public-call UMUL8

## What is now measured

The comparison runs **the checksum-locked original V1 resident PRG** (not a
reconstruction of the V1 source) against three **source-linked operation-first
UMUL8** implementations on exactly the same 1,000 seeded, edge and uniform
8-bit operand pairs. All calls execute the real public entry through RTS
under the same in-repository NMOS 6502 CPU model, with an initialized V1
resident. Every call checks the full 16-bit product, Carry clear, preserved
X/Y, stable stack, and a shared output/carry digest.

The selective implementations are tested at two distinct code, public I/O
and ZP placements. Results report mean, p95, min and max **full-call**
cycles, per-variant source data and each actual placement.

```sh
python3 tools/benchmark_historical_selective_umul8.py \
  --out build/matched-umul8/historical-v1-versus-selective.json
```


This is the first reproducible historical resident versus operation-first
**identical-input** CPU-model public-ABI baseline. It is *not* a proof that
the fastest V1–V5 kernel is now installed for every operation: in
particular, V3's REU-backed UMUL8 estimates cannot be compared directly
against ordinary stock-C64 timings without hardware and transport parity.
The remaining 55 operations and any native-VICE performance claims remain
unqualified by this experiment.

**Next:** Run the common historical DIV/MOD corpus against actual selective
callers, extend full-ABI parity to 16/24/32-bit operations, and benchmark
common worst-case frames in native VICE. Keep memory-saving Pareto options
even when they cost more cycles.

This experiment does not alter installer defaults, V1–V5 reference
binaries, REU compatibility images or the validated math kernels.
