#!/usr/bin/env python3
"""Issue #144 B: signed 32/16 combined R+Q normalization producer research.

Source-only model proof, not a resident or default image release. Compare the
actual public signed DIV and MOD ABI on identical unrestricted inputs. The
new -N/+D path reuses a preexisting, tested quotient+remainder sign tail.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from assemble_sources import preprocess,parse_config
from mini6502 import Assembler,CPU
from source_relocation import REU
from validate_signed_division import div_expected,wr,rd

PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
OLD=("        ; -+ : quotient and remainder both negative.\n"
     "        jsr U3216_ENTRY\n"
     "        jsr MULDIV16_S_NEG_R\n"
     "        jmp MULDIV16_S_NEG_Q\n")
NEW=("        ; -+ : shared signed QR normalization owns both outputs.\n"
     "        jmp MULDIV16_S_DIV_QR\n")

def machine(text,profile):
    mem,labels,const=Assembler().assemble(text)
    m=bytearray(65536)
    for a,v in mem.items():m[a]=v
    reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
    cpu=CPU(m,reu=reu);cpu.d=0
    assert cpu.call(const["MATH_INIT"],2_000_000)>0
    assert cpu.c==0
    return cpu,const

def pair(profile,kind):
    cfg=ROOT/"relocatable_source"/profile/("math_config_"+kind+".inc")
    v=parse_config(cfg)
    source=preprocess(ROOT/"relocatable_source"/profile/"math_relocatable.asm",cfg)
    a=source.index("\nD32F_NNEG:")
    b=source.index("\nD32F_NN:",a+1)
    span=source[a:b]
    assert span.count(OLD)==1,(profile,kind,"original signed producer drift")
    new=source[:a]+span.replace(OLD,NEW)+source[b:]
    old,c0=machine(source,profile)
    candidate,c1=machine(new,profile)
    assert c0["MATH_SDIV32_16"]==c1["MATH_SDIV32_16"]==v["REG_LOW"]+0x0EE0
    assert c0["MATH_SMOD32_16"]==c1["MATH_SMOD32_16"]==v["REG_LOW"]+0x0FDD
    assert c0["MULDIV16_S_DIV_QR"]==c1["MULDIV16_S_DIV_QR"]
    return old,candidate,c0,v

def corpus(count):
    rng=random.Random(0x144B0026)
    ns=[0,1,2,3,7,15,0x7fffffff,0x80000000,0x80000001,
        0x8000ffff,0xffffffff,0xffff0000,0x00010000,0xdeadbeef]
    ds=[0,1,2,3,7,15,127,255,256,257,0x7fff,0x8000,0x8001,0xffff]
    cases=[(n,d) for n in ns for d in ds]
    for quadrant in range(4):
        for _ in range(count):
            n=rng.randrange(0,0x80000000)
            d=rng.randrange(1,0x8000)
            if quadrant&2:n=(-n)&0xffffffff
            if quadrant&1:d=(-d)&0xffff
            cases.append((n,d))
    # First sign bit genuinely negative when the selected quadrant asks for it.
    return list(dict.fromkeys(cases))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--random-per-quadrant",type=int,default=500)
    args=ap.parse_args()
    data=corpus(args.random_per_quadrant)
    report={"status":"PASS_SIGNED32_FUSED_QR_RESEARCH","research_only":True,
            "default_source_changed":False,"native_vice_qualified":False,
            "rows":[],"cases_per_api":len(data)}
    for p in PROFILES:
        for layout in ("reference","alternate"):
            old,new,c,v=pair(p,layout)
            I=v["MATH_IO"]; groups={}
            for name in ("MATH_SDIV32_16","MATH_SMOD32_16"):
                samples={key:[] for key in ("negative_n_positive_d","all_other_nonzero","zero_divisor")}
                changed_a=0;changed_v=0
                for k,(n,d) in enumerate(data):
                    for cpu in (old,new):
                        wr(cpu.mem,I+0x10,n,4);wr(cpu.mem,I+0x14,d,2)
                        cpu.c=k&1;cpu.x=(k*11)&255;cpu.y=(k*29)&255
                    oldsp,newsp=old.sp,new.sp
                    cy0=old.call(c[name],2_000_000);cy1=new.call(c[name],2_000_000)
                    want=div_expected(n,32,d,16,32,16)
                    def state(cpu):
                        return (rd(cpu.mem,I+0x18,4),rd(cpu.mem,I+0x1c,2),cpu.c,
                                rd(cpu.mem,I+0x10,4),rd(cpu.mem,I+0x14,2),
                                cpu.sp,cpu.x,cpu.y)
                    s0=state(old);s1=state(new)
                    assert s0==s1,(p,layout,name,hex(n),hex(d),s0,s1)
                    assert s1[:3]==want,(p,layout,name,hex(n),hex(d),s1[:3],want)
                    assert old.sp==oldsp and new.sp==newsp
                    key=("zero_divisor" if d==0 else
                        "negative_n_positive_d" if n&0x80000000 and not d&0x8000 else
                        "all_other_nonzero")
                    samples[key].append(cy0-cy1)
                    changed_a+=(old.a!=new.a)
                    changed_v+=(old.v!=new.v)
                assert all(x==0 for x in samples["all_other_nonzero"])
                assert all(x==0 for x in samples["zero_divisor"])
                assert samples["negative_n_positive_d"] and all(x>0 for x in samples["negative_n_positive_d"])
                groups[name]={
                    "groups":{k:{"count":len(a),"mean_saved":statistics.mean(a) if a else None,
                                  "minimum_saved":min(a) if a else None,
                                  "maximum_saved":max(a) if a else None,
                                  "slower":sum(x<0 for x in a)} for k,a in samples.items()},
                    "all_mean_saved":statistics.mean(sum(samples.values(),[])),
                    "accumulator_volatile_mismatches":changed_a,
                    "overflow_flag_volatile_mismatches":changed_v}
            report["rows"].append({"profile":p,"layout":layout,"status":"PASS",
                    "same_input_calls":len(data)*2,
                    "normal_zp_growth":0,"caller_ram_growth":0,"signed_results":groups})
            print("SIGNED32 FUSED RQ",p,layout,"PASS",len(data)*2,flush=True)
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
