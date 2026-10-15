#!/usr/bin/env python3
"""Issue144 architecture stop/go: compare two real quotient-byte calls to 16-bit tail.

All inputs have full-width 32-bit numerator and high-bit-set 16-bit divisor,
so s=0 and no normalization cost. Multiplication-oracle and lookup-oracle
variants are intentionally NONEXECUTABLE optimization lower bounds. They
inject precomputed table/product bytes from Python before each CPU call.
The real candidate requires REU lookup and 8x8 shift-add multiplication.
Pair all methods on identical inputs with the known shared-subtract 16-bit
restoring tail. This is not public ABI or native/VIC-bus timing proof.
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
from issue144_u3216_radix256_numerical_research import LOOKUP_Q_R
from issue144_u3216_reu_digit_6510_screen import ASM
from issue144_u3216_shared_take_tail_research import assemble,execute

MUL_START="    ; q0 * divisor-low:"
MUL_END="    ; T = ((t0+Rlo)"
REU_START="    lda $71\n    asl"
REU_END="    ; q0 * divisor-low:"
EXPECTED_REU="    lda #$91\n    sta $df01\n"
ORACLE_MUL="""    ; qhat already in REU record, exact product injected by oracle
    lda $76
    sta $75

"""

def variant_src(which):
    src=ASM
    if which in ("oracle_mul","oracle_both"):
        a=src.index(MUL_START);b=src.index(MUL_END,a)
        src=src[:a]+ORACLE_MUL+src[b:]
    if which=="oracle_both":
        a=src.index(REU_START);b=src.index(REU_END,a)
        assert EXPECTED_REU in src[a:b]
        src=src[:a]+src[b:]
    assert which in ("real","oracle_mul","oracle_both")
    return src

def corpus():
    r=random.Random(0x144D3256)
    v=[(r.getrandbits(32),r.randrange(32768,65536)) for _ in range(650)]
    for d in (32768,32769,33023,49152,65534,65535):
        for n in (0,1,d,d+1,0xffff,0x10000,0x80000000,0xffffffff):
            v.append((n,d))
    return v

def stats(a):
    r=sorted(a)
    return {"cases":len(a),"mean":statistics.mean(a),"p50":statistics.median(a),
            "p95":r[int(.95*(len(r)-1))],"max":r[-1],"min":r[0]}

def main():
    pairs=corpus()
    cpu,api=load("v4_reu_16m")
    assert len(cpu.reu)>=0x210000
    assert not any(cpu.reu[0x200000:0x210000])
    cpu.reu[0x200000:0x210000]=LOOKUP_Q_R
    base=assemble("shared")
    baseline=[]
    for n,d in pairs:
        q,r,cycles=execute(base,n,d)
        assert q==((n//d)&65535) and r==n%d
        baseline.append(cycles)
    result={"status":"PASS_SYNTHETIC_RADIX256_COST_GATE",
            "scope":"two lower quotient digits, high divisor only, no normalization",
            "pairs":len(pairs),"baseline_shared_subtract_tail":stats(baseline),
            "variants":{},"optimistic_variants_are_not_executable_producers":True,
            "public_32by16_fast_core_replaced":False,
            "physical_reu_timing_measured":False}
    fingerprint=hashlib.sha256()
    for n,d in pairs: fingerprint.update(n.to_bytes(4,"little")+d.to_bytes(2,"little"))
    result["corpus_sha256"]=fingerprint.hexdigest()
    for variant in ("real","oracle_mul","oracle_both"):
        code,labels,_=Assembler().assemble(variant_src(variant))
        assert min(code)==0x0d00 and max(code)<0x1000
        for pc,val in code.items(): cpu.mem[pc]=val
        cycles_all=[];benefit=[]
        for n,d in pairs:
            rem=(n>>16)%d
            digits=[]
            total=0
            for byte in ((n>>8)&255,n&255):
                cpu.mem[0x70]=rem&255
                cpu.mem[0x71]=(rem>>8)&255
                cpu.mem[0x72]=d&255
                cpu.mem[0x73]=d>>8
                cpu.mem[0x74]=byte
                cpu.mem[0x75]=0
                off=(((d>>8)-128)<<9)|((rem>>8)<<1)
                guess=LOOKUP_Q_R[off]
                if variant=="oracle_both":
                    cpu.mem[0x76]=guess
                    cpu.mem[0x77]=LOOKUP_Q_R[off+1]
                if variant!="real":
                    p=guess*(d&255)
                    cpu.mem[0x7c]=p&255
                    cpu.mem[0x7d]=p>>8
                cy=cpu.call(labels["digit"],8000)
                total+=cy
                digits.append(cpu.mem[0x75])
                rem=cpu.mem[0x70]|(cpu.mem[0x71]<<8)
            lowq=(digits[0]<<8)|digits[1]
            assert (lowq,rem)==(((n//d)&65535),n%d),(
                variant,hex(n),hex(d),digits,rem,n//d,n%d)
            cycles_all.append(total)
        savings=[a-b for a,b in zip(baseline,cycles_all)]
        result["variants"][variant]={"code_bytes":len(code),
          "two_digits":stats(cycles_all),
          "mean_tail_cycles_saved_vs_shared":statistics.mean(savings),
          "worst_tail_saving":min(savings),
          "fraction_faster":sum(x>0 for x in savings)/len(savings),
          "fraction_slower":sum(x<0 for x in savings)/len(savings),
          "cost_included":{
             "REU_lookup":variant!="oracle_both",
             "8x8_multiply":variant=="real",
             "carry_remainder_correction":True}}
        print(variant,result["variants"][variant],flush=True)
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
