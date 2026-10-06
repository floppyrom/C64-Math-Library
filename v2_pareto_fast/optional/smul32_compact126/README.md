# Optional compact126 SMUL32 overlay — V2 Pareto-Fast

This directory exposes the exact validated `compact126` signed 32x32 -> 64 kernel for V2 as a **manual exclusive overlay source**. It is not selected by the fixed resident 54-entry API.

V2 has enough aggregate ZP capacity, but the record kernel overlaps resident executable state. Before entering this mode, preserve and later restore:

- ZP: `$0A-$1F` and `$8E-$FF`
- page $01 executable interval: `$0100-$017D`
- ordinary RAM executable intervals: `$1200-$12F2` and `$1300-$133A`
- quarter-square data: the existing `$7000/$7200/$7400/$7600` table family

Do not execute normal profile code that uses the overlaid state until it has been restored. V2 has no dedicated BEGIN/END lifecycle for this alternate, so save/restore is the integrator's responsibility.

See `../../../docs/SMUL32_COMPACT126.md` and `../../../validation/records/SMUL32_COMPACT126_100K.json`.
