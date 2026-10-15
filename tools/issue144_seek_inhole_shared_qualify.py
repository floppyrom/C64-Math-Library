#!/usr/bin/env python3
"""Issue144 D: source-reproduced in-resident SEEK16 acceleration using freed U3216 RAM.

Opt-in research only. Builds both inputs from *current* source inside a temporary
checkout; never patches the release working tree. Public CPU-model and x64sc
checks preserve every SEEK16 state byte, carry, X, SP and following STEP.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"routines/movement"))
from mini6502 import CPU
from benchmark_seek_profiles import api,corpus,SPEEDS,EUCLID
from seek_model import expected_frames
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
SHARED="relocatable_source/division/udiv32_16_split_direct.inc"
OPT_SHARED="optional/issue144_u3216_shared_take_inline/udiv32_16_split_direct_shared.inc"
ALT="optional/issue144_seek_inhole_shared"
REU_NAMES={"v3_reu_512k":"c64_math_v3_reu_512k_source_built.reu",
           "v4_reu_16m":"c64_math_v4_reu_16m_source_built.reu"}

def cmd(args,cwd):
    p=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
    if p.returncode:raise AssertionError((args,p.returncode,p.stdout[-1500:],p.stderr[-2500:]))
    return p.stdout.strip()

def build(root,profile,out,kind="reference"):
    cmd([sys.executable,str(root/"tools/assemble_sources.py"),
         "--profile",profile,"--config-kind",kind,"--out",str(out)],root)
    filename="math_"+profile+"_source_built.prg"
    path=out/kind/profile/filename
    assert path.is_file(),path
    return path

def copy_checkout(destination):
    shutil.copytree(ROOT,destination,ignore=shutil.ignore_patterns(
        ".git","__pycache__","build_source","build_hybrid","build_pareto"))
    assert (destination/SHARED).is_file()

def restore_production_baseline(root):
    base=root/"optional/issue144_production_baseline"
    for path in (SHARED,)+tuple(
        profile+"/resident/movement/native/seek_dda.asm" for profile in PROFILES
    ):
        pinned=base/path
        assert pinned.is_file(),pinned
        (root/path).write_bytes(pinned.read_bytes())

def install_optin(root):
    old=(root/SHARED).read_text()
    candidate=(root/OPT_SHARED).read_text()
    assert candidate.count("U3216_FORCE")==0
    (root/SHARED).write_text(candidate)
    for profile in PROFILES:
        dest=root/profile/"resident/movement/native/seek_dda.asm"
        source=root/ALT/profile/"seek_dda.asm"
        original=dest.read_text()
        modified=source.read_text()
        assert original.count("s16i_r0:\n        jsr s16_addmin")==1
        assert modified.count("s16i_frac_remote:")==1
        assert modified.count("s16i_euclid_remote:")==1
        assert "* = U3216_MAIN_END" in modified
        dest.write_text(modified)

def machine(prg,reu):
    raw=prg.read_bytes()
    addr=int.from_bytes(raw[:2],"little")
    assert addr==0x1000
    mem=bytearray(65536)
    mem[addr:addr+len(raw)-2]=raw[2:]
    cpu=CPU(mem,reu=bytearray(reu.read_bytes()) if reu else None)
    cpu.d=0
    cpu.call(0x3280,2_000_000)
    return cpu

def paired_model(profile,base_dir,cand_dir,moves):
    a=api(profile)
    def locate(folder):
        here=folder/"reference"/profile
        p=here/("math_"+profile+"_source_built.prg")
        reu=here/REU_NAMES[profile] if profile in REU_NAMES else None
        return p,reu
    base_prg,base_reu=locate(base_dir)
    cand_prg,cand_reu=locate(cand_dir)
    if base_reu:
        assert hashlib.sha256(base_reu.read_bytes()).digest()==hashlib.sha256(cand_reu.read_bytes()).digest(),profile
    base=machine(base_prg,base_reu)
    candidate=machine(cand_prg,cand_reu)
    pos={k:v for k,v in a.items() if k.startswith("MATH_SEEK16_") and "_POS_" in k}
    assert a["MATH_X"]==0xc000
    savings={"all":[],"major":[],"euclid":[],"speed05":[],"speed1":[],"speed15":[],"speed2":[],"speed3":[],"speed4":[]}
    n=0
    speeds={0x80:"speed05",0x100:"speed1",0x180:"speed15",0x200:"speed2",0x300:"speed3",0x400:"speed4"}
    for j,(x0,y0,x1,y1) in enumerate(corpus(320)[:moves]):
        slot=j&7
        for speed in SPEEDS:
            for mode in (speed,speed|EUCLID):
                for cpu in (base,candidate):
                    m=cpu.mem
                    m[pos["MATH_SEEK16_POS_XL"]+slot]=x0&255
                    m[pos["MATH_SEEK16_POS_XH"]+slot]=x0>>8
                    m[pos["MATH_SEEK16_POS_Y"]+slot]=y0
                    m[0xc000:0xc002]=bytes((x1&255,x1>>8))
                    m[0xc004]=y1
                    m[0xc010:0xc012]=mode.to_bytes(2,"little")
                    cpu.x=slot
                a0=base.call(a["MATH_SEEK16_INIT"],200000)
                a1=candidate.call(a["MATH_SEEK16_INIT"],200000)
                frames=expected_frames(x0,y0,x1,y1,mode,"step")
                assert base.c==candidate.c==int(not frames),(profile,j,mode,"carry")
                assert base.x==candidate.x==slot and base.sp==candidate.sp,(profile,j,mode,"x/sp")
                assert base.mem[0x90e8:0x91e0]==candidate.mem[0x90e8:0x91e0],(profile,j,mode,"state")
                d=a0-a1
                savings["all"].append(d)
                savings["major" if mode==speed else "euclid"].append(d)
                savings[speeds[speed]].append(d)
                if frames:
                    base.x=candidate.x=slot
                    base.call(a["MATH_SEEK16_STEP"],200000)
                    candidate.call(a["MATH_SEEK16_STEP"],200000)
                    assert base.mem[0x90e8:0x91e0]==candidate.mem[0x90e8:0x91e0],(profile,j,mode,"STEP state")
                    assert base.c==candidate.c and base.x==candidate.x and base.sp==candidate.sp,(profile,j,mode,"STEP flags")
                n+=1
    def summary(seq):
        return {"cases":len(seq),"saved_mean":round(statistics.fmean(seq),6),
                "saved_worst":min(seq),"saved_p95":sorted(seq)[int(.95*(len(seq)-1))],
                "slower":sum(x<0 for x in seq)}
    result={"profile":profile,"calls":n,"status":"PASS_PAIRED_PUBLIC_MODEL",
            "categories":{k:summary(v) for k,v in savings.items()}}
    assert n==moves*len(SPEEDS)*2
    assert result["categories"]["all"]["saved_worst"]>=0
    return result

def real_vice(baseline,candidate,vice):
    import native_issue39_seek_all_modes as native
    original_source=native.resident
    original_scenarios=native.SCENARIOS
    original_frames=native.FRAMES
    report={}
    try:
        native.SCENARIOS=tuple((16,"step",s) for s in
            (0x0080,0x0100,0x0180,0x0200,0x0300,0x0400,0x8100))
        native.FRAMES=24
        with tempfile.TemporaryDirectory(prefix="issue144_seek_inhole_native_") as dst:
            tmp=Path(dst)
            for i,profile in enumerate(PROFILES):
                def get_resident(folder):
                    return (folder/"reference"/profile/("math_"+profile+"_source_built.prg")).read_bytes()
                raw_a=get_resident(baseline)
                raw_b=get_resident(candidate)
                assert len(raw_a)==len(raw_b)
                native.resident=lambda p,raw=raw_a:raw
                old,_,_=native.native(profile,22360+i*2,tmp,vice)
                native.verify(profile,old)
                native.resident=lambda p,raw=raw_b:raw
                new,_,_=native.native(profile,22361+i*2,tmp,vice)
                native.verify(profile,new)
                assert old==new,(profile,"real VICE frame/state/status/X/SP mismatch")
                report[profile]={"status":"PASS_REAL_VICE","public_init_calls":2*len(native.SCENARIOS),
                    "step_calls":2*len(native.SCENARIOS)*native.FRAMES,
                    "dump_sha256":hashlib.sha256(new).hexdigest(),"bytes_identical":len(new)}
    finally:
        native.resident=original_source
        native.SCENARIOS=original_scenarios
        native.FRAMES=original_frames
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--moves",type=int,default=160)
    p.add_argument("--native",action="store_true")
    opt=p.parse_args()
    assert 8<=opt.moves<=408
    if opt.native and not os.getenv("VICE_WRAPPER"):
        raise RuntimeError("--native requires VICE_WRAPPER")
    with tempfile.TemporaryDirectory(prefix="issue144_seek_inhole_public_") as location:
        base=Path(location)
        original=base/"baseline_checkout"
        alternative=base/"alternative_checkout"
        copy_checkout(original)
        copy_checkout(alternative)
        restore_production_baseline(original)
        install_optin(alternative)
        b=base/"baseline"
        c=base/"candidate"
        report={"status":"PASS_SOURCE_ONLY_OPTIN","profile_results":[],
                "native":"not_requested","production_binary_modification":False}
        for profile in PROFILES:
            base_prg=build(original,profile,b)
            cand_prg=build(alternative,profile,c)
            assert len(base_prg.read_bytes())==len(cand_prg.read_bytes())
            build(alternative,profile,c,kind="alternate")
            validate=cmd([sys.executable,str(alternative/"tools/validate_source_build.py"),
                          profile,"--build",str(c/"reference")],alternative)
            assert "PASS" in validate,validate
            measured=paired_model(profile,b,c,opt.moves)
            report["profile_results"].append(measured)
            print(profile,"PASS",measured["calls"],"paired INIT+STEP",
                  measured["categories"]["all"],flush=True)
        if opt.native:
            report["native"]=real_vice(b,c,os.environ["VICE_WRAPPER"])
        print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
