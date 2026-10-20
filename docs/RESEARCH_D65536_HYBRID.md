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
