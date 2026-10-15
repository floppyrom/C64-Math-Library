#!/usr/bin/env python3
"""Issue144 V5 derived V1 root proof on real NMOS 6510 via native x64sc.

Narrow root-only test. Does not certify the full imported V5 mixed-call ABI
or external IRQ/NMI concurrency, and does not measure wall/bus cycles.
"""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
from pathlib import Path

from issue144_v5_isqrt32_inheritance_screen import pair, PROFILE
from native_issue144_isqrt32_normal_resident import native, E


def main():
    vice = os.environ.get("VICE_WRAPPER")
    assert vice, "native V5 root proof needs VICE_WRAPPER=x64sc"
    report = {"status": "PASS_V5_ROOT_NATIVE", "native_public_calls": 0,
              "reference_images_unchanged": True, "full_hybrid_mixed_not_proven": True,
              "physical_wall_bus_time_not_measured": True, "maps": {}}
    with tempfile.TemporaryDirectory(prefix="issue144_v5_root_vice_") as name:
        tmp = Path(name)
        for i, layout in enumerate(("reference", "alternate")):
            old, new, vals, touched, manifest, oldhash = pair(layout, tmp / layout)
            api = {"MATH_INIT": vals["REG_API"] + 0x280,
                   "MATH_ISQRT32": vals["REG_GAME_API"] + 0x30}
            io = vals["MATH_IO"]
            orig = native(PROFILE, layout, old, api, io, 24820 + 4*i, tmp, vice)
            opt = native(PROFILE, layout, new, api, io, 24821 + 4*i, tmp, vice)
            assert orig == opt, (layout, "native 6510 root/carry/status mismatch")
            report["maps"][layout] = {
                "status": "PASS_48_NATIVE_PUBLIC_CALLS", "calls": len(E)*2,
                "changed_resident_bytes": len(touched),
                "identical_capture_sha256": hashlib.sha256(orig).hexdigest(),
                "public_root_status_equal": True}
            report["native_public_calls"] += 2*len(E)
            print("V5 INHERITED ROOT X64SC", layout, "PASS", 2*len(E), flush=True)
    assert report["native_public_calls"] == 96
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
