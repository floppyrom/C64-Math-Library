#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build
import build_hybrid

FIXED=["v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
IO=0xC000; MASK64=(1<<64)-1
def parse_api(path):
    d={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try:d[k]=int(v[1:],16)
            except:pass
    return d
def load(prg,inc):
    b=prg.read_bytes(); a=b[0]|b[1]<<8
    m=bytearray(65536);m[a:a+len(b)-2]=b[2:]
    c=CPU(m);c.d=0;aa=parse_api(inc);c.call(aa["MATH_INIT"],2_000_000)
    return c,aa
def wr(m,a,v,n=4):
    for i in range(n):m[a+i]=(v>>(8*i))&255
def rd(m,a,n):return sum(m[a+i]<<(8*i) for i in range(n))
def si(v):return v-(1<<32) if v&0x80000000 else v
def corpus(seed):
    e=[0,1,2,3,7,15,16,31,63,127,128,255,0x7ffffffe,0x7fffffff,0x80000000,0x80000001,0xfffffffd,0xfffffffe,0xffffffff]
    p=[(x,y) for x in e for y in e]
    r=random.Random(seed);p += [(r.randrange(1<<32),r.randrange(1<<32)) for _ in range(30000)]
    return p
def bench(cpu,entry,pairs,shr=False):
    cyc=[];err=0; q={"pp":[0,0],"pn":[0,0],"np":[0,0],"nn":[0,0]}
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y);before=bytes(cpu.mem[IO:IO+8])
        cc=cpu.call(entry,3_000_000); prod=(si(x)*si(y))&MASK64
        if shr: got=rd(cpu.mem,IO+8,6);exp=(prod>>16)&((1<<48)-1)
        else: got=rd(cpu.mem,IO+8,8);exp=prod
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+8])!=before:
            err+=1
            if err<5:print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        k=("n" if x&0x80000000 else "p")+("n" if y&0x80000000 else "p")
        q[k][0]+=cc;q[k][1]+=1;cyc.append(cc)
    return {"cases":len(pairs),"errors":err,"mean_cycles":sum(cyc)/len(cyc),
            "min_cycles":min(cyc),"max_cycles":max(cyc),
            "quadrant_means":{k:v[0]/v[1] for k,v in q.items()},"cycles":cyc}
def comp(b,c,name,pairs,shr=False):
    x=bench(b[0],b[1][name],pairs,shr);y=bench(c[0],c[1][name],pairs,shr)
    ds=[bb-aa for aa,bb in zip(x["cycles"],y["cycles"])]
    x.pop("cycles");y.pop("cycles")
    return {"baseline":x,"candidate":y,"delta_mean_cycles":sum(ds)/len(ds),
            "delta_min":min(ds),"delta_max":max(ds),
            "delta_distribution":{str(d):ds.count(d) for d in sorted(set(ds))}}
def fixed_candidate(p,tmp):
    build(p,ROOT/"relocatable_source"/p/"math_config_reference.inc",tmp)
    return load(tmp/f"math_{p}_source_built.prg",tmp/"math_api.inc")
def main():
    result={}
    for pi,p in enumerate(FIXED):
        td=Path(tempfile.mkdtemp(prefix="s32cr-"+p+"-"))
        try:
            base=load(ROOT/p/"resident"/f"math_{p}_game_math.prg",ROOT/p/"resident"/"math_api.inc")
            cand=fixed_candidate(p,td); pairs=corpus(0x532000+pi)
            full=comp(base,cand,"MATH_SMUL32",pairs)
            base=load(ROOT/p/"resident"/f"math_{p}_game_math.prg",ROOT/p/"resident"/"math_api.inc")
            cand=fixed_candidate(p,td); shr=comp(base,cand,"MATH_SMUL32_SHR16",pairs,True)
            if full["candidate"]["errors"] or shr["candidate"]["errors"]:raise SystemExit((p,"error"))
            result[p]={"smul32":full,"shr16":shr}
        finally:shutil.rmtree(td,ignore_errors=True)
    # V5 is rebuilt from the modified V1 source, so validate the inherited path too.
    td=Path(tempfile.mkdtemp(prefix="s32cr-v5-"))
    try:
        out=td/"reference"/"v5_hybrid_lowzp"
        build_hybrid.build(ROOT/"relocatable_source/v5_hybrid_lowzp/math_config_reference.inc",out)
        pairs=corpus(0x532005)
        base=load(ROOT/"v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg",ROOT/"v5_hybrid_lowzp/resident/math_api.inc")
        cand=load(out/"math_v5_hybrid_lowzp_game_math.prg",out/"math_api.inc")
        full=comp(base,cand,"MATH_SMUL32",pairs)
        base=load(ROOT/"v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg",ROOT/"v5_hybrid_lowzp/resident/math_api.inc")
        cand=load(out/"math_v5_hybrid_lowzp_game_math.prg",out/"math_api.inc")
        shr=comp(base,cand,"MATH_SMUL32_SHR16",pairs,True)
        if full["candidate"]["errors"] or shr["candidate"]["errors"]:raise SystemExit(("v5","error"))
        result["v5_hybrid_lowzp"]={"smul32":full,"shr16":shr}
    finally:shutil.rmtree(td,ignore_errors=True)
    print(json.dumps({"status":"PASS","profiles":result},indent=2))
if __name__=="__main__":main()
