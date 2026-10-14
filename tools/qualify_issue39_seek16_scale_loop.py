#!/usr/bin/env python3
"""Research-only exact public SEEK16_INIT branch-collapse comparison.

Applies the candidate in the temporary Actions checkout only. Neither shipped
binaries nor the canonical generator are modified in the PR.
"""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mini6502 import CPU
import validate_source_build as vsb

P = ("v1_balanced", "v2_pareto_fast", "v3_reu_512k",
     "v4_reu_16m", "v5_hybrid_lowzp")
K = ("reference", "alternate")
SOURCE = ROOT / "tools/seek_kernel.py"
OLD = """        lda SK_DMAJL
        ldy SK_T
s16i_scale:
        beq s16i_scaled
        lsr SK_T
        ror
        lsr SK_EMIN
        ldy SK_T
        jmp s16i_scale
s16i_scaled:"""
NEW = """        lda SK_DMAJL
        ldy SK_T
        beq s16i_scaled
s16i_scale:
        lsr SK_T
        ror
        lsr SK_EMIN
        ldy SK_T
        bne s16i_scale
s16i_scaled:"""

def run(*args):
    subprocess.run([sys.executable, str(ROOT / "tools" / args[0]), *args[1:]],
                   cwd=ROOT, check=True)

def build():
    run("generate_sources.py")
    for kind in K:
        run("assemble_sources.py", "--profile", "all", "--config-kind", kind)
        run("build_hybrid.py", "--config-kind", kind)

def folder(profile, kind):
    return ROOT / ("build_hybrid" if profile == P[-1] else "build_source") / kind / profile

def image(profile, kind):
    d = folder(profile, kind)
    m = json.loads((d / "source_build_manifest.json").read_text())
    return (d / m["output_prg"]).read_bytes()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def cpu_from_built(profile, kind):
    c, api, io, man, _ = vsb.load(profile, folder(profile, kind).parent)
    return c, api, io, man

def mirror(c):
    return CPU(bytearray(c.mem), reu=bytearray(c.reu) if c.reu is not None else None,
               a=c.a, x=c.x, y=c.y, sp=c.sp, pc=c.pc,
               c=c.c, z=c.z, i=c.i, d=c.d, v=c.v, n=c.n)

def install_old(c, old):
    pos = old[0] | old[1] << 8
    c.mem[pos:pos + len(old) - 2] = old[2:]

def fields(c, symbols, slot):
    start = symbols["MATH_SEEK16_POS_XL"]
    # Entire eight-slot SEEK16 state, not merely the current object's XY.
    return bytes(c.mem[start:start + 248])

def flags(c):
    return (c.a, c.x, c.y, c.sp, c.c, c.z, c.i, c.d, c.v, c.n)

def prepare(c, io, sym, slot, case):
    x0, y0, x1, y1, speed = case
    c.mem[sym["MATH_SEEK16_POS_XL"] + slot] = x0 & 255
    c.mem[sym["MATH_SEEK16_POS_XH"] + slot] = (x0 >> 8) & 255
    c.mem[sym["MATH_SEEK16_POS_Y"] + slot] = y0
    c.mem[io] = x1 & 255
    c.mem[io + 1] = x1 >> 8
    c.mem[io + 4] = y1
    c.mem[io + 0x10] = speed & 255
    c.mem[io + 0x11] = speed >> 8
    c.x = slot

def corpus():
    r = random.Random(0x39A14)
    edges = [
        (0, 0, 0, 0), (0, 0, 319, 199),
        (319, 199, 0, 0), (319, 0, 0, 199),
        (255, 127, 256, 127), (256, 127, 255, 127),
        (123, 50, 123, 0), (12, 150, 300, 150),
        (60000, 0, 59999, 255), (50000, 255, 17233, 0),
        (32767, 99, 0, 99), (0, 0, 32767, 255),
        (20, 33, 20, 33), (1000, 200, 1100, 5)
    ]
    speeds = (0x0080, 0x0100, 0x0180, 0x0200, 0x0400,
              0x7E80, 0x8080, 0x8100, 0x8180, 0x8200, 0x8400,
              0xFE80)
    cases = [(a,b,c,d,s) for a,b,c,d in edges for s in speeds]
    for _ in range(288):
        x0 = r.randrange(65536)
        x1 = (x0 + r.randint(-32767,32767)) & 65535
        cases.append((x0, r.randrange(256), x1, r.randrange(256),
                      r.choice(speeds)))
    return cases

