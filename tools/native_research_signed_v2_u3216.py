#!/usr/bin/env python3
"""Native VICE r46284 Q/R/C proof for historical V2 magnitude signed32/16."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import native_selective_sdiv32_16 as native
import research_signed_v2_u3216 as candidate


def main():
    vice = os.environ.get("VICE_WRAPPER", "")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must identify installed pinned x64sc")
    calls = 0
    with tempfile.TemporaryDirectory(prefix="native_signed_v2_3216_") as d:
        root = Path(d)
        for seq, (code, io, zp) in enumerate(
                ((0x8000, 0xC000, 0x50), (0x7123, 0xC040, 0x70))):
            packed, labels, meta = candidate.assemble(code, io, zp)
            image = bytes((code & 255, code >> 8)) + bytes(
                packed[a] for a in range(code, code + candidate.IMAGE_BYTES))
            for alias in ("FAST_SDIV32_16_V2MAG", "FAST_SMOD32_16_V2MAG"):
                tag = "signed_v2mag_%04x_%s" % (code, alias)
                digest = native.verify(
                    vice, image, labels[alias], code, io, tag,
                    8350 + seq*2 + (alias.startswith("FAST_SMOD")), root)
                calls += native.N
                print("NATIVE SIGNED V2 MAGNITUDE", tag, "PASS",
                      native.N, digest, flush=True)
    assert calls == 2*2*native.N
    print("NATIVE SIGNED V2 MAGNITUDE RELOCATABLE PUBLIC ABI PASS", calls, flush=True)


if __name__ == "__main__":
    main()
