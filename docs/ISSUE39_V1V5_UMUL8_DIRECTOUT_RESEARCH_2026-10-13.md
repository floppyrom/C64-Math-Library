# Issue39: V1/V5 UMUL8 direct low-result store (unpromoted research)

Research-screen record, 13 October 2026. **Not a release or public-ABI change.**

The public V1/V5 8×8 wrapper traditionally reads the low product byte
from a transient zero-page slot after the arithmetic core has calculated
it. The candidate stores that byte directly into the public output slot.
The wrapper can return immediately after writing the high byte. The
private core grows by one byte into existing padding; the public slot
shrinks its reachable tail. Only 11 old-address bytes differ.

Source-only research include:
`relocatable_source/v1_balanced/umul8_directout_trial.inc`.
It is deliberately **not** wired into shipped source generation and does
not modify reference images.

`tools/screen_issue39_v1v5_umul8_directout.py` exhaustively compares
all 65,536 operands for each profile, checks product, public input,
carry, stack, and output sentinel, and checks the same six-cycle
saving on each input. Run:
```sh
python3 tools/screen_issue39_v1v5_umul8_directout.py
```

Preliminary independent archived-image workbench: 65,536/65,536
per profile PASS; CPU-model means 90.490234 → 84.490234
(−6 cycles every call). Reference V1 and V5 builds change exactly
11 bytes in their resident images and do not increase PRG span or ZP.
An alternate V1 build also completed.

Preliminary native VICE 3.13.2 on archived images: 256 complete
public calls (64 old + 64 new for each of V1 and V5), equal product,
inputs, carry, stack, and output sentinels. As with earlier V2 UMUL8
direct-output work, non-carry N/Z/V flags differ; these are not
guaranteed by the public contract. Native cycles were **not**
measured.

Still required before production promotion: replay from current main
source-built residents, reference + alternate maps, V5 hybrid,
signed/unsigned mixed-call isolation, standalone source regeneration,
native VICE replay against current residents, checksum/package audits,
and new performance tables. Keep issue #39 OPEN. No private
OptiSearch source is included.
