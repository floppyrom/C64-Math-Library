# Frame 8: matched public-call source-model hotspot attribution

The independently raster-synchronised [24-frame PAL/VIC/CIA sweep](NATIVE_PAL_24_FRAME_SWEEP.md)
found that the 31-ZP FAST31/table-ISQRT/V2 unsigned-and-signed DIV/MOD
configuration requires **19,883 native PAL PHI2 slots** for synthetic frame
8 with normal text display. Its *isolated synthetic burst* exceeds the
nominal PAL 19,656-slot budget by **227 slots**. The compact 0-ZP
configuration takes 66,031 slots on the same frame and input history.

The next question is: **which public calls are worth optimizing first?**

`tools/frame8_source_hotspots.py` provides explicit and reproducible
source-model attribution. It relinks both **exact** source choices through
the production operation-first linker at the qualified `$4123/$C040/$70`
map. It executes the complete deterministic public ABI benchmark again,
checks matched original frame/ordinal/operation/input digests, then ranks
the frame-8 calls and the seven operation families by **source-model
entry-through-RTS cycles plus six JSR cycles**. It reports modeled cycle
savings for the *same inputs*, preserving PRG and source SHA provenance.

Run it on its own for **modeled** hotspots:

```sh
python3 tools/frame8_source_hotspots.py --frame 8 \
  --out build/pal-vic-cia/frame8-model-hotspots.json
```

Or combine that ranking with the **actual independent native whole-burst
measurements**:

```sh
python3 tools/frame8_source_hotspots.py --frame 8 \
  --native-sweep build/pal-vic-cia/24-native-bursts.json \
  --out build/pal-vic-cia/frame8-source-attribution.json
```

The native input is rejected if any required frame/display combination,
exact installed PRG hash, public call count, identity digest, output/carry
digest, source choice, or prior measured summary differs from the original
registered workload. These validation checks prevent casually pairing
unrelated binaries or traces with source-model calls.

**Crucial:** The native CIA timer measured an entire native burst *with*
operand stores, output capture and VIC contention. It did **not** measure
entry-to-RTS cycles for each public call separately. The per-call and
per-operation rankings are therefore explicitly **source CPU-model
attribution**, not experimentally measured hardware hotspot values.
Subtracting modeled component costs from the native whole-burst length
is not a physical PAL speedup proof. A new kernel must still be built
and verified under native x64sc against identical ABI inputs at both
relocations, then remeasured using this exact full-frame native probe.

The tool does not modify V1–V5, REU/Turbo/QS16 compatibility, source
selection or performance-frontier registrations. The next acceptance
goal is measurable worst-frame savings, not improving unrelated averages.
