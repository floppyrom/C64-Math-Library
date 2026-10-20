# Native PAL verification of the signed-only D65536 installed winner

The operation-first CPU-model [nine-plan frame replay](D65536_FRAME_CHOICES.md)
selects **FAST31 + original unsigned V2 + signed D65536** for this exact
150-call/24-frame arithmetic history: peak 13,849 modeled CPU+JSR
cycles with 8,992 B worst-placement RAM and 31 ZP. Selecting both
signed and unsigned D65536 instead gives 13,897 modeled peak cycles
and 9,213 B RAM.

`tools/native_installed_d65536_pal.py` independently validates whether
that source-model resource/PAL choice survives an *actual native*
VIC/CIA elapsed-slot measurement in pinned x64sc r46284. It uses the
**ordinary production linker**, no temporary source-emitter patch, to
build and compare three exact seven-API public plans:

- FAST31, signed and unsigned stock V2
- FAST31, signed and unsigned D65536
- FAST31, unsigned stock V2 and signed D65536

Each PRG's SHA256, seven pinned public variants, source-file SHA256s,
public entry addresses, exact RAM and ZP are checked against the
two-relocation, fully replay-registered frame evidence. The independent
native probe executes each of the same 24 original synthetic frames
with the VIC text display disabled and enabled, capturing CIA Timer A/B
PHI2 elapsed slots and every call's public result and carry. All
three native samples of a frame must agree on input-history and
public-output SHA; incomplete/duplicate samples are rejected.

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 -m unittest discover -s tools -p 'test_native_installed_d65536_pal.py' -v
python3 tools/native_installed_d65536_pal.py \
  --out build/registered/d65536-installed-native-three-plan-pal.json
```

The report gives true native elapsed slots, display-steal overhead,
per-frame nominal headroom, worst burst, missed *isolated-burst*
deadlines, and fully qualified physical PRG/source provenance.

## Verified pinned native results (x64sc r46284)

CI completed **144 independent PAL/VIC/CIA burst probes** on the three
*ordinary installed* PRGs. All 24 original synthetic frames were
checked with display on and off, and every source plan produced
identical public result/carry and input-history hashes.

| Seven-operation installed source plan | Worst VIC-on slots | Worst-frame margin | Linked RAM, $4123 map | Missed bursts |
|---|---:|---:|---:|---:|
| Original FAST31 + signed/unsigned V2 | 19,883 | −227 | 8,957 B | 1/24 |
| FAST31 + both signed/unsigned D65536 | 17,618 | +2,038 | 9,213 B | 0/24 |
| **FAST31 + unsigned V2, signed D65536** | **17,580** | **+2,076** | **8,957 B** | **0/24** |

All peaks occurred in synthetic frame 8. Signed-only saves **2,303
native PHI2 slots** relative to stock, beats both-fast-path by **38
slots**, and preserves exactly the stock RAM/ZP allocation at this map.
It therefore demonstrates an actual whole-plan Pareto gain, not just
the source CPU-model improvement. All results remain workload-specific.
The qualified signed-only linked PRG SHA256 is
`9c8911e0d785520b4cf4bc57947a81bd80f9ea62029fd7ec70963024faec5fa5`.

**This is not a real 50 Hz application.** Every frame is a separate
raster-aligned math burst with instrumented operand staging; interrupts
are disabled, and no SID player, sprites, REU DMA or game logic runs.
Even a peak below 19,656 PAL slots only leaves nominal room for work
not yet measured. Production profile retirement requires continuous
frame playback with real interrupts/music/VIC/REU application workload.
