#!/usr/bin/env python3
"""Research gate for the V2-V4 SMUL32 mixed-sign bounded-carry candidate."""
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILES=["v2_pareto_fast","v3_reu_512k","v4_reu_16m"]
BASE_REU={
 "v3_reu_512k":ROOT/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
 "v4_reu_16m":ROOT/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}
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

def load_prg(prg,api_path,reu_path=None):
    b=prg.read_bytes(); load=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[load:load+len(b)-2]=b[2:]
    reu=bytearray(reu_path.read_bytes()) if reu_path else None
    cpu=CPU(mem,reu=reu); cpu.d=0
    api=parse_api(api_path)
    cpu.call(api["MATH_INIT"],2_000_000)
    return cpu,api

def bench(cpu,entry,pairs):
    io=0xC000; total=0; lo=None; hi=None; errors=0; vector=[]
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
        total+=cy; vector.append(cy)
        lo=cy if lo is None else min(lo,cy); hi=cy if hi is None else max(hi,cy)
    return {"cases":len(pairs),"errors":errors,"mean_cycles":total/len(pairs),"min_cycles":lo,"max_cycles":hi},vector

def corpus(seed,count=2048):
    edges=edge_values(32)
    pairs=[(x,y) for x in edges for y in edges]
    rng=random.Random(seed)
    pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(count)]
    return pairs

def main():
    tmp=Path(tempfile.mkdtemp(prefix="smul32-bounded-"))
    out={"profiles":{},"shared":{}}
    try:
        shared_pairs=corpus(0x5A170020,19963)  # 361 edges + 19,963 random = 20,324.
        shared_vectors={}
        for pi,profile in enumerate(PROFILES,1):
            profile_out=tmp/profile
            build(profile,ROOT/"relocatable_source"/profile/"math_config_reference.inc",profile_out)
            cand_reu=(profile_out/f"c64_math_{profile}_source_built.reu") if profile in BASE_REU else None
            base_cpu,base_api=load_prg(
                ROOT/profile/"resident"/f"math_{profile}_game_math.prg",
                ROOT/profile/"resident"/"math_api.inc",
                BASE_REU.get(profile))
            cand_cpu,cand_api=load_prg(
                profile_out/f"math_{profile}_source_built.prg",
                profile_out/"math_api.inc",
                cand_reu)
            pairs=corpus(0x5A17_0000+pi*0x100+32)
            baseline,_=bench(base_cpu,base_api["MATH_SMUL32"],pairs)
            candidate,_=bench(cand_cpu,cand_api["MATH_SMUL32"],pairs)

            # Fresh CPUs for the larger shared-corpus run, so no call-history
            # state can influence comparison.
            base_cpu,base_api=load_prg(
                ROOT/profile/"resident"/f"math_{profile}_game_math.prg",
                ROOT/profile/"resident"/"math_api.inc",
                BASE_REU.get(profile))
            cand_cpu,cand_api=load_prg(
                profile_out/f"math_{profile}_source_built.prg",
                profile_out/"math_api.inc",
                cand_reu)
            base_shared,_=bench(base_cpu,base_api["MATH_SMUL32"],shared_pairs)
            cand_shared,vec=bench(cand_cpu,cand_api["MATH_SMUL32"],shared_pairs)
            shared_vectors[profile]=vec
            out["profiles"][profile]={
                "canonical_baseline":baseline,
                "canonical_candidate":candidate,
                "canonical_delta":candidate["mean_cycles"]-baseline["mean_cycles"],
                "shared_baseline":base_shared,
                "shared_candidate":cand_shared,
                "shared_delta":cand_shared["mean_cycles"]-base_shared["mean_cycles"],
            }
            if candidate["errors"] or cand_shared["errors"]:
                raise SystemExit(f"{profile}: correctness failure")
            if candidate["mean_cycles"]>=baseline["mean_cycles"]:
                raise SystemExit(f"{profile}: canonical candidate is not faster")
            if cand_shared["mean_cycles"]>=base_shared["mean_cycles"]:
                raise SystemExit(f"{profile}: shared-corpus candidate is not faster")

        v2=shared_vectors[PROFILES[0]]
        out["shared"]["candidate_cycle_vectors_identical"]={
            p:sum(a==b for a,b in zip(v2,shared_vectors[p]))
            for p in PROFILES[1:]
        }
        print(json.dumps(out,indent=2))
        for p,n in out["shared"]["candidate_cycle_vectors_identical"].items():
            if n!=len(shared_pairs):
                raise SystemExit(f"{p}: candidate cycle vector differs from V2")
        print("SMUL32 MIXED-SIGN BOUNDED CANDIDATE PASS")
    finally:
        shutil.rmtree(tmp,ignore_errors=True)

if __name__=="__main__":
    main()
