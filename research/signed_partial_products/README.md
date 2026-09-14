# Signed partial-product research bundle

This directory is non-production research evidence for the 2026-09-14 signed
multiply pass.  The only production algorithm change selected by this work is the
already-integrated direct SMUL8 kernel.

Files:

- `sources/smul16_hybrid_xsigned.a` — direct signed high-row 16×16 candidate.
- `sources/signed32x8_baseline.a` — matched unsigned-row + correction reference.
- `sources/signed32x8_direct.a` — matched direct signed-partial 32×8 row.
- `mixed8_signed_bound.py` — exhaustive S8×U8 primitive check.
- `mixed8_signed_index.py` — exhaustive U8×S8 primitive check.
- `compare_signed32x8_rows.py` — deterministic matched row comparison.
- `results/` — consolidated JSON/CSV outcomes.

The Python scripts use the repository's `tools/mini6502.py` and do not mutate the
resident images.
