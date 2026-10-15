#!/usr/bin/env python3
"""Issue #144 C: independently prove V5 inherited V1-root ISQRT32 trial.

Research only: modifies the in-memory V5 hybrid build, NEVER canonical
V1/V5 source, reference PRG/REU or published performance.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
import statistics
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from assemble_sources import parse_config
from build_hybrid import build as build_hybrid, load_prg
from issue144_v1_isqrt32_normal_resident_feasibility import probe
from mini6502 import CPU
from validate_unsigned_division import rd, wr

PROFILE = "v5_hybrid_lowzp"
HELPER = 0x0AA8


def corpus():
    rng = random.Random(0x14450015)
    nums = [0, 1, 2, 3, 4, 7, 15, 16, 17, 255, 256, 257, 65535,
            65536, 65537, 0x12345678, 0x7FFFFFFF, 0x80000000,
            0x80000001, 0xFFFFFFFE, 0xFFFFFFFF]
    nums += [rng.getrandbits(32) for _ in range(1280)]
    for root in (0, 1, 2, 3, 7, 15, 127, 255, 256, 257, 1023, 32767, 65535):
        for off in (-1, 0, 1):
            n = root * root + off
            if 0 <= n <= 0xFFFFFFFF:
                nums.append(n)
    return list(dict.fromkeys(nums))


def pair(layout: str, outdir: Path):
    cfg = ROOT / "relocatable_source" / PROFILE / ("math_config_" + layout + ".inc")
    v = parse_config(cfg)
    geometry, v1_pair = probe(layout, HELPER)
    assert v1_pair is not None, geometry
    v1_before, v1_after, v1_api, v1_io = v1_pair
    manifest = build_hybrid(cfg, outdir)
    raw, lo, hi = load_prg(outdir / manifest["output_prg"])
    start = v["REG_GAME"] + 0x0A40
    stop = v["REG_GAME"] + 0x0AE0
    assert len(raw) == 65536
    assert v1_api == v["REG_GAME_API"] + 0x30
    assert v1_io == v["MATH_IO"]
    assert manifest["normal_zp_bytes"] == 31
    # Guard against V5 importing or overwriting even one byte of the
    # original V1 resident root interval, including the unused helper area.
    for a in range(start, stop):
        assert raw[a] == v1_before.mem[a], (
            layout, "V5/V1 resident ownership drift", hex(a),
            raw[a], v1_before.mem[a])
    touched = [a for a in range(start, stop)
               if v1_before.mem[a] != v1_after.mem[a]]
    assert touched, "empty candidate"
    modified = bytearray(raw)
    for a in touched:
        modified[a] = v1_after.mem[a]
    assert all(raw[a] == modified[a] for a in range(65536)
               if not (start <= a < stop))
    assert raw[v1_api] == modified[v1_api] == 0x4C
    assert bytes(raw[v1_api:v1_api+3]) == bytes(modified[v1_api:v1_api+3])
    assert (raw[v1_api+1] | (raw[v1_api+2] << 8)) == start
    assert all(raw[a] == modified[a] for a in range(v["MATH_IO"], v["MATH_IO"] + 0x20))
    def cpu(mem):
        c = CPU(bytearray(mem))
        c.d = 0
        c.call(v["REG_API"] + 0x280, 2_000_000)
        return c
    return cpu(raw), cpu(modified), v, touched, manifest, hashlib.sha256(bytes(raw)).hexdigest()


def model(layout: str, outdir: Path, count=None):
    old, new, v, touched, manifest, digest = pair(layout, outdir)
    io = v["MATH_IO"]
    entry = v["REG_GAME_API"] + 0x30
    root16 = v["REG_GAME_API"] + 0x2D
    cases = corpus() if count is None else corpus()[:count]
    changes = []
    for i, n in enumerate(cases):
        for c in (old, new):
            wr(c.mem, io + 0x10, n, 4)
            c.x = (11*i) & 255
            c.y = (29*i) & 255
            c.c = i & 1
        old_sp, new_sp = old.sp, new.sp
        t_old = old.call(entry, 500_000)
        t_new = new.call(entry, 500_000)
        expected = math.isqrt(n)
        assert rd(old.mem, io+8, 2) == rd(new.mem, io+8, 2) == expected, (layout, hex(n))
        assert old.c == new.c == 0, (layout, hex(n), "carry")
        assert rd(old.mem, io+0x10, 4) == rd(new.mem, io+0x10, 4) == n
        assert old.x == new.x and old.y == new.y, (layout, hex(n), "registers")
        assert old.sp == old_sp and new.sp == new_sp, (layout, hex(n), "stack")
        changes.append(t_old - t_new)
        if i % 37 == 0:
            # Mixed root16/root32 sequential ownership smoke test,
            # not a full 56-entry IRQ/NMI or mixed-call certification.
            for c in (old, new):
                wr(c.mem, io+0x10, n & 0xFFFF, 2)
            old.call(root16, 500_000)
            new.call(root16, 500_000)
            assert rd(old.mem, io+8, 2) == rd(new.mem, io+8, 2) == math.isqrt(n & 0xFFFF)
    assert changes and min(changes) > 0, (layout, min(changes))
    v_sorted = sorted(changes)
    return {
        "layout": layout, "status": "PASS_V5_SOURCE_INHERITANCE_MODEL",
        "paired_root32_calls": len(changes),
        "root16_interleaving_smokes": (len(cases)+36)//37,
        "mean_cycles_saved": statistics.mean(changes),
        "min_cycles_saved": v_sorted[0],
        "p95_cycles_saved": v_sorted[int(0.95*(len(v_sorted)-1))],
        "max_cycles_saved": v_sorted[-1],
        "slower_cases": sum(x < 0 for x in changes),
        "changed_resident_bytes": len(touched),
        "resident_addresses_first": [hex(a) for a in touched[:4]],
        "no_normal_zp_growth": True, "no_caller_owned_ram": True,
        "v5_hybrid_source_sha256": manifest["source_inputs"]["v1_source_sha256"],
        "v5_baseline_memory_sha256": digest,
        "v5_full_56_api_mixed_native_not_yet_qualified": True,
        "published_images_unchanged": True,
    }


def main():
    with tempfile.TemporaryDirectory(prefix="issue144_v5_isqrt_inherit_") as temp:
        root = Path(temp)
        result = {kind: model(kind, root/kind) for kind in ("reference", "alternate")}
        assert result["reference"]["mean_cycles_saved"] == result["alternate"]["mean_cycles_saved"]
        print(json.dumps({"status": "PASS_V5_INHERITANCE_RESEARCH",
                          "maps": result, "canonical_source_modified": False},
                         indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
