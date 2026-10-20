# Replaying full linked-source frame evidence before installation

A reproducible full-PRG SHA-256 is **not enough** to establish a
performance number. One could preserve the source hashes, the measured
PRG SHA, public ABI and resource map, yet change the `peak_frame_math_cycles`
field in an imported report. This would otherwise allow a false positive
for a hard frame-cycle limit.

The **opt-in** operation-first `--objective frame` therefore does not
treat imported reports as trusted timing authority. It re-executes the
registered mixed-source measurement and compares the **entire report**
to freshly generated data before choosing a kernel combination. Its
attestation is only as strong as the pinned CPU model, source tree,
public-call corpus and benchmark producer.

The first registered benchmark is exactly the signed `MATH_SMUL32`,
unsigned `MATH_UMUL32` and `MATH_ISQRT16` 150-call,
24-synthetic-frame corpus; eight complete candidate image combinations
at **two** measured code/I/O/ZP/scratch relocations.

```sh
mkdir -p build/frame-proof
python3 tools/mixed3_frame_parity.py \
  --out build/frame-proof/mixed3.json
python3 tools/frame_evidence_replay.py \
  --report build/frame-proof/mixed3.json \
  --out build/frame-proof/replay-proof.json
python3 tools/math_builder.py \
  --objective frame \
  --config examples/operation-first-frame.json \
  --frame-report build/frame-proof/mixed3.json \
  --build --out build/frame-proof/selected/selection_manifest.json
```

Failures are fatal before publication: an unsupported producer,
unmeasured relocation, unknown operation, changed input history,
mismatched physical source SHA, different PRG, differing actual
RAM/ZP resource, incorrect cycle aggregates or falsified
peak/p95/total math-only frame costs all reject the build.

**No generic certification:** Arbitrary operations and traces are not
suddenly measured by this research gate. Future workloads must add an
explicitly qualified deterministic producer. Existing standard builder
objectives remain unchanged; the old five profiles and independent
V3/V4 REU compatibility bundles are not modified.

**No PAL guarantee:** even faithful source-linked CPU-model replay
does not account for raster phase, badline stalls, VIC-II fetch/DMA,
SID/IRQ workload, REU transfers or the rest of an application's work
within a physical 50Hz frame. The native VICE integration proves
actual binary *correctness*, not worst real-frame timing.
