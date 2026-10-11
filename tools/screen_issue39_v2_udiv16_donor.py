#!/usr/bin/env python3
"""Issue39 V2 16-bit donor/dispatcher *research* (never modifies shipped PRGs).

Lift the *certified V1 public UDIV16/UMOD16 engine* from $4200-$4342
into currently zero V2 $B000-$B142; relocate its sole JMP $42AB->$4338
to $B0AB->$B138. Screen a 13-byte D-high threshold selector at $B200,
preserving V2's original fast $B800 divider for low D-high classes.
This is not evidence of safe source placement or V5 integration.
"""
from pathlib import Path
import hashlib,json,sys
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus,band,SPECS
OUT=ROOT/'validation/review/ISSUE39_V2_UDIV16_UMOD16_DONOR_SCREEN.json'
ENTRY={'MATH_UDIV16':0x3140,'MATH_UMOD16':0x3220}
N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
B=0xB000
LIMITS=(1,2,4,8,12,16,24,32,48,64,96,128,192,256)

def copy_donor(mem1,mem2):
    donor=bytearray(mem1[0x4200:0x4343])
    assert len(donor)==323 and donor[:3]==bytes.fromhex('af11c0')
    assert donor[0xAB:0xAE]==bytes.fromhex('4c3843')
    assert not any(mem2[B:B+len(donor)])
    assert not any(mem2[0xB200:0xB20D])
    donor[0xAC:0xAE]=bytes((0x38,0xB1))
    mem2[B:B+len(donor)]=donor
    return hashlib.sha256(donor).hexdigest()

def prepare(cpu,mode,t=0):
    mem=cpu.mem
    if mode=='donor':
        for address in ENTRY.values():mem[address:address+3]=bytes((0x4c,0,0xb0))
    if mode=='selector':
        assert 1<=t<=255
        mem[0xB200:0xB20D]=bytes((0xAD,0x15,0xC0,0xC9,t,0x90,0x03,0x4C,0,0xB0,0x4C,0,0xB8))
        for address in ENTRY.values():mem[address:address+3]=bytes((0x4c,0,0xB2))
    return cpu

def sample(cpu,entry,n,d,op):
    m=cpu.mem
    wr(m,N,n,2);wr(m,D,d,2)
    wr(m,Q,0xA55A,2);wr(m,R,0x5AA5,2)
    cycles=cpu.call(entry,1_000_000)
    eq,er,ec=expected(n,d,16,16,0)
    got=(rd(m,Q,2),rd(m,R,2),cpu.c)
    assert got==(eq,er,ec),(op,n,d,got,(eq,er,ec))
    assert rd(m,N,2)==n and rd(m,D,2)==d,(op,n,d,'inputs changed')
    return cycles

def main():
    ref,er=load('v1_balanced')
    base,eb=load('v2_pareto_fast')
    donor,ed=load('v2_pareto_fast')
    selector,es=load('v2_pareto_fast')
    h=copy_donor(ref.mem,donor.mem)
    assert copy_donor(ref.mem,selector.mem)==h
    prepare(donor,'donor')
    report={'status':'PASS','qualification':'research screen only; no shipped source or PRG changes',
            'new_code_islands':{'donor':['B000','B142',323],'selector':['B200','B20C',13]},
            'new_normal_zp_bytes':0,'lifted_V1_sha256':h,'routines':{}}
    for op in ENTRY:
        spec=next(s for s in SPECS if s[0]==op)
        _,nb,db,qb,rb,shift,rem_only,count=spec
        _,vec=corpus(op,nb,db,shift,count)
        rows=[]
        for n,d,kind in vec:
            cyc1=sample(ref,er[op],n,d,op)
            cyc2=sample(base,eb[op],n,d,op)
            cycd=sample(donor,ed[op],n,d,op)
            assert cyc1==cycd,(op,n,d,cyc1,cycd)
            rows.append((n,d,kind,cyc1,cyc2,band(n,d,0)))
        aggregate={'V1':sum(x[3] for x in rows)/len(rows),'V2':sum(x[4] for x in rows)/len(rows)}
        groups=defaultdict(lambda: [0,0,0])
        for n,d,kind,v1,v2,cl in rows:
            a=groups[cl];a[0]+=1;a[1]+=v1;a[2]+=v2
        classes={k:{'cases':v[0],'v1_mean':v[1]/v[0],'v2_mean':v[2]/v[0]} for k,v in groups.items()}
        candidates=[]
        for t in LIMITS:
            if t==256:continue # 256 is V2 baseline, no selector needed
            prepare(selector,'selector',t)
            values=[]
            for n,d,kind,v1,v2,cl in rows:
                values.append(sample(selector,es[op],n,d,op))
            changes=[v-basecy for v,(_,_,_,_,basecy,_) in zip(values,rows)]
            candidates.append({'min_divisor_high':t,'mean_cycles':sum(values)/len(values),
                               'mean_delta_vs_V2':sum(changes)/len(changes),
                               'faster':sum(x<0 for x in changes),
                               'equal':sum(x==0 for x in changes),
                               'slower':sum(x>0 for x in changes),
                               'worst_regression':max(changes)})
        candidates.sort(key=lambda x:x['mean_cycles'])
        dxy=[dcy-bcy for _,_,_,dcy,bcy,_ in rows]
        theoretical_best=sum(min(dcy,bcy) for _,_,_,dcy,bcy,_ in rows)/len(rows)
        report['routines'][op]={'cases':len(rows),'mean_cycles':aggregate,
            'classes':classes,'ideal_costless_case_oracle_mean':theoretical_best,
            'whole_donor_faster':sum(x<0 for x in dxy),
            'whole_donor_slower':sum(x>0 for x in dxy),
            'whole_donor_equal':sum(x==0 for x in dxy),
            'best_selectors':candidates[:8],'all_selectors':candidates}
        print(op,'cases',len(rows),'means',aggregate,'oracle',theoretical_best,flush=True)
        for x in candidates[:6]:
            print('  gate',x['min_divisor_high'],'mean',f"{x['mean_cycles']:.6f}",
                  'delta',f"{x['mean_delta_vs_V2']:+.6f}",'faster',x['faster'],'slower',x['slower'],
                  'max_regression',x['worst_regression'],flush=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 U16 DONOR/SELECTOR SCREEN PASS (NO PROMOTION)',flush=True)

if __name__=='__main__':main()
