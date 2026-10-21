# Source-built Turbo16 standalone REU preflight package

Issue #376, experimental hardware-qualification stage. This **does not** make REU selectable in the global operation-first installer, and no old V3/V4 resident code or frozen REU image is imported.

## Build an independent loadable PRG

```sh
python3 tools/reu_turbo16_standalone_package.py --reu-kib 512 --bank 4 --out build/my-turbo16-512
python3 tools/reu_turbo16_standalone_package.py --reu-kib 16384 --bank 200 --out build/my-turbo16-16m
```

Each build creates a single 6510 load-address PRG, a manifest containing the export addresses, exact resource claims and source hashes. The source-built PRG contains a 122-byte original Turbo16 executable-ZP overlay in C64 RAM staging, its 21-byte public binder, real $92 DMA SWAP controller, source-materialized V3/V4-identical four 512-byte square-table planes, and a REU preflight/overlay upload routine. No frozen historical PRG or REU file is needed.

The **only exported lifecycle** is `T16_REU_INSTALL` then `T16_REU_BEGIN`, `T16_REU_CALL`, `T16_REU_END`. Carry set from INSTALL rejects absent/unresponsive hardware, an already initialized service, or an unsuitable CPU-port memory configuration. BEGIN/CALL/END reject uninstalled use; the existing guarded SWAP controller enforces no nesting. The original lower-level controller symbols must not be invoked directly by users. INSTALL temporarily masks IRQ while issuing DMA and restores the saved processor interrupt flag; user IRQ routines must **not** run while the exclusive executable ZP is overlaid between BEGIN and END. Nested normal math inside that lifetime is not supported.

The preflight checks real hardware transfer behavior by performing one-byte C64→REU and REU→C64 DMA at offset $FFFF of the selected bank, deliberately changing the local C64 source byte between DMA directions so an absent device cannot appear successful through unchanged RAM. For bank ≥8 it writes an independent distinct marker at offset $FFFF of the bank's low-three-bit alias and rereads the high bank; mirroring is rejected. These probes are destructive **only in declared REU-owned regions**.

## Memory ownership and limits

This first intentionally simple loadable artifact uses a **large $3000–$77FF PRG envelope** (including zero-filled gaps), plus public math I/O $C000–$C01F, all of executable ZP $3E–$B7, and the REU hardware registers $DF00–$DF0A. The selected 64KiB REU bank is exclusive; the 16MiB configuration also requires ownership of **one byte** at `(bank & 7):$FFFF` to reject smaller-device aliasing. The machine must map I/O2 as I/O, and nothing else may use those REU registers during the service. Callers supply any known reservations explicitly:

```sh
python3 tools/reu_turbo16_standalone_package.py --out build/my-turbo16 \
  --reserved-zp 0x02-0x2f --reserved-ram 0x9000-0x9fff \
  --reserved-reu-bank 2
```

Overlaps are fatal, not warnings. For an existing operation-first project, add `--stock-manifest build_my_math/selective_manifest.json` to import the **actual installed stock code span, public I/O, scratch and ZP reservations** and fail closed on collisions, including reported game/IRQ reservations. If the stock manifest includes persistent SEEK or other object state without an exact per-family extent, the preflight intentionally rejects it rather than guessing. This is a read-only coexistence audit, **not** automatic global memory reallocation. The PRG is **not** suitable for linking into a random project or existing operation-first PRG without the still-missing global allocator integration. In particular, stock math might occupy the reserved PRG envelope; `--reserved-ram` must cover application *and stock-library* placements. A declared size is not treated as an actual hardware size until the runtime DMA/alias check passes.

## Qualification

```sh
python3 -m unittest discover -s tools -p 'test_reu_turbo16_standalone_package.py' -v
VICE_WRAPPER=/path/to/pinned/x64sc python3 tools/native_reu_turbo16_standalone.py \
  --out build/reu-native/preflight.json
```

The native regression (pinned VICE r46284 CI) runs four cases: no REU, correct 512KiB, correct 16MiB, and 512KiB hardware deliberately given a 16MiB package. It checks that the failed cases do not activate or corrupt the overlay, and that both successful sizes produce two math batches and exactly restore the caller's ZP after each END.

This first stage does **not** prove full real-time VIC contention/IRQ coexistence, hardware DMA cycle timings, mixed-source global placement, original V3/V4 full-ABI parity, source independent mathematical table regeneration, or automatic operation-first REU selection. Preserve the normal 56 stock APIs and all existing historical compatibility assets.
