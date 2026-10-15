#!/usr/bin/env python3
"""Issue144 B: independent complete public 32/16 hybrid producer screen.

One optional, caller-owned RAM source; Dhigh=$00 delegates D8/D0 to stock.
$0100<=D<=$7FFF uses the previously proved no-overflow unrolled tail.
D>=$8000 uses the new sign-bit-reject/shared-take unrolled tail. Both share
the same certified high-word helper, public input copy and output epilogue.
Tests true Q32/R16/C, input preservation and SP with public entry timings.
No modifications to shipped library, generator, REU, ZP or ABI.
"""
from __future__ import annotations
import hashlib, json, random, re, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from validate_udiv32_16_integrated import load_resident,one
from issue144_u3216_nooverflow_public_optional_screen import body as low_body, NAMES
from issue144_u3216_shared_take_tail_research import source as shared_src

PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
OPS=("MATH_UDIV32_16","MATH_UMOD32_16")
ENTRY=0x0800

def high_body():
    s=shared_src("shared")
    for i in range(16):
        k="bcs TAKE_"+str(i)+"\n"
        assert s.count(k)==1
        s=s.replace(k,k+"bpl NEXT_"+str(i)+"\n")
    lines=s.splitlines()[3:-2]
    out=[]
    for line in lines:
        for before,after in (
            ("$34","U3216_LN1"),("$33","U3216_LN0"),
            ("$32","U3216_R0"),("$31","U3216_D1"),("$30","U3216_D0")):
            line=line.replace(before,after)
        line=re.sub(r"\b(STEP|TAKE|NEXT)_(\d+)\b",r"H_\1_\2",line)
        out.append(line)
    return "\n".join(out)+"\n"

def hybrid_source():
    const="\n".join(k+" = $"+format(v,"02X") for k,v in NAMES.items())
    start="""
!cpu 6510
* = $0800
OPT_U3216_HYBRID:
    lda $c015
    bne DOIT
    jmp $31b0
DOIT:
    lda $c010
    sta U3216_LN0
    lda $c011
    sta U3216_LN1
    lda $c012
    sta U3216_N0
    lda $c013
    sta U3216_N1
    lda $c014
    sta U3216_D0
    lda $c015
    sta U3216_D1
    jsr $420c
    lda U3216_R1
    ldx U3216_D1
    bmi HI_JUMP
    jmp LOW_FIRST
HI_JUMP:
    jmp HIGH_FIRST
LOW_FIRST:
"""
    epilogue="""
    jmp FINISH
HIGH_FIRST:
"""
    finish="""
FINISH:
    sta $c01d
    lda U3216_LN0
    sta $c018
    lda U3216_LN1
    sta $c019
    lda U3216_Q2
    sta $c01a
    lda U3216_Q3
    sta $c01b
    lda U3216_R0
    sta $c01c
    clc
    rts
"""
    return const+"\n"+start+low_body()+epilogue+high_body()+finish

def generated():
    mem,labels,_=Assembler().assemble(hybrid_source())
    assert min(mem)==ENTRY and labels["OPT_U3216_HYBRID"]==ENTRY
    assert max(mem)<0x1000,("crosses installed resident",hex(max(mem)))
    return mem

def inputs():
    r=random.Random(0x144B3216A5)
    ds=(0,1,2,127,255,256,257,0x7ffe,0x7fff,0x8000,0x8001,0xfffe,0xffff)
    ns=(0,1,2,255,65535,65536,0x12345678,0x7fffffff,0x80000000,0xffffffff)
    rows=[(n,d,"edges") for d in ds for n in ns]
    rows += [(r.getrandbits(32),r.randint(1,65535),"uniform") for _ in range(640)]
    rows += [(r.getrandbits(32),r.randint(256,0x7fff),"lowdiv") for _ in range(640)]
    rows += [(r.getrandbits(32),r.randint(0x8000,0xffff),"highdiv") for _ in range(640)]
    rows += [(r.getrandbits(32),r.randint(1,255),"d8") for _ in range(256)]
    rows += [(r.getrandbits(32),0,"zero") for _ in range(64)]
    return rows

def stats(nums):
    if not nums:return None
    a=sorted(nums)
    return {"n":len(a),"mean":statistics.mean(a),
            "p05":a[int(.05*(len(a)-1))],"p95":a[int(.95*(len(a)-1))],
            "worst":a[0],"best":a[-1],
            "slower":sum(x<0 for x in a),"faster":sum(x>0 for x in a)}

def main():
    mem=generated()
    rows=inputs()
    digest=hashlib.sha256(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little") for n,d,_ in rows)).hexdigest()
    out={"status":"PASS_FULL_PUBLIC_HYBRID_SOURCE_SCREEN","profile_count":len(PROFILES),
      "cases_per_api_profile":len(rows),
      "corpus_sha256":digest,
      "code_bytes":len(mem),"code_start":hex(ENTRY),"code_end":hex(max(mem)),
      "code_sha256":hashlib.sha256(bytes(mem[k] for k in sorted(mem))).hexdigest(),
      "additional_normal_zp":0,"uses_existing_resident_scratch":True,
      "caller_owned_RAM_required":True,"not_irq_nmi_reentrant":True,
      "real_VICE_not_yet_qualified":True,"public_resident_modified":False,
      "profiles":{}}
    for p in PROFILES:
        before,api=load_resident(p)
        after,_=load_resident(p)
        for pc,b in mem.items():after.mem[pc]=b
        r={}
        for op in OPS:
            all_saves=[];groups={}
            for idx,(n,d,group) in enumerate(rows):
                a,ok1,got1,truth=one(before,api[op],n,d)
                b,ok2,got2,truth2=one(after,ENTRY,n,d)
                assert ok1 and ok2 and got1==got2==truth==truth2,(
                   p,op,idx,hex(n),hex(d),got1,got2,truth)
                gain=a-b
                all_saves.append(gain);groups.setdefault(group,[]).append(gain)
            r[op]={"all":stats(all_saves),
                    "categories":{k:stats(v) for k,v in groups.items()}}
        out["profiles"][p]=r
        print(p,r,flush=True)
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
