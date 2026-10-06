#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILE="v2_pareto_fast"
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
def bench(cpu,entry,pairs):
    io=0xC000; total=0; lo=None; hi=None; errors=0; cycles=[]
    for x,y in pairs:
        wr(cpu.mem,io,x); wr(cpu.mem,io+4,y)
        before=bytes(cpu.mem[io:io+8])
        cy=cpu.call(entry,2_000_000)
        got=rd(cpu.mem,io+8)
        exp=(signed32(x)*signed32(y))&MASK64
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[io:io+8])!=before:
            errors+=1
            if errors<=8: print("ERROR",hex(x),hex(y),hex(got),hex(exp),"C",cpu.c)
        total+=cy; cycles.append(cy)
        lo=cy if lo is None else min(lo,cy); hi=cy if hi is None else max(hi,cy)
    return {"cases":len(pairs),"errors":errors,"mean_cycles":total/len(pairs),"min_cycles":lo,"max_cycles":hi,"cycles":cycles}
def edges():
    s=1<<31; m=(1<<32)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def canonical():
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+1*0x100+32)
    pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(2048)]
    return pairs
def q1_focus():
    e=edges(); xs=[x for x in e if not x&0x80000000]; ys=[y for y in e if y&0x80000000]
    pairs=[(x,y) for x in xs for y in ys]
    rng=random.Random(0x5131B0)
    pairs += [(rng.randrange(0,0x80000000),rng.randrange(0x80000000,1<<32)) for _ in range(20000)]
    return pairs
def compare(base,cand,pairs):
    b=bench(base[0],base[1]["MATH_SMUL32"],pairs)
    c=bench(cand[0],cand[1]["MATH_SMUL32"],pairs)
    deltas=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    for r in (b,c): r.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(deltas)/len(deltas),
            "delta_min":min(deltas),"delta_max":max(deltas)}
def main():
    base=load_prg(ROOT/PROFILE/"resident"/f"math_{PROFILE}_game_math.prg",
                  ROOT/PROFILE/"resident"/"math_api.inc")
    out=Path(tempfile.mkdtemp(prefix="smul32-q1-tail-"))
    try:
        build(PROFILE,ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc",out)
        cand=load_prg(out/f"math_{PROFILE}_source_built.prg",out/"math_api.inc")
        # Reload independent CPU pairs for each corpus to keep state identical.
        result={}
        result["canonical"]=compare(base,cand,canonical())
        base2=load_prg(ROOT/PROFILE/"resident"/f"math_{PROFILE}_game_math.prg",
                       ROOT/PROFILE/"resident"/"math_api.inc")
        cand2=load_prg(out/f"math_{PROFILE}_source_built.prg",out/"math_api.inc")
        result["q1_focus"]=compare(base2,cand2,q1_focus())
    finally:
        shutil.rmtree(out,ignore_errors=True)
    result["status"]="PASS"
    print(json.dumps(result,indent=2))
    if result["canonical"]["candidate"]["errors"] or result["q1_focus"]["candidate"]["errors"]:
        raise SystemExit("correctness failure")
    if result["canonical"]["delta_mean_cycles"] >= 0:
        raise SystemExit("no public mean win")
    print("SMUL32 Q1 BOUNDED+TAIL PASS")
if __name__=="__main__": main()
