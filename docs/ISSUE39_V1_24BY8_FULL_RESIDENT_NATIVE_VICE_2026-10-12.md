# Issue #39 — V1 61-byte 24÷8 accumulator: full-resident native VICE verification

**12 October 2026. PASS: 384 native VICE x64sc old/new public-entry executions.** This certificate supplements the original PR #81 isolated-kernel native test; it does not replace or reinterpret the public deterministic 6502 cycle measurements.

The **actual merged V1 resident** `v1_balanced/resident/math_v1_balanced_game_math.prg` (SHA-256 `cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd`) was exported from [GitHub Actions run 38281410266](https://github.com/floppyrom/C64-Math-Library/actions/runs/38281410266). The exact preceding PR #78 full resident was recreated from it by restoring only the $1D00 source island to the archived 69-byte old implementation and its 15 zero padding bytes. Reconstruction SHA-256 matched `28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0`.

Under native VICE x64sc, a RAM-backed harness calls `MATH_INIT=$3280`, then each real public entry: `MATH_UDIV24=$3170` and `MATH_UMOD24=$3223`. For each API, 96 identical operand pairs are executed on PR #78 and PR #81 residents — **192 native calls per API; 384 total**. The deterministic input families include zero divisors, 24÷8, 24÷16, 24÷24, 16-bit numerator, boundary values and random pairs.

| Comparison | UDIV24 | UMOD24 |
|---|---:|---:|
| Old resident native calls | 96 | 96 |
| New resident native calls | 96 | 96 |
| Incorrect Q/R/C or mathematical oracle | 0 | 0 |
| Old/new divergences | 0 | 0 |
| N/D clobber, Q3/R3 sentinel overwrite or stack mismatch | 0 | 0 |

The harness verifies three output bytes each of quotient and remainder, carry including zero-divisor behavior, three preserved bytes each of N/D, untouched Q3/R3 sentinels and unchanged stack pointer. All checks passed. **VICE did not measure cycle timing**; the published means remain deterministic complete-public-entry emulator counts: UDIV24 170.238165→166.190196, UMOD24 246.822279→234.433355 on identical input corpora.

Evidence: `validation/review/ISSUE39_V1_24BY8_ACCUMULATOR_FULL_RESIDENT_NATIVE_VICE.json`.

Portable reproduction materials: `Issue39_PR81_V1_FullResident_Native_VICE_Proof_2026-10-12.zip` (the native harness script and the machine-readable test report). Source script SHA-256: `2a107ef5b8c23d9ac62ad79cd7092175cd5c47e3be81715da6f44d9f62f9d82a`. It requires the exact PR #81 resident export, a working native x64sc binary with remote monitor, and the bundled in-repo `tools/mini6502.py` assembler.

**Release status:** PR #81 remains the released source-backed 61-byte V1 kernel; PR #82 separately records no unconditional resident promotion for OptiSearch biased UMOD16. The entire unsigned DIV/MOD audit and issue #39 remain **OPEN** pending other width/profile decisions. This native certificate does not claim the whole issue or DIV/MOD family is complete.
