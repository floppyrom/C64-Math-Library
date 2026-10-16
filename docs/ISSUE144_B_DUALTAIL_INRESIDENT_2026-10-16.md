# Issue #144 B — source-owned low-divisor dual-tail qualification

16 October 2026. **Explicit opt-in only, not the universal shipped/default divider.**

## Result and architecture

Existing V2/V3/V4 source-owned **`REG_LOW+$0C00..+$0DCC`** is an 461-byte zero-filled island in both reference and alternate maps, inside an already declared 8-KiB resident region. The original source segment contains no emitted labels there. The original V2 byte-source has two extra expected source-fixup operands elsewhere in REG_LOW after the division-core growth; V3/V4 have none. We deliberately do not infer code ownership from the obsolete historical SEGMENTS.csv or unoccupied bytes in the generated all-interval `!byte` provenance.

Relocate the independent 461-byte low-D no-overflow quotient producer into this source-owned island. Existing high-D 16-bit restoring division is unchanged. Divisor classes are handled at **the private U3216 divisor dispatch**, not at a new public entry:
- `D=0` and `1<=D<256`: retained canonical zero and byte-divisor paths.
- `$0100<=D<=$7FFF`: a separate, 16-stage no-overflow low-word quotient producer, a mathematically valid fast path for an already reduced high-word remainder.
- `$8000<=D<=$FFFF`: current shared-take restoring 16-bit low-word producer.

All four public UDIV32_16, UMOD32_16, SDIV32_16, SMOD32_16 APIs still compute complete **Q32/R16/carry**, preserve public N32/D16, and retain stack balance and externally visible CPU status/register behavior. No additional zero-page, caller-owned RAM, data table, REU bank, ISA extension, or IRQ code is introduced.

## Evidence

The independently compiled in-memory source [full-public model](../tools/issue144_u3216_inresident_dualtail_model.py) passed **51,252 paired baseline/candidate calls** on V2, V3 and V4, *each* with reference and alternate relocated layouts. All signed quadrants, zero divisors, narrow/low/high divisors, full-width operands and extrema pass. The code island is unchanged after `MATH_INIT` and after interleaved calls to `MATH_UMUL16`, `MATH_ISQRT32` and `MATH_UDIV16`.

The [pinned x64sc 6510 harness](../tools/native_issue144_u3216_inresident_dualtail.py) passed **1,152 paired baseline/candidate native public calls** (4 entries × 3 profiles × 2 maps × 24 operands × 2 versions), including signed/unsigned Q/R/carry, preserved inputs, A/X/Y, full processor flags and SP. **No actual physical VIC/REU DMA time was measured.**

The [disposable real source-build](../tools/issue144_u3216_inresident_fullabi_stage.py) passed **all 56 stable public entries** on all six V2–V4 layouts, with **21,678 CPU-model API calls each (130,068 total)**, and trapped **no writes** from those public routines into the resident 461-byte code island. Builds generated real source-resident PRGs and REU images in a temporary output directory, and restored the canonical source file afterward. No shipped reference PRG/REU or `PERFORMANCE.md` is changed.

Reusing the exact previous dual-tail corpus preserves the published paired modeled savings:

| Case / workload | Mean saved per public call | Worst saved |
|---|---:|---:|
| Unsigned eligible `$0100..$7FFF` | 27.0299 cycles | +26 |
| Unsigned `$8000..$FFFF` | −0.4852 | −1 |
| Unsigned D8 / zero | approximately −2 | −2 |
| Unsigned mixed corpus | **10.8715 cycles** | −2 |
| Signed four-quadrant/edge-enriched corpus | **19.9919 cycles** | −2 |

Neither corpus mean can be substituted for a statistically representative application-workload benchmark or measured VIC bus throughput. The two-cycle worst overhead is explicitly retained, so this is not strict class-by-class Pareto dominance and is not the final issue #144 unrestricted producer.

## V5 hybrid linker is a strict exclusion

**Do not pass the patched V2 division donor to the current V5 hybrid builder.** Its existing relocated importer does not copy and relocate the additional `REG_LOW+$0C00` tail, leaving its branch pointing at unrelated V1-derived bytes. An independent full V5 source-build probe caught an unsupported opcode while executing a public `MATH_UMULDIV16` composition call. The [V5 isolation regression](../tools/issue144_u3216_inresident_v5_hybrid_probe.py) explicitly detects that unsupported inheritance, restores the original donor, then proves **both ordinary V5 reference/alternate layouts pass all 56 entries, 21,678 calls each, at 31 normal ZP bytes**.

Use the [isolated opt-in builder](../tools/build_issue144_u3216_resident_optin.py) **only** for V2, V3, V4:

```bash
python3 tools/build_issue144_u3216_resident_optin.py --profile v2_pareto_fast --config-kind reference --out build_issue144_dualtail_optin
python3 tools/build_issue144_u3216_resident_optin.py --profile all --config-kind alternate --out build_issue144_dualtail_optin
```

It copies the public source package into a disposable directory, assembles the selected source with the 461-byte resident tail, executes the 56-entry validator, then copies source-built PRG, REU (if applicable), API and provenance manifests to the chosen destination without mutating the user's canonical checkout. V1 and V5 are deliberately refused.

## Remaining qualification gates

The V2–V4 model/native/source-build proof supports a **source-owned, relocatable opt-in library variant**, not arbitrary nested reentrancy. Its private shared ZP makes simultaneous nested library arithmetic unsafe without caller-arranged register/ZP saving; inspect true IRQ/NMI preemption and dynamic indirect references before claiming use across those contexts. No shipped reference binary, 56-entry ABI, normal ZP budget, released PERFORMANCE table or universal V5 default is changed. Workstream B stays open for a larger all-domain throughput improvement and robust V5 linker integration.
