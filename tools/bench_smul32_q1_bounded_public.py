#!/usr/bin/env python3
"""Research gate for the V2 SMUL32 q1 swapped bounded-carry candidate.

Builds the relocatable V2 source, executes the exact public SMUL32 corpus used by
validate_signed_multiply.py, and compares it with the checked-in resident
baseline on identical inputs. This file is branch-local research scaffolding.
"""
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

MASK=lambda bits:(1<<bits)-1

def signed(v,bits):
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def wr(mem,addr,value,n):
    for i in range(n): mem[addr+i]=(value>>(8*i))&0xff

def rd(mem,addr,n):
    return sum(mem[addr+i]<<(8*i) for i in range(n))

def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        name,val=[x.strip() for x in line.split("=",1)]
        if name.startswith("MATH_") and val.startswith("$"):
            try: out[name]=int(val[1:],16)
            except ValueError: pass
    return out

def edge_values(bits):
    m=MASK(bits); s=1<<(bits-1)
    vals=[0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]
    return list(dict.fromkeys(v&m for v in vals))

def load_prg(prg,api_path):
    b=prg.read_bytes(); load=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[load:load+len(b)-2]=b[2:]
    cpu=CPU(mem); cpu.d=0
    api=parse_api(api_path)
    cpu.call(api["MATH_INIT"],2_000_000)
    return cpu,api

def bench(cpu,entry,pairs):
    io=0xC000; total=0; lo=None; hi=None; errors=0
    for x,y in pairs:
        wr(cpu.mem,io,x,4); wr(cpu.mem,io+4,y,4)
        bx=bytes(cpu.mem[io:io+4]); by=bytes(cpu.mem[io+4:io+8])
        cy=cpu.call(entry,2_000_000)
        got=rd(cpu.mem,io+8,8)
        exp=(signed(x,32)*signed(y,32))&MASK(64)
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[io:io+4])!=bx or bytes(cpu.mem[io+4:io+8])!=by:
            errors+=1
            if errors<=8:
                print("ERROR",hex(x),hex(y),hex(got),hex(exp),"C",cpu.c)
        total+=cy; lo=cy if lo is None else min(lo,cy); hi=cy if hi is None else max(hi,cy)
    return {"cases":len(pairs),"errors":errors,"mean_cycles":total/len(pairs),"min_cycles":lo,"max_cycles":hi}

def main():
    profile="v2_pareto_fast"
    edges=edge_values(32)
    pairs=[(x,y) for x in edges for y in edges]
    rng=random.Random(0x5A17_0000+1*0x100+32)
    pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(2048)]

    baseline_cpu,baseline_api=load_prg(
        ROOT/profile/"resident"/f"math_{profile}_game_math.prg",
        ROOT/profile/"resident"/"math_api.inc")
    baseline=bench(baseline_cpu,baseline_api["MATH_SMUL32"],pairs)

    out=Path(tempfile.mkdtemp(prefix="smul32-q1-bounded-"))
    try:
        man=build(profile,ROOT/"relocatable_source"/profile/"math_config_reference.inc",out)
        cand_cpu,cand_api=load_prg(out/f"math_{profile}_source_built.prg",out/"math_api.inc")
        candidate=bench(cand_cpu,cand_api["MATH_SMUL32"],pairs)
    finally:
        shutil.rmtree(out,ignore_errors=True)

    result={"baseline":baseline,"candidate":candidate,
            "delta_cycles":candidate["mean_cycles"]-baseline["mean_cycles"]}
    print(json.dumps(result,indent=2))
    if candidate["errors"]:
        raise SystemExit("candidate correctness failure")
    if candidate["mean_cycles"] >= baseline["mean_cycles"]:
        raise SystemExit("candidate is not faster on identical public corpus")
    print("SMUL32 Q1 BOUNDED PUBLIC PASS")

if __name__=="__main__":
    main()
