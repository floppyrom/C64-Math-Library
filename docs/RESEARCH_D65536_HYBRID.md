# Research-only: exact $00010000 divisor path in wide public DIV/MOD

The native frame-8 PAL/VIC/CIA sweep measured **19,883 PHI2 slots** for
the 31-ZP FAST31/table-root/V2-divisor source mix, 227 past the full nominal
19,656-slot frame limit *without* music, sprites, IRQ or REU. A single
source-model `SMOD32_32` public call consumed 2,710 modeled cycles when
`N=$80000001` (signed −2,147,483,647) and `D=$00010000` (65,536).
Current V2-hybrid unsigned dispatch handles `D<65536` via the historical
32/16 producer but sends `D=65536` to the full-width fallback.

`tools/research_d65536_hybrid.py` prototypes a **new separate assembled
source candidate**. It preserves the *exact* unchanged historical V2 32/16
core, exact unchanged wide 32/32 fallback, original public N/D and
Q/R/C semantics, and both signed normalization and restoration. Only its
own dispatcher is replaced by freshly assembled source. For precisely
`D=$00010000`, unsigned `Q=N>>16`, `R=N&$FFFF`; all other divisors
still call the original narrow or full-width producer. The signed wrapper
calls this magnitude core and restores signs.

The research-only candidate occupies **96 extra bytes** of main RAM
(unsig 0xA20 vs 0x9C0; signed 0xBA0 vs 0xB40), with the same 12 ZP bytes.
Its dispatch introduces small overhead on some other divisors; the winner
must be judged by complete workload cycles/peak, not by one favorable case.

```sh
python3 -m unittest discover -s tools -p 'test_research_d65536_hybrid.py' -v
python3 tools/research_d65536_hybrid.py \
  --out build/research/d65536-comparison.json
```

The research workflow measures **both actual source implementations** at
two independent relocations, with identical existing 384-case signed or
unsigned public operand corpora plus 16 directed edge inputs. It validates
complete 32-bit quotient/remainder/carry, original N/D preservation, stack
and executable code immutability, zero divisor, negatives, and boundary
divisors. It explicitly reports mean/worst, target-hit and fallback costs,
but **it does not claim native PAL speed**, frame-8 workload parity or
general installer availability.

**Do not register or select this research path in production yet.** The next
gate is native x64sc validation against the same public corpus and complete
24-frame PAL/VIC timing, followed by a Pareto comparison of *peak frame,
RAM and ZP*, and checking that the historical V2 still wins where expected.
No legacy V1–V5 profile, 56-API operation-first catalog, REU or Turbo/QS16
asset is changed by this experiment.

## Separate native PAL qualification step

`tools/native_research_d65536.py` builds both old and research unsigned
and signed public source images at the qualified `$4123/$C040/$70` map.
It drives each source through existing native x64sc public **Q32/R32/C**
oracles using an identical 96-pair edge-enriched corpus, including the
exact frame-8 `$80000001/$00010000` input, and independently checks that
old/new native capture digests match.

The same exact signed public input is also run by a one-call VIC/CIA
raster-synchronised PAL microprobe, with the display on and off. Its
measured PHI2-slot difference *includes identical operand staging,
instrumentation and VIC contention*, and therefore is an isolated-call
native time delta, **not a 24-frame whole-project optimization**.

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 -m unittest discover -s tools -p 'test_native_research_d65536.py' -v
python3 tools/native_research_d65536.py \
  --out build/research/d65536-native-isolated-pal.json
```

The dedicated CI workflow runs this only after the source-model corpus
passes, and labels all outputs research-only. The original stock source
and linker API remain untouched.

## Separate seven-operation native PAL regression

`tools/research_d65536_seven_pal.py` constructs the same **exact seven
public operation** mix used by the source-registered PAL workload. It
reuses the normal builder/linker for the five other source registrations,
then *temporarily* inserts the experimental unsigned and signed
assemblies, with their true 96-byte-larger footprints, into this one
throwaway local source-linked image. It never writes a new entry into the
persistent `MODULES` catalog or modifies the installed V2 variant.

The resulting source-evidence artifact names the original production
baseline PRG SHA, experimental PRG SHA and this experimental emitter's
own source SHA. Any production-format manifest produced during the
temporary injection is expressly **not valid production provenance**,
because the experimental variant is not a qualified catalog entry.

The probe replays each of the same 24 synthetic frames twice per
configuration (normal VIC display on and display off), with native
CIA1 A/B elapsed-clock capture and per-call output/carry hashes. It
reports the full-project native worst burst, frame-8 saving, resource
delta, and which isolated synthetic frames exceed 19,656 PAL slots.

```sh
python3 -m unittest discover -s tools -p 'test_research_d65536_seven_pal.py' -v
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 tools/research_d65536_seven_pal.py --frames all \
  --out build/research/d65536-seven-frame-native-pal.json
```

This is a research-only **mixed-source benchmark**. Although complete
native bursts are measured, it still excludes music, IRQ, sprites, REU
DMA and real 50 Hz consecutive-frame scheduling. Production installer
registration, workload-specific Pareto selection, and profile retirement
remain explicitly separate follow-ups.

### Identical-link baseline reconciliation

The PAL test now constructs a **third source-linked control** with the
same seven operations, same code/IO/ZP placement, same pinned variants,
and ordinary unmodified V2 source emitters. Its PRG **must be byte-for-byte
identical to the independently built production frame-selected PRG**,
including exported public addresses. Only after that proof does it compare
the separate candidate's actual occupied RAM against the same control
linker. It verifies **+96 raw source bytes per independent signed
and unsigned producer** (192 bytes in all) while separately measuring the
*actual linked program's image-size delta*.

The first exact-link comparison reported **256 additional linked RAM bytes**,
not 192, indicating 64 further bytes from whole-link image layout/alignment.
The tests now require the linked-image byte delta and recorded RAM-resource
delta to agree while retaining a strict +192-byte producer-source floor.
The installer report's *worst-placement resource envelope* is not by itself
an authoritative exact RAM-length comparator for a particular link.
The revised tests reject mixed source-pinning or unexplained memory
differences instead of treating a discrepancy as an optimized result.
