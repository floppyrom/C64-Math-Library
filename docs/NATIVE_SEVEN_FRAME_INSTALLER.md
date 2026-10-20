# Exact seven-API frame-selected PRGs in native VICE

The `--objective frame` operation-first installer now links seven APIs
into the same image: UMUL32, SMUL32, ISQRT16, and signed/unsigned
32/32 DIV and MOD. Source-linked synthetic CPU-model replay qualifies
four compact/fast configurations across two relocations.

This independent **native x64sc r46284** qualification rebuilds two
**exact frame-selected** linked PRGs at the already-measured
`$4123/$C040/$70` code/math-I/O/ZP placement:

- **Peak objective, 64-byte ZP cap**: the measured performance-oriented
  complete linked source image
- **RAM objective, 0-byte ZP cap**: the compact, tableless,
  no-zero-page complete linked source image

Both outputs are created by the **normal production
`tools/math_builder.py --objective frame --build` command**, using the
full replay-registered seven-API report, with source pins, all seven
entrypoints, selected option, linked RAM/ZP use and SHA-256 matched
against the originally qualified exact PRG. No native test is run
against a binary that differs from its benchmarked image.

The independent existing native VICE harnesses then execute 96 public
calls for *each of seven API exports* on both installed full images,
validating multiplication product, sqrt, unsigned Q/R/C and signed
truncating Q/R/C, source input preservation and expected results.
Total: **1,344 independent native public calls across two PRGs**.

Why only one of the two source-qualified origins? The other qualified
`$2000` math-code placement overlaps these existing independent
native verification harnesses and their input/output capture buffers
at `$2000..$405F`. Native correctness evidence must never be
obtained by overwriting parts of the actual linked PRG under test.
The `$4123` placement keeps all verification buffers below the linked
program, and all code below the math-I/O page.

Run with pinned x64sc:

```sh
python3 -m unittest discover -s tools -p 'test_native_seven_frame_installer.py' -v
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
bash tools/vice/verify_headless.sh "$VICE_WRAPPER"
python3 tools/native_seven_frame_installer.py
```

**Scope limitation:** Native emulator correctness does not prove
physical PAL frame timing; the only frame-cycle figures remain
deterministic arithmetic-only CPU-model peak/p95/total cycles. No
badline/raster IRQ, SID, REU DMA or actual mixed application frame
duration is measured. No claim about arbitrary subsets of 56 APIs,
nor the retirement of legacy profiles, is made. Original V1–V5
reference PRGs and V3/V4 REU compatibility bundles remain untouched.
