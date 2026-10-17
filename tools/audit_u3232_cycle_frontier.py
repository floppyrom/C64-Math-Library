#!/usr/bin/env python3
"""Source-authenticated unsigned 32/32 DIV+MOD public-call cycle tail audit.

Research only: no automatic source promotion and no new CPU/native VICE timing
claim. Each candidate is called on IDENTICAL inputs at TWO code placements,
with the real public ABI (Q32/R32/C, preserved N/D, SP and immutable code).
Grouped means, nearest-rank p95, maxima and paired deltas expose workloads
hidden by one corpus mean. All costs are mini6502 model cycles through RTS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

from mini6502 import CPU,load_sparse
import selective_linker
import selective_speed_u3232 as speed

ROOT=Path(__file__).resolve().parents[1]
MASK=0xffffffff
SEED=0x32322027
BANDS=("divisor_zero","quotient_zero","quotient_one","quotient_2_to_15",
       "divisor_8bit","divisor_16bit","divisor_24bit","divisor_32bit",
       "divisor_power_of_two")
MAPS=((0x8000,0xc000,0xc020,0x50),(0x7123,0xc040,0xc080,0x70))
APIS=("MATH_UDIV32_32","MATH_UMOD32_32")

def corpus(per_band=64):
    if not isinstance(per_band,int) or not 1<=per_band<=256:
        raise ValueError("per_band must be an integer between 1 and 256")
    rng=random.Random(SEED)
    out={key:[] for key in BANDS}
    for _ in range(per_band):
        out["divisor_zero"].append((rng.getrandbits(32),0))
        d=rng.randrange(1<<24,1<<32)
        out["quotient_zero"].append((rng.randrange(d),d))
        d=rng.randrange(1<<20,1<<31)
        out["quotient_one"].append((d+rng.randrange(d),d))
        d=rng.randrange(1,1<<26)
        q=rng.randrange(2,16)
        out["quotient_2_to_15"].append((q*d+rng.randrange(d),d))
        n=rng.getrandbits(32)
        out["divisor_8bit"].append((n,rng.randrange(1,256)))
        out["divisor_16bit"].append((rng.getrandbits(32),
                                       rng.randrange(256,1<<16)))
        out["divisor_24bit"].append((rng.getrandbits(32),
                                       rng.randrange(1<<16,1<<24)))
        out["divisor_32bit"].append((rng.getrandbits(32),
                                       rng.randrange(1<<24,1<<32)))
        out["divisor_power_of_two"].append((rng.getrandbits(32),
                                               1<<rng.randrange(32)))
    if any(len(seq)!=per_band for seq in out.values()):
        raise AssertionError("unexpected band case counts")
    if any(not (0<=n<=MASK and 0<=d<=MASK)
           for seq in out.values() for n,d in seq):
        raise AssertionError("overflowed 32/32 corpus")
    return out

def fingerprint(groups):
    return hashlib.sha256(b"".join(
        n.to_bytes(4,"little")+d.to_bytes(4,"little")
        for name in BANDS for n,d in groups[name])).hexdigest()

def describe(ticks):
    ordered=sorted(ticks)
    if not ordered:
        raise ValueError("empty cycle distribution")
    return {"cases":len(ordered),"mean":round(sum(ordered)/len(ordered),6),
            "median":(ordered[(len(ordered)-1)//2]+ordered[len(ordered)//2])/2,
            "p95":ordered[math.ceil(len(ordered)*0.95)-1],
            "worst":ordered[-1],"best":ordered[0]}

def _run_one(api,ident,mod,location,groups,root):
    code,io,scratch,zp=location
    image,entry=speed.assemble_source(api,ident,mod,code,io,scratch,zp,root)
    cpu=CPU(load_sparse(image));initial_sp=cpu.sp
    ticks={}
    for name in BANDS:
        measured=[]
        for i,(n,d) in enumerate(groups[name]):
            nb=n.to_bytes(4,"little");db=d.to_bytes(4,"little")
            cpu.mem[io+16:io+20]=nb
            cpu.mem[io+20:io+24]=db
            cpu.mem[io+24:io+28]=b"\x55"*4
            cpu.mem[io+28:io+32]=b"\x66"*4
            cpu.c=(i^n^d)&1
            cpu.d=0
            cycles=cpu.call(entry,150000)
            q=int.from_bytes(cpu.mem[io+24:io+28],"little")
            r=int.from_bytes(cpu.mem[io+28:io+32],"little")
            want_q=n//d if d else 0
            want_r=n%d if d else 0
            if ((api=="MATH_UDIV32_32" and q!=want_q)
                or r!=want_r or cpu.c!=int(d==0)
                or cpu.sp!=initial_sp
                or cpu.mem[io+16:io+20]!=nb
                or cpu.mem[io+20:io+24]!=db):
                raise AssertionError((api,ident,name,hex(n),hex(d),
                                      (q,r,cpu.c),(want_q,want_r,int(d==0))))
            measured.append(cycles)
        ticks[name]=measured
    if any(cpu.mem[addr]!=byte for addr,byte in image.items()):
        raise AssertionError((api,ident,"unexpected code mutation"))
    return ticks

def audit(per_band=64,root=ROOT,maps=MAPS):
    groups=corpus(per_band)
    results={"status":"QUALIFIED_CPU_MODEL_DIAGNOSTIC_NO_PROMOTION",
             "source":"tools/audit_u3232_cycle_frontier.py",
             "corpus_sha256":fingerprint(groups),
             "per_band":per_band,"bands":list(BANDS),
             "timing":"mini6502 complete public calls through RTS; NOT native VICE timing",
             "locations":{}}
    for code,io,scratch,zp in maps:
        name="$%04X"%code
        rec={}
        for api in APIS:
            mods=selective_linker.MODULES[api]
            if set(mods)!=speed.EXPECTED[api]:
                raise AssertionError((api,"uncertified candidate-set change"))
            candidates={}
            sequences={}
            for ident,mod in sorted(mods.items()):
                observations=_run_one(api,ident,mod,(code,io,scratch,zp),groups,root)
                sequences[ident]=observations
                all_ticks=[tick for band in BANDS for tick in observations[band]]
                candidates[ident]={
                    "source":mod["source"],
                    "source_sha256":hashlib.sha256((root/mod["source"]).read_bytes()).hexdigest(),
                    "code_bytes":sum(n for _,n in mod["segments"]),
                    "zp_bytes":mod["zp"],"private_ram_scratch_bytes":mod["scratch"],
                    "overall":describe(all_ticks),
                    "bands":{band:describe(observations[band]) for band in BANDS}
                }
            baseline=next((z for z in
                           ("link:shared-aligned-zerozp","link:aligned-zerozp")
                           if z in sequences),sorted(sequences)[0])
            paired={}
            for ident in sorted(sequences):
                if ident==baseline:
                    continue
                bands={}
                for band in BANDS:
                    changes=[now-prev for now,prev in zip(
                        sequences[ident][band],sequences[baseline][band])]
                    bands[band]={
                        "mean_delta":round(sum(changes)/len(changes),6),
                        "worst_regression":max(changes),
                        "faster_cases":sum(x<0 for x in changes),
                        "slower_cases":sum(x>0 for x in changes),
                        "equal_cases":sum(x==0 for x in changes)}
                paired[ident]=bands
            rec[api]={"baseline":baseline,"candidates":candidates,
                      "paired_cycle_deltas":paired}
        results["locations"][name]=rec
    return results

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases-per-band",type=int,default=64)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=audit(args.cases_per_band)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    for origin,ops in report["locations"].items():
        for api,measurement in ops.items():
            for variant,entry in measurement["candidates"].items():
                val=entry["overall"]
                print("U3232 STRATIFIED",origin,api,variant,
                      "mean",val["mean"],"p95",val["p95"],"worst",val["worst"],
                      "bytes",entry["code_bytes"],"zp",entry["zp_bytes"],
                      flush=True)
    print("U3232 STRATIFIED VERIFIED",
          sum(len(rec["candidates"]) for apis in report["locations"].values()
              for rec in apis.values()),
          "candidate-map observations",
          args.cases_per_band*len(BANDS),"inputs per candidate",flush=True)

if __name__=="__main__":
    main()
