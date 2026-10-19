# Historical V1–V5 trigonometry: authenticated public speed basis

The stock-C64 operation-first installer already links the exact original
SIN8 (11 code bytes), COS8 (15) and SINCOS8 (22) instructions and the same
shared **256-byte immutable SINE8 table** recovered from all five shipped
resident PRGs. No alternate slower or approximate trigonometry algorithm
is introduced by this migration.

The source-qualified `speed` objective previously refused these three
operations for lack of a matched, full-public-call cycle model, despite
their already being independently linkable and source/native validated.
The new model measures every 8-bit input phase for each original kernel
at both code relocations. It validates X retention, Y/Z sentinels, output
bits, C=0, stack depth, immutable code/table bytes, source SHA256
provenance and exact 256-byte table reuse. It reports mean, p95, max and
the phase-byte corpus digest in the operation-first speed manifest.

## Important distinctions

- These are **single-variant certified speed models**, not a faster new
  algorithm or a speed claim relative to the original V1–V5 code.
- The builder can now estimate the costs of all three when composing a
  weighted workload with other qualified operations, without silently
  excluding the three trig calls from global speed optimization.
- Selecting SIN8, COS8 and SINCOS8 together links only **one** 256-byte
  shared table page. The three kernels occupy 48 bytes total, plus
  alignment padding and the common public I/O window.
- Source-model CPU cycles are not real PAL/VIC-II badline or IRQ frame
  timing. Native VICE r46284 tests the actual six source-linked entries
  at two memory origins; weighted mixed-frame physical qualification
  remains a separate profile-retirement gate.
- The five historical profile releases remain immutable and available.

With this qualification the number of APIs supported by authenticated
speed planning grows from 37 to 40 on the **main-based draft branch**
(and would be 44 when the four pending UMULDIV16, SMULDIV16, SDIV16 and
SMOD16 migrations complete). Do not count unpublished code as merged.
