# Source-only Turbo16 REU arithmetic-plus-SWAP CPU integration

The source-assembled Turbo16 kernel, CALL wrapper, DMA SWAP controller and
the four 512-byte source-derived tables are now exercised as a complete
**CPU-model experiment**, without loading a historical resident PRG as an
input to the experiment.

Table bytes are emitted from SHA-locked V3 and V4 *source text*, and their
correctness has separately been checked against both archived reference
PRGs. The DMA experiment places these bytes in configurable RAM and runs
224 real 16×16 product calls across two batches and two memory layouts.
It verifies products, Carry, caller input registers, 122-byte zero-page
restoration, interrupt-disable state, rejection of nested BEGIN and
persistence of Turbo16's executable self-modified operands inside REU.

```sh
python3 -m unittest discover -s tools -p 'test_reu_turbo16_source_integrated_swap.py' -v
python3 tools/reu_turbo16_swap_experiment.py --out build/turbo16-source-swap
```

**Release boundary:** this does not yet produce an independently installed
`math_selective.prg` + companion REU image, establish global application
resource ownership or prove native REU bus timing in x64sc. The lookup
planes are source-materialized constants, not independently derived
mathematically, and missing-hardware errors remain unqualified.

Next are a relocatable, bank-reserved builder package, native 512 KiB /
16 MiB VICE REU execution with DMA/IRQ interactions, and comparison against
the full historical V3/V4 BEGIN/CALL/END public ABI under identical inputs.
The user-facing stock-C64 installer and all historical compatibility assets
remain unchanged.
