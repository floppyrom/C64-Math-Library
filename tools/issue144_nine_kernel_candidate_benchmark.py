#!/usr/bin/env python3
"""Issue144 P4: nine expensive public APIs, same-input source candidate vs frozen PRG.

This reproducible benchmark creates current-source PRGs in temporary storage,
never edits historical binaries or PERFORMANCE.md, and measures 6502 instruction
cycles through the public RTS (not VIC/REU physical wall-clock time). All pairs
are checked against independent integer arithmetic or SEEK16 movement traces.
The candidate is a source release candidate; do not present it as shipped.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,random,statistics,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"routines/movement"))
from issue144_isqrt32_release_candidate import (PROFILES,FROZEN,REUS,radicands,
                                                 frozen_seals,digest,machine)
from assemble_sources import build as build_source
from build_hybrid import build as build_hybrid
from validate_source_build import unhx
from validate_signed_division import div_expected
from validate_unsigned_division import expected as uexpected
from benchmark_multiply_refresh import wr,rd,si
from seek_model import expected_frames

OPS=("MATH_ISQRT32","MATH_SEEK16_INIT","MATH_SMUL32_SHR16",
     "MATH_UMUL32_SHR16","MATH_SMUL32","MATH_UMUL32",
     "MATH_SMOD32_16","MATH_UMOD32_16","MATH_UDIV32_16")
MASK64=(1<<64)-1
SIGNED={"MATH_SMUL32_SHR16","MATH_SMUL32","MATH_SMOD32_16"}
MUL={"MATH_SMUL32_SHR16","MATH_UMUL32_SHR16","MATH_SMUL32","MATH_UMUL32"}
DIV={"MATH_SMOD32_16","MATH_UMOD32_16","MATH_UDIV32_16"}
SPEEDS=(0x80,0x100,0x180,0x200,0x8100,0x8180)

def corpus(limit):
    rng=random.Random(0x14420261016)
    edge32=(0,1,2,3,7,15,127,128,255,256,65535,65536,65537,
            0x7fffffff,0x80000000,0x80000001,0xffffffff)
    edge16=(0,1,2,3,127,255,256,257,0x7fff,0x8000,0xffff)
    pairs=list(dict.fromkeys((x,y) for x in edge32 for y in edge32))
    pairs.extend((rng.getrandbits(32),rng.getrandbits(32)) for _ in range(limit))
    # Divisor zero, high divisor, low divisor and byte divisor are represented.
    division=list(dict.fromkeys((n,d) for n in edge32 for d in edge16))
    division.extend((rng.getrandbits(32),rng.getrandbits(16)) for _ in range(limit))
    division.extend((rng.getrandbits(32),0) for _ in range(20))
    seek=[(0,0,319,199,0x100),(319,199,0,0,0x8100),
          (0,0,0,0,0x100),(160,100,1,100,0x80),
          (10,20,300,190,0x180)]
    seek += [(rng.randrange(320),rng.randrange(200),rng.randrange(320),
              rng.randrange(200),SPEEDS[i%len(SPEEDS)])
             for i in range(limit//2)]
    return pairs,division,seek

def init_machine(profile,prg,reu,entries):
    from mini6502 import CPU
    b=Path(prg).read_bytes()
    load=int.from_bytes(b[:2],"little")
    mem=bytearray(65536)
    mem[load:load+len(b)-2]=b[2:]
    c=CPU(mem,reu=bytearray(Path(reu).read_bytes()) if reu else None)
    c.d=0
    api={name:unhx(value) for name,value in entries.items()}
    # Alternate source layouts relocate MATH_INIT away from the historical
    # $3280. Never call a hardcoded reference-map init on a relocated PRG.
    assert "MATH_INIT" in api
    c.call(api["MATH_INIT"],2_000_000)
    assert c.c==0,(profile,"MATH_INIT",hex(api["MATH_INIT"]))
    return c,api

def api_frozen(profile):
    import re
    out={}
    for line in (ROOT/profile/"resident/math_api.inc").read_text().splitlines():
        m=re.match(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)",line)
        if m:out[m.group(1)]=int(m.group(2),16)
    return out

def sample(c,api,op,item,io):
    N=io+0x10;D=io+0x14;Q=io+0x18;R=io+0x1c
    X=io;Y=io+4;Z=io+8
    if op=="MATH_ISQRT32":
        n=item;wr(c.mem,N,n,4);before=bytes(c.mem[N:N+4])
        cy=c.call(api[op],4000000)
        assert rd(c.mem,Z,2)==math.isqrt(n)
        assert c.c==0 and bytes(c.mem[N:N+4])==before
        return cy,(rd(c.mem,Z,2),c.c)
    if op in MUL:
        x,y=item;wr(c.mem,X,x,4);wr(c.mem,Y,y,4)
        before=bytes(c.mem[X:X+8])
        cy=c.call(api[op],4000000)
        prod=(si(x,32)*si(y,32)) if op in SIGNED else x*y
        shifted=op.endswith("SHR16")
        val=((prod>>16)&((1<<48)-1)) if shifted else (prod&MASK64)
        n=6 if shifted else 8
        got=rd(c.mem,Z,n)
        assert got==val,(op,hex(x),hex(y),hex(got),hex(val))
        assert c.c==0 and bytes(c.mem[X:X+8])==before
        return cy,(got,c.c)
    if op in DIV:
        n,d=item;wr(c.mem,N,n,4);wr(c.mem,D,d,2)
        before=bytes(c.mem[N:N+4])+bytes(c.mem[D:D+2])
        cy=c.call(api[op],4000000)
        want=(div_expected(n,32,d,16,32,16)
              if op in SIGNED else uexpected(n,d,32,16))
        got=(rd(c.mem,Q,4),rd(c.mem,R,2),c.c)
        assert got==want,(op,hex(n),hex(d),got,want)
        assert bytes(c.mem[N:N+4])+bytes(c.mem[D:D+2])==before
        return cy,got
    assert op=="MATH_SEEK16_INIT"
    x0,y0,x1,y1,sp=item;slot=3
    sx=api["MATH_SEEK16_POS_XL"]+slot
    sh=api["MATH_SEEK16_POS_XH"]+slot
    sy=api["MATH_SEEK16_POS_Y"]+slot
    c.mem[sx]=x0&255;c.mem[sh]=x0>>8;c.mem[sy]=y0
    wr(c.mem,X,x1,2);c.mem[Y]=y1;wr(c.mem,N,sp,2);c.x=slot
    before=bytes(c.mem[X:X+2])+bytes(c.mem[Y:Y+1])+bytes(c.mem[N:N+2])
    cy=c.call(api[op],4000000)
    movement=expected_frames(x0,y0,x1,y1,sp,"step")
    assert c.c==int(not movement) and c.x==slot
    assert bytes(c.mem[X:X+2])+bytes(c.mem[Y:Y+1])+bytes(c.mem[N:N+2])==before
    return cy,((x0,y0,x1,y1,sp),movement,slot)

def trace_seek(c,api,rec):
    move,expected,slot=rec
    sxl=api["MATH_SEEK16_POS_XL"]+slot
    sxh=api["MATH_SEEK16_POS_XH"]+slot
    sy=api["MATH_SEEK16_POS_Y"]+slot
    result=[]
    for xy,arrive in expected[:min(5,len(expected))]:
        c.x=slot
        c.call(api["MATH_SEEK16_STEP"],4000000)
        got=(c.mem[sxl]|c.mem[sxh]<<8,c.mem[sy],c.c,c.x)
        assert got==(xy[0],xy[1],int(arrive),slot),(move,got,xy,arrive)
        result.append(got)
    return result

def summarise(old,new):
    saved=[x-y for x,y in zip(old,new)]
    so,sc=sorted(old),sorted(new)
    z=sorted(saved)
    return {"calls":len(saved),"frozen_mean":statistics.mean(old),
            "source_mean":statistics.mean(new),"mean_saved":statistics.mean(saved),
            "frozen_p95":so[int(.95*(len(so)-1))],
            "source_p95":sc[int(.95*(len(sc)-1))],
            "p05_saved":z[int(.05*(len(z)-1))],
            "worst_saved":z[0],"best_saved":z[-1],
            "slower_calls":sum(x<0 for x in saved)}

def run_profile(p,stage,layout,sets):
    config=ROOT/"relocatable_source"/p/("math_config_"+layout+".inc")
    dest=stage/p
    manifest=(build_hybrid(config,dest) if p=="v5_hybrid_lowzp"
              else build_source(p,config,dest))
    prg=dest/manifest["output_prg"]
    reu=(dest/manifest["reu_image"]["file"] if manifest.get("reu_image") else None)
    assert digest(prg)==manifest["output_sha256"]
    frozen_api=api_frozen(p)
    old,_=init_machine(p,FROZEN[p],REUS.get(p),{k:f"${v:04X}" for k,v in frozen_api.items()})
    candidate,api=init_machine(p,prg,reu,manifest["public_entries"])
    # The 56 stable public *functions* and caller-visible SEEK state arrays
    # are separate API include records; the manifest lists only functions.
    import re
    for line in (dest/"math_api.inc").read_text().splitlines():
        m=re.match(r"\s*(MATH_SEEK16_POS_[A-Z]+)\s*=\s*\$([0-9A-Fa-f]+)",line)
        if m:api[m.group(1)]=int(m.group(2),16)
    assert set(OPS).issubset(api) and len(manifest["public_entries"])==56
    assert all(k in api for k in ("MATH_SEEK16_POS_XL","MATH_SEEK16_POS_XH","MATH_SEEK16_POS_Y"))
    io_new=unhx(manifest["public_io"].split("-")[0]);io_old=0xc000
    result=[]
    for op in OPS:
        inputs=(radicands() if op=="MATH_ISQRT32" else
                sets[2] if op=="MATH_SEEK16_INIT" else
                sets[1] if op in DIV else sets[0])
        oldcycles=[];newcycles=[]
        for item in inputs:
            oldcy,oldout=sample(old,frozen_api,op,item,io_old)
            newcy,newout=sample(candidate,api,op,item,io_new)
            if op=="MATH_SEEK16_INIT":
                assert oldout[0]==newout[0]
                assert trace_seek(old,frozen_api,oldout)==trace_seek(candidate,api,newout)
            else:
                assert oldout==newout,(p,layout,op,item,oldout,newout)
            oldcycles.append(oldcy);newcycles.append(newcy)
        v=summarise(oldcycles,newcycles)
        result.append({"profile":p,"layout":layout,"routine":op,**v,
                       "frozen_prg_sha256":digest(FROZEN[p]),
                       "source_prg_sha256":digest(prg)})
        print("ISSUE144 NINE KERNEL",p,layout,op,"PASS",v["calls"],
              "mean_saved",round(v["mean_saved"],3),flush=True)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--layout",choices=("reference","alternate"),default="reference")
    ap.add_argument("--random",type=int,default=128)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    asserts=frozen_seals()
    sets=corpus(a.random)
    with tempfile.TemporaryDirectory(prefix="issue144_nine_kernel_") as tmp:
        stage=Path(tmp)
        rows=[]
        for p in PROFILES:rows.extend(run_profile(p,stage,a.layout,sets))
    assert frozen_seals()==asserts
    record={"status":"PASS_NINE_KERNEL_MATCHED_CANDIDATE_RESEARCH",
            "layout":a.layout,"source_binary_release_class":"candidate_not_shipped",
            "physical_bus_timing_measured":False,
            "IRQ_NMI_certified":False,"sampled_routines":len(OPS),
            "source_profiles":len(PROFILES),
            "complete_public_correctness_and_seek_followup":True,
            "benchmark_rows":rows}
    assert len(rows)==45
    if a.out:
        a.out.mkdir(parents=True,exist_ok=True)
        columns=("profile","layout","routine","calls","frozen_mean","source_mean",
                 "mean_saved","frozen_p95","source_p95","p05_saved",
                 "worst_saved","best_saved","slower_calls",
                 "frozen_prg_sha256","source_prg_sha256")
        with (a.out/("ISSUE144_NINE_KERNEL_"+a.layout+".csv")).open("w",newline="") as stream:
            w=csv.DictWriter(stream,fieldnames=columns,extrasaction="ignore")
            w.writeheader();w.writerows(rows)
        (a.out/("ISSUE144_NINE_KERNEL_"+a.layout+".json")).write_text(
                json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("NINE KERNELS",a.layout,"PASS",len(rows),"rows",
          "calls",sum(x["calls"] for x in rows),flush=True)
    print(json.dumps({"status":record["status"],
                      "layout":a.layout,
                      "per_profile":{p:{x["routine"]:round(x["mean_saved"],3)
                                        for x in rows if x["profile"]==p}
                                     for p in PROFILES}},indent=2))

if __name__=="__main__":main()
