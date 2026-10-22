# Operation-first REU acceleration: Turbo16, Turbo32 and QS16

**What do the three options actually do?** Turbo16 and Turbo32 execute fast
multiplication code in the C64's **zero page**, using the REU to save and
restore that code and the caller's zero-page contents by DMA. QS16 takes a
different approach: it stores a large **quarter-square multiplication lookup
table in REU RAM**, retrieving values by DMA for each multiplication.

**The REU is memory plus a DMA controller, not a second CPU or a hardware
multiplier.** In all three modes, the C64's 6510 performs the arithmetic.
The benefit is access to an executable zero-page overlay or a much larger
lookup table, not arithmetic being calculated inside the REU.

These are **three optional, source-built companions** to the normal
[operation-first C64 builder](OPERATION_FIRST_USER_SETUP.md), not different
versions of the 56 standard APIs or historical V3/V4 resident profiles.
They were integrated in [PR #393](https://github.com/floppyrom/C64-Math-Library/pull/393).
Choose **one service per project**; normal stock-C64 multiplication remains
available as a fallback.

## At a glance

| | Turbo16 | Turbo32 | QS16 |
| --- | --- | --- | --- |
| **Calculates** | Unsigned 16 × 16 → 32-bit product | Unsigned 32 × 32 → 64-bit product | Unsigned 16 × 16 → 32-bit product |
| **Uses the REU for** | DMA-swapping 122 bytes of executable zero-page code | DMA-swapping 135 bytes of executable zero-page code | Storing a 512KiB quarter-square lookup table |
| **During each multiply** | C64 executes a zero-page routine; no REU table fetch | C64 executes a zero-page routine; no REU table fetch | C64 fetches two 4-byte table entries by REU DMA and subtracts them |
| **Best reason to select** | Repeated 16-bit multiplies when the zero-page overlay is acceptable | Repeated 32-bit multiplies that need the entire 64-bit result | Experimenting with large-table 16-bit multiplication without consuming 512KiB of C64 RAM |
| **Stock fallback** | `UMUL16` | `UMUL32` | `UMUL16` |
| **Hardware** | 512KiB or 16MiB REU | 512KiB or 16MiB REU | 16MiB REU only |
| **Flag** | `--reu-turbo16` | `--reu-turbo32` | `--reu-qs16` |

**Important performance distinction:** neither the word *Turbo* nor use of a
large REU table guarantees lower elapsed time than the fastest stock-C64
variant. Include INSTALL/BEGIN/END, DMA bus stalls, workload size, and any
screen/SID/IRQ work when comparing a complete application. No general
DMA-inclusive speed ranking or 25/50 fps certificate is claimed here.

## Turbo16: fast 16-bit multiplication through executable zero page

Turbo16 multiplies two **unsigned 16-bit integers** and produces the
**exact 32-bit product**. For example, `$1234 × $0003 = $0000369C`.

The arithmetic is a source-built, self-modifying **quarter-square**
multiplication kernel with 2,048 bytes of square-table planes in C64 RAM.
Its 122-byte hot code occupies zero page (`$3E–$B7`) *only during the
active batch*. The REU holds the inactive code image.

1. **INSTALL** checks a real REU DMA round trip and verifies that the
   configured bank is not an alias of a smaller device. It uploads the
   executable overlay to the selected REU bank.
2. **BEGIN** performs a 122-byte REU **SWAP**: the caller's previous
   zero-page contents are saved in REU RAM, and the executable kernel
   appears in C64 zero page.
3. **CALL** multiplies the operands entirely on the C64, using its
   zero-page routine and resident square tables. Repeated CALLs do not
   have to swap the overlay again.
4. **END** SWAPs those 122 bytes back: the caller's original zero page is
   restored, and the (possibly self-modified) executable code is kept in
   the REU for a later batch.

**Choose Turbo16** when many 16-bit products are needed together and you
can dedicate the overlay's zero-page region during that batch. It is
*not* a zero-page-free routine and is not suitable for arbitrary nested
math/IRQ use while active.

## Turbo32: the same idea for full-width 32-bit products

Turbo32 multiplies two **unsigned 32-bit integers** to produce the
**exact 64-bit product**. For example,
`$00010000 × $00000003 = $0000000000030000`.

It uses a different arithmetic kernel: a 135-byte executable/data
zero-page overlay (`$0A–$90`), RAM-side preparation and summation code,
and 2,048 bytes of resident quarter-square table planes. The REU
performs a **135-byte SWAP on BEGIN and END**, not a full multiplication
during every CALL.

As with Turbo16, INSTALL verifies the hardware and selected bank,
BEGIN saves the caller's zero page and activates the kernel,
CALL computes on the 6510, and END restores the exact previous
zero-page bytes. No hardware stack-page reservation is part of this
Turbo32 kernel's permanent resource claim.

**Choose Turbo32** for workloads requiring many 32-bit products, such as
high-precision fixed-point calculations or accumulated geometry, **when
the complete 64-bit output is actually useful**. For a game that only
needs 8- or 16-bit intermediates, the smaller stock arithmetic may be
the better choice.

## QS16: use the REU as a very large multiplication table

QS16 also computes an **exact unsigned 16 × 16 → 32-bit product**, but
it does **not** run an executable zero-page multiplication overlay.

It uses the quarter-square identity:

\[
a\times b=Q(a+b)-Q(|a-b|),\qquad Q(n)=\lfloor n^2/4\rfloor.
\]

With unsigned 16-bit inputs, `a+b` can reach 131,070. The table
therefore holds **131,071 four-byte records** (524,284 meaningful bytes).
It occupies **eight complete, aligned 64KiB REU banks = 524,288 bytes**;
the final four bytes are padding.

- **INSTALL** generates the mathematical table *on the C64*, one 1KiB
  block at a time. Each block is DMA-written to REU memory, read back,
  and byte-verified. No prebuilt historical `.reu` image is required.
  This is a substantial **one-time initialization**, not something to
  repeat every frame.
- **BEGIN** saves the 16-byte scratch zero-page area (`$4E–$5D`),
  sets up the REU service, and marks the batch active.
- **CALL** computes sum and absolute difference, fetches **two four-byte
  entries** from REU RAM by DMA, and subtracts one from the other to
  produce the 32-bit product in C64 RAM.
- **END** closes the batch and restores the caller's 16 scratch ZP bytes.

**Choose QS16** when you specifically want to explore a table-based
16-bit multiplication path, have a genuine **16MiB REU**, and can
amortize installation over a sufficiently long session. The table's
raw data occupies only about 512KiB, but this *implementation*
intentionally requires **eight aligned banks in the upper half** of a
16MiB device, plus smaller-capacity alias checks; it is **not**
supported on an ordinary 512KiB REU.

Because QS16 performs REU DMA reads for **every CALL**, it must be
benchmarked against both stock math and Turbo16 with real bus timing.
Do not assume it is automatically the fastest 16-bit multiply.

## How the public interface works

All three services use the same **guarded batch pattern**:

1. Load the generated stock `math_selective.prg` and the separate
   `<service>_reu.prg` at their documented, nonoverlapping addresses.
2. Call the service's **INSTALL** once after loading. **Carry clear**
   means success; **Carry set** means the hardware/probe/installation
   failed. On failure, do not call BEGIN or CALL—use the selected
   stock-C64 fallback instead.
3. Call **BEGIN** (Carry clear on success) and perform as many
   **CALL** operations as the workload needs. Never nest BEGIN or call
   outside an active batch.
4. Call **END** exactly once to restore zero-page ownership before
   returning to normal game/library/IRQ routines.

| Service | Generated public entry symbols |
| --- | --- |
| Turbo16 | `MATH_T16_REU_INSTALL`, `MATH_T16_REU_BEGIN`, `MATH_T16_REU_CALL`, `MATH_T16_REU_END` |
| Turbo32 | `MATH_T32_REU_INSTALL`, `MATH_T32_REU_BEGIN`, `MATH_T32_REU_CALL`, `MATH_T32_REU_END` |
| QS16 | `MATH_Q16_REU_INSTALL`, `MATH_Q16_REU_BEGIN`, `MATH_Q16_REU_CALL`, `MATH_Q16_REU_END` |

**Operand and result locations are separate from stock math.** The REU
service uses its own 32-byte public I/O region at `$C000–$C01F`:

| Address | Purpose |
| --- | --- |
| `$C000` | Operand X (little-endian, 2 bytes for Turbo16/QS16, 4 for Turbo32) |
| `$C004` | Operand Y (same width as X) |
| `$C008` | Product Z (little-endian, 4 bytes for Turbo16/QS16, 8 for Turbo32) |

The operation-first **stock** math I/O defaults to `$C040` in an REU
project and has a different generated API. Always use the stock
`math_api.inc` and the service's `math_reu_<service>.inc` for call
addresses; do **not** pass stock operands by assuming the two I/O blocks
are identical. Use the service's `<service>_reu_manifest.json` to
check its exact exports and hardware claims.

A batch is exclusive: **do not call normal math that uses the same ZP,
run an IRQ that touches the reserved region, or try another REU service
before END**. Even though the Turbo overlays restore caller ZP, they
do not make overlapping concurrent execution safe.

## Memory and hardware requirements

| Service | C64 RAM reservation* | Exclusive ZP during a batch | REU RAM claimed |
| --- | ---: | --- | --- |
| Turbo16 | 18,464 B | `$3E–$B7` (122 B) | One complete 64KiB bank; overlay swaps 122 B |
| Turbo32 | 18,464 B | `$0A–$90` (135 B) | One complete 64KiB bank; overlay swaps 135 B |
| QS16 | 18,468 B | `$4E–$5D` (16 B) | Eight complete 64KiB banks (512KiB table) |

*These conservative C64 costs reserve the **whole** `$3000–$77FF`
module load-image envelope (18,432 B) plus `$C000–$C01F`
public I/O (32 B), and for QS16 also `$C020–$C023` (4 B)
scratch. They are **not** the count of executable instructions.
The module installer reserves these before choosing the stock kernels,
then enforces combined user RAM/ZP budgets and prevents collisions.

All services require exclusive ownership of the REU's **I/O2
registers `$DF00–$DF0A`**, their declared REU banks and the alias-probe
bytes in smaller-capacity mirror locations. Preflight probes can alter
these explicitly owned locations. Do not assign them to another
application component. By default, Turbo modules use REU bank 4 on
512KiB or bank 200 on 16MiB; QS16 uses banks **200–207** on 16MiB.
Use `--reu-bank` and `--reu-reserved-bank` for other verified layouts.

## Build one of the three modes

The simplest approach is `make builder-setup`. Select the ordinary
operations, `balanced` / `speed` / `size` / `zp` objective,
RAM/ZP budgets, and **none / Turbo16 / Turbo32 / QS16**.

Alternatively, run one of these noninteractive commands from the
repository root (use a **new config and directory name** for each):

**Turbo16 (512KiB):**

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --objective size \
  --ram-budget 27000 --zp-budget 200 \
  --reu-turbo16 --reu-kib 512 \
  --config-out math-t16.json --build-dir build_t16
```

**Turbo32 (512KiB):**

```sh
python3 tools/configure_math.py \
  --operation UMUL32 --objective size \
  --ram-budget 30000 --zp-budget 210 \
  --reu-turbo32 --reu-kib 512 \
  --config-out math-t32.json --build-dir build_t32
```

**QS16 (16MiB):**

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --objective size \
  --ram-budget 30000 --zp-budget 210 \
  --reu-qs16 --reu-kib 16384 \
  --config-out math-qs16.json --build-dir build_qs16
```

Each build creates a saved configuration and **two distinct loadable
PRGs** with complementary include files:

| Generated file | Purpose |
| --- | --- |
| `math_selective.prg` / `math_api.inc` | Normal stock-C64 math, including required fallback |
| `selective_manifest.json` | Stock operations, selected variants and exact RAM/ZP placement |
| `<service>_reu.prg` / `math_reu_<service>.inc` | Independently built hardware companion and public entry addresses |
| `<service>_reu_manifest.json` | Companion resources, bank/capacity, code source hashes, exports |
| `math_project_manifest.json` | **Combined** RAM/ZP use, both PRG checksums and REU bank ownership |

To rebuild a saved hardware configuration, use the builder rather than
rerunning the first-time installer over existing paths:

```sh
python3 tools/math_builder.py --config math-t32.json --build \
  --out build_t32_rebuilt/selection_manifest.json
```

No historical resident profile or precomputed historical REU image is
needed. The C64-only stock builder remains the default without an
explicit REU selection, and `--objective speed` does not silently choose
hardware acceleration.

## Qualification and limitations

The source-built modules have CPU-model arithmetic, lifecycle and ZP
restoration tests, and pinned native VICE x64sc preflights for real DMA,
absent/mirrored hardware and repeated batches. Operation-first
acceptance also tests selection, global memory accounting and saved
configuration builds. This is **merged integration**, not merely an
unbuilt proposal.

It **does not certify** a speedup in every case, real-hardware operation,
arbitrary mixed IRQ/VIC/SID or application frame timing, nested calls,
simultaneous services, or a specific 25/50 fps effect. The meaningful
measurement for an application includes transfer/DMA time, BEGIN/END,
arithmetic CALLs, rendering and music under a realistic workload.
Use [per-routine stock CPU metrics](OPERATION_FIRST_ROUTINE_METRICS.md)
and generated manifests as separate reference points, not as an
apples-to-apples REU speed comparison.

## Historical compatibility

The original V3/V4 PRGs and `.reu` images remain frozen for **regression
and existing applications**. Modern Turbo16, Turbo32 and QS16 are
source-built and do **not** link or import these legacy residents.
Do not load old V3/V4 residents alongside the generated stock
operation-first PRG.

See [historical REU export information](REU_COMPAT_EXPORT.md). Targeting
1541, 1571 or 1581 math backends is separate from this C64+REU
integration.
