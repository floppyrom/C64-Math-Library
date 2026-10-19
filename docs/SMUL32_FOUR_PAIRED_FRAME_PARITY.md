# Same-public-input four-way SMUL32 signed full64 frame comparison

Four already linkable sources for `MATH_SMUL32` are compared on the
same **150 complete signed public calls across 24 synthetic frames**, at
code/I/O origins `$8000/$C000` and `$7123/$C040`.

The four are:

- Compact 293-byte signed zero-ZP implementation (12 RAM scratch).
- Unified six-entry 375-byte zero-ZP implementation (12 RAM scratch).
- Original V2 signed FAST31 implementation with 31 ZP and four aligned tables.
- FAST31 shared full64 image, which may also serve unsigned multiply.

All comparisons verify the **signed 64-bit** mathematical result, preserved
public X/Y operands, carry C=0, hardware stack restoration and source-exact
linked PRG image including only the existing FAST31 self-modifying byte
whitelist. Candidate frame keys include identical signed operands, caller
A/X/Y/C/D initial state, code/I/O placement and public API.

For every candidate, the deterministic JSON report records full source
SHA-256, emitted PRG SHA-256, actual RAM/ZP footprint, mean complete
public call cycles, peak/p95 and total 24-frame math cycles, and any
individual slower calls or frame regressions against the compact source.

```sh
python3 -m unittest discover -s tools -p 'test_smul32_four_paired_frames.py' -v
python3 tools/smul32_four_paired_frames.py --out build/smul32_four_frame_report.json
```

This is source-linked 6510 instruction-cycle **math-only model** evidence
including the scorer's six caller-JSR cycles per call. It is **not** a
physical PAL/VIC-II/IRQ/SID/REU frame measurement and is not permission
to discard compact Pareto sources or the V1–V5 legacy binaries.
