# Turbo16 quarter-square lookup tables: source-backed module

This phase builds the four exact **512-byte lookup planes** required by the
Turbo16 executable overlay without extracting them from a historical binary
as a runtime build dependency.

The bytes are materialized directly from checksum-locked historical
`relocatable_source/v3_reu_512k/math_relocatable.asm` and
`relocatable_source/v4_reu_16m/math_relocatable.asm`. The 6-KiB REG_TABLE
prefix is parsed in both sources. Four planes at offsets `$1000`, `$1200`,
`$1400`, and `$1600` must match **exactly** between both historical source
tiers; frozen V3 and V4 resident PRGs serve only as independent test oracles.
Any source hash change, data nonliteral, disagreement, or incorrect size
causes the build to fail.

```sh
python3 tools/reu_turbo16_source_tables.py --out build/turbo16-source-tables
python3 -m unittest discover -s tools -p 'test_reu_turbo16_source_tables.py' -v
```

The output contains four 512-byte planes and a manifest with source hashes
and output hashes. It does *not* require copying V3/V4 PRG bytes to produce
the lookup payload.

**Qualification boundary:** these are faithfully materialized historical
source constants, **not** an independent mathematical re-derivation of the
optimized quarter-square offsets. Likewise, table extraction does not
provide REU DMA BEGIN/END, memory/bank allocation, an installable PRG/REU,
or native REU VICE proof. The existing operation-first 56-operation
installer still has no selectable Turbo16 REU backend.

The subsequent milestone is to combine these verified source tables with
the executable Turbo16 kernel, CALL binder and experimental SWAP lifecycle,
then verify the assembled package and real native REU hardware timing.
