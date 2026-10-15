#!/usr/bin/env python3
"""Issue #144 B: all-domain dual-tail direct-divisor dispatch, assembled 6510.

D16 $0100..$7FFF uses mathematically no-17th-bit-overflow 16-step low-tail.
D16 $8000..$FFFF retains original production tail. D8/D0 retain production
dispatch. All public Q32/R16/C and N/D preserve exactly. Source-only optional
research: second tail occupies $0800 caller-owned RAM and is NOT eligible for
default promotion until resident placement and mixed-call/IRQ gates are proven.
"""
from __future__ import annotations
import hashlib,json,statistics,sys,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import preprocess,parse_config
from issue144_signed32_rq_tail_fusion_screen import machine
from validate_udiv32_16_integrated import one
from issue144_u3216_fullcall_source_transplant_screen import cases as common_cases
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
OPS=("MATH_UDIV32_16","MATH_UMOD32_16")
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

def low_divisor_tail():
    out=["* = $0800","U3216_LOW_DIV:",
         "        ; On this entry 256<=D<=32767, so 2R+bit<65536.",
         "        jsr U3216_DIV16","        lda U3216_R1"]
    for i in range(16):
        q="U3216_LN1" if i<8 else "U3216_LN0"
        out += [f"U3216_LD_B{i}:",
                f"        rol {q}","        rol U3216_R0","        rol",
                "        cmp U3216_D1",f"        bcc U3216_LD_NEXT{i}",
                f"        bne U3216_LD_TAKE{i}",
                "        ldx U3216_R0","        cpx U3216_D0",
                f"        bcc U3216_LD_NEXT{i}",
                f"U3216_LD_TAKE{i}:",
                "        tax","        lda U3216_R0",
                "        sbc U3216_D0","        sta U3216_R0",
                "        txa","        sbc U3216_D1","        sec",
                f"U3216_LD_NEXT{i}:"]
        if i==7:out.append("        rol U3216_LN1")
    out+=["        rol U3216_LN0","        clc",
          "        jmp U3216_FINISH","U3216_LD_END:"]
    return "\n".join(out)+"\n"

def builds(profile,kind):
    cfg=ROOT/"relocatable_source"/profile/("math_config_"+kind+".inc")
    v=parse_config(cfg)
    orig=preprocess(ROOT/"relocatable_source"/profile/"math_relocatable.asm",cfg)
    assert orig.count(ENTRY_OLD)==1
    assert orig.count(STUB_BEFORE)==1
    new=orig.replace(ENTRY_OLD,ENTRY_NEW).replace(STUB_BEFORE,STUB_AFTER)
    new+="\n"+low_divisor_tail()
    baseline,api=machine(orig,profile)
    candidate,other=machine(new,profile)
    assert api["MATH_UDIV32_16"]==other["MATH_UDIV32_16"]
    assert api["MATH_UMOD32_16"]==other["MATH_UMOD32_16"]
    assert (candidate.mem[0x0800:other["U3216_LD_END"]] != baseline.mem[0x0800:other["U3216_LD_END"]])
    assert other["U3216_LD_END"]<=0x0A40,(profile,kind,"caller owned trial too large",hex(other["U3216_LD_END"]))
    assert other["U3216_MAIN_END"]<v["REG_KERNEL"]+0x1272
    return baseline,candidate,api,v,other["U3216_LD_END"]-0x0800

def vectors():
    v=[("common",n,d) for n,d in common_cases()]
    rng=random.Random(0x144B16D)
    v += [("lowD",rng.getrandbits(32),rng.randrange(256,32768)) for _ in range(512)]
    v += [("highD",rng.getrandbits(32),rng.randrange(32768,65536)) for _ in range(512)]
    return v

def stats(a):
    s=sorted(a)
    return {"cases":len(a),"mean_saved":statistics.mean(a),
            "worst_saved":s[0],"p05_saved":s[int(.05*(len(s)-1))],
            "p95_saved":s[int(.95*(len(s)-1))],
            "best_saved":s[-1],"slower":sum(x<0 for x in a),
            "equal":sum(x==0 for x in a)}

def main():
    pairs=vectors()
    report={"status":"PASS_DUALTAIL_ALL_DOMAIN_SOURCE_SCREEN","per_api_cases":len(pairs),
            "corpus_sha256":hashlib.sha256(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little") for _,n,d in pairs)).hexdigest(),
            "profiles":{},"normal_zp_growth":0,
            "caller_owned_code":True,"native_vice_qualified":False,"public_binaries_unchanged":True}
    for profile in PROFILES:
        report["profiles"][profile]={}
        for kind in ("reference","alternate"):
            old,new,api,v,sz=builds(profile,kind)
            results={}
            for operation in OPS:
                groups={k:[] for k in ("D0","D8","lowD","highD")}
                for idx,(kind0,n,d) in enumerate(pairs):
                    oldsp,newsp=old.sp,new.sp
                    x,ok1,r1,expect=one(old,api[operation],n,d,v["MATH_IO"])
                    y,ok2,r2,_=one(new,api[operation],n,d,v["MATH_IO"])
                    assert ok1 and ok2 and r1==r2==expect,(profile,kind,operation,idx,hex(n),hex(d),r1,r2,expect)
                    assert old.sp==oldsp and new.sp==newsp,(profile,kind,operation,"stack")
                    k="D0" if d==0 else "D8" if d<256 else "lowD" if d<32768 else "highD"
                    groups[k].append(x-y)
                result={k:stats(vv) for k,vv in groups.items()}
                result["full"]=stats(sum(groups.values(),[]))
                result["candidate_optional_code_bytes"]=sz
                results[operation]=result
            report["profiles"][profile][kind]=results
            print("ISSUE144 DUALTAIL",profile,kind,"PASS",len(pairs)*2,flush=True)
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
