#!/usr/bin/env python3
"""Issue144 B: full-width numerator, D16<0x8000, 16-step tail proof.

Source-only independent research; no public binary/ABI modified.
The intermediate residual satisfies 0 <= r < d. For 1<=d<0x8000,
2*r + input_bit <= 2*(0x7ffe)+1 < 0x10000, so the 17th
carry from ROL high is unreachable. Delete the forced-subtract branch
and redundant forced-subtract body from EVERY iteration, keeping the
ordinary compare-before-subtract path. This is an exact normal 6510
producer for the sixteen low dividend bits only. High quotient/remainder
are seeded by the 16/16 mathematical oracle, NOT by any call to C64ML.
Do not claim a public ABI or unrestricted divisor improvement.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,random,statistics,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from issue144_u3216_shared_take_tail_research import source,assemble,execute

START="$2070"

def low_d_source():
    s=source("baseline")
    for i in range(16):
        first=f"bcs FORCE_{i}\n"
        last=f"NEXT_{i}:"
        assert s.count(first)==1, (i,first)
        a=s.index(first)
        b=s.index(last,a)
        segment=s[a:b]
        assert segment.count(f"FORCE_{i}:")==1
        assert segment.count(f"TAKE_{i}:")==1
        assert segment.count("sbc $31")==2
        replacement=(
            "    cmp $31\n"
            f"    bcc NEXT_{i}\n"
            f"    bne TAKE_{i}\n"
            "    ldx $32\n"
            "    cpx $30\n"
            f"    bcc NEXT_{i}\n"
            f"TAKE_{i}:\n"
            "    tax\n"
            "    lda $32\n"
            "    sbc $30\n"
            "    sta $32\n"
            "    txa\n"
            "    sbc $31\n"
        )
        s=s[:a]+replacement+s[b:]
    assert "FORCE_" not in s
    return s

def corpus():
    rng=random.Random(0x144003216)
    ds=[1,2,3,7,15,31,127,128,255,256,257,258,
        511,512,513,1023,1024,0x1fff,0x2000,0x3fff,
        0x4000,0x4001,0x7ffe,0x7fff]
    ns=[0,1,2,3,7,255,256,65535,65536,65537,
        0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    v=[(n,d) for d in ds for n in ns]
    v.extend((rng.getrandbits(32),rng.randint(1,0x7fff)) for _ in range(10240))
    v.extend((rng.getrandbits(32),rng.randint(1,255)) for _ in range(2400))
    assert len(v)==12976
    return v

def stats(v):
    sorted_v=sorted(v)
    return {"n":len(v),"mean":statistics.mean(v),"median":statistics.median(v),
            "p95":sorted_v[int((len(v)-1)*.95)],"min":min(v),"max":max(v)}

def main():
    original=assemble("baseline")
    candidate,_,_=Assembler().assemble(low_d_source())
    assert min(candidate)==min(original)==0x2070
    pairs=corpus()
    baseline=[]
    after=[]
    fingerprint=hashlib.sha256()
    for n,d in pairs:
        assert 1<=d<0x8000
        fingerprint.update(n.to_bytes(4,"little")+d.to_bytes(2,"little"))
        q0,r0,c0=execute(original,n,d)
        q1,r1,c1=execute(candidate,n,d)
        want=((n//d)&0xffff,n%d)
        assert (q0,r0)==(q1,r1)==want,(hex(n),hex(d),q0,r0,q1,r1,want)
        baseline.append(c0)
        after.append(c1)
    saving=[x-y for x,y in zip(baseline,after)]
    report={
       "status":"PASS_RESTRICTED_D_LOW16_TAIL_ONLY",
       "numerator_domain":"all N32",
       "divisor_domain":"1<=D16<0x8000 (NOT unrestricted D16)",
       "tail_only_no_public_call_or_native_VICE_proof":True,
       "highword_seed":"mathematical oracle",
       "pairs":len(pairs),
       "corpus_sha256":fingerprint.hexdigest(),
       "origin":"$2070",
       "baseline_code_bytes":len(original),
       "candidate_code_bytes":len(candidate),
       "baseline_cycles":stats(baseline),
       "candidate_cycles":stats(after),
       "savings":stats(saving),
       "slower_cases":sum(x<0 for x in saving),
       "equal_cases":sum(x==0 for x in saving),
       "all_cases_speedup_or_equal":all(x>=0 for x in saving),
       "scratch_extra_zp":0,
       "default_math_library_modified":False,
       "optisearch_private_source_published":False
    }
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    main()
