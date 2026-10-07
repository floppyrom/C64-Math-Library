#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU, Assembler
from assemble_sources import build, preprocess

PROFILES=["v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
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
    if ds==0: return 0,0,1
    q=abs(ns)//abs(ds)
    if (ns<0)^(ds<0): q=-q
    r=ns-q*ds
    return q&0xffff,r&0xffff,0

def edges():
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,
      0x7ffe,0x7fff,0x8000,0x8001,0xfffd,0xfffe,0xffff]))

def canonical(pi):
    e=edges(); p=[(n,d) for n in e for d in e]
    rng=random.Random(0xD1000000+pi*0x10000+16*0x100+16)
    p += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(4096)]
    p += [(rng.randrange(65536),0) for _ in range(128)]
    return p

def pp_focus(pi):
    e=[v for v in edges() if not v&0x8000]
    p=[(n,d) for n in e for d in e]
    rng=random.Random(0xD16F100+pi)
    p += [(rng.randrange(0x8000),rng.randrange(1,0x8000)) for _ in range(20000)]
    return p

def bench(cpu,entry,cases):
    total=0; lo=None; hi=None; errs=0; cyc=[]
    for n,d in cases:
        wr(cpu.mem,N,n); wr(cpu.mem,D,d)
        bn=bytes(cpu.mem[N:N+2]); bd=bytes(cpu.mem[D:D+2])
        c=cpu.call(entry,4_000_000)
        eq,er,ec=expected(n,d); gq=rd(cpu.mem,Q); gr=rd(cpu.mem,R)
        if (gq,gr,cpu.c)!=(eq,er,ec) or bytes(cpu.mem[N:N+2])!=bn or bytes(cpu.mem[D:D+2])!=bd:
            errs+=1
            if errs<=6: print("ERROR",hex(n),hex(d),hex(gq),hex(gr),cpu.c,hex(eq),hex(er),ec)
        total+=c; cyc.append(c); lo=c if lo is None else min(lo,c); hi=c if hi is None else max(hi,c)
    return {"cases":len(cases),"errors":errs,"mean_cycles":total/len(cases),"min_cycles":lo,"max_cycles":hi,"cycles":cyc}

def compare(base,cand,cases):
    b=bench(base[0],base[1]["MATH_SDIV16"],cases)
    c=bench(cand[0],cand[1]["MATH_SDIV16"],cases)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles"); c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),
            "delta_min":min(ds),"delta_max":max(ds)}

def layout(profile):
    src=ROOT/"relocatable_source"/profile/"math_relocatable.asm"
    cfg=ROOT/"relocatable_source"/profile/"math_config_reference.inc"
    mem,labels,const=Assembler().assemble(preprocess(src,cfg))
    a=labels["D16F_sg_code_end"]; b=labels["D16F_cg_code_start"]
    return {"signed_end":a,"unsigned_start":b,"gap":b-a}

def main():
    result={}
    for pi,p in enumerate(PROFILES):
        lay=layout(p)
        if lay["gap"]!=0: raise AssertionError((p,lay))
        tmp=Path(tempfile.mkdtemp(prefix="sdiv16-late-"+p+"-"))
        try:
            build(p,ROOT/"relocatable_source"/p/"math_config_reference.inc",tmp)
            def pair():
                return (
                  load(ROOT/p/"resident"/f"math_{p}_game_math.prg",ROOT/p/"resident"/"math_api.inc"),
                  load(tmp/f"math_{p}_source_built.prg",tmp/"math_api.inc")
                )
            base,cand=pair(); can=compare(base,cand,canonical(pi))
            base,cand=pair(); pp=compare(base,cand,pp_focus(pi))
            if can["candidate"]["errors"] or pp["candidate"]["errors"]: raise AssertionError((p,can,pp))
            if can["delta_mean_cycles"]>=0: raise AssertionError(("no canonical win",p,can))
            result[p]={"layout":lay,"canonical":can,"pp_focus":pp}
        finally:
            shutil.rmtree(tmp,ignore_errors=True)
    print(json.dumps({"status":"PASS","profiles":result},indent=2))
    print("SDIV16 LATE COPY CROSS-PROFILE PASS")

if __name__=="__main__": main()
