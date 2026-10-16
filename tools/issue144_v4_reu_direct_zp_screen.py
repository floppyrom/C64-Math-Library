#!/usr/bin/env python3
"""Independent opt-in V4 REU->ZP root screen, never mutates canonical V4.

Reassembles current-main source and optional direct-ZP source in a disposable
clone, compares ordinary full-domain public calls, ABI and native x64sc.
The same eight ZP bytes are permuted; volatile temporary ZP byte snapshots
are NOT a public ABI contract. Physical REU/VIC/IRQ safety remains open.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import statistics
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))
from mini6502 import CPU

PROFILE = "v4_reu_16m"
MOD = "relocatable_source/v4_reu_16m/isqrt32_reu_prefix.asm"
OPTION = "optional/issue144_v4_isqrt32_direct_reu_zp/v4_reu_16m.asm"
EDGE = [0, 1, 2, 3, 4, 7, 15, 16, 17, 255, 256, 257, 65535,
        65536, 65537, 0x7fffffff, 0x80000000, 0xffffffff]


def build(repo, layout, out):
    args = [sys.executable, str(repo/"tools/assemble_sources.py"),
            "--profile", PROFILE, "--config-kind", layout,
            "--out", str(out)]
    subprocess.run(args, cwd=repo, check=True, capture_output=True, text=True)
    profile = out / layout / PROFILE
    man = json.loads((profile/"source_build_manifest.json").read_text())
    prg = profile/man["output_prg"]
    reu = profile/man["reu_image"]["file"]
    assert hashlib.sha256(prg.read_bytes()).hexdigest()==man["output_sha256"]
    assert hashlib.sha256(reu.read_bytes()).hexdigest()==man["reu_image"]["sha256"]
    return prg, reu, man


def cpu(prg, reu):
    # Match the repository's proven source-test loader *exactly*. The native
    # README's public entry coordinates are not an initialization substitute.
    from validate_source_build import load
    c,pub,io,manifest,initcycles = load(PROFILE,prg.parent.parent)
    assert pub["MATH_ISQRT32"]==0x5e30, (pub["MATH_ISQRT32"],manifest)
    assert io==0xc000 and Path(manifest["_resolved_reu_path"]).read_bytes()==reu.read_bytes()
    assert c.mem[0x5e30]==0x4c, ("bad public JMP before first call",c.mem[0x5e30])
    return c


def inp_cases():
    r = random.Random(0x144d1ec7)
    out = list(EDGE)
    for k in (0,1,3,15,255,256,1023,4095,16383,32767,65535):
        for n in (k*k-1,k*k,k*k+1):
            if 0<=n<=0xffffffff:out.append(n)
    out.extend(r.getrandbits(32) for _ in range(1024))
    return list(dict.fromkeys(out))


def call(c,n):
    c.mem[0xc010:0xc014]=n.to_bytes(4,"little")
    saved_n=bytes(c.mem[0xc010:0xc014])
    sp=c.sp
    cycles=c.call(0x5e30, 2_000_000)
    got=int.from_bytes(c.mem[0xc008:0xc00a],"little")
    if got!=math.isqrt(n):
        print("DEBUG_BAD_ROOT",hex(n),"got",got,"expected",math.isqrt(n),
              "prg-entry",bytes(c.mem[0x5e30:0x5e33]).hex(),
              "zp",bytes(c.mem[0x54:0x5c]).hex(),
              "scratch",bytes(c.mem[0xc020:0xc024]).hex(),
              "reu-reg",bytes(c.mem[0xdf02:0xdf0b]).hex(),
              flush=True)
        raise AssertionError((hex(n),got,math.isqrt(n)))
    assert bytes(c.mem[0xc010:0xc014])==saved_n and c.c==0 and c.sp==sp
    # The REU C64 buffer register must again identify its original $C020
    # scratch address so that unrelated REU clients do not inherit $0054.
    assert c.mem[0xdf02]==0x20 and c.mem[0xdf03]==0xc0, (
        "REU C64 destination not restored",hex(c.mem[0xdf02]),hex(c.mem[0xdf03]))
    return cycles,(got,c.c,c.n,c.z,c.a,c.x,c.y,c.sp)


def compare(old, new, reu, vectors):
    a=cpu(old,reu); b=cpu(new,reu)
    deltas=[]
    for n in vectors:
        x,sa=call(a,n)
        y,sb=call(b,n)
        assert sa==sb,("public register/status difference",hex(n),sa,sb)
        deltas.append(x-y)
    return {"same_inputs":len(vectors),
            "mean_saved_cycles":statistics.fmean(deltas),
            "median_saved_cycles":statistics.median(deltas),
            "minimum_saved_cycles":min(deltas),
            "maximum_saved_cycles":max(deltas),
            "slower_calls":sum(x<0 for x in deltas),
            "cycles_by_class":{"zero":deltas[0],"max":deltas[EDGE.index(0xffffffff)]}}


def main():
    source=(ROOT/MOD).read_text()
    candidate=(ROOT/OPTION).read_text()
    assert source!=candidate
    assert candidate.count("sta $DF01")==1
    assert candidate.count("sta $DF02")==2
    assert candidate.count("sta $DF03")==2
    assert "IS32_ROOT0  = ZP_MAIN+$52" in candidate
    assert "IS32_RES0   = ZP_MAIN+$54" in candidate
    assert "lda #<REU_SCRATCH" in candidate
    corpus=inp_cases()
    with TemporaryDirectory(prefix="issue144_v4_direct_zp_") as tmpname:
        tmp=Path(tmpname)
        clone=tmp/"checkout"
        shutil.copytree(ROOT,clone,ignore=shutil.ignore_patterns(
            ".git","__pycache__","build_source","build_hybrid","build_pareto"))
        path=clone/MOD
        results=[]
        for layout in ("reference","alternate"):
            path.write_text(source)
            old_prg,old_reu,man0=build(clone,layout,tmp/"old")
            path.write_text(candidate)
            new_prg,new_reu,man1=build(clone,layout,tmp/"new")
            assert old_reu.read_bytes()==new_reu.read_bytes()
            if layout=="reference":
                from validate_source_build import validate as full_baseline_validator
                baseline_test=full_baseline_validator(PROFILE,tmp/"old"/layout)
                print("BASELINE_FULL_VALIDATOR",baseline_test["status"],baseline_test["machine_calls"],flush=True)
            m=compare(old_prg,new_prg,new_reu,corpus)
            assert m["minimum_saved_cycles"]>=0 and m["mean_saved_cycles"]>0,m
            m["layout"]=layout
            m["old_prg_sha256"]=hashlib.sha256(old_prg.read_bytes()).hexdigest()
            m["new_prg_sha256"]=hashlib.sha256(new_prg.read_bytes()).hexdigest()
            m["reu_sha256"]=hashlib.sha256(new_reu.read_bytes()).hexdigest()
            # Full all-56 API source validator; this also catches REU transport
            # lifetime interactions with ordinary math calls and root state.
            from validate_source_build import validate
            validation=validate(PROFILE,tmp/"new"/layout)
            assert validation["status"]=="PASS" and validation["public_entries_executed"]==56
            m["full_public_calls"]=validation["machine_calls"]
            results.append(m)
        native="NOT_RUN_NO_VICE_WRAPPER"
        if os.environ.get("VICE_WRAPPER"):
            # Existing independent full REU native root harness, same input
            # corpus, 24 baseline + 24 candidate real x64sc calls.
            from issue144_v4_isqrt_maskshift_source_native_qualify import native as native_root
            b=native_root(os.environ["VICE_WRAPPER"],tmp/"old/reference/v4_reu_16m/math_v4_reu_16m_source_built.prg",
                          tmp/"old/reference/v4_reu_16m/c64_math_v4_reu_16m_source_built.reu",20511,tmp)
            c=native_root(os.environ["VICE_WRAPPER"],tmp/"new/reference/v4_reu_16m/math_v4_reu_16m_source_built.prg",
                          tmp/"new/reference/v4_reu_16m/c64_math_v4_reu_16m_source_built.reu",20512,tmp)
            assert b==c,"native outputs or captured carry differ"
            native={"status":"PASS_REAL_EMULATOR","paired_root_calls":24,
                    "output_sha256":hashlib.sha256(c).hexdigest()}
    assert len(results)==2
    print(json.dumps({"status":"PASS_RESEARCH_OPTIN_NO_DEFAULT_CHANGE",
                      "contract":"same 8 byte normal ZP workspace, direct REU DMA root+residual, restored REU C64 address",
                      "corpus_sha256":hashlib.sha256(b"".join(n.to_bytes(4,"little") for n in corpus)).hexdigest(),
                      "native":native,"maps":results,
                      "historical_prgs_reu_modified":False,
                      "hardware_timing_certified":False},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
