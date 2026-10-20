# Replay-attested seven-API whole-project frame selection

The normal operation-first `--objective frame` installer now accepts one
explicitly registered **complete seven-operation source-linked project**:
UMUL32, SMUL32, ISQRT16, UDIV32_32, UMOD32_32, SDIV32_32 and SMOD32_32.

It does **not** infer a seven-API peak by summing independent three- and
four-operation frame benchmarks. Four whole-source combinations are
linked at two ROM-safe origins, $2000 and $4123, and each re-executes
the same 150 full public arithmetic calls across 24 synthetic frames.
It verifies the entire source and PRG SHA, signed/unsigned arithmetic
ABI, operand retention, stack state, shared RAM/ZP, mean-independent
peak/p95/total mathematical CPU-model cycles, and every source pin.

The resulting standard `math_selective.prg` is byte-identical to the
measured image at the requested qualified memory map. Test both a
fastest-eligible plan with resource budgets and a zero-ZP compact
fallback using the same report.

```sh
python3 tools/mixed_seven_frame_parity.py --out build/seven/measured.json
python3 tools/frame_evidence_replay.py --report build/seven/measured.json
python3 tools/math_builder.py \
  --objective frame --config examples/operation-first-seven-frame.json \
  --frame-report build/seven/measured.json --build \
  --out build/seven/selected/selection_manifest.json
```

A checksum-consistent but falsified peak, altered input/source/corpus,
unqualified address, missing API or impossible resource/peak limit is
rejected before binary publication. Ordinary balanced/speed/size/ZP
selection remains unchanged.

This replay is still a **specific synthetic project**, not a generalized
automatic physical worst-frame solver for all 56 APIs. VIC-II badlines,
IRQ, SID, REU DMA, application work and physical PAL clocks are not
measured. The original V1–V5 source/PRG references and independent
V3/V4 REU/Turbo/QS16 compatibility bundles remain preserved.
