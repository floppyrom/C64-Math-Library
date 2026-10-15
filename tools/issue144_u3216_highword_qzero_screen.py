#!/usr/bin/env python3
"""Issue #144 B: skip 16/16 high-word division when N.high16 < D16.

An all-domain, normal-resident candidate: it always produces full Q32/R16/C,
including D8 and D=0 through unchanged dispatch. Both published unsigned
public entries are measured against identical-source unmodified baselines,
on V2/V3/V4, reference and alternate relocations. Does not rewrite source.
No private donor/OptiSearch code. No shipped binary or PERF changes.
"""
from __future__ import annotations
import argparse,hashlib,json,random,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from assemble_sources import preprocess,parse_config
from issue144_signed32_rq_tail_fusion_screen import machine
from validate_udiv32_16_integrated import one
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
OPERATIONS=("MATH_UDIV32_16","MATH_UMOD32_16")
OLD="""U3216_GENERAL:
        jsr U3216_DIV16
        lda U3216_R1
U3216_B0:"""
NEW="""U3216_GENERAL:
        ; N.high16<D means high quotient = 0 and residual = N.high16.
        ; D=0 and D8 have already been handled in U3216_ENTRY.
        lda U3216_N1
        cmp U3216_D1
        bcc U3216_HQ_ZERO
        bne U3216_HQ_DIV
        lda U3216_N0
        cmp U3216_D0
        bcc U3216_HQ_ZERO
U3216_HQ_DIV:
        jsr U3216_DIV16
        lda U3216_R1
        jmp U3216_B0
U3216_HQ_ZERO:
        lda U3216_N0
        sta U3216_R0
        lda U3216_N1
        sta U3216_R1
        lda #0
        sta U3216_Q2
        sta U3216_Q3
        lda U3216_R1
U3216_B0:"""
# The LDA-highword-divider path above contains a needless JMP if its body
# is situated before the QZERO fast exit. Tested as a conservative first
# geometry; a later single-fallthrough design may remove the JMP overhead.

def load(profile,kind):
    cfg=ROOT/"relocatable_source"/profile/("math_config_"+kind+".inc")
    vals=parse_config(cfg)
    source=preprocess(ROOT/"relocatable_source"/profile/"math_relocatable.asm",cfg)
    assert source.count(OLD)==1,(profile,kind,"U3216 source drift")
    updated=source.replace(OLD,NEW)
    old,labels=machine(source,profile)
    new,newlabels=machine(updated,profile)
    assert labels["MATH_UDIV32_16"]==newlabels["MATH_UDIV32_16"]
    assert labels["MATH_UMOD32_16"]==newlabels["MATH_UMOD32_16"]
    assert labels["U3216_B0"]<labels["U3216_MAIN_END"]<vals["REG_KERNEL"]+0x1272
    assert newlabels["U3216_B0"]<newlabels["U3216_MAIN_END"]<vals["REG_KERNEL"]+0x1272
    for n in ("U3216_D8","U3216_FINISH","U3216_ZERO"):
        assert labels[n]==newlabels[n],(profile,kind,n,"unrelated address shifted")
    return old,new,labels,vals

def vectors():
    rng=random.Random(0x144B3216)
    v=[]
    v.extend(("uniform",rng.getrandbits(32),rng.randrange(256,65536)) for _ in range(512))
    # High-word quotient is mathematically zero, but low 16-bit quotient
    # remains unrestricted and is still produced by the original 16 steps.
    for _ in range(384):
        d=rng.randrange(256,65536)
        high=rng.randrange(d)
        v.append(("qhi_zero",(high<<16)|rng.getrandbits(16),d))
    for _ in range(384):
        d=rng.randrange(256,65536)
        high=rng.randrange(d,65536)
        v.append(("qhi_nonzero",(high<<16)|rng.getrandbits(16),d))
    v.extend(("D8",rng.getrandbits(32),rng.randrange(1,256)) for _ in range(128))
    v.extend(("D0",rng.getrandbits(32),0) for _ in range(40))
    for d in (1,2,3,127,128,255,256,257,32767,32768,32769,65535):
        for n in (0,1,d-1,d,d+1,0xffff,0x10000,0xffffffff):
            v.append(("edge",n,d))
    assert len(v)==1544,len(v)
    return v

def percentile(s,p):
    arr=sorted(s);return arr[int(p*(len(arr)-1))]

def stats(gains):
    return {"cases":len(gains),"mean_saved":statistics.mean(gains),
            "p05_saved":percentile(gains,.05),
            "p95_saved":percentile(gains,.95),
            "worst_saved":min(gains),"best_saved":max(gains),
            "slower":sum(g<0 for g in gains),
            "equal":sum(g==0 for g in gains)}

def main():
    corpus=vectors()
    digest=hashlib.sha256(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little") for _,n,d in corpus)).hexdigest()
    report={"status":"PASS_FULL_PUBLIC_SOURCE_MODEL_RESEARCH","producer":"zero_highword_quotient_skip",
            "corpus_sha256":digest,"cases_per_API":len(corpus),
            "reference_images_unchanged":True,"native_VICE_qualified":False,
            "normal_ZP_added":0,"caller_RAM_added":0,
            "profiles":{}}
    for p in PROFILES:
        report["profiles"][p]={}
        for layout in ("reference","alternate"):
            old,new,labels,config=load(p,layout)
            io=config["MATH_IO"]
            result={}
            for op in OPERATIONS:
                by={k:[] for k in ("uniform","qhi_zero","qhi_nonzero","D8","D0","edge")}
                flags_changed=0
                for i,(domain,n,d) in enumerate(corpus):
                    sp0,sp1=old.sp,new.sp
                    c0,k0,v0,want=one(old,labels[op],n,d,io)
                    c1,k1,v1,_=one(new,labels[op],n,d,io)
                    assert k0 and k1 and v0==v1==want,(p,layout,op,i,domain,hex(n),hex(d),v0,v1,want)
                    assert (old.sp,new.sp)==(sp0,sp1),(p,layout,op,i,"stack")
                    by[domain].append(c0-c1)
                    flags_changed+=old.status()!=new.status()
                allg=sum(by.values(),[])
                result[op]={"all":stats(allg),"groups":{k:stats(v) for k,v in by.items()},
                            "noncarry_flags_changed":flags_changed}
            report["profiles"][p][layout]=result
            print("U3216 HIGHWORD QZERO",p,layout,"PASS",len(corpus)*len(OPERATIONS),flush=True)
    print(json.dumps(report,sort_keys=True,indent=2))

if __name__=="__main__":main()
