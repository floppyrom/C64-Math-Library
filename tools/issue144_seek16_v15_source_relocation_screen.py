#!/usr/bin/env python3
"""Issue144 D: prove normal-resident V1/V5 SEEK16 candidate on both source maps.

Research-only: build the existing independently authored accumulator option in
the old resident INIT slot. Do not change canonical source, reference PRGs,
public API, or private OptiSearch inputs. Native VICE is a separate gate.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
import re
import statistics
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
from assemble_sources import preprocess,parse_config
from issue144_seek16_v15_normal_resident_feasibility import candidate,BEGIN,LIMIT
from issue144_seek16_accum_all_profiles_v2 import make,SPEEDS
from benchmark_seek_profiles import corpus
from source_relocation import addr_expr

P="v1_balanced"
ORIGIN=0x3000
P_HELPER=0x38A2

def normal_asm():
    report,blob=candidate(P)
    assert blob and report["source_bytes"]==399
    source,mem,labels=make(P)
    assert source.startswith("!cpu 6510\n")
    assert source.count("* = $0D00")==1 and source.count("* = $0F60")==1
    source=source.replace("!cpu 6510\n","",1)
    source=source.replace("* = $0D00","* = REG_API+$0723",1)
    source=source.replace("* = $0F60","* = REG_API+$08A2",1)
    # Local address-derived labels collide with historical source-assembler
    # labels. Qualify all internal symbols with a unique final-owner prefix.
    source=re.sub(r"\bL[0-9A-Fa-f]{4}\b",lambda m:"ISS144_"+m.group(0),source)
    # Fully symbolic addresses are mandatory: no reference-map operands in
    # the candidate are allowed to leak into the alternate memory map.
    source=re.sub(r"\$([0-9A-Fa-f]{4})\b",
                  lambda m:addr_expr(P,int(m.group(1),16)),source)
    assert "$C0" not in source and "* = REG_API+$0723" in source
    return source

def source_pair(layout):
    cfg=ROOT/"relocatable_source"/P/("math_config_"+layout+".inc")
    values=parse_config(cfg)
    original=preprocess(ROOT/"relocatable_source"/P/"math_relocatable.asm",cfg)
    patch=normal_asm()
    before,_,symbols=Assembler().assemble(original)
    after,labels,csymbols=Assembler().assemble(original+"\n"+patch)
    assert values["REG_API"]+0x723==labels["ISS144_L3723"]
    assert labels["SEEK_ACCUM_ONCE"]==values["REG_API"]+0x8A2
    changed=sorted(a for a in set(before)|set(after)
                   if before.get(a,0)!=after.get(a,0))
    lo,hi=values["REG_API"]+0x723,values["REG_API"]+0x8CE
    assert changed and all(lo<=a<hi for a in changed),(
        layout,"modified bytes outside SEEK16_INIT resident island",changed[:12])
    assert len(changed)<=399
    assert csymbols["MATH_SEEK16_INIT"]==symbols["MATH_SEEK16_INIT"]
    assert before[symbols["MATH_SEEK16_INIT"]]==after[csymbols["MATH_SEEK16_INIT"]]==0x4C
    assert (before[symbols["MATH_SEEK16_INIT"]+1],
            before[symbols["MATH_SEEK16_INIT"]+2])==(
            after[csymbols["MATH_SEEK16_INIT"]+1],
            after[csymbols["MATH_SEEK16_INIT"]+2])
    def machine(code):
        ram=bytearray(65536)
        for a,b in code.items():ram[a]=b
        c=CPU(ram);c.d=0
        c.call(symbols["MATH_INIT"],2_000_000)
        return c
    # The public state constants live in math_api.inc rather than the
    # relocatable assembler's core symbol table. Derive them from the
    # verified map, not from frozen reference addresses.
    public=dict(csymbols)
    public.update(MATH_X=values["MATH_IO"],MATH_Y=values["MATH_IO"]+4,
                  MATH_N=values["MATH_IO"]+0x10,
                  MATH_SEEK16_POS_XL=values["REG_LOW"]+0x988,
                  MATH_SEEK16_POS_XH=values["REG_LOW"]+0x990,
                  MATH_SEEK16_POS_Y=values["REG_LOW"]+0x998)
    return machine(before),machine(after),public,values,len(changed),patch

def feed(cpu,api,move,speed,slot):
    x0,y0,x1,y1=move
    for name,v in (("MATH_SEEK16_POS_XL",x0&255),("MATH_SEEK16_POS_XH",x0>>8),("MATH_SEEK16_POS_Y",y0)):
        cpu.mem[api[name]+slot]=v
    for at,value in ((api["MATH_X"],x1&255),(api["MATH_X"]+1,x1>>8),
                     (api["MATH_Y"],y1),(api["MATH_N"],speed&255),
                     (api["MATH_N"]+1,speed>>8)):
        cpu.mem[at]=value
    cpu.x=slot

def run(layout,moves):
    old,new,api,v,diffs,source=source_pair(layout)
    init=api["MATH_SEEK16_INIT"];step=api["MATH_SEEK16_STEP"]
    lo=v["REG_LOW"]+0x980;hi=v["REG_LOW"]+0xB00
    savings=[];count=0;followups=0
    for k,move in enumerate(corpus(320)[:moves]):
        for si,speed in enumerate(SPEEDS):
            slot=(k*7+si)&7
            feed(old,api,move,speed,slot);feed(new,api,move,speed,slot)
            spold,spnew=old.sp,new.sp
            a=old.call(init,4_000_000);b=new.call(init,4_000_000)
            assert old.mem[lo:hi]==new.mem[lo:hi],(layout,k,hex(speed),"INIT-state")
            assert (old.c,old.x,old.sp)==(new.c,new.x,new.sp)
            assert old.sp==spold and new.sp==spnew
            savings.append(a-b);count+=1
            for c in (old,new):c.x=slot
            old.call(step,4_000_000);new.call(step,4_000_000)
            assert old.mem[lo:hi]==new.mem[lo:hi],(layout,k,hex(speed),"STEP-state")
            assert old.c==new.c;followups+=1
    assert count==moves*len(SPEEDS)
    assert min(savings)>=-1,(layout,min(savings))
    return {"status":"PASS_SEEK16_SOURCE_RELOCATED",
            "layout":layout,"public_INIT_pairs":count,"public_STEP_pairs":followups,
            "mean_cycles_saved":statistics.mean(savings),
            "min_cycles_saved":min(savings),"max_cycles_saved":max(savings),
            "slower_calls":sum(n<0 for n in savings),
            "normal_ZP_growth":0,"caller_RAM_growth":0,
            "modified_resident_bytes":diffs,
            "symbolic_module_sha256":hashlib.sha256(source.encode()).hexdigest(),
            "native_VICE_qualified":False,
            "full_56_entry_source_validator_qualified":False}

def main():
    result={layout:run(layout,80) for layout in ("reference","alternate")}
    print(json.dumps({"status":"PASS_V1V5_RELOCATED_RESEARCH",
                      "layouts":result,
                      "derived_V5_build_qualification_pending":True,
                      "canonical_sources_untouched":True},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
