# Normalize and ATAN2 size refresh

Compared with commit `7a74e750556c1da09db8759f9ed479cd92bd6d17`, the installed
routines occupy less C64 RAM and have no slower calls in the comparison corpus.

| Routine | Profiles | Previous code | Current code | Previous C64 tables | Current C64 tables | Bytes saved | Previous mean cycles | Current mean cycles |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Normalize | V1/V2/V5 | 915 | 881 | 2,816 | 2,560 | **290** | 161.332256 | **160.150080** |
| Normalize | V3/V4 | 867 | 849 | 1,024 | 1,024 | **18** | 157.552684 | **156.661198** |
| ATAN2 sum-fast | V2/V3/V5 | 92 | 88 | 1,024 | 1,024 | **4** | 44.962814 | **44.962814** |

Code counts in this table include the public three-byte JMP. ATAN2 body-only
counts are 89 and 85 bytes. V1 compact ATAN2 and V4 exact REU ATAN2 are unchanged;
the optional three-page `sum_small` remains slower than the installed fast tier.

Normalize saves 7.77% of its occupied code plus tables on stock profiles.
Combined normalize/ATAN2 savings are 290, 294, 22, 18 and 294 bytes for V1–V5.
These are occupied-byte savings, not reductions in the contiguous PRG file:
the shipped PRG load addresses, file spans and two REU images are unchanged.
The stock layout frees the old code page at `REG_LOW+$0900..+$09FF`; the
integrated profile still reserves its enclosing region. Standalone users can
use the exact code/table islands documented alongside the native sources.

## Changes

- Stock normalize uses four ratio-index pages instead of five. Its quantizer
  is `L(v)=floor(127.85*log2(v)+0.5)-895`; major bytes have an implicit zero high
  byte. The lookup instruction sequence takes the same number of cycles.
- Remove redundant zero loads and the positive-quadrant comparison branch.
  Small vectors pass their minor byte directly to the lookup or DMA setup.
  The positive sign path branches directly to its quadrant.
- Place each stock quadrant within one page so taken branches and reduction
  loops do not acquire page-crossing penalties when the code shrinks.
- Sum-fast ATAN2 clears carry once at entry. Loads and sign branches preserve
  carry until the biased addition, which clears it for the return contract.

## Accuracy and validation

Stock normalize outputs change: 105,107 of the 107,396 comparison vectors
produce different component bytes. V1/V2/V5 still agree exactly. The full
723,073-cell signed-Q8.8 certificate bounds angular error by
**0.361659109 degrees** and component error by **201 Q1.15 LSB**, inside the
existing 0.3621-degree / 202-LSB contract. This preserves the accuracy limit,
not bit-for-bit stock output compatibility. REU normalize and all ATAN2
outputs remain bit-identical to the previous commit.

Every profile is compared against the prior resident binary on 107,396
normalize inputs. All three changed ATAN2 profiles are compared on every
signed-byte input pair: 65,536 cases each, identical cycles and outputs.
Reference and alternate maps have identical normalize cycle/output vectors.
Additional checks cover all normalized major/minor pairs, all signed-byte
vectors, small-vector boundaries, input preservation, carry, scratch bounds,
cold stock loads and interleaved arithmetic calls. ATAN2 is independently
checked with py65 and ACME, including both initial carry states and a layout
that crosses a code-page boundary.

The mixed-call validator now uses the ordinary `MATH_UMUL32` entry before
testing `MATH_UMUL32_READY`. The previous test incorrectly used READY after
arbitrary calls had overwritten its required pointer state; that failure
also reproduces on the baseline commit. No multiply implementation changed.

Evidence and reproducible tools:

- `validation/SIZE_OPTIMIZATION_VALIDATION.json`
- `tools/validate_size_optimization.py` (requires baseline git history)
- `validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json`
- `validation/normalize/LOG_RATIO_FULL_DOMAIN_PRECISION_CERTIFICATE.json`
- `validation/normalize/OPTIMIZED_VALIDATION.json`
- `validation/ATAN2_OPTIMIZATION_VALIDATION.json`
- `make normalize`