def compare(old, profile, kind, cases):
    fresh = image(profile, kind)
    assert old[:2] == fresh[:2] and len(old) == len(fresh), (profile,kind,"PRG span changed")
    baseline, new = None, None
    new, api, io, man = cpu_from_built(profile, kind)
    baseline = mirror(new)
    install_old(baseline, old)
    sym = vsb.seek_symbols(folder(profile, kind))
    assert "MATH_SEEK16_POS_XL" in sym and "MATH_SEEK16_INIT" in api
    # All differing PRG bytes must belong to the SEEK16 INIT code island.
    import generate_seek_sources as gs
    from mini6502 import Assembler
    base = "v1_balanced" if profile == P[-1] else profile
    cfg = (ROOT / "relocatable_source" / base / ("math_config_" + kind + ".inc")).read_text()
    import seek_kernel as kern
    expr, note = gs.SCRATCH[base]
    mem, labels, _ = Assembler().assemble(cfg + "\n" + kern.library(base,gs.LAYOUTS[base],expr,note))
    start = labels["seek16_init"]
    old_size = 312 if profile in (P[0],P[-1]) else 271
    diffs = [i for i,(a,b) in enumerate(zip(old[2:],fresh[2:])) if a != b]
    load = old[0] | old[1]<<8
    addresses = [load+i for i in diffs]
    assert diffs and all(start <= a < start+old_size for a in addresses), (
        profile,kind,"non-SEEK16-init byte changed",addresses[:30],hex(start))
    assert len(mem) > 0
    summary = defaultdict(lambda: [0,0,0])
    steps = 0
    for index,case in enumerate(cases):
        slot = index & 7
        prepare(new,io,sym,slot,case)
        prepare(baseline,io,sym,slot,case)
        carry = index & 1
        new.c = baseline.c = carry
        original_inputs = bytes(new.mem[io:io+0x12])
        a = baseline.call(api["MATH_SEEK16_INIT"],200000)
        b = new.call(api["MATH_SEEK16_INIT"],200000)
        assert flags(baseline) == flags(new), (profile,kind,index,"INIT registers/flags")
        assert fields(baseline,sym,slot) == fields(new,sym,slot), (profile,kind,index,"INIT state")
        assert bytes(new.mem[io:io+0x12]) == original_inputs == bytes(baseline.mem[io:io+0x12])
        is_e = bool(case[4]&0x8000)
        group = "euclidean" if is_e else "major"
        data = summary[group]
        data[0] += 1
        data[1] += a-b
        data[2] = max(data[2],a-b)
        assert a >= b, (profile,kind,index,a,b)
        # After a representative selection of INITs, run identical frame
        # sequences to arrival, including repeated post-arrival calls.
        if index % 9 == 0 and abs(case[2]-case[0]) <= 400:
            for stepper in ("MATH_SEEK16_STEP",):
                for frame in range(1100):
                    aa = baseline.call(api[stepper],50000)
                    bb = new.call(api[stepper],50000)
                    steps += 2
                    assert aa == bb, (profile,kind,index,frame,"STEP timing")
                    assert flags(baseline) == flags(new), (profile,kind,index,frame,"STEP flags")
                    assert fields(baseline,sym,slot) == fields(new,sym,slot), (
                        profile,kind,index,frame,"STEP state")
                    if new.c:
                        for _ in range(2):
                            baseline.call(api[stepper],50000)
                            new.call(api[stepper],50000)
                            steps += 2
                            assert fields(baseline,sym,slot) == fields(new,sym,slot)
                        break
                else:
                    raise AssertionError((profile,kind,index,"STEP did not arrive"))
    return {
        "baseline_prg_sha256":sha(old), "candidate_prg_sha256":sha(fresh),
        "changed_bytes":len(diffs), "changed_address_min":hex(min(addresses)),
        "changed_address_max":hex(max(addresses)), "allowed_init_start":hex(start),
        "init_pairs":len(cases), "paired_step_calls":steps,
        "cycles":{k:{"cases":v[0],"sum_saved":v[1],"max_saved":v[2],
                     "mean_saved":v[1]/v[0]} for k,v in summary.items()}
    }

def main():
    source = SOURCE.read_text()
    assert source.count(OLD) == 1 and NEW not in source, "baseline template drift"
    run("generate_seek_sources.py","--check")
    build()
    original = {(p,k):image(p,k) for p in P for k in K}
    # The baseline must reproduce shipped reference profile images.
    st=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    for p in P:
        assert sha(original[(p,"reference")]) == st["reference_prg_sha256"][p], (
            p,"baseline no longer matches shipped PRG")
    SOURCE.write_text(source.replace(OLD,NEW,1))
    run("generate_seek_sources.py")
    run("generate_seek_sources.py","--check")
    build()
    results = {}
    corpus_items = corpus()
    for p in P:
        results[p] = {}
        for kind in K:
            row = compare(original[(p,kind)],p,kind,corpus_items)
            results[p][kind] = row
            print(p,kind,"PASS",row["init_pairs"],"paired INIT calls",
                  row["changed_bytes"],"changed bytes",row["cycles"],flush=True)
    cert={"status":"PASS_SOURCE_RESEARCH_NOT_PRODUCTION",
          "candidate":"SEEK16 Euclidean scale-loop JMP->BNE branch inversion",
          "source_maps":list(K), "profiles":results,
          "baseline_cases_per_map_profile":len(corpus_items),
          "native_vice_validation":False, "release_certified":False,
          "private_optisearch_published":False}
    dest=ROOT/"validation/review/ISSUE39_SEEK16_SCALE_LOOP_RESEARCH_2026-10-14.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n")
    print("RESEARCH PASS",dest)

if __name__ == "__main__":
    main()
