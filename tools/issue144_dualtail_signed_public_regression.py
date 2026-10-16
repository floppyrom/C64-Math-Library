#!/usr/bin/env python3
"""Issue #144 B signed public ABI regression for V2-V4 dual-tail 32/16.

Same-input ordinary SDIV32_16 and SMOD32_16 via the production signed front
ends; variant changes only U3216 division magnitude input routing. This
checks carry, full Q32/R16, preserved N/D, balanced stack and repeat-call
isolation. Source-only optional caller-owned $0800 code, not a default release.
"""
from __future__ import annotations
import hashlib,json,random,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from issue144_u3216_dualtail_direct_dispatch_screen import builds,PROFILES
from validate_signed_division import div_expected,wr,rd

OPS=("MATH_SDIV32_16","MATH_SMOD32_16")
def vectors():
    rng=random.Random(0x144B51)
    out=[]
    ds=[0,1,2,3,7,15,127,128,255,256,257,32767,32768,32769,65535,0xffff,0xff00,0x8001,0x7f00]
    ns=[0,1,2,3,7,0x7fffffff,0x80000000,0x80000001,0xffffffff,0xffff0000,0x00010000,0xdeadbeef,0x12345678]
    for n in ns:
        for d in ds:out.append(("edges",n,d))
    for quadrant in range(4):
        for k in range(350):
            n=rng.randrange(1,0x80000000)
            d=rng.randrange(1,32769)
            if quadrant&2:n=(-n)&0xffffffff
            if quadrant&1:d=(-d)&0xffff
            out.append((f"quadrant{quadrant}",n,d))
    for k in range(160):
        n=rng.getrandbits(32)
        out.append(("divzero",n,0))
    for k in range(160):
        n=rng.getrandbits(32)
        out.append(("highmag",n,0x8000))
    return out

def stats(v):
    a=sorted(v)
    return {"calls":len(v),"mean_cycles_saved":statistics.mean(v),
            "p05_saved":a[int(.05*(len(a)-1))],
            "p95_saved":a[int(.95*(len(a)-1))],
            "worst_saved":a[0],"best_saved":a[-1],
            "slower":sum(x<0 for x in v)}

def exercise(cpu,entry,io,n,d):
    N,D,Q,R=io+0x10,io+0x14,io+0x18,io+0x1c
    wr(cpu.mem,N,n,4);wr(cpu.mem,D,d,2)
    sp=cpu.sp
    cy=cpu.call(entry,4_000_000)
    got=(rd(cpu.mem,Q,4),rd(cpu.mem,R,2),cpu.c)
    assert cpu.sp==sp,("unbalanced stack",hex(n),hex(d))
    assert (rd(cpu.mem,N,4),rd(cpu.mem,D,2))==(n,d),("modified inputs",hex(n),hex(d))
    return cy,got,cpu.status(),cpu.a,cpu.x,cpu.y

def main():
    corpus=vectors()
    result={"status":"PASS_DUALTAIL_SIGNED32_16_PUBLIC_MODEL",
            "source_optimized_unsigned_magnitude_only":True,
            "native_signed_vice_qualified":False,
            "caller_owned_RAM_bytes":461,
            "ordinary_binaries_unchanged":True,
            "pairs_per_api_per_layout":len(corpus),
            "sha256":hashlib.sha256(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little") for _,n,d in corpus)).hexdigest(),
            "profiles":{}}
    for profile in PROFILES:
        result["profiles"][profile]={}
        for layout in ("reference","alternate"):
            original,trial,api,config,size=builds(profile,layout)
            assert size==461
            io=config["MATH_IO"]
            rr={}
            for op in OPS:
                classes={}
                changed_status=0
                for idx,(domain,n,d) in enumerate(corpus):
                    a0,g0,s0,acc0,x0,y0=exercise(original,api[op],io,n,d)
                    a1,g1,s1,acc1,x1,y1=exercise(trial,api[op],io,n,d)
                    want=div_expected(n,32,d,16,32,16)
                    assert g0==g1==want,(profile,layout,op,idx,domain,hex(n),hex(d),g0,g1,want)
                    if s0!=s1: changed_status+=1
                    classes.setdefault(domain,[]).append(a0-a1)
                all_deltas=sum(classes.values(),[])
                rr[op]={"overall":stats(all_deltas),
                         "classes":{k:stats(x) for k,x in classes.items()},
                         "volatile_status_differences":changed_status}
            result["profiles"][profile][layout]=rr
            print("SIGNED DUALTAIL",profile,layout,"PASS",len(corpus)*len(OPS),flush=True)
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=="__main__":main()
