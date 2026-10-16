#!/usr/bin/env python3
"""Issue144 B: source-owned REG_LOW+$0C00 dual-tail producer qualification.

The fast low-D routine is relocated from caller-owned $0800 to an all-zero
source-generated island inside the **already claimed** REG_LOW region. The
source is assembled in a temporary model, preserving canonical source and
reference PRGs/REUs. The all-zero island does not by itself certify runtime
ownership: full API, live data, native and interrupt gates are separate.
"""
from __future__ import annotations
import hashlib,json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess,parse_config
from issue144_signed32_rq_tail_fusion_screen import machine
from issue144_u3216_dualtail_direct_dispatch_screen import (
    low_divisor_tail,ENTRY_OLD,ENTRY_NEW,STUB_BEFORE,STUB_AFTER,
    vectors as unsigned_vectors,OPS as UOPS,PROFILES)
from issue144_dualtail_signed_public_regression import (
    vectors as signed_vectors,OPS as SOPS,exercise as signed_exercise)
from validate_signed_division import div_expected,wr,rd
from validate_udiv32_16_integrated import one as unsigned_one
OFFSET=0x0c00
NBYTES=461

def builds(profile,layout):
    config=ROOT/"relocatable_source"/profile/("math_config_"+layout+".inc")
    v=parse_config(config)
    baseline=preprocess(ROOT/"relocatable_source"/profile/"math_relocatable.asm",config)
    assert baseline.count(ENTRY_OLD)==baseline.count(STUB_BEFORE)==1
    original,api=machine(baseline,profile)
    start=v["REG_LOW"]+OFFSET
    tail=low_divisor_tail().replace("* = $0800",f"* = ${start:04X}",1)
    assert tail.startswith(f"* = ${start:04X}"),(profile,layout,"tail origin drift")
    candidate=baseline.replace(ENTRY_OLD,ENTRY_NEW).replace(STUB_BEFORE,STUB_AFTER)+"\n"+tail
    new,labels=machine(candidate,profile)
    low=start;end=labels["U3216_LD_END"]
    assert end-start==NBYTES,(profile,layout,"tail unexpected bytes",end-start)
    old_bytes=bytes(original.mem[start:end])
    assert set(old_bytes)=={0},(profile,layout,"old runtime source island not empty",
                                [(hex(start+i),hex(x)) for i,x in enumerate(old_bytes) if x][:12])
    asm,oldlabels,_=Assembler().assemble(baseline)
    assert all(not low<=pc<end for pc in oldlabels.values()),(profile,layout,"live old symbols overlap")
    newmem,_,_=Assembler().assemble(candidate)
    assert bytes(new.mem[low:end])==bytes(newmem[p] for p in range(low,end)),(
           profile,layout,"MATH_INIT or other runtime wrote over relocated tail")
    assert api["MATH_UDIV32_16"]==labels["MATH_UDIV32_16"]
    assert api["MATH_UMOD32_16"]==labels["MATH_UMOD32_16"]
    assert v["REG_LOW"]<=low and end<=v["REG_LOW"]+0x2000
    # The shared U3216 source expands by several bytes before the seek/mixed
    # entrypoints; source-linked absolute address operands can legitimately
    # change. Report them explicitly and enforce a tightly bounded fixup count.
    relocations=[(hex(i-v["REG_LOW"]),hex(original.mem[i]),hex(new.mem[i]))
                 for i in range(v["REG_LOW"],low) if original.mem[i]!=new.mem[i]]
    assert len(relocations)<=12,(profile,layout,"unexpected source relink footprint",relocations[:24])
    print("IN-RESIDENT SOURCE FIXUPS",profile,layout,relocations,flush=True)
    return original,new,api,v,NBYTES

def summarise(values):
    s=sorted(values)
    return {"cases":len(s),"mean_saved":statistics.mean(s),"worst_saved":s[0],
            "p05_saved":s[int(.05*(len(s)-1))],"p95_saved":s[int(.95*(len(s)-1))],
            "best_saved":s[-1],"slower_cases":sum(x<0 for x in s)}

