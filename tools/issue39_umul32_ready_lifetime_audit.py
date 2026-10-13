#!/usr/bin/env python3
"""Audit whether V1/V5 normal UMUL32 pointer repair may be skipped after mixed calls.

A changed high-byte pointer is not itself proof of failure: test full 64-bit
results on real mixed-call states, comparing ordinary/READY public APIs. Does
not modify any published PRG, source, pointer design or private OptiSearch.
"""
from __future__ import annotations
from pathlib import Path
import argparse, copy, hashlib, json, random, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from benchmark_multiply_refresh import load, wr, rd
P=('v1_balanced','v5_hybrid_lowzp')
# V1/V5 FAST31 shared ZP_MAIN=$02: six pointer high bytes at odd offsets.
HIGHS=(0x03,0x05,0x07,0x09,0x0b,0x0d)
OPS=('MATH_UMUL8','MATH_UMUL16','MATH_UMUL24','MATH_SMUL8',
 'MATH_SMUL16','MATH_SMUL24','MATH_SMUL32',
 'MATH_UDIV8','MATH_UDIV16','MATH_UDIV24',
 'MATH_ISQRT16','MATH_ISQRT32','MATH_ATAN2_8','MATH_UMUL32_SHR16')
X=0xc000
def setinputs(cpu,x,y):
    wr(cpu.mem,X,x,4)
    wr(cpu.mem,X+4,y,4)
    wr(cpu.mem,X+0x10,0x12345678,4)
    wr(cpu.mem,X+0x14,0x1010101,4)
def snapshot(cpu):
    return tuple(cpu.mem[a] for a in HIGHS)
def result(cpu,addr,x,y):
    setinputs(cpu,x,y)
    cpu.d=0
    cycles=cpu.call(addr,30_000)
    out=rd(cpu.mem,X+8,8)
    good=(out==x*y and cpu.c==0 and rd(cpu.mem,X,4)==x and rd(cpu.mem,X+4,4)==y)
    return good,cycles,out
def audit(profile,states):
    pairs=[
        (0,0),(1,1),(0xffffffff,0xffffffff),(0x80000000,0x80000000),
        (0x12345678,0xdeadbeef),(0x0000ffff,0xffffff00)
    ]
    rng=random.Random(0xC6393224)
    pairs.extend((rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(20))
    rows=[];safe_count=ready_count=ready_bad=0
    for op in OPS:
        for index,(x,y) in enumerate(states):
            cpu,api=load(profile)
            original=snapshot(cpu)
            # An ordinary UMUL32 call establishes a known-good pointer image.
            good,_,_=result(cpu,api['MATH_UMUL32'],0x12345678,0x9abcdef0)
            assert good,(profile,'setup ordinary')
            intact=snapshot(cpu)
            setinputs(cpu,x,y)
            try:
                cpu.d=0
                cpu.call(api[op],2_000_000)
            except Exception as e:
                raise AssertionError((profile,op,index,str(e))) from e
            after=snapshot(cpu)
            affected=[hex(HIGHS[j]) for j in range(len(HIGHS)) if intact[j]!=after[j]]
            mismatch=None
            for u,v in pairs:
                # Each comparison starts at exactly the same polluted state.
                ca=copy.deepcopy(cpu)
                cb=copy.deepcopy(cpu)
                ga,cyca,va=result(ca,api['MATH_UMUL32'],u,v)
                try:
                    gb,cycb,vb=result(cb,api['MATH_UMUL32_READY'],u,v)
                    reason='incorrect_product_or_contract' if not gb else None
                except RuntimeError as exc:
                    gb,cycb,vb=False,None,0
                    reason='READY_exception_'+str(exc)
                assert ga,(profile,op,index,'normal UMUL32 invalid',hex(u),hex(v),hex(va))
                safe_count+=1;ready_count+=1
                if not gb:
                    ready_bad+=1
                    if mismatch is None:
                        mismatch=dict(x=hex(u),y=hex(v),ready_product=hex(vb),
                                      expected_product=hex(u*v),cycles_ordinary=cyca,
                                      cycles_ready=cycb,reason=reason)
            rows.append(dict(prior_op=op,state=index,pointer_high_bytes_changed=affected,
                 pointer_high_before=[hex(v) for v in intact],
                 pointer_high_after=[hex(v) for v in after],
                 ready_wrong_first_witness=mismatch))
    assert safe_count==ready_count==len(rows)*len(pairs)
    return dict(profile=profile,states_tested=len(rows),normal_calls=safe_count,
       ready_calls=ready_count,ready_wrong_calls=ready_bad,
       dirty_states=sum(bool(v['pointer_high_bytes_changed']) for v in rows),
       witnesses=[x for x in rows if x['ready_wrong_first_witness']],
       states=rows)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    states=((0x12345678,0x9abcdef0),(0xffffffff,0xffffffff),
            (0x80008000,0x1001001),(0xdeadbeef,0x10203040))
    output=dict(status='PASS_AUDIT_RESEARCH_ONLY',
                public_abi_unmodified=True,production_prgs_modified=False,
                profiles={},pointer_highs=[hex(a) for a in HIGHS],
                readiness_contract='READY requires valid stable pointer highs; never assume mixed-call safety')
    for p in P:
        entry=audit(p,states)
        output['profiles'][p]=entry
        print('UMUL32 READY LIFETIME',p,'states',entry['states_tested'],
              'pointer-dirty',entry['dirty_states'],'READY bad calls',
              entry['ready_wrong_calls'],'normal valid',entry['normal_calls'],flush=True)
        for w in entry['witnesses'][:5]:
            print('WITNESS',p,w['prior_op'],w['state'],w['pointer_high_bytes_changed'],
                 w['ready_wrong_first_witness'],flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+chr(10))
    print('ISSUE39 UMUL32 READY MIXED-CALL LIFETIME AUDIT PASS',flush=True)
if __name__=='__main__':main()
