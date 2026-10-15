#!/usr/bin/env python3
"""Issue144 all-D16 *tail-only* dual-producer projected performance triage.

LOW divisor: no-17th-bit branch tail proven in PR #164.
HIGH divisor: shared-forced-subtract tail proven in PR #161.
Every pair uses one shared uniform N32/D16 corpus, oracle-seeded high-word
remainder, and real assembled NMOS 6502 instruction cycles for BOTH paths.
Independent full-public V2 UDIV32_16 baseline on EXACT SAME input pairs
measures the denominator for a *projected* benefit; no dispatcher/control
overhead is installed here. This does not qualify a full-public combined
implementation or a 5% shipped speedup; it is explicitly an upper-bound screen.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import random
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from issue144_u3216_shared_take_tail_research import assemble,execute
from issue144_u3216_nooverflow_lowd_tail_screen import low_d_source
from benchmark_multiply_refresh import load

def pairs():
    r=random.Random(0x144DD2026)
    p=[(r.getrandbits(32),r.randrange(1,65536)) for _ in range(4096)]
    for d in (1,2,3,0xff,0x100,0x101,0x7ffe,0x7fff,
              0x8000,0x8001,0xff00,0xffff):
        for n in (0,1,d-1,d,d+1,0xffff,0x10000,
                  0x7fffffff,0x80000000,0xffffffff):
            p.append((n,d))
    return p

def stats(v):
    s=sorted(v);return {"mean":statistics.mean(v),"median":statistics.median(v),
       "p95":s[int(.95*(len(s)-1))],"min":s[0],"max":s[-1]}

def main():
    generic=assemble("baseline")
    shared=assemble("shared")
    no_over,_,_=Assembler().assemble(low_d_source())
    assert (len(generic),len(shared),len(no_over))==(684,492,444)
    old,api=load("v2_pareto_fast")
    results={}
    digest=hashlib.sha256()
    gains=[]
    full_cycles=[]
    groups={"D_1_255":[],"D_256_32767":[],"D_32768_65535":[]}
    allpairs=pairs()
    for n,d in allpairs:
        digest.update(n.to_bytes(4,"little")+d.to_bytes(2,"little"))
        q0,r0,c0=execute(generic,n,d)
        source=no_over if d<32768 else shared
        q1,r1,c1=execute(source,n,d)
        oracle=(n//d&65535,n%d)
        assert (q0,r0)==(q1,r1)==oracle,(hex(n),hex(d),oracle,
                                         q0,r0,q1,r1)
        old.mem[0xc010:0xc014]=n.to_bytes(4,"little")
        old.mem[0xc014:0xc016]=d.to_bytes(2,"little")
        cycles=old.call(api["MATH_UDIV32_16"],100000)
        q=int.from_bytes(old.mem[0xc018:0xc01c],"little")
        rem=int.from_bytes(old.mem[0xc01c:0xc01e],"little")
        assert (q,rem,old.c)==(n//d,n%d,0),(hex(n),hex(d),q,rem,old.c)
        saved=c0-c1
        full_cycles.append(cycles)
        gains.append(saved)
        key="D_1_255" if d<256 else "D_256_32767" if d<32768 else "D_32768_65535"
        groups[key].append((saved,cycles))
    absolute=statistics.mean(gains)
    baseline=statistics.mean(full_cycles)
    ans={
       "status":"PASS_DUAL_TAIL_IDENTICAL_CORPUS_TRIAGE_ONLY",
       "pairs":len(allpairs),
       "corpus_sha256":digest.hexdigest(),
       "source_bytes_tail_variants":{"baseline":684,"high_D_shared":492,"low_D_nooverflow":444},
       "full_public_baseline_cycles":stats(full_cycles),
       "tail_only_ideal_savings":stats(gains),
       "ideal_fraction_of_full_public_mean":absolute/baseline,
       "mean_saved_at_hypothetical_dispatch_cost_0_2_4_6_cycles":
         {str(k):{"mean_saved":absolute-k,"fraction_of_public":(absolute-k)/baseline}
          for k in (0,2,4,6)},
       "never_claim_full_public_replacement":True,
       "zero_divisor_excluded":True,
       "preexisting_shipped_API_unchanged":True,
       "requires_two_producer_tail_blocks":True,
       "real_6510_dispatch_placement_not_built":True,
       "native_VICE_not_qualified":True,
       "extra_normal_ZP_not_measured_for_splice":True,
       "private_optisearch_source_used":False,
       "groups":{k:{"count":len(v),"mean_tail_saved":statistics.mean(x[0] for x in v),
                    "mean_public_baseline":statistics.mean(x[1] for x in v),
                    "tail_speedup_percent_of_public":100*sum(x[0] for x in v)/sum(x[1] for x in v)}
                 for k,v in groups.items()}
    }
    print(json.dumps(ans,indent=2))
if __name__=="__main__":
    main()
