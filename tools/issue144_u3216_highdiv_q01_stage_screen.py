#!/usr/bin/env python3
"""Issue 144 B: actual high-divisor 16/16 pre-producer 0-or-1 quotient screen.

For D >= $8000, floor(Nhi16/D) can be only 0 or 1, so bypassing the
general high-word divide might reduce ordinary full N32/D16 cost.

Compare the exact shipped V2 resident's internal 16/16 helper at $420C
against a separately assembled, standalone NMOS 6510 compare/subtract.
These are INTERNAL STAGE measurements (not public UDIV32_16 cycles);
do not replace normal math, publish an unqualified ABI, or claim VICE pass.
"""
from __future__ import annotations
import hashlib
import json
import random
import statistics
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import load

# The certified V2/V3/V4 U3216 split producer uses scratch:
# N0/N1=$10/$11, D0/D1=$12/$13, Q2/Q3=$14/$15, R0/R1=$16/$17.
# This trial intentionally uses precisely that internal stage ABI.
ASM="""
!cpu 6510
* = $0D00
highword_q0or1:
    lda $11
    cmp $13
    bcc quotient_zero
    bne quotient_one
    lda $10
    cmp $12
    bcc quotient_zero
quotient_one:
    sec
    lda $10
    sbc $12
    sta $16
    lda $11
    sbc $13
    sta $17
    lda #$01
    sta $14
    lda #$00
    sta $15
    clc
    rts
quotient_zero:
    lda $10
    sta $16
    lda $11
    sta $17
    lda #$00
    sta $14
    sta $15
    clc
    rts
"""
COMMON_BASE=0x420C

def vectors():
    rng=random.Random(0x144321601)
    result=[]
    for d in (0x8000,0x8001,0x8002,0x80ff,0x9000,0xbfff,
              0xc000,0xff00,0xff01,0xfffe,0xffff):
        for n in (0,1,d-1,d,d+1,0x7fff,0x8000,0x8001,
                  0xffff,max(0, d//2),min(0xffff,2*d-1)):
            if 0<=n<=0xffff:
                result.append((n,d))
    for _ in range(12000):
        result.append((rng.getrandbits(16),rng.randrange(32768,65536)))
    return result

def put(cpu,n,d):
    for address,val in ((0x10,n&255),(0x11,n>>8),(0x12,d&255),
                        (0x13,d>>8),(0x14,0xA5),(0x15,0x5A),
                        (0x16,0x3C),(0x17,0xC3)):
        cpu.mem[address]=val
    cpu.d=0
    cpu.c=0

def get(cpu):
    q=cpu.mem[0x14]+(cpu.mem[0x15]<<8)
    r=cpu.mem[0x16]+(cpu.mem[0x17]<<8)
    return q,r

def stats(values):
    s=sorted(values)
    return {"mean":statistics.mean(values),"median":statistics.median(values),
            "p95":s[int(.95*(len(s)-1))],
            "min":s[0],"max":s[-1]}

def main():
    pairs=vectors()
    old,api=load("v2_pareto_fast")
    new,api2=load("v2_pareto_fast")
    assert api["MATH_UDIV32_16"]==0x31B0
    code,labels,_=Assembler().assemble(ASM)
    assert min(code)==0x0D00 and max(code)<0x0E00
    for pc,val in code.items(): new.mem[pc]=val
    orig=[],changed=[],outcome=[]
    digest=hashlib.sha256()
    for index,(n,d) in enumerate(pairs):
        digest.update(n.to_bytes(2,"little")+d.to_bytes(2,"little"))
        put(old,n,d);put(new,n,d)
        s0,s1=old.sp,new.sp
        a=old.call(COMMON_BASE,20000)
        b=new.call(labels["highword_q0or1"],20000)
        expected=divmod(n,d)
        z0,z1=get(old),get(new)
        assert z0==z1==expected,(index,hex(n),hex(d),z0,z1,expected,
                                 "carry",(old.c,new.c))
        assert old.mem[0x10:0x14]==new.mem[0x10:0x14] and old.sp==s0 and new.sp==s1
        orig.append(a);changed.append(b);outcome.append("q0" if n<d else "q1")
    delta=[x-y for x,y in zip(orig,changed)]
    result={
       "status":"PASS_INTERNAL_STAGE_6502_MODEL",
       "scope":"16/16 high-word quotient stage only, D>=0x8000",
       "profile":"v2_pareto_fast","cases":len(pairs),
       "corpus_sha256":digest.hexdigest(),
       "baseline_internal_helper_address":"$420C",
       "candidate_address":"$0D00",
       "candidate_code_bytes":len(code),
       "original_highword_cycles":stats(orig),
       "candidate_q0or1_cycles":stats(changed),
       "cycles_saved":stats(delta),
       "slower_cases":sum(x<0 for x in delta),
       "cycles_by_q0or1":{},
       "baseline_C_flags":list(sorted(set(old.c for _ in (0,)))),
       "normal_public_32by16_call_verified":False,
       "native_vice_verified":False,
       "all_D16_unrestricted_public_entry_optimized":False,
       "resident_prg_changed":False,
       "private_optisearch_published":False
    }
    for kind in ("q0","q1"):
        selected=[delta[i] for i,v in enumerate(outcome) if v==kind]
        result["cycles_by_q0or1"][kind]={"cases":len(selected),"saved":stats(selected)}
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
