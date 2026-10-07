#!/usr/bin/env python3
from pathlib import Path
import random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

P="v2_pareto_fast"; N=0xc010; D=0xc014; Q=0xc018; R=0xc01c
def mask(b): return (1<<b)-1
def sgn(v,b): return v-(1<<b) if v&(1<<(b-1)) else v
def wr(m,a,v,n):
    for i in range(n): m[a+i]=(v>>(8*i))&255
def rd(m,a,n): return sum(m[a+i]<<(8*i) for i in range(n))
def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try: out[k]=int(v[1:],16)
            except: pass
    return out
def load(prg,inc):
    b=prg.read_bytes(); a=b[0]|b[1]<<8
    mem=bytearray(65536); mem[a:a+len(b)-2]=b[2:]
    c=CPU(mem); c.d=0; api=parse_api(inc); c.call(api["MATH_INIT"],2_000_000)
    return c,api
def exp(nr,nb,dr,db,qb,rb,sh=0):
    n=sgn(nr,nb)<<sh; d=sgn(dr,db)
    if d==0:return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)^(d<0):q=-q
    r=n-q*d
    return q&mask(qb),r&mask(rb),0
def edge(bits):
    s=1<<(bits-1); m=mask(bits)
    return list(dict.fromkeys(x&m for x in [0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def run(cpu,entry,name,cases,nb,db,qb,rb,sh=0):
    nn=(nb+7)//8; dn=(db+7)//8; qn=(qb+7)//8; rn=(rb+7)//8
    for ci,(nr,dr) in enumerate(cases):
        wr(cpu.mem,N,nr,nn); wr(cpu.mem,D,dr,dn)
        bn=bytes(cpu.mem[N:N+nn]); bd=bytes(cpu.mem[D:D+dn])
        try:
            cpu.call(entry,4_000_000)
        except RuntimeError as e:
            print("STEP_LIMIT",name,"case",ci,hex(nr),hex(dr),str(e))
            raise
        eq,er,ec=exp(nr,nb,dr,db,qb,rb,sh)
        gq=rd(cpu.mem,Q,qn); gr=rd(cpu.mem,R,rn)
        if (gq,gr,cpu.c)!=(eq,er,ec) or bytes(cpu.mem[N:N+nn])!=bn or bytes(cpu.mem[D:D+dn])!=bd:
            print("BAD",name,"case",ci,hex(nr),hex(dr),"got",hex(gq),hex(gr),cpu.c,"exp",hex(eq),hex(er),ec)
            raise SystemExit(2)
    print(name,"PASS",len(cases))
def main():
    tmp=Path(tempfile.mkdtemp(prefix="diag-div-"))
    try:
        build(P,ROOT/"relocatable_source"/P/"math_config_reference.inc",tmp)
        # Production promotion is surgical: preserve the known-good resident
        # image and overlay only the SDIV16 signed front-end $7A00-$7C2A.
        base_path=ROOT/P/"resident"/f"math_{P}_game_math.prg"
        cand_path=tmp/f"math_{P}_source_built.prg"
        bb=bytearray(base_path.read_bytes()); cb=cand_path.read_bytes()
        blo=bb[0]|bb[1]<<8; clo=cb[0]|cb[1]<<8
        assert blo==clo
        for addr in range(0x7A00,0x7C2B):
            bb[2+addr-blo]=cb[2+addr-clo]
        patched=tmp/f"math_{P}_patched_resident.prg"
        patched.write_bytes(bb)
        cpu,api=load(patched,tmp/"math_api.inc")
        pi=1
        defs=[('MATH_SDIV8',8,8,8,8,0),('MATH_SDIV16',16,16,16,16,0),
              ('MATH_SDIV24',24,24,24,24,0),('MATH_SDIV32_16',32,16,32,16,0),
              ('MATH_SDIV32_32',32,32,32,32,0),('MATH_SDIV16_SHL8',16,16,24,16,8)]
        aliases=[('MATH_SMOD8',8,8,8,8,0),('MATH_SMOD16',16,16,16,16,0),
                 ('MATH_SMOD24',24,24,24,24,0),('MATH_SMOD32_16',32,16,32,16,0),
                 ('MATH_SMOD32_32',32,32,32,32,0)]
        for name,nb,db,qb,rb,sh in defs:
            if name=='MATH_SDIV8':
                cases=[(n,d) for n in range(256) for d in range(256)]
            else:
                en=edge(nb); ed=edge(db); cases=[(n,d) for n in en for d in ed]
                rng=random.Random(0xD1000000+pi*0x10000+nb*0x100+db+sh)
                count=6144 if name=='MATH_SDIV32_32' else 4096
                cases += [(rng.randrange(1<<nb),rng.randrange(1<<db)) for _ in range(count)]
                cases += [(rng.randrange(1<<nb),0) for _ in range(128)]
            run(cpu,api[name],name,cases,nb,db,qb,rb,sh)
        for ai,(name,nb,db,qb,rb,sh) in enumerate(aliases):
            rng=random.Random(0xA1100000+pi*0x1000+ai)
            cases=[(n,d) for n in edge(nb) for d in edge(db)]
            cases += [(rng.randrange(1<<nb),rng.randrange(1<<db)) for _ in range(1024)]
            run(cpu,api[name],name,cases,nb,db,qb,rb,sh)
        print("V2 SOURCE CANDIDATE ALL SIGNED DIVISION PASS")
    finally:
        shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__": main()
