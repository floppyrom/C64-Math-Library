#!/usr/bin/env python3
"""Independent all-domain public-ABI shared-take U3216 research, source-only opt-in.

Build candidate entirely in memory; never modify checkout or shipped PRG/REU.
"""
import argparse
import hashlib
import json
import random
import statistics
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler, CPU
from assemble_sources import preprocess
from validate_unsigned_division import REU, load, wr, rd, expected

PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
SOURCE=ROOT/"relocatable_source/division/udiv32_16_split_direct.inc"
ALT=ROOT/"optional/issue144_u3216_shared_take_inline/udiv32_16_split_direct_shared.inc"

def source_built(profile):
    src=ROOT/"relocatable_source"/profile/"math_relocatable.asm"
    cfg=src.with_name("math_config_reference.inc")
    old=SOURCE.read_text()
    opt=ALT.read_text()
    assert opt!=old and len(opt)<len(old)
    expanded=preprocess(src,cfg)
    assert expanded.count(old)==1,"unexpected source insertion geometry"
    memory,labels,const=Assembler().assemble(expanded.replace(old,opt,1))
    ram=bytearray(65536)
    for addr,byte in memory.items():ram[addr]=byte
    reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
    cpu=CPU(ram,reu=reu)
    cpu.d=0
    assert cpu.call(0x3280,2_000_000)>0
    return cpu,labels,const

def samples(seed,count):
    rng=random.Random(seed)
    ds=[0,1,2,3,15,127,128,255,256,257,511,32767,32768,32769,65535]
    ns=[0,1,2,255,256,65535,65536,0x12345678,0x7fffffff,0x80000000,0xffffffff]
    pairs=[(n,d,"edge") for d in ds for n in ns]
    pairs += [(rng.getrandbits(32),rng.getrandbits(16),"uniform") for _ in range(count)]
    pairs += [(rng.getrandbits(32),rng.randrange(256,32768),"lowD") for _ in range(count//2)]
    pairs += [(rng.getrandbits(32),rng.randrange(32768,65536),"highD") for _ in range(count//2)]
    pairs += [(rng.getrandbits(32),rng.randrange(1,256),"D8") for _ in range(max(40,count//8))]
    pairs += [(rng.getrandbits(32),0,"D0") for _ in range(40)]
    return pairs

def stat(values):
    return {"cases":len(values),"mean_saved":round(statistics.mean(values),4),
            "worst_saved":min(values),"best_saved":max(values),
            "slower":sum(v<0 for v in values)}

def run(profile,count):
    baseline,api=load(profile)
    candidate,labels,const=source_built(profile)
    for name in ("MATH_UDIV32_16","MATH_UMOD32_16"):
        assert api[name]==const.get(name,labels.get(name)),(profile,name,"public entry moved")
    corpus=samples(0x1440A11E+PROFILES.index(profile),count)
    bins={name:[] for name in ("all","edge","uniform","lowD","highD","D8","D0")}
    for k,(n,d,group) in enumerate(corpus):
        for cpu in (baseline,candidate):
            wr(cpu.mem,0xc010,n,4)
            wr(cpu.mem,0xc014,d,2)
        entry=api["MATH_UDIV32_16" if k%2==0 else "MATH_UMOD32_16"]
        a=baseline.call(entry,4_000_000)
        b=candidate.call(entry,4_000_000)
        truth=expected(n,d,32,16)
        for cpu in (baseline,candidate):
            got=rd(cpu.mem,0xc018,4),rd(cpu.mem,0xc01c,2),cpu.c
            assert got==truth,(profile,k,hex(n),hex(d),got,truth)
            assert (rd(cpu.mem,0xc010,4),rd(cpu.mem,0xc014,2))==(n,d)
        bins["all"].append(a-b)
        bins[group].append(a-b)
    return {"profile":profile,"status":"PASS_RESEARCH_PUBLIC_MODEL","cases":len(corpus),
            "category":{key:stat(val) for key,val in bins.items() if val},
            "corpus_sha256":hashlib.sha256(b"".join(
                n.to_bytes(4,"little")+d.to_bytes(2,"little") for n,d,_ in corpus)).hexdigest(),
            "source_sha256":hashlib.sha256(ALT.read_bytes()).hexdigest(),
            "limitations":"CPU-model public calls, not native VICE or V5, no default promotion"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--profile",choices=PROFILES+("all",),default="v2_pareto_fast")
    parser.add_argument("--random",type=int,default=1200)
    args=parser.parse_args()
    assert 10<=args.random<=10000
    profiles=PROFILES if args.profile=="all" else (args.profile,)
    result=[run(profile,args.random) for profile in profiles]
    print(json.dumps({"status":"PASS_RESEARCH","profiles":result},indent=2))

if __name__=="__main__":
    main()
