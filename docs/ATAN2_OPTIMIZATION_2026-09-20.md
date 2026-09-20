# Smaller and faster standalone ATAN2 kernels — 2026-09-20

Three new stock-6502 alternatives improve the existing ATAN2 size/speed
trade-offs. They use only documented instructions, no zero page, no mutable
scratch, and no initialization. Complete ACME sources include their tables.

`compact_opt` and `sum_fast` have since been installed in V1–V3 and imported
into V5. `sum_small` remains an optional standalone kernel. The fixed addresses
and public API are unchanged, while the installed profile tables and manifests
now use the optimized layouts described below.

## Measured results

Baseline: repository commit `33ea1e80711dcc938f98f4dd4f64f0816c78d8dd`.
The baseline assembly and table sources are unchanged by this work.

| Implementation | Code | Tables | Code + tables | Mean cycles | Min–max | Extra ZP |
|---|---:|---:|---:|---:|---:|---:|
| Previous compact | 106 B | 512 B | 618 B | 50.441345 | 30–53 | 0 |
| **Installed V1 `compact_opt`** | **94 B** | **512 B** | **606 B** | **48.447189** | **29–50** | **0** |
| Previous fast | 94 B | 1280 B | 1374 B | 46.953064 | 30–48 | 0 |
| **New `sum_small`** | **92 B** | **768 B** | **860 B** | **45.958908** | **29–48** | **0** |
| **Installed V2/V3/V5 `sum_fast`** | **89 B** | **1024 B** | **1113 B** | **44.962814** | **29–47** | **0** |

- `compact_opt` is **3.95% faster** and removes 12 code bytes while reusing the
  existing compact tables and preserving every existing result.
- `sum_small` is **2.12% faster than the existing fast kernel**, with **40% fewer
  table bytes** and 514 fewer total code/table bytes.
- `sum_fast` is **4.24% faster than the existing fast kernel**, with **20% fewer
  table bytes** and 261 fewer total code/table bytes. It preserves every
  existing result.

Timings enumerate the entire 65,536-vector signed-byte domain with equal
weight. They include a 3-cycle public JMP and the 6-cycle RTS, but exclude the
caller's 6-cycle JSR. Code is at `$8000`; lookup tables are page aligned.
These are CPU instruction counts, excluding VIC DMA stalls and interrupts.
Other code placements can incur branch page-crossing penalties.

Memory totals count live code and tables. Add 3 bytes for the public JMP.
The inputs/output occupy the existing three addressed bytes; no workspace is
added. The ordinary JSR return address uses two hardware-stack bytes, with
zero additional stack usage. A flat PRG also contains address-gap padding,
which is distinct from the routine's live footprint.

## Contract and accuracy

- Signed 8-bit `x` at `X0`, signed 8-bit `y` at `Y0`; inputs preserved.
- Unsigned phase in `Z0` and A: `$00=+X`, `$40=+Y`, `$80=-X`, `$C0=-Y`.
- `(0,0)` returns zero. Every axis is exact, including `-128` inputs.
- D must be clear. Either entry carry is accepted; C is clear on return.
- A/X/Y and arithmetic flags are volatile; the interrupt-disable flag is
  preserved. No self-modifying code is used.

The error metric is circular distance from **rounded mathematical atan2** in
256 phase units per turn. All kernels have maximum error **one phase unit**
against that integer reference. This is not a claim of exact correctly rounded
atan2 on every vector or a continuous-angle error bound of exactly 1.40625°.

| Kernel | Identical to shipped result | Exact rounded-reference results | Results one unit away |
|---|---:|---:|---:|
| Existing compact/fast | 65,536 | 43,136 | 22,400 |
| `compact_opt` | 65,536 | 43,136 | 22,400 |
| `sum_small` | 65,334 | 42,966 | 22,570 |
| `sum_fast` | 65,536 | 43,136 | 22,400 |

`sum_small` changes 202 finite near-horizontal results by one unit. Its smaller
table set retains the same worst-case accuracy contract. Choose `compact_opt`
or `sum_fast` when exact parity with the shipped approximation matters.

## 1. Compact instruction changes

The original nonzero-X path takes a branch around the axis handler. The new
body lets that common path fall through, saving a cycle. Two reflected
quadrants replace load/complement/add sequences with an immediate quadrant
base followed by `SEC / SBC angle_table,X`, saving two cycles on those paths.

The axis handler is reduced to 14 bytes:

```asm
axis:
    clc
    lda Y0
    beq axis_store
    asl             ; C = sign of y
    lda #$80
    ror             ; $40 or $C0; bit zero of $80 clears C
axis_store:
    sta Z0
    rts
```

For zero Y the branch stores A=0 with C already clear. The ordinary memory I/O
contract is retained; register-only timing is not substituted in the table.

