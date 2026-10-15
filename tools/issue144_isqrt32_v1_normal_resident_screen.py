#!/usr/bin/env python3
"""Issue144 C: V1 full-domain ISQRT32 direct highword seed in EXISTING normal resident slot.

Independent in-memory source experiment; no PRGs, REUs, canonical source or
caller RAM touched. The V5 low-ZP hybrid shares the historical V1 algorithm but
requires separate builder qualification; it is NOT proved by this V1 screen.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
from assemble_sources import preprocess,parse_config
from validate_unsigned_division import wr,rd

PROFILE="v1_balanced"
REGION_START=0x0A40
REGION_LENGTH=0xC0
OLD_MARK="    lda MATH_IO+$10\n    sta V1_SCRATCH+$08\n"

def module():
    original=(ROOT/"optional/issue144_isqrt32_highword_direct"/(PROFILE+".asm")).read_text()
    assert original.startswith("!cpu 6510\n* = $0C00\n")
    source=original.replace("!cpu 6510\n","")
    pairs=(
        ("* = $0C00","* = REG_GAME+$0A40"),
        ("* = $0C90","* = REG_GAME+$0AD0"),
        ("$C008","MATH_IO+$08"),("$C009","MATH_IO+$09"),
        ("$C010","MATH_IO+$10"),("$C011","MATH_IO+$11"),
        ("$C012","MATH_IO+$12"),("$C013","MATH_IO+$13"),
        ("$9800","REG_TABLE+$3800"),("$9900","REG_TABLE+$3900"),
        ("$C901","REG_GAME+$0801"),("$CA24","REG_GAME+$0924"),
        ("$C041","V1_SCRATCH+$01"),("$C042","V1_SCRATCH+$02"),
        ("$C043","V1_SCRATCH+$03"),("$C044","V1_SCRATCH+$04"),
        ("$C045","V1_SCRATCH+$05")
    )
    for before,after in pairs:
        assert before in source,before
        source=source.replace(before,after)
    assert "* = REG_GAME+$0A40" in source and "* = REG_GAME+$0AD0" in source
    assert all("$C0"+str(x) not in source for x in ("10","11","12","13"))
    return "; V1 Issue144 C normal-resident ISQRT32 direct highword (research opt-in)\n"+source

def build(kind):
    source=ROOT/"relocatable_source"/PROFILE/"math_relocatable.asm"
    cfg=source.with_name("math_config_"+kind+".inc")
    vals=parse_config(cfg)
    expanded=preprocess(source,cfg)
    assert expanded.count(OLD_MARK)==1
    custom=module()
    base,base_labels,base_symbols=Assembler().assemble(expanded)
    trial,trial_labels,trial_symbols=Assembler().assemble(expanded+"\n"+custom)
    s=vals["REG_GAME"]+REGION_START
    e=s+REGION_LENGTH
    altered=[addr for addr in sorted(set(base)|set(trial)) if base.get(addr,0)!=trial.get(addr,0)]
    assert altered and all(s<=addr<e for addr in altered),(kind,len(altered),list(map(hex,altered[:8])))
    assert trial_labels["LCB40"]==s and trial_labels["LC8DB"]==s+0x90
    entry=vals["REG_GAME_API"]+0x30
    assert base_symbols["MATH_ISQRT32"]==trial_symbols["MATH_ISQRT32"]==entry
    assert trial[entry]==0x4C and trial[entry+1]|(trial[entry+2]<<8)==s
    def load(code):
        mem=bytearray(65536)
        for addr,b in code.items():mem[addr]=b
        cpu=CPU(mem);cpu.d=0
        assert cpu.call(base_symbols["MATH_INIT"],2_000_000)>0
        return cpu
    return load(base),load(trial),base_symbols,vals["MATH_IO"],len(altered),len(custom),custom

def values(n,seed):
    rng=random.Random(seed)
    data=[0,1,2,3,4,7,15,16,17,63,64,65,255,256,257,0xFFFF,0x10000,
          0x10001,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    data.extend(rng.getrandbits(32) for _ in range(n))
    for root in (0,1,2,3,15,255,256,257,1023,16383,32767,65535):
        for d in (-1,0,1):
            x=root*root+d
            if 0<=x<=0xffffffff:data.append(x)
    return list(dict.fromkeys(data))

def trial(kind,count):
    old,new,api,io,diff,codebytes,source=build(kind)
    corpus=values(count,0x144C151+int(kind=="alternate"))
    cycles=[];vflag=0
    for i,n in enumerate(corpus):
        for cpu in (old,new):
            wr(cpu.mem,io+0x10,n,4)
            cpu.x=(i*11)&255
            cpu.y=(i*29)&255
            cpu.c=i&1
        sp0,sp1=old.sp,new.sp
        a=old.call(api["MATH_ISQRT32"],500000)
        b=new.call(api["MATH_ISQRT32"],500000)
        root=math.isqrt(n)
        assert (rd(old.mem,io+0x08,2),rd(new.mem,io+0x08,2))==(root,root),(kind,i,hex(n))
        assert old.c==new.c==0 and (old.sp,new.sp)==(sp0,sp1),(kind,i,'carry or stack')
        assert rd(old.mem,io+0x10,4)==rd(new.mem,io+0x10,4)==n,(kind,i,'N')
        assert old.x==new.x and old.y==new.y,(kind,i,'XY')
        cycles.append(a-b)
        vflag+=int(old.v!=new.v)
        if i%193==0:
            for cpu in (old,new):
                wr(cpu.mem,io+0x10,n&65535,4)
                cpu.call(api["MATH_ISQRT16"],500000)
                assert rd(cpu.mem,io+0x08,2)==math.isqrt(n&65535)
    assert cycles and min(cycles)>0
    ordered=sorted(cycles)
    return {"status":"PASS_SOURCE_ONLY_PUBLIC_MODEL","profile":PROFILE,"layout":kind,
            "cases":len(corpus),"mean_saved":statistics.mean(cycles),
            "minimum_saved":min(cycles),"p95_saved":ordered[int(.95*(len(ordered)-1))],
            "maximum_saved":max(cycles),"slower_calls":sum(x<0 for x in cycles),
            "vflag_mismatches":vflag,"modified_root_bytes":diff,"source_characters":codebytes,
            "module_sha256":hashlib.sha256(source.encode()).hexdigest(),
            "extra_normal_ZP":0,"extra_caller_RAM":0,
            "native_VICE_qualified":False,"V5_hybrid_qualified":False,
            "reference_PRG_REU_modified":False}

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--count",type=int,default=1200)
    opts=a.parse_args()
    assert 32<=opts.count<=10000
    result={"status":"PASS_V1_RESEARCH","layouts":{}}
    for kind in ("reference","alternate"):
        row=trial(kind,opts.count);result["layouts"][kind]=row
        print("ISQRT32 V1 RESIDENT",kind,row,flush=True)
    print(json.dumps(result,indent=2,sort_keys=True))
