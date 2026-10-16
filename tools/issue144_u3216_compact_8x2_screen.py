#!/usr/bin/env python3
"""Issue #144 B: compact 8x2 zero-overflow dual quotient tail, public ABI screen.

Repeat eight unrolled quotient bits twice with indexed ROL LN0,X: X=1 for
the high quotient byte, X=0 for low. This avoids 461 bytes of duplicated
unrolling at a cost of one extra cycle/bit and phase bookkeeping. In the
no-overflow domain $0100 <= D <= $7FFF, R<D guarantees bit-17 never rises.

This is *research only*: $0800 remains caller-owned in the screen. A source
hole is a candidate for review, not proof of code ownership or IRQ safety.
"""
from __future__ import annotations
import hashlib,json,random,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess,parse_config
from source_relocation import REGIONS,REGION_DEFAULT
from issue144_signed32_rq_tail_fusion_screen import machine
from issue144_u3216_fullcall_source_transplant_screen import cases
from validate_udiv32_16_integrated import one

PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
OPERATIONS=("MATH_UDIV32_16","MATH_UMOD32_16")
ENTRY_OLD="""U3216_ENTRY:
        lda U3216_D1
        bne U3216_GENERAL"""
ENTRY_NEW="""U3216_ENTRY:
        lda U3216_D1
        bmi U3216_GENERAL
        bne U3216_LOW_STUB"""
STUB_BEFORE="""U3216_GENERAL:
        jsr U3216_DIV16"""
STUB_AFTER="""U3216_LOW_STUB:
        jmp U3216_LOW_DIV
U3216_GENERAL:
        jsr U3216_DIV16"""

def compact_tail():
    out=["* = $0800","U3216_LOW_DIV:",
         "        jsr U3216_DIV16",
         "        lda U3216_R1","        ldx #1",
         "U3216_LOW_ROUND:"]
    for i in range(8):
        out += [f"U3216_LOW_BIT{i}:",
                "        rol U3216_LN0,x",
                "        rol U3216_R0",
                "        rol",
                "        cmp U3216_D1",
                f"        bcc U3216_LOW_NEXT{i}",
                f"        bne U3216_LOW_TAKE{i}",
                "        ldy U3216_R0",
                "        cpy U3216_D0",
                f"        bcc U3216_LOW_NEXT{i}",
                f"U3216_LOW_TAKE{i}:",
                "        tay",
                "        lda U3216_R0",
                "        sbc U3216_D0",
                "        sta U3216_R0",
                "        tya",
                "        sbc U3216_D1",
                "        sec",
                f"U3216_LOW_NEXT{i}:"]
    out += ["        rol U3216_LN0,x",
            "        sta U3216_R1",
            "        txa",
            "        beq U3216_LOW_DONE",
            "        ldx #0",
            "        lda U3216_R1",
            "        jmp U3216_LOW_ROUND",
            "U3216_LOW_DONE:",
            "        lda U3216_R1",
            "        clc",
            "        jmp U3216_FINISH",
            "U3216_LOW_END:"]
    return "\n".join(out)+"\n"

def prepared(profile,layout):
    cfg=ROOT/"relocatable_source"/profile/("math_config_"+layout+".inc")
    vals=parse_config(cfg)
    source=preprocess(ROOT/"relocatable_source"/profile/"math_relocatable.asm",cfg)
    assert source.count(ENTRY_OLD)==1 and source.count(STUB_BEFORE)==1
    new=source.replace(ENTRY_OLD,ENTRY_NEW).replace(STUB_BEFORE,STUB_AFTER)
    new+="\n"+compact_tail()
    baseline,api=machine(source,profile)
    candidate,second=machine(new,profile)
    assert api["MATH_UDIV32_16"]==second["MATH_UDIV32_16"]
    assert api["MATH_UMOD32_16"]==second["MATH_UMOD32_16"]
    assert baseline.mem[0x0800:second["U3216_LOW_END"]]!=candidate.mem[0x0800:second["U3216_LOW_END"]]
    assert second["U3216_LOW_DIV"]==0x0800
    assert second["U3216_MAIN_END"]<vals["REG_KERNEL"]+0x1272
    return baseline,candidate,api,vals,second["U3216_LOW_END"]-0x0800,source

