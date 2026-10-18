# Historical fast 24-bit multiplication: donor selection before transplantation

The operation-first installer links all 56 APIs, but **UMUL24** and **SMUL24**
still have only one independently selectable implementation each: a
156-byte unsigned restoring shift/add core and a 227-byte signed source
built from that core. Both use ordinary RAM scratch and **zero ZP**.
The compact 24-round arithmetic path is not a historical speed winner.

The five profile releases contain faster 24-bit multipliers, potentially
with dedicated ZP, precomputed tables, REU or source-dependent state.
Before importing a kernel, run the same complete X/Y -> Z public API inputs
through all five original initialized resident PRGs and through a linked
operation-first PRG at two placements:

    python3 tools/research_mul24_historical_parity.py \
      --out build/mul24_donor_audit.json

The test compares **512 identical input pairs per operation**, including
the most important sign boundaries and random cases. It checks all six
product bytes, the C=0 contract, preserved X/Y inputs and stack balance.
It records source hashes and means, p95, maxima and input-sign quadrants.

## Important distinction

The resident V1–V5 public routines and independently linked compact kernels
are at different physical addresses and may rely on resident-level state
or different REU behavior. Their side-by-side cycle figures are
**research ranking evidence**, NOT authenticated operation-first speed
selection. No historical PRG is modified or embedded in the new installer.

Once a donor is selected:
1. Import **source**, not an opaque resident binary; account for tables,
   writable code, ZP and scratch, initialization and all state sharing.
2. Qualify source-linked UMUL24 and SMUL24 separately and together with
   other 56 resident APIs, twice relocated and with pinned native VICE.
3. Compare both complete calls on exactly the same corpus at the **same**
   linked origin and validate peak arithmetic frame cycles, p95/max and
   slow individual calls.
4. Preserve the 156-byte and 227-byte compact zero-ZP variants as selectable
   alternatives. Only promote a new fast donor if it earns a Pareto
   advantage; do not equate compact correctness with historical parity.

The already preserved biased quarter-square carry-neutral technique in
`docs/BIASED_QUARTERSQUARE_CARRY_OFFSETS.md` should be examined as a
candidate component for multiply donors when source compatibility allows,
rather than discarded during the migration.
