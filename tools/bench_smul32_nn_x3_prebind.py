#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
PROFILE_INDEX={"v2_pareto_fast":1,"v3_reu_512k":2,"v4_reu_16m":3}
MASK64=(1<<64)-1

def signed32(v): return v-(1<<32) if v&0x80000000 else v
def wr(mem,a,v,n=4):
    for i in range(n): mem[a+i]=(v>>(8*i))&255
def rd(mem,a,n=8):
    return sum(mem[a+i]<<(8*i) for i in range(n))
def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try: out[k]=int(v[1:],16)
            except ValueError: pass
    return out
def load_prg(prg,api_path):
    b=prg.read_bytes(); load=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[load:load+len(b)-2]=b[2:]
    cpu=CPU(mem); cpu.d=0; api=parse_api(api_path)
    cpu.call(api["MATH_INIT"],2_000_000)
    return cpu,api
def bench(pair,pairs):
    cpu,api=pair; entry=api["MATH_SMUL32"]; io=0xC000
    total=0; lo=None; hi=None; errors=0; cycles=[]
    for x,y in pairs:
        wr(cpu.mem,io,x); wr(cpu.mem,io+4,y)
        before=bytes(cpu.mem[io:io+8])
        cy=cpu.call(entry,2_000_000)
        got=rd(cpu.mem,io+8); exp=(signed32(x)*signed32(y))&MASK64
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[io:io+8])!=before:
            errors+=1
            if errors<=8: print("ERROR",hex(x),hex(y),hex(got),hex(exp),"C",cpu.c)
        total+=cy; cycles.append(cy)
        lo=cy if lo is None else min(lo,cy); hi=cy if hi is None else max(hi,cy)
    return {"cases":len(pairs),"errors":errors,"mean_cycles":total/len(pairs),
            "min_cycles":lo,"max_cycles":hi,"cycles":cycles}
def edges():
    s=1<<31; m=(1<<32)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def canonical(pi):
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+pi*0x100+32)
    pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(2048)]
    return pairs
def nn_focus():
    e=edges(); xs=[x for x in e if x&0x80000000]; ys=[y for y in e if y&0x80000000]
    pairs=[(x,y) for x in xs for y in ys]
    rng=random.Random(0x5133B0)
    pairs += [(rng.randrange(0x80000000,1<<32),rng.randrange(0x80000000,1<<32))
              for _ in range(20000)]
    return pairs
def shared(n=6000):
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x51A33B7)
    pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(n)]
    return pairs
def compare(base,cand,pairs):
    b=bench(base,pairs); c=bench(cand,pairs)
    deltas=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    bcy=b.pop("cycles"); ccy=c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(deltas)/len(deltas),
            "delta_min":min(deltas),"delta_max":max(deltas),
            "_baseline_cycles":bcy,"_candidate_cycles":ccy}
def clean(c):
    c=dict(c); c.pop("_baseline_cycles",None); c.pop("_candidate_cycles",None); return c

def main():
    out=Path(tempfile.mkdtemp(prefix="smul32-nn-x3-"))
    result={"canonical":{},"shared":{}}
    try:
        built={}
        for p in PROFILES:
            d=out/p; d.mkdir(parents=True)
            build(p,ROOT/"relocatable_source"/p/"math_config_reference.inc",d)
            built[p]=d
        for p in PROFILES:
            base=load_prg(ROOT/p/"resident"/f"math_{p}_game_math.prg",ROOT/p/"resident"/"math_api.inc")
            cand=load_prg(built[p]/f"math_{p}_source_built.prg",built[p]/"math_api.inc")
            result["canonical"][p]=clean(compare(base,cand,canonical(PROFILE_INDEX[p])))
        p="v2_pareto_fast"
        base=load_prg(ROOT/p/"resident"/f"math_{p}_game_math.prg",ROOT/p/"resident"/"math_api.inc")
        cand=load_prg(built[p]/f"math_{p}_source_built.prg",built[p]/"math_api.inc")
        result["nn_focus"]=clean(compare(base,cand,nn_focus()))
        sp=shared()
        vectors=[]
        for p in PROFILES:
            base=load_prg(ROOT/p/"resident"/f"math_{p}_game_math.prg",ROOT/p/"resident"/"math_api.inc")
            cand=load_prg(built[p]/f"math_{p}_source_built.prg",built[p]/"math_api.inc")
            c=compare(base,cand,sp); vectors.append(c["_candidate_cycles"])
            result["shared"][p]=clean(c)
        result["shared_cycle_vectors_identical"]=all(v==vectors[0] for v in vectors[1:])
    finally:
        shutil.rmtree(out,ignore_errors=True)
    errors=sum(v["candidate"]["errors"] for v in result["canonical"].values())+result["nn_focus"]["candidate"]["errors"]+sum(v["candidate"]["errors"] for v in result["shared"].values())
    wins=[v["delta_mean_cycles"]<0 for v in result["canonical"].values()]
    result["status"]="PASS" if errors==0 and all(wins) and result["shared_cycle_vectors_identical"] else "FAIL"
    print(json.dumps(result,indent=2))
    if result["status"]!="PASS": raise SystemExit("NN X3 multi-profile gate failed")
    print("SMUL32 NN X3 PREBIND MULTI-PROFILE PASS")
if __name__=="__main__": main()
