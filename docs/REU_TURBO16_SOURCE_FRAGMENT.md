# Turbo16 independently relocatable source fragments — first executable step

This is an **experimental source build**, not native operation-first REU
support. V3/V4 historical compatibility bundles remain unchanged and must
never be concatenated with the generated selective math PRG.

The source of the Turbo16 arithmetic body is the already-present, historical
source-qualified `relocatable_source/turbo/turbo16_overlay.asm`.
The public direct-output CALL binder comes from the existing
`relocatable_source/turbo/turbo16_runtime.asm`. Both are read
as exact SHA256SUMS-locked source rather than copied from a resident binary.

Build only the two executable fragments:

```sh
python3 tools/reu_turbo16_fragment.py --out build/turbo16-fragments
python3 tools/reu_turbo16_fragment.py --zp-base 0x20 --math-io 0xc040 \
  --table-base 0x5000 --api-base 0x4000 \
  --out build/turbo16-altmap
```


The assembler checks that the overlay is **122 contiguous bytes of
executable 6510 code in zero page**, the binder fits one 64-byte slot,
its ABI entry agrees with the reference +2 entry, the public math I/O
does not overlap its tables or code, and that the two placements build
independently. A manifest reports exact source SHA, output segment SHA,
relocation, and the four 512-byte square table dependencies.

This deliberately does not fabricate the 2 KiB square tables, build an
REU bank payload, implement BEGIN/END DMA, preserve caller ZP state,
or prove two-batch behavior. The resulting source-assembled fragment is
**not directly usable by a user** and is never advertised as `link:REU`.
The operation-first builder still only selects qualified non-REU stock
routines. Run the test:

```sh
python3 -m unittest discover -s tools -p 'test_reu_turbo16_fragment.py' -v
```


Next milestone for [independently linkable Turbo16](https://github.com/floppyrom/C64-Math-Library/issues/376):
source-backed tables and REU DMA BEGIN/END, exact ZP save/restore and
exclusive ownership, then identical-input V3/V4 and native VICE regression
at 512 KiB and 16 MiB. Only that can qualify real selectable REU support.
