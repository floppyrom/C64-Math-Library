#!/usr/bin/env python3
from pathlib import Path
import random,re,sys,json

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU,Assembler,REV
from assemble_sources import preprocess

IO=0xC000
MASK=(1<<64)-1

def parse_api(path):
    out={}
    for line in Path(path).read_text().splitlines():
        m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m: out[m.group(1)]=int(m.group(2),16)
    return out

def load(prg_path,inc_path):
    api=parse_api(inc_path)
    b=Path(prg_path).read_bytes();load=b[0]|b[1]<<8
    mem=bytearray(65536);mem[load:load+len(b)-2]=b[2:]
    cpu=CPU(mem);cpu.d=0
    cpu.call(api['MATH_INIT'],2_000_000)
    return cpu,api

def wr(mem,a,v,n=4):
    for i in range(n): mem[a+i]=(v>>(8*i))&0xff

def rd(mem,a,n=8):
    return sum(mem[a+i]<<(8*i) for i in range(n))

def sv(v):
    return v-(1<<32) if v&(1<<31) else v

def edge_values():
    m=(1<<32)-1;s=1<<31
    vals=[0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]
    return list(dict.fromkeys(x&m for x in vals))

def corpus():
    e=edge_values()
    pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+1*0x100+32)
    pairs += [(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(2048)]
    return pairs

def pp_stress():
    rng=random.Random(0x51A32C0)
    return [(rng.randrange(1<<31),rng.randrange(1<<31)) for _ in range(20000)]

def run(cpu,api,pairs):
    total=0;mn=None;mx=None;errors=0;quad={k:[0,0] for k in ('PP','PN','NP','NN')}
    cycles=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y)
        before=bytes(cpu.mem[IO:IO+8])
        cy=cpu.call(api['MATH_SMUL32'],2_000_000)
        got=rd(cpu.mem,IO+8); exp=(sv(x)*sv(y))&MASK
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+8])!=before:
            errors+=1
            if errors<=5: print('ERROR',hex(x),hex(y),hex(got),hex(exp),'C',cpu.c)
        total+=cy;cycles.append(cy);mn=cy if mn is None else min(mn,cy);mx=cy if mx is None else max(mx,cy)
        q=('N' if x>>31 else 'P')+('N' if y>>31 else 'P')
        quad[q][0]+=cy;quad[q][1]+=1
    return {'cases':len(pairs),'errors':errors,'mean_cycles':total/len(pairs),'min_cycles':mn,'max_cycles':mx,
            'quadrants':{q:{'cases':n,'mean_cycles':s/n if n else None} for q,(s,n) in quad.items()},
            '_cycles':cycles}

def clean(r):
    return {k:v for k,v in r.items() if k!='_cycles'}

def compare(pairs,base,cand):
    rb=run(*base,pairs); rc=run(*cand,pairs)
    deltas=[c-b for b,c in zip(rb['_cycles'],rc['_cycles'])]
    qd={q:rc['quadrants'][q]['mean_cycles']-rb['quadrants'][q]['mean_cycles']
        for q in rb['quadrants'] if rb['quadrants'][q]['cases']}
    return {'baseline':clean(rb),'candidate':clean(rc),
            'delta_mean_cycles':sum(deltas)/len(deltas),
            'delta_min':min(deltas),'delta_max':max(deltas),
            'quadrant_delta_mean':qd}

class TraceCPU(CPU):
    trace_lo=0
    trace_hi=0
    branch_counts=None
    def step(self):
        pc=self.pc
        if self.trace_lo <= pc < self.trace_hi:
            oc=self.mem[pc]
            if oc in REV:
                op,mode=REV[oc]
                if mode=='rel':
                    off=self.mem[(pc+1)&0xffff]; off=off-256 if off&128 else off
                    target=(pc+2+off)&0xffff
                    cond={'bpl':not self.n,'bmi':self.n,'bvc':not self.v,'bvs':self.v,
                          'bcc':not self.c,'bcs':self.c,'bne':not self.z,'beq':self.z}[op]
                    k=(pc,op,target)
                    rec=self.branch_counts.setdefault(k,[0,0])
                    rec[0]+=1
                    rec[1]+=int(cond)
        return super().step()

def branch_profile(pairs,start_label,end_label):
    cfg=ROOT/'relocatable_source/v2_pareto_fast/math_config_reference.inc'
    src=ROOT/'relocatable_source/v2_pareto_fast/math_relocatable.asm'
    memdict,labels,const=Assembler().assemble(preprocess(src,cfg))
    api=parse_api(ROOT/'build_source/reference/v2_pareto_fast/math_api.inc')
    b=(ROOT/'build_source/reference/v2_pareto_fast/math_v2_pareto_fast_source_built.prg').read_bytes()
    load=b[0]|b[1]<<8
    mem=bytearray(65536);mem[load:load+len(b)-2]=b[2:]
    cpu=TraceCPU(mem);cpu.d=0;cpu.branch_counts={}
    cpu.trace_lo=labels[start_label];cpu.trace_hi=labels[end_label]
    cpu.call(api['MATH_INIT'],2_000_000)
    for x,y in pairs:
        wr(cpu.mem,IO,x);wr(cpu.mem,IO+4,y)
        cpu.call(api['MATH_SMUL32'],2_000_000)
    revlabels={v:k for k,v in labels.items()}
    out=[]
    for (pc,op,target),(n,taken) in sorted(cpu.branch_counts.items()):
        if n < max(10,len(pairs)//100):
            continue
        out.append({'pc':f'${pc:04X}','op':op,'target':revlabels.get(target,f'${target:04X}'),
                    'executions':n,'taken':taken,'taken_rate':taken/n})
    return out

def quadrant_stress(kind,n=5000):
    rng=random.Random(0x51A3200 + sum(map(ord,kind)))
    lo=lambda: rng.randrange(1<<31)
    hi=lambda: rng.randrange(1<<31,1<<32)
    fs={'PP':(lo,lo),'PN':(lo,hi),'NP':(hi,lo),'NN':(hi,hi)}
    fx,fy=fs[kind]
    return [(fx(),fy()) for _ in range(n)]

def main():
    base=load(ROOT/'v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg',
              ROOT/'v2_pareto_fast/resident/math_api.inc')
    cand=load(ROOT/'build_source/reference/v2_pareto_fast/math_v2_pareto_fast_source_built.prg',
              ROOT/'build_source/reference/v2_pareto_fast/math_api.inc')
    stress=pp_stress()
    out={'canonical':compare(corpus(),base,cand),'pp_stress':compare(stress,base,cand),
         'branch_profiles':{
           'PP':branch_profile(quadrant_stress('PP'),'S32V28_q0_summation','S32V28_q0_cg_code_end'),
           'PN':branch_profile(quadrant_stress('PN'),'S32V28_q1_summation','S32V28_q1_cg_code_end'),
           'NP':branch_profile(quadrant_stress('NP'),'S32V28_q2_summation','S32V28_q2_cg_code_end'),
           'NN':branch_profile(quadrant_stress('NN'),'S32V28_summation','S32V28_cg_code_end')}}
    errors=out['canonical']['candidate']['errors']+out['pp_stress']['candidate']['errors']
    out['status']='PASS' if errors==0 else 'FAIL'
    print('SMUL32_RESEARCH_RESULT '+json.dumps(out,sort_keys=True))
    if errors: raise SystemExit(1)
if __name__=='__main__': main()
