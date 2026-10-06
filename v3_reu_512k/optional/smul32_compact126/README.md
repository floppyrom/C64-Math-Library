# Optional compact126 SMUL32 overlay — V3 REU 512K

This directory exposes the exact validated `compact126` signed 32x32 -> 64 kernel for V3 as an **exclusive Turbo-style overlay source**. It is not selected by the fixed resident 54-entry API.

A production BEGIN/END wrapper must preserve and restore:

- ZP: `$0A-$1F` and `$8E-$FF`
- page $01 executable interval: `$0100-$017D`
- ordinary RAM executable intervals: `$1200-$12F2` and `$1300-$133A`

Do not install the overlay persistently: it overlaps resident executable-ZP and ordinary-RAM profile state, including normal multiply/Turbo ownership. The resident quarter-square data at `$7000/$7200/$7400/$7600` can be shared.

See `../../../docs/SMUL32_COMPACT126.md` and `../../../validation/records/SMUL32_COMPACT126_100K.json`.
