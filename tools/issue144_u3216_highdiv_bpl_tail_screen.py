#!/usr/bin/env python3
"""Issue144: high-divisor BPL fast reject, complete 16-bit low quotient tail.

All candidates are self-contained NMOS 6502 assembler fragments. They are
NOT installed public UDIV/UMOD32_16 and do not include high-word DIV16.
The only extra predicate is valid if $8000<=D<=$FFFF: on a nonoverflown
shifted remainder whose high byte is <$80, quotient bit must be zero.
Includes identical-input baseline and shared-take comparator.
"""
from __future__ import annotations
import hashlib, json, random, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from issue144_u3216_shared_take_tail_research import source as shared_source, execute
from mini6502 import Assembler

def candidate_source(which):
    if which=="highdiv_bpl":
        s=shared_source("shared")
        for i in range(16):
            before="bcs TAKE_"+str(i)+"\n"
            assert s.count(before)==1, i
            s=s.replace(before,before+"bpl NEXT_"+str(i)+"\n")
        return s
    return shared_source(which)

def code(which):
    a, _, _ = Assembler().assemble(candidate_source(which))
    assert min(a)==0x2070
    return a

def inputs():
    r=random.Random(0x144B5032)
    out=[(r.getrandbits(32), r.randrange(0x8000,0x10000)) for _ in range(18000)]
    for d in (0x8000,0x8001,0x8002,0x807f,0x8080,0x80ff,
              0x8100,0x9fff,0xa000,0xc000,0xfeff,0xff00,0xfffe,0xffff):
        for n in (0,1,2,d-1,d,d+1,d*2-1,d*2,d*2+1,
                  0xffff,0x10000,0x10001,0x7fffffff,
                  0x80000000,0xfffffffe,0xffffffff):
            out.append((n,d))
    return out

def summarize(values):
    values=sorted(values)
    return {"mean":statistics.mean(values),"median":statistics.median(values),
            "min":values[0],"p05":values[int(.05*(len(values)-1))],
            "p95":values[int(.95*(len(values)-1))],"max":values[-1]}

def main():
    variants={name:code(name) for name in ("baseline","shared","highdiv_bpl")}
    samples=inputs()
    digest=hashlib.sha256()
    cycles={name:[] for name in variants}
    for i,(n,d) in enumerate(samples):
        digest.update(n.to_bytes(4,"little")+d.to_bytes(2,"little"))
        exp=((n//d)&65535,n%d)
        for name,mem in variants.items():
            q,r,cy=execute(mem,n,d)
            assert (q,r)==exp,(name,i,hex(n),hex(d),(q,r),exp)
            cycles[name].append(cy)
    saved_from_stock=[a-b for a,b in zip(cycles["baseline"],cycles["highdiv_bpl"])]
    saved_from_shared=[a-b for a,b in zip(cycles["shared"],cycles["highdiv_bpl"])]
    result={"status":"PASS_HIGH_DIVISOR_TAIL_MODEL_SCREEN",
        "scope":"low-16 quotient and remainder only; high-word oracle seeded",
        "requires_divisor_range":"$8000-$FFFF",
        "cases":len(samples),"corpus_sha256":digest.hexdigest(),
        "resident_equivalence_or_native_vice_qualified":False,
        "code_bytes":{name:len(mem) for name,mem in variants.items()},
        "cycles":{name:summarize(cys) for name,cys in cycles.items()},
        "save_from_shipped_like_tail":summarize(saved_from_stock),
        "save_from_shared_take_tail":summarize(saved_from_shared),
        "regressions_vs_shared":sum(v<0 for v in saved_from_shared),
        "regressions_vs_baseline":sum(v<0 for v in saved_from_stock),
        "accepted_restriction":"D>=32768 required: invalid on lower divisor",
        "full_public_call_speedup_not_measured":True,
        "public_binaries_modified":False}
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
