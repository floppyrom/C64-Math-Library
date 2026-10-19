# Original V1/V5 VEC2_NORMALIZE_Q8_8 measured public-call speed

The operation-first installer already links the certified historical V1/V5
VEC2 log-ratio normalized Q8.8 -> signed Q1.15 source. This migration
**authenticates speed selection for the unchanged kernel**; it does not
introduce a slower portable replacement or change any historical binaries.

## Canonical public and memory contract

- Source: `routines/vector/vec2_normalize_q8_8_source.asm`
- Variant: `link:certified-stock`, one independently linkable 3,587-byte
  page-aligned code+table image (plus 0–255 bytes alignment padding),
  four exclusive ZP bytes, no ordinary scratch, 32-byte public I/O
- Inputs: signed Q8.8 X16 and Y16 at public I/O +0 and +4, preserved
- Outputs: signed Q1.15 X16 and Y16 at I/O +8..+11; C=1 iff zero vector
- Historical code uses NMOS LAX and exactly bounded self-modifying
  `LDX abs,Y` address high bytes in the quadrant code region. The
  module explicitly requires **writable executable RAM**, not ROM
- Exactly the original certified 2,560 ratio/log/component table bytes
  and original full-domain angular/magnitude error certificate remain
  intact; no REU, hardware initialization or rewritten approximation

## Public timing qualification

Measure **512 identical deterministic signed input pairs** including all
20×20 edge combinations and additional repeatable cases. Source-model
measurements include complete public entry-through-RTS cycles (mean,
95th percentile and maximum), Q1.15 outputs, carry, preserved X/Y,
stack depth, exact aligned RAM/ZP resources and canonical source SHA.
Two RAM origins (`$8000`, `$7123`) and independent I/O/ZP placements
are required.

The original SMC instructions are audited so only the exact high operand
bytes of up to eight `LDX abs,Y` instructions can change. The original
`test_selective_vec2_normalize.py` precision regression remains active,
and pinned headless VICE r46284 validates 96 public calls at each origin.

This is **not** physical PAL/VIC-II badline/IRQ timing; busiest-frame
cycle budgets still require application-specific scheduling. With the
original source as the only variant, speed objective authenticates the
existing behavior and must fail closed on insufficient memory or ZP.

Historical profiles remain available until all 56 independently linkable
operations and hardware-dependent services meet the complete performance
parity and reliability acceptance gates.
