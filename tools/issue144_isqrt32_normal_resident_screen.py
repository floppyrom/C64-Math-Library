#!/usr/bin/env python3
"""Issue144 C: all-input direct highword sqrt seed in NORMAL V2/V3 resident space.

Independent reusable opt-in; does not mutate checkout, PRGs, REUs or the
public ABI. Assemble both complete relocatable profiles in memory, not an
overlay in caller RAM. Native VICE and binary promotion are separate gates.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
from assemble_sources import preprocess,parse_config
from validate_unsigned_division import wr,rd,expected
PROFILES=("v2_pareto_fast","v3_reu_512k")
OLD_START="    lda MATH_IO+$10\n    sta ZP_MAIN+$59\n    lda MATH_IO+$11\n    sta ZP_MAIN+$5A\n"
OLD_END="; MATH_INIT-installed native SMUL16 executable-ZP image, assembled symbolically."
OLD_ENTRY=0x0A40
NEW_HELPER=0x0AD0

def resident_candidate(p):
    src=(ROOT/"relocatable_source"/p/"math_relocatable.asm").read_text()
    a=src.index(OLD_START); assert src.count(OLD_START)==1
    b=src.index(OLD_END,a); original=src[a:b]
    assert original.count("    jsr REG_GAME_API+$002D")==1
    assert original.count("    clc\n    rts")==1
    assert original.count("!byte $00")>=5
    seed=(ROOT/"optional/issue144_isqrt32_highword_direct"/(p+".asm")).read_text()
    assert seed.startswith("!cpu 6510\n* = $0C00\n")
    main=seed.replace("!cpu 6510\n","")
    # Reuse the physical root's existing $CB40..$CC00 resident allocation.
    main=main.replace("* = $0C00","* = REG_GAME+$0A40")
    main=main.replace("* = $0C90","* = REG_GAME+$0AD0")
    for address,expr in (
        ("$C008","MATH_IO+$08"),("$C009","MATH_IO+$09"),
        ("$C010","MATH_IO+$10"),("$C011","MATH_IO+$11"),
        ("$C012","MATH_IO+$12"),("$C013","MATH_IO+$13"),
        ("$9800","REG_TABLE+$3800"),("$9900","REG_TABLE+$3900"),
        ("$C85C","REG_GAME+$075C"),("$C867","REG_GAME+$0767"),
        ("$C966","REG_GAME+$0866"),("$C971","REG_GAME+$0871"),
        ("$54","ZP_MAIN+$52"),("$55","ZP_MAIN+$53"),
        ("$56","ZP_MAIN+$54"),("$57","ZP_MAIN+$55"),
        ("$58","ZP_MAIN+$56"),
    ): main=main.replace(address,expr)
    assert "* = REG_GAME+$0A40" in main and "* = REG_GAME+$0AD0" in main
    assert "jsr REG_GAME+" in main and "ZP_MAIN+" in main
    out=src[:a]+main+"\n"+src[b:]
    assert len(out)>200000 and out!=src
    return src,out,hashlib.sha256(main.encode()).hexdigest()

def assembled(p,layout):
    a,b,sha=resident_candidate(p)
    cfg=ROOT/"relocatable_source"/p/("math_config_"+layout+".inc")
    vals=parse_config(cfg)
    src=ROOT/"relocatable_source"/p/"math_relocatable.asm"
    expanded=preprocess(src,cfg)
    # Identical expansion prefix/suffix; substitute precisely the one root span.
    root_a=expanded.index(OLD_START);root_b=expanded.index(OLD_END,root_a)
    canon=a[a.index(OLD_START):a.index(OLD_END,a.index(OLD_START))]
    assert expanded[root_a:root_b]==canon
    new=b[b.index("* = REG_GAME+$0A40"):b.index(OLD_END,b.index("* = REG_GAME+$0A40"))]
    cand=expanded[:root_a]+new+expanded[root_b:]
    mem0,labels0,c0=Assembler().assemble(expanded)
    mem1,labels1,c1=Assembler().assemble(cand)
    io=vals["MATH_IO"];resident_base=vals["REG_GAME"]
    bounds=(resident_base+OLD_ENTRY,resident_base+0x0B00)
    modified=[i for i in sorted(set(mem0)|set(mem1)) if mem0.get(i,0)!=mem1.get(i,0)]
    assert modified and all(bounds[0]<=x<bounds[1] for x in modified),(p,layout,"unexpected source mutation",modified[:16])
    assert c0["MATH_ISQRT32"]==c1["MATH_ISQRT32"]==vals["REG_GAME_API"]+0x30
    assert labels1["LCB40"]==bounds[0]
    assert (labels1["LC836"] if p==PROFILES[0] else labels1["LC841"])==resident_base+NEW_HELPER
    # Public root trampoline must still dispatch to original normal resident slot.
    assert mem1[c1["MATH_ISQRT32"]]==0x4C
    assert (mem1[c1["MATH_ISQRT32"]+1]|mem1[c1["MATH_ISQRT32"]+2]<<8)==bounds[0]
    def cpu(code):
        ram=bytearray(65536)
        for pos,val in code.items():ram[pos]=val
        # No V3 REU access in this CPU-only sqrt path; normal MATH_INIT supported.
        m=CPU(ram);m.d=0; assert m.call(c1["MATH_INIT"],2000000)>0
        return m
    return cpu(mem0),cpu(mem1),c1,io,sha,{"begin":hex(bounds[0]),"end_exclusive":hex(bounds[1]),"modified_bytes":len(modified)}

def corpus(count,seed):
    rng=random.Random(seed)
    values=[0,1,2,3,4,7,15,16,17,255,256,257,65535,65536,65537,0x12345678,0x7fffffff,0x80000000,0xffffffff]
    values += [rng.getrandbits(32) for _ in range(count)]
    for root in (0,1,2,3,7,15,127,255,256,257,1023,32767,65535):
        for offset in (-1,0,1):
            n=root*root+offset
            if 0<=n<=0xffffffff:values.append(n)
    return list(dict.fromkeys(values))

def stats(values):
    v=sorted(values)
    return {"mean":statistics.mean(values),"minimum":v[0],"p05":v[int(.05*(len(v)-1))],"p95":v[int(.95*(len(v)-1))],"maximum":v[-1],"slower":sum(x<0 for x in values)}
def run(profile,layout,count):
    old,new,api,io,sha,bounds=assembled(profile,layout)
    nums=corpus(count,0x144C032+PROFILES.index(profile)*7001+(0 if layout=="reference" else 17))
    changes=[];vflags=0
    for k,n in enumerate(nums):
        for cpu in (old,new):
            wr(cpu.mem,io+0x10,n,4)
            cpu.c=k&1;cpu.x=(k*11)&0xff;cpu.y=(k*29)&0xff
        sp0,sp1=old.sp,new.sp
        a=old.call(api["MATH_ISQRT32"],500000)
        b=new.call(api["MATH_ISQRT32"],500000)
        root=math.isqrt(n)
        assert rd(old.mem,io+8,2)==rd(new.mem,io+8,2)==root,(profile,layout,k,hex(n),"root")
        assert old.c==new.c==0,(profile,layout,k,"carry")
        assert rd(old.mem,io+0x10,4)==rd(new.mem,io+0x10,4)==n,(profile,layout,k,"input")
        assert old.sp==sp0 and new.sp==sp1,(profile,layout,k,"stack")
        assert (old.x,old.y)==(new.x,new.y),(profile,layout,k,"X/Y")
        vflags+=(old.v!=new.v)
        changes.append(a-b)
    assert changes and min(changes)>0,(profile,layout,stats(changes))
    return {"profile":profile,"layout":layout,"status":"PASS_PUBLIC_MODEL_FULL_DOMAIN",
            "cases":len(nums),"source_sha256":sha,"slot":bounds,
            "cycles_saved":stats(changes),"volatile_V_flag_mismatches":vflags,
            "case_sha256":hashlib.sha256(b"".join(x.to_bytes(4,"little") for x in nums)).hexdigest(),
            "normal_api_preserved":True,"external_caller_RAM":0,"added_normal_ZP":0,
            "native_VICE_qualified":False,"reference_PRGs_and_REUs_changed":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--count",type=int,default=800)
    opts=parser.parse_args()
    assert 32<=opts.count<=10000
    result={"status":"PASS_RESEARCH_ONLY","profiles":{}}
    for p in PROFILES:
        result["profiles"][p]={}
        for layout in ("reference","alternate"):
            row=run(p,layout,opts.count)
            result["profiles"][p][layout]=row
            print("ISQRT32 NORMAL RESIDENT",p,layout,row["cycles_saved"],flush=True)
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
