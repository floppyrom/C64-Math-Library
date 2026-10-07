#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
IO=0xC000; MASK32=(1<<32)-1
RES_REU={
 "v3_reu_512k":ROOT/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
 "v4_reu_16m":ROOT/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}

def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try: out[k]=int(v[1:],16)
            except ValueError: pass
    return out
def load(prg,inc,reu=None):
    b=Path(prg).read_bytes(); a=b[0]|b[1]<<8
    mem=bytearray(65536); mem[a:a+len(b)-2]=b[2:]
    rb=bytearray(Path(reu).read_bytes()) if reu else None
    c=CPU(mem,reu=rb); c.d=0; api=parse_api(Path(inc)); c.call(api["MATH_INIT"],2_000_000)
    return c,api
def wr(m,a,v,n=2):
    for i in range(n): m[a+i]=(v>>(8*i))&255
def rd(m,a,n): return sum(m[a+i]<<(8*i) for i in range(n))
def si(v): return v-(1<<16) if v&0x8000 else v
def edges():
    s=1<<15; m=(1<<16)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def canonical(pi):
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+pi*0x100+16)
    pairs += [(rng.randrange(1<<16),rng.randrange(1<<16)) for _ in range(4096)]
    return pairs
def xneg():
    e=edges(); xs=[x for x in e if x&0x8000]; ys=e
    pairs=[(x,y) for x in xs for y in ys]
    rng=random.Random(0x516200)
    pairs += [(rng.randrange(0x8000,1<<16),rng.randrange(1<<16)) for _ in range(10000)]
    return pairs
def bench(cpu,entry,pairs,shr=False):
    total=0; lo=None; hi=None; errs=0; cyc=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x); wr(cpu.mem,IO+4,y)
        bx=bytes(cpu.mem[IO:IO+2]); by=bytes(cpu.mem[IO+4:IO+6])
        cc=cpu.call(entry,2_000_000)
        prod=(si(x)*si(y))&MASK32
        exp=((prod>>8)&0xFFFFFF) if shr else prod
        got=rd(cpu.mem,IO+8,3 if shr else 4)
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+2])!=bx or bytes(cpu.mem[IO+4:IO+6])!=by:
            errs+=1
            if errs<=5: print("ERROR",hex(x),hex(y),hex(got),hex(exp),cpu.c)
        total+=cc; cyc.append(cc); lo=cc if lo is None else min(lo,cc); hi=cc if hi is None else max(hi,cc)
    return {"cases":len(pairs),"errors":errs,"mean_cycles":total/len(pairs),"min_cycles":lo,"max_cycles":hi,"cycles":cyc}
def comp(base,cand,name,pairs,shr=False):
    b=bench(base[0],base[1][name],pairs,shr); c=bench(cand[0],cand[1][name],pairs,shr)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles"); c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}
def main():
    allr={}
    for pi,p in enumerate(PROFILES):
        tmp=Path(tempfile.mkdtemp(prefix="smul16-cross-"+p+"-"))
        try:
            info=build(p,ROOT/"relocatable_source"/p/"math_config_reference.inc",tmp)
            cprg=tmp/info["output_prg"]; capi=tmp/"math_api.inc"
            creu=(tmp/info["output_reu"]) if info.get("output_reu") else None
            rprg=ROOT/p/"resident"/f"math_{p}_game_math.prg"; rapi=ROOT/p/"resident"/"math_api.inc"; rreu=RES_REU.get(p)
            def pair(): return load(rprg,rapi,rreu),load(cprg,capi,creu)
            base,cand=pair(); r={"canonical":comp(base,cand,"MATH_SMUL16",canonical(pi))}
            base,cand=pair(); r["xneg_focus"]=comp(base,cand,"MATH_SMUL16",xneg())
            base,cand=pair(); r["shr8"]=comp(base,cand,"MATH_SMUL16_SHR8",canonical(pi),True)
            r["status"]="PASS" if all(v["candidate"]["errors"]==0 for v in r.values() if isinstance(v,dict) and "candidate" in v) else "FAIL"
            if r["status"]!="PASS" or r["canonical"]["delta_mean_cycles"]>=0: raise SystemExit((p,r))
            allr[p]=r
        finally:
            shutil.rmtree(tmp,ignore_errors=True)
    print(json.dumps({"status":"PASS","profiles":allr},indent=2))
if __name__=="__main__": main()
