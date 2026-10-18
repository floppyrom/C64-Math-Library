# Frame-cycle arithmetic trace scorer (research gate)

The operation-first builder currently minimizes weighted public-call **mean**
cycles for source-qualified variants. That does not by itself guarantee that a
C64 demonstration meets its **busiest-frame cycle budget**.

## Usage

    python3 tools/frame_cycle_budget.py --baseline before.csv --frame-count 100 --budget 6000 --out frame_report.json
    python3 tools/frame_cycle_budget.py --baseline before.csv --candidate after.csv --frame-count 100 --budget 6000

CSV header (one row per actual measured public call):

    frame,call,operation,input_id,cycles,variant,measurement_basis,placement

The zero-based frame and call-ordinal identify the position in the frame.
The operation is the public MATH_* entry; input_id must identify the entire
argument tuple, including relevant processor state or initialized state.
Prefer SHA-256 of the canonical serialized input. The scorer can enforce
matching IDs but cannot prove the exporter hashed the inputs correctly.

Cycles must be **measured for that individual call, entry through RTS**.
Historical-profile means are not valid observations. Six cycles for each
caller JSR are included by default; choose --jsr-cycles 0 to omit them.

The variant names the linked kernel, and the source SHA and full build manifest
must be archived alongside the trace. A file cannot mix variants for the same
operation. The measurement_basis names the clock methodology; a Mini6502
CPU-model cycle count must **not** be compared against a native VICE cycle
count. The placement records code and public I/O locations, for example
$8000/$C000. A pair must have identical placement; repeat separately at a
second relocation.

The scorer reports total, mean, p95, and peak per-frame math cycles;
over-budget frame counts, math-only peak headroom and each operation's
contribution to the busiest frame. --frame-count includes zero-math frames.
Paired comparison requires the exact same set of frames, call ordinals,
operations and hashed arguments. It rejects incompatible timing bases,
placements and unpaired workloads.

Nominal PAL 6510 frame total is **19,656 cycles** (312 x 63). Set --budget
to the application's **arithmetic slice**, not the full frame, if other work
already consumes cycles. This is **not** a hardware frame guarantee: the
report excludes VIC bus contention, IRQs, input stores, sprite multiplexing,
music, REU DMA and the rest of application execution. Native VICE recorded
instruction cycles are also not externally measured elapsed time.

## Qualification boundary and follow-up

This utility **scores imported measurements**. It does not itself execute VICE
or supply a faster 6502 kernel. The five regression tests use hypothetical
fixture counts and must not be advertised as benchmark gains. Integrate a
producer that captures actual per-call cycle traces from the linked binary,
preserving the source, ABI, corpus and memory-map provenance.

Prioritize signed 24/32-bit DIV/MOD and signed 32-bit multiply/SHR16, including
divisor magnitudes, zero, sign extremes, and clustered busiest-frame calls.
Compare historical V1-V5 and OptiSearch donors through identical operands,
public-call ABI and placement. Keep small/low-ZP Pareto kernels even if they
are slower. The main builder does not yet optimize the peak-frame objective:
measured matched input traces are a prerequisite before promoting that
selection strategy.


## Built-in signed-wide trace producer

Use the deterministic **synthetic stress** workload generator to record
real CPU-model cycles from the 56-operation builder's linked source image:

    python3 tools/export_wide_frame_trace.py --frames 40 --code-base 0x8000 --io-base 0xc000 --out build/wide_8000.csv
    python3 tools/export_wide_frame_trace.py --frames 40 --code-base 0x7123 --io-base 0xc040 --out build/wide_7123.csv
    python3 tools/frame_cycle_budget.py --baseline build/wide_8000.csv --frame-count 40

The generator exercises six signed-wide public entries: SMUL32,
SMUL32_SHR16, SDIV32_16, SMOD32_16, SDIV32_32 and SMOD32_32. It mixes
divisor-zero/edge cases, full-width signed values and sparse/clustered
calls at deterministic frames. Each call is checked against Python's exact
signed mathematical reference, checks carry and stack semantics, and
produces input SHA-256 and actual CPU.call instruction cycles. It saves a
companion .manifest.json containing source variant/provenance, resource
footprint, image checksum and the CSV digest.

Two different relocations are deliberately scored **separately**. This
producer does not yet emit competing historical-kernel traces, does not
run native VICE and is not a measured real-game workload. The native VICE
regressions in the existing builder workflow remain required for qualifying
any eventual kernel promotion.
