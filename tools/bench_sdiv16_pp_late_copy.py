#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILE="v2_pareto_fast"
N=0xC010; D=0xC014; Q=0xC018; R=0xC01C

def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try: out[k]=int(v[1:],16)
            except ValueError: pass
    return out
def load(prg,inc):
    b=prg.read_bytes(); a=b[0]|b[1]<<8
    mem=bytearray(65536); mem[a:a+len(b)-2]=b[2:]
    c=CPU(mem); c.d=0; api=parse_api(inc); c.call(api["MATH_INIT"],2_000_000)
    return c,api
def wr(m,a,v):
    m[a]=v&255; m[a+1]=(v>>8)&255
def rd(m,a): return m[a]|m[a+1]<<8
def si(v): return v-65536 if v&0x8000 else v
def expected(n,d):
    ns,ds=si(n),si(d)
    if ds==0:return 0,0,1
    q=abs(ns)//abs(ds)
    if (ns<0)^(ds<0):q=-q
    r=ns-q*ds
    return q&0xffff,r&0xffff,0
def edges():
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,0x7ffe,0x7fff,0x8000,0x8001,0xfffd,0xfffe,0xffff]))
def canonical():
    e=edges(); p=[(n,d) for n in e for d in e]
    rng=random.Random(0xD1001210)
    p += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(50000)]
    p += [(rng.randrange(65536),0) for _ in range(512)]
    return p
def pp():
    e=[v for v in edges() if not v&0x8000]
    p=[(n,d) for n in e for d in e]
    rng=random.Random(0xD16F001)
    p += [(rng.randrange(0x8000),rng.randrange(1,0x8000)) for _ in range(50000)]
    return p
def bench(cpu,entry,cases):
    total=0; lo=None; hi=None; errs=0; cyc=[]; buckets={"q0":[0,0],"q1":[0,0],"qge2":[0,0]}
    for n,d in cases:
        wr(cpu.mem,N,n);wr(cpu.mem,D,d)
        bn=bytes(cpu.mem[N:N+2]);bd=bytes(cpu.mem[D:D+2])
        c=cpu.call(entry,4_000_000)
        eq,er,ec=expected(n,d); gq=rd(cpu.mem,Q); gr=rd(cpu.mem,R)
        if (gq,gr,cpu.c)!=(eq,er,ec) or bytes(cpu.mem[N:N+2])!=bn or bytes(cpu.mem[D:D+2])!=bd:
            errs+=1
            if errs<=6: print("ERROR",hex(n),hex(d),hex(gq),hex(gr),cpu.c,hex(eq),hex(er),ec)
        if ec or si(n)==0 or abs(si(n))<abs(si(d)): k="q0"
        elif abs(eq if eq<0x8000 else eq-0x10000)==1: k="q1"
        else:k="qge2"
        buckets[k][0]+=c;buckets[k][1]+=1
        total+=c;cyc.append(c);lo=c if lo is None else min(lo,c);hi=c if hi is None else max(hi,c)
    return {"cases":len(cases),"errors":errs,"mean_cycles":total/len(cases),"min_cycles":lo,"max_cycles":hi,
            "bucket_means":{k:(v[0]/v[1] if v[1] else None) for k,v in buckets.items()},
            "bucket_counts":{k:v[1] for k,v in buckets.items()},"cycles":cyc}
def compare(base,cand,cases):
    b=bench(base[0],base[1]["MATH_SDIV16"],cases);c=bench(cand[0],cand[1]["MATH_SDIV16"],cases)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles");c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}
def main():
    tmp=Path(tempfile.mkdtemp(prefix="sdiv16-pp-"))
    try:
        build(PROFILE,ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc",tmp)
        def pair():return (
            load(ROOT/PROFILE/"resident"/f"math_{PROFILE}_game_math.prg",ROOT/PROFILE/"resident"/"math_api.inc"),
            load(tmp/f"math_{PROFILE}_source_built.prg",tmp/"math_api.inc"))
        base,cand=pair();out={"canonical":compare(base,cand,canonical())}
        base,cand=pair();out["pp_focus"]=compare(base,cand,pp())
        out["status"]="PASS" if not out["canonical"]["candidate"]["errors"] and not out["pp_focus"]["candidate"]["errors"] else "FAIL"
        print(json.dumps(out,indent=2))
        if out["status"]!="PASS" or out["canonical"]["delta_mean_cycles"]>=0: raise SystemExit(1)
    finally:shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__":main()
