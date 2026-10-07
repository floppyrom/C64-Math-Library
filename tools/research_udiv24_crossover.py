#!/usr/bin/env python3
"""Sweep the UDIV24 aligned-tail crossover threshold.

The production source exposes CPX #8 at DU24F_overshoot.  Patch only that
immediate in independently loaded source-built V2 images, so every threshold
shares identical code placement and differs by one byte.
"""
from pathlib import Path
import random,sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU,Assembler
import assemble_sources as AS
from validate_unsigned_division import load as load_resident,wr,rd
from validate_division_latency_escape import one

PROFILE='v2_pareto_fast'
SRC=ROOT/'relocatable_source'/PROFILE/'math_relocatable.asm'
CFG=ROOT/'relocatable_source'/PROFILE/'math_config_reference.inc'

def built(threshold):
    mem,lab,const=Assembler().assemble(AS.preprocess(SRC,CFG))
    m=bytearray(65536)
    for a,b in mem.items():m[a]=b
    pc=lab['DU24F_overshoot']
    assert m[pc]==0xE0 and m[pc+1]==8,(hex(pc),m[pc:pc+2])
    m[pc+1]=threshold
    c=CPU(m);c.d=0;c.call(const['MATH_INIT'],2_000_000)
    return c,const['MATH_UDIV24'],const['MATH_IO']

def corpus():
    r=random.Random(0x24C2055)
    v=[(r.randrange(1<<24),r.randrange(1,1<<16)) for _ in range(3000)]
    ds=[1,2,3,7,15,16,31,63,127,128,255,256,257,511,1023,4095,16383,32767,65535]
    qs=[0,1,2,3,7,15,31,63,127,128,255,256,257,511,512,1023,1024,2047,2048,4095,4096,8191,8192,16383,16384,32767]
    for d in ds:
        for q in qs:
            for z in (-1,0,1):
                n=d*q+z
                if 0<=n<1<<24:v.append((n,d))
        for n in (0,1,d-1,d,d+1,0xffff,0x10000,0x7fffff,0xffffff,max(0,0xffffff-d)):
            if 0<=n<1<<24:v.append((n,d))
    return list(dict.fromkeys(v))

def main():
    vec=corpus()
    old,A=load_resident(PROFILE); eo=A['MATH_UDIV24']
    oldcy=[]
    for n,d in vec:
        cy,ok,_,_=one(old,eo,0xc000,n,d,24,24,0xA5)
        assert ok,(hex(n),hex(d))
        oldcy.append(cy)
    out={'status':'PASS','cases':len(vec),'thresholds':[]}
    for t in range(8,16):
        c,en,io=built(t); newcy=[]
        for n,d in vec:
            cy,ok,g,e=one(c,en,io,n,d,24,24,0xA5)
            assert ok,(t,hex(n),hex(d),g,e)
            newcy.append(cy)
        delta=[a-b for a,b in zip(oldcy,newcy)]
        row={
          'x_threshold':t,'quotient_threshold':1<<t,
          'mean_cycles':sum(newcy)/len(newcy),'max_cycles':max(newcy),
          'saved_mean_cycles':sum(delta)/len(delta),
          'worst_regression_cycles':max(0,-min(delta)),
          'slower_cases':sum(x<0 for x in delta),
          'substantive_slower_cases':sum(x<-4 for x in delta),
          'wins':sum(x>0 for x in delta),
        }
        out['thresholds'].append(row);print(json.dumps(row,sort_keys=True),flush=True)
    # Minimax first, then regression severity, then mean.
    out['best_by_minimax']=min(out['thresholds'],key=lambda x:(x['max_cycles'],x['worst_regression_cycles'],x['mean_cycles']))
    out['best_no_substantive_regression']=min(
      (x for x in out['thresholds'] if x['substantive_slower_cases']==0),
      key=lambda x:(x['max_cycles'],x['mean_cycles']),default=None)
    print('BEST',json.dumps(out['best_by_minimax'],sort_keys=True))
    print('BEST_NO_SUBSTANTIVE',json.dumps(out['best_no_substantive_regression'],sort_keys=True))
    p=ROOT/'validation/research/UDIV24_CROSSOVER_SWEEP.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