## 2. A log sum that also clears carry

Retain the original quantizer:

```text
q(m) = floor(11.63 * log2(m)), for 1 <= m <= 128
0 <= q(m) <= 81
```

The original kernel subtracts two logarithms and later executes `CLC` before
returning. The new sum kernels store two differently biased log pages:

```text
LOGX[x] = q(abs(x))                         (x != 0)
LOGY[y] = 82 - q(abs(y))                   (y != 0)
LOGY[0] = 174
```

After `CLC / ADC LOGY,X`, a nonzero pair produces
`index = 82 + q(abs(x)) - q(abs(y))`, in **1–163**. A zero Y produces
`index = 174 + q(abs(x))`, in **174–255**. These ranges do not overlap and
neither can overflow. The addition therefore gives both the lookup index and
the required **C=0** return state. Zero X is handled by the small axis path.

The angle table is a reindexing of the original table, so this transformation
does not change the approximation. Two angle pages suffice for `sum_fast`:

| x sign | y sign | Output |
|---|---|---|
| nonnegative | nonnegative | `QPOS[index]` |
| nonnegative | negative | `QNEG[index]` |
| negative | nonnegative | `QNEG[index] EOR $80` |
| negative | negative | `QPOS[index] EOR $80` |

`QNEG` stores the negated first-quadrant angle. Two log pages plus two angle
pages occupy 1024 bytes, versus one log page plus four angle pages in the
1280-byte original fast implementation. Carry survives the loads, XOR, store,
and RTS, removing the final CLC instructions on every nonzero-X path.

## 3. Removing the second angle page

`sum_small` uses the same two log pages and one positive angle page. Finite
angle entries are clamped to at least 1, while Y=0 entries stay zero.

With C=0 from the index addition, `LDA #1 / SBC QPOS,X` computes `-angle`.
For the nonzero negative-Y path the angle is at least 1, so this subtraction
always borrows and leaves C=0. The other reflected quadrant uses
`LDA #$81 / SBC QPOS,X / CLC`, yielding `128-angle`. The remaining negative-X
quadrant applies `EOR #$80`.

The clamp is the reason this variant has a small output difference near the
horizontal axes. It removes a complete 256-byte angle page while retaining the
exhaustively checked one-unit error bound.

## Use and reproduce

Complete sources:

- [compact_opt](../routines/atan2/standalone/atan2_s8_s8_u8_compact_opt.asm)
- [sum_small](../routines/atan2/standalone/atan2_s8_s8_u8_sum_small.asm)
- [sum_fast](../routines/atan2/standalone/atan2_s8_s8_u8_sum_fast.asm)

For example:

```sh
acme -f cbm -o atan2.prg routines/atan2/standalone/atan2_s8_s8_u8_sum_small.asm
python3 routines/atan2/benchmark.py --json
python3 routines/atan2/export_optimized.py --check
python3 -m pip install py65==1.2.0
python3 routines/atan2/validate_optimized.py --acme /path/to/acme
```

The exported routine is `atan2_s8_s8_u8`, with its default public JMP at `$7F00`
and body at `$8000`. Set X0/Y0, clear decimal mode, call it, and read Z0 or A.
Edit the declared code/I/O/table addresses to integrate it into a game. Keep
the tables page aligned and the regions disjoint. The default sum layouts use
`$9400/$9500/$9600`, plus `$9700` for `sum_fast`; the compact layout uses
`$9600/$9700`. These addresses are illustrative standalone allocations.

## Verification evidence

[`ATAN2_OPTIMIZATION_VALIDATION.json`](../validation/ATAN2_OPTIMIZATION_VALIDATION.json)
records source hashes, full cycle/error distributions, and output/cycle-vector
hashes. Certification covers:

- **917,504 input cases**, each executed in the bundled `mini6502` and
  independent **py65 1.2.0**, with exact result and instruction-cycle agreement.
- Both original kernels across the full domain, and all three new kernels
  across the full domain with entry C=0 and C=1.
- Both the reference layout and a relocated layout: body at `$88E9`, I/O at
  `$B000/$B004/$B008`, and tables from `$A000`. The relocated body crosses a
  code page, exercising branch penalties; it is intentionally slower than the
  published aligned placement.
- Guarded writes: only Z0 and the two ordinary return-address stack bytes may
  be written. Input preservation, returned A/C, decimal mode, stack balance,
  interrupt-disable preservation, exact axes, and the error bound are checked
  on every case.
- **Six ACME 0.96.4 comparisons**, one per new kernel/layout. Complete exported
  PRGs, including tables and address-gap padding, match the bundled assembler
  byte for byte. Generated exports are also checked for staleness.

No hardware wall-clock benchmark or fixed-profile integration is claimed by
this standalone certification. The source and evidence provide three concrete
choices that can be integrated with the destination program's memory map.
