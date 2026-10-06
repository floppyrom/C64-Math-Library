#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import random, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler, CPU, REV
from assemble_sources import preprocess, parse_config

PROFILE="v2_pareto_fast"
SRC=ROOT/"relocatable_source"/PROFILE/"math_relocatable.asm"
CFG=ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc"
MASK64=(1<<64)-1

class TraceCPU(CPU):
    def __post_init__(self):
        super().__post_init__()
        self.hits=Counter()
        self.branches=Counter()
    def step(self):
        pc=self.pc
        self.hits[pc]+=1
        oc=self.rd(pc)
        if oc in REV:
            op,mode=REV[oc]
            if mode=="rel":
                cond={"bpl":not self.n,"bmi":self.n,"bvc":not self.v,"bvs":self.v,"bcc":not self.c,"bcs":self.c,"bne":not self.z,"beq":self.z}[op]
                off=self.rd((pc+1)&0xffff)
                off=off-256 if off&128 else off
                target=(pc+2+off)&0xffff
                self.branches[(pc,op,target,1 if cond else 0)]+=1
        return super().step()

def wr(mem,addr,v,n=4):
    for i in range(n): mem[addr+i]=(v>>(8*i))&255

def rd(mem,addr,n=8):
    return sum(mem[addr+i]<<(8*i) for i in range(n))

def signed32(v):
    return v-(1<<32) if v&0x80000000 else v

def main():
    text=preprocess(SRC,CFG)
    md,labels,const=Assembler().assemble(text)
    mem=bytearray(65536)
    for a,b in md.items(): mem[a]=b
    cfg=parse_config(CFG)
    io=cfg["MATH_IO"]
    init=labels.get("MATH_INIT",const.get("MATH_INIT"))
    entry=labels.get("MATH_SMUL32",const.get("MATH_SMUL32"))
    if init is None or entry is None:
        raise SystemExit(("missing entry",init,entry))
    cpu=TraceCPU(mem); cpu.d=0
    cpu.call(init,2_000_000)
    cpu.hits.clear()

    edge=[0,1,2,3,7,15,16,31,63,127,128,255,
          0x7ffffffe,0x7fffffff,0x80000000,0x80000001,
          0xfffffffd,0xfffffffe,0xffffffff]
    xs=[v for v in edge if v&0x80000000]
    ys=[v for v in edge if not (v&0x80000000)]
    pairs=[(x,y) for x in xs for y in ys]
    rng=random.Random(0x5132B0)
    pairs += [(rng.randrange(0x80000000,1<<32),rng.randrange(0,0x80000000))
              for _ in range(20000)]

    total=0; lo=None; hi=None
    for x,y in pairs:
        wr(cpu.mem,io,x); wr(cpu.mem,io+4,y)
        cy=cpu.call(entry,2_000_000)
        got=rd(cpu.mem,io+8)
        exp=(signed32(x)*signed32(y))&MASK64
        if got!=exp or cpu.c!=0:
            raise SystemExit(f"bad {x:08x} {y:08x}: {got:016x} != {exp:016x} C={cpu.c}")
        total+=cy; lo=cy if lo is None else min(lo,cy); hi=cy if hi is None else max(hi,cy)

    qlabels={name:addr for name,addr in labels.items() if name.startswith("S32V28_q2_")}
    rows=[]
    for name,addr in qlabels.items():
        h=cpu.hits[addr]
        if h:
            rows.append((h/len(pairs),h,name,addr))
    rows.sort(reverse=True)
    print(f"Q2 PROFILE PASS cases={len(pairs)} mean={total/len(pairs):.6f} min={lo} max={hi}")
    print("label_hits_per_call:")
    for per,h,name,addr in rows:
        print(f"{per:10.6f}  {h:9d}  0x{addr:04x}  {name}")

    revlabels={}
    for name,addr in labels.items():
        revlabels.setdefault(addr,[]).append(name)
    qlo=labels["S32V28_q2_summation"]
    qhi=labels["S32V28_q2_cg_code_end"]
    agg={}
    for (pc,op,target,taken),count in cpu.branches.items():
        if qlo <= pc < qhi:
            k=(pc,op,target)
            if k not in agg:
                agg[k]=[0,0]
            agg[k][0]+=count
            if taken:
                agg[k][1]+=count
    print("branch_profile:")
    for (pc,op,target),(ex,tak) in sorted(agg.items()):
        labs="|".join(revlabels.get(target,[]))
        print(f"0x{pc:04x} {op:3s} -> 0x{target:04x} {labs:36s} exec={ex:7d} taken={tak:7d} pct={100*tak/ex:7.3f}")

if __name__=="__main__":
    main()
