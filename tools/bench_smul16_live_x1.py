#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
IO=0xC000; MASK32=(1<<32)-1

def api(path):
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
    c=CPU(m);c.d=0;aa=api(inc);c.call(aa["MATH_INIT"],2_000_000)
    return c,aa
def wr(m,a,v,n=2):
    for i in range(n):m[a+i]=(v>>(8*i))&255
def rd(m,a,n):return sum(m[a+i]<<(8*i) for i in range(n))
def si(v):return v-65536 if v&0x8000 else v
def cases(seed):
    e=[0,1,2,3,7,15,16,31,63,127,128,255,0x7ffe,0x7fff,0x8000,0x8001,0xfffd,0xfffe,0xffff]
    p=[(x,y) for x in e for y in e]
    r=random.Random(seed)
    p += [(r.randrange(65536),r.randrange(65536)) for _ in range(30000)]
    return p
def bench(cpu,entry,pairs,shr=False):
    cyc=[];errs=0
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y)
        before=bytes(cpu.mem[IO:IO+8])
        cc=cpu.call(entry,2_000_000)
        prod=(si(x)*si(y))&MASK32
        if shr:
            got=rd(cpu.mem,IO+8,3);exp=(prod>>8)&0xffffff
        else:
            got=rd(cpu.mem,IO+8,4);exp=prod
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+8])!=before:
            errs+=1
            if errs<6:print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        cyc.append(cc)
    return {"cases":len(pairs),"errors":errs,"mean_cycles":sum(cyc)/len(cyc),
            "min_cycles":min(cyc),"max_cycles":max(cyc),"cycles":cyc}
def cmp(b,c,pairs,name,shr=False):
    x=bench(b[0],b[1][name],pairs,shr);y=bench(c[0],c[1][name],pairs,shr)
    ds=[bb-aa for aa,bb in zip(x["cycles"],y["cycles"])]
    x.pop("cycles");y.pop("cycles")
    return {"baseline":x,"candidate":y,"delta_mean_cycles":sum(ds)/len(ds),
            "delta_min":min(ds),"delta_max":max(ds),
            "delta_distribution":{str(d):ds.count(d) for d in sorted(set(ds))}}
def main():
    out={}
    for pi,p in enumerate(PROFILES):
        tmp=Path(tempfile.mkdtemp(prefix="smul16-live-"+p+"-"))
        try:
            build(p,ROOT/"relocatable_source"/p/"math_config_reference.inc",tmp)
            def pair():
                return (load(ROOT/p/"resident"/f"math_{p}_game_math.prg",ROOT/p/"resident"/"math_api.inc"),
                        load(tmp/f"math_{p}_source_built.prg",tmp/"math_api.inc"))
            pairs=cases(0x516100+pi)
            b,c=pair();full=cmp(b,c,pairs,"MATH_SMUL16")
            b,c=pair();shr=cmp(b,c,pairs,"MATH_SMUL16_SHR8",True)
            if full["candidate"]["errors"] or shr["candidate"]["errors"]:raise SystemExit((p,"errors"))
            out[p]={"smul16":full,"shr8":shr}
        finally:shutil.rmtree(tmp,ignore_errors=True)
    print(json.dumps({"status":"PASS","profiles":out},indent=2))
    if any(v["smul16"]["delta_mean_cycles"]>=0 for v in out.values()):raise SystemExit("no win")
if __name__=="__main__":main()
