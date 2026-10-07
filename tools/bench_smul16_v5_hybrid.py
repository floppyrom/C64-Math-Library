#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
import build_hybrid

IO=0xC000; MASK32=(1<<32)-1
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
    m=bytearray(65536); m[a:a+len(b)-2]=b[2:]
    c=CPU(m); c.d=0; api=parse_api(inc); c.call(api["MATH_INIT"],2_000_000)
    return c,api
def wr(m,a,v,n=2):
    for i in range(n):m[a+i]=(v>>(8*i))&255
def rd(m,a,n):return sum(m[a+i]<<(8*i) for i in range(n))
def si(v):return v-65536 if v&0x8000 else v
def corpus():
    e=[0,1,2,3,7,15,16,31,63,127,128,255,0x7ffe,0x7fff,0x8000,0x8001,0xfffd,0xfffe,0xffff]
    p=[(x,y) for x in e for y in e]
    r=random.Random(0x516105)
    p += [(r.randrange(65536),r.randrange(65536)) for _ in range(30000)]
    return p
def bench(cpu,entry,pairs,shr=False):
    cyc=[]; errors=0
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y);before=bytes(cpu.mem[IO:IO+8])
        cc=cpu.call(entry,2_000_000); prod=(si(x)*si(y))&MASK32
        if shr: got=rd(cpu.mem,IO+8,3); exp=(prod>>8)&0xffffff
        else: got=rd(cpu.mem,IO+8,4); exp=prod
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+8])!=before:
            errors+=1
            if errors<6:print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        cyc.append(cc)
    return {"cases":len(pairs),"errors":errors,"mean_cycles":sum(cyc)/len(cyc),
            "min_cycles":min(cyc),"max_cycles":max(cyc),"cycles":cyc}
def compare(base,cand,name,pairs,shr=False):
    a=bench(base[0],base[1][name],pairs,shr); b=bench(cand[0],cand[1][name],pairs,shr)
    ds=[y-x for x,y in zip(a["cycles"],b["cycles"])]
    a.pop("cycles");b.pop("cycles")
    return {"baseline":a,"candidate":b,"delta_mean_cycles":sum(ds)/len(ds),
            "delta_min":min(ds),"delta_max":max(ds),
            "delta_distribution":{str(d):ds.count(d) for d in sorted(set(ds))}}
def main():
    td=Path(tempfile.mkdtemp(prefix="v5-smul16-cp-"))
    try:
        cfg=ROOT/"relocatable_source/v5_hybrid_lowzp/math_config_reference.inc"
        out=td/"reference"/"v5_hybrid_lowzp"
        build_hybrid.build(cfg,out)
        base=load(ROOT/"v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg",
                  ROOT/"v5_hybrid_lowzp/resident/math_api.inc")
        cand=load(out/"math_v5_hybrid_lowzp_game_math.prg",out/"math_api.inc")
        pairs=corpus()
        full=compare(base,cand,"MATH_SMUL16",pairs)
        base=load(ROOT/"v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg",
                  ROOT/"v5_hybrid_lowzp/resident/math_api.inc")
        cand=load(out/"math_v5_hybrid_lowzp_game_math.prg",out/"math_api.inc")
        shr=compare(base,cand,"MATH_SMUL16_SHR8",pairs,True)
        result={"status":"PASS" if full["candidate"]["errors"]==shr["candidate"]["errors"]==0 else "FAIL",
                "smul16":full,"shr8":shr}
        print(json.dumps(result,indent=2))
        if result["status"]!="PASS" or full["delta_mean_cycles"]>=0:raise SystemExit(1)
    finally:shutil.rmtree(td,ignore_errors=True)
if __name__=="__main__":main()
