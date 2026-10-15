#!/usr/bin/env python3
"""Issue144 B: disposable full-public-call 32/16 source transplant.

The shipped images and source are NOT modified in the git branch. The script
temporarily patches one generated-core source include inside its test checkout,
assembles complete V2/V3/V4 reference/alternate images, and compares the real
MATH_UDIV32_16 and MATH_UMOD32_16 entries to the immutable stock PRGs.
No private OptiSearch code is imported.
"""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_udiv32_16_integrated import load_resident, load_source, one

CORE = ROOT / "relocatable_source/division/udiv32_16_split_direct.inc"
PROFILES = ("v2_pareto_fast", "v3_reu_512k", "v4_reu_16m")
OPS = ("MATH_UDIV32_16", "MATH_UMOD32_16")


def transplant(source: str) -> str:
    out = source
    for i in range(16):
        first = f"        bcs U3216_FORCE{i}\n"
        endmark = f"U3216_NO{i}:"
        assert out.count(first) == 1, (i, "force branch")
        start = out.index(first)
        end = out.index(endmark, start)
        original = out[start:end]
        assert original.count(f"U3216_TAKE{i}:") == 1
        assert original.count(f"U3216_FORCE{i}:") == 1
        assert original.count(f"        sbc U3216_D1") == 2
        fragment = (
            f"        bcs U3216_TAKE{i}\n"
            "        cmp U3216_D1\n"
            f"        bcc U3216_NO{i}\n"
            f"        bne U3216_TAKE{i}\n"
            "        ldx U3216_R0\n"
            "        cpx U3216_D0\n"
            f"        bcc U3216_NO{i}\n"
            f"U3216_TAKE{i}:\n"
            "        tax\n"
            "        lda U3216_R0\n"
            "        sbc U3216_D0\n"
            "        sta U3216_R0\n"
            "        txa\n"
            "        sbc U3216_D1\n"
            "        sec\n"
        )
        out = out[:start] + fragment + out[end:]
    assert out.count("U3216_FORCE") == 0
    assert out != source
    return out


def cases():
    r = random.Random(0x144F3216)
    v = [(r.getrandbits(32), r.randrange(1, 65536)) for _ in range(512)]
    v += [(r.getrandbits(32), r.randrange(1, 256)) for _ in range(256)]
    v += [(r.getrandbits(32), 0) for _ in range(48)]
    ds = [1, 2, 3, 7, 255, 256, 257, 32768, 65535]
    ns = [0, 1, 2, 255, 65535, 65536, 0x7fffffff, 0x80000000, 0xffffffff]
    v += [(n, d) for d in ds for n in ns]
    v += [(r.getrandbits(32), r.randrange(1, 65536)) for _ in range(383)]
    # 1280 independent pairs including genuine uniform full-width N32 and D16=0.
    assert len(v) == 1280
    return v


def build_source_references():
    subprocess.run([sys.executable, "tools/generate_sources.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    for profile in PROFILES:
        for kind in ("reference", "alternate"):
            subprocess.run([sys.executable, "tools/assemble_sources.py",
                            "--profile", profile, "--config-kind", kind,
                            "--out", "build_u3216"], cwd=ROOT,
                           check=True, capture_output=True, text=True)


def compare():
    vectors = cases()
    digest = hashlib.sha256(b"".join(n.to_bytes(4, "little") +
                    d.to_bytes(2, "little") for n, d in vectors)).hexdigest()
    result = {"status": "PASS_SOURCE_BUILT_PUBLIC_ENTRIES", "scope":
              "nonproduction temporary source transplant", "cases": len(vectors),
              "corpus_sha256": digest, "profiles": {}}
    for profile in PROFILES:
        old, old_api = load_resident(profile)
        result["profiles"][profile] = {}
        for kind in ("reference", "alternate"):
            new, api, io = load_source(profile, kind)
            rows = {}
            for op in OPS:
                gains = []
                uniform_gains = []
                for idx, (n, d) in enumerate(vectors):
                    sp0, sp1 = old.sp, new.sp
                    c0, ok0, got0, exp = one(old, old_api[op], n, d)
                    c1, ok1, got1, _ = one(new, api[op], n, d, io)
                    assert ok0 and ok1 and got0 == got1 == exp, (
                        profile, kind, op, idx, hex(n), hex(d), got0, got1, exp)
                    assert old.sp == sp0 and new.sp == sp1
                    gain = c0-c1
                    gains.append(gain)
                    if idx < 512:
                        uniform_gains.append(gain)
                ranked = sorted(gains)
                rows[op] = {
                    "mean_saving": sum(gains)/len(gains),
                    "uniform_fullwidth_saving": sum(uniform_gains)/len(uniform_gains),
                    "slower_cases": sum(x < 0 for x in gains),
                    "fast_cases": sum(x > 0 for x in gains),
                    "worst_saving": ranked[0],
                    "p5_saving": ranked[int(0.05*(len(ranked)-1))],
                    "best_saving": ranked[-1],
                }
            result["profiles"][profile][kind] = rows
            print(profile, kind, rows, flush=True)
    print(json.dumps(result, indent=2))
    return result


def main():
    original = CORE.read_text()
    patched = transplant(original)
    print("source before/after length:", len(original), len(patched))
    try:
        CORE.write_text(patched)
        build_source_references()
        compare()
    finally:
        CORE.write_text(original)


if __name__ == "__main__":
    main()