def interleave(old,new,api,io,iteration,region):
    # These independent routines execute other resident code and may use
    # temporary data; the retired region must remain executable unchanged.
    calls=[("MATH_UMUL16",{"MATH_X":2,"MATH_Y":3}),
           ("MATH_ISQRT32",{"MATH_N":4}),
           ("MATH_UDIV16",{"MATH_N":2,"MATH_D":2})]
    entry,values=calls[iteration%len(calls)]
    for cpu in (old,new):
        for name,width in values.items():
            for byte in range(width):
                cpu.mem[api[name]+byte]=(iteration*117+byte*29)&255
        cpu.c=iteration&1;cpu.x=(iteration*11)&255;cpu.y=(iteration*7)&255
    cy0=old.call(api[entry],2_000_000)
    cy1=new.call(api[entry],2_000_000)
    # Unlike the indexed test, both machines must have same public behavior.
    for name in ("MATH_X","MATH_Y","MATH_N","MATH_D","MATH_Q","MATH_R","MATH_Z"):
        a=api[name];span=4 if name not in ("MATH_D",) else 2
        assert old.mem[a:a+span]==new.mem[a:a+span],(entry,name)
    assert old.c==new.c and old.sp==new.sp,(entry,"status/stack")
    assert bytes(new.mem[region[0]:region[1]])==region[2],(entry,"runtime tail clobbered")
    return cy0,cy1

def main():
    u=unsigned_vectors()
    s=signed_vectors()
    report={"status":"PASS_IN_RESIDENT_LOWTAIL_PUBLIC_MODEL",
            "experiment":"source-owned REG_LOW plus $0C00",
            "normal_zp_growth":0,"caller_RAM_bytes":0,
            "relocated_secondary_tail_bytes":NBYTES,
            "historical_PRGs_and_REUs_unchanged":True,
            "native_vice_qualified":False,
            "ordinary_full_library_mixed_validation_completed":False,
            "signed_vectors":len(s),"unsigned_vectors":len(u),"profiles":{}}
    for profile in PROFILES:
        report["profiles"][profile]={}
        for layout in ("reference","alternate"):
            old,new,api,config,size=builds(profile,layout)
            io=config["MATH_IO"]
            begin=config["REG_LOW"]+OFFSET
            region=(begin,begin+size,bytes(new.mem[begin:begin+size]))
            results={}
            for op in (*UOPS,*SOPS):
                corpus=u if op in UOPS else s
                delta=[]
                for i,item in enumerate(corpus):
                    domain,n,d=item
                    if op in UOPS:
                        a0,ok0,out0,want=unsigned_one(old,api[op],n,d,io)
                        a1,ok1,out1,_=unsigned_one(new,api[op],n,d,io)
                        assert ok0 and ok1 and out0==out1==want,(
                            profile,layout,op,i,domain,hex(n),hex(d),out0,out1,want)
                    else:
                        a0,out0,flags0,acc0,x0,y0=signed_exercise(old,api[op],io,n,d)
                        a1,out1,flags1,acc1,x1,y1=signed_exercise(new,api[op],io,n,d)
                        want=div_expected(n,32,d,16,32,16)
                        assert out0==out1==want,(profile,layout,op,i,domain,hex(n),hex(d),out0,out1,want)
                        assert (flags0,acc0,x0,y0)==(flags1,acc1,x1,y1),(
                            profile,layout,op,i,"volatile A/X/Y/full flags differ")
                    delta.append(a0-a1)
                    if i%97==0:interleave(old,new,api,io,i,region)
                    if i%73==0:
                        assert bytes(new.mem[begin:begin+size])==region[2],(
                            profile,layout,op,i,"live code overwritten")
                results[op]=summarise(delta)
            report["profiles"][profile][layout]={"result":results,
                    "REG_LOW_tail_location":hex(begin),
                    "MATH_INIT_and_mixed_call_integrity":True,
                    "no_caller_RAM":True}
            print("IN-RESIDENT DUALTAIL",profile,layout,"PASS",
                  len(u)*2+len(s)*2,"public paired calls",flush=True)
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":main()