def corpus():
    base=[("common",n,d) for n,d in cases()]
    rng=random.Random(0x14408202)
    base.extend(("lowD",rng.getrandbits(32),rng.randrange(256,32768)) for _ in range(512))
    base.extend(("highD",rng.getrandbits(32),rng.randrange(32768,65536)) for _ in range(512))
    return base

def stats(v):
    a=sorted(v)
    return {"count":len(v),"mean_saved":statistics.mean(v),"min_saved":a[0],
            "p05_saved":a[int(.05*(len(a)-1))],
            "p95_saved":a[int(.95*(len(a)-1))],
            "max_saved":a[-1],"slower":sum(x<0 for x in v)}

def geometry(profile,layout,source,candidate_bytes):
    mem,labels,_=Assembler().assemble(source)
    cfg=ROOT/"relocatable_source"/profile/("math_config_"+layout+".inc")
    val=parse_config(cfg)
    regions=[]
    for name,start,end in REGIONS:
        lo=val[name]; hi=lo+end-start+1
        p=lo; holes=[]
        while p<hi:
            if p in mem:p+=1;continue
            q=p
            while q<hi and q not in mem:q+=1
            if q-p>=96:holes.append({"start":hex(p),"end_exclusive":hex(q),"bytes":q-p})
            p=q
        regions.append({"region":name,"largest_hole":max([h["bytes"] for h in holes],default=0),
                        "candidate_spans":sorted(holes,key=lambda h:-h["bytes"])[:8]})
    possible=[{"region":x["region"],"spans":[h for h in x["candidate_spans"] if h["bytes"]>=candidate_bytes]} for x in regions]
    return {"regions":regions,"candidate_contiguous_unoccupied_spans":possible,
            "note":"Unoccupied bytes inside a region do not establish runtime ownership; mixed-call and data lifetime need separate proof"}

def main():
    vectors=corpus()
    report={"status":"PASS_COMPACT_DUALTAIL_CPU_MODEL",
            "cases_per_public_API":len(vectors),
            "corpus_sha256":hashlib.sha256(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little") for _,n,d in vectors)).hexdigest(),
            "caller_RAM_candidate_only":True,"native_vice_qualified":False,"profiles":{}}
    for profile in PROFILES:
        report["profiles"][profile]={}
        for layout in ("reference","alternate"):
            old,new,api,v,sz,source=prepared(profile,layout)
            scores={}
            for operation in OPERATIONS:
                deltas={"D0":[],"D8":[],"lowD":[],"highD":[]}
                for idx,(_,n,d) in enumerate(vectors):
                    sp0,sp1=old.sp,new.sp
                    oc,ok0,got0,want=one(old,api[operation],n,d,v["MATH_IO"])
                    nc,ok1,got1,_=one(new,api[operation],n,d,v["MATH_IO"])
                    assert ok0 and ok1 and got0==got1==want,(profile,layout,operation,idx,hex(n),hex(d),got0,got1,want)
                    assert old.sp==sp0 and new.sp==sp1,(profile,layout,operation,"stack")
                    domain="D0" if d==0 else "D8" if d<256 else "lowD" if d<32768 else "highD"
                    deltas[domain].append(oc-nc)
                scores[operation]={"groups":{k:stats(v) for k,v in deltas.items()},
                                   "overall":stats(sum(deltas.values(),[]))}
            report["profiles"][profile][layout]={"candidate_bytes":sz,
                    "results":scores,"source_geometry":geometry(profile,layout,source,sz)}
            print("ISSUE144 COMPACT",profile,layout,"PASS",len(vectors)*len(OPERATIONS),"code",sz,flush=True)
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
