#!/usr/bin/env python3
"""Issue144 D: V1/V5 normal-resident SEEK16_INIT slot-geometry / public-call screen.

Research only. Reassemble the pre-existing full-domain optional accumulator
inline source into the original normal resident INIT allocation, placing its
fractional helper in reclaimed tail bytes of the SAME resident entry island.
No caller RAM, new ZP, public trampolines or shipped images are changed.
"""
from __future__ import annotations
import json, statistics
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler
from benchmark_seek_profiles import load, corpus
from issue144_seek16_accum_all_profiles_v2 import make,feed,SPEEDS

BEGIN=0x3723
LIMIT=0x38CE       # original resident accumulator-helper start, kept intact
LOW_MAIN=0x0D00
LOW_HELP=0x0F60
STATES=(0x1980,0x1B00)

def candidate(profile):
    code,placed,labels=make(profile)
    main=[a for a in placed if a<LOW_HELP]
    tail=[a for a in placed if a>=LOW_HELP]
    assert main and tail
    assert min(main)==LOW_MAIN and min(tail)==LOW_HELP
    assert all(a<LOW_HELP for a in main)
    assert len(set(main))==len(main) and len(set(tail))==len(tail)
    main_len=max(main)-LOW_MAIN+1
    tail_len=max(tail)-LOW_HELP+1
    spare=LIMIT-BEGIN-main_len-tail_len
    report={'profile':profile,'source_main_bytes':main_len,
            'source_tail_bytes':tail_len,
            'normal_original_span_bytes':LIMIT-BEGIN,
            'source_bytes':len(placed),
            'spare_bytes_after_relocation':spare}
    if spare<0:
        report['status']='REJECT_NO_RESIDENT_FIT'
        return report,None
    helper=LIMIT-tail_len
    assert BEGIN+main_len<=helper and helper+tail_len==LIMIT
    assert code.count('* = $0D00')==1 and code.count('* = $0F60')==1
    source=code.replace('* = $0D00','* = $%04X'%BEGIN)
    source=source.replace('* = $0F60','* = $%04X'%helper)
    mem,lbl,_=Assembler().assemble(source)
    assert mem and min(mem)==BEGIN and max(mem)<LIMIT
    assert len(mem)==len(placed),(profile,len(mem),len(placed))
    assert all(BEGIN<=a<LIMIT for a in mem)
    assert lbl['L3723']==BEGIN and lbl['SEEK_ACCUM_ONCE']==helper
    report.update(status='FIT_SOURCE_ASSEMBLED',helper_address=hex(helper),
                  executable_bytes=len(mem),modified_interval=[hex(BEGIN),hex(LIMIT)])
    return report,mem

def verify(profile,moves):
    report,code=candidate(profile)
    if code is None:return report
    stock,api=load(profile)
    candidate_cpu,_=load(profile)
    public=api['MATH_SEEK16_INIT']
    assert stock.mem[public]==candidate_cpu.mem[public]==0x4C
    assert stock.mem[public+1:public+3]==BEGIN.to_bytes(2,'little')
    assert candidate_cpu.mem[public+1:public+3]==BEGIN.to_bytes(2,'little')
    # No previously live helper, movement-state or external code is changed.
    helper_before=bytes(stock.mem[LIMIT:0x38F8])
    for addr,value in code.items():candidate_cpu.mem[addr]=value
    assert candidate_cpu.mem[LIMIT:0x38F8]==helper_before
    assert candidate_cpu.mem[0x19F0:0x1B00]==stock.mem[0x19F0:0x1B00]
    saved=[];cases=0;steps=0
    for i,move in enumerate(corpus(320)[:moves]):
        for si,speed in enumerate(SPEEDS):
            slot=(i*7+si)&7
            feed(stock,api,move,speed,slot);feed(candidate_cpu,api,move,speed,slot)
            sp_before=(stock.sp,candidate_cpu.sp)
            a=stock.call(public,4_000_000)
            b=candidate_cpu.call(public,4_000_000)
            assert stock.mem[STATES[0]:STATES[1]]==candidate_cpu.mem[STATES[0]:STATES[1]],(profile,i,speed,'init')
            assert (stock.c,stock.x,stock.sp)==(candidate_cpu.c,candidate_cpu.x,candidate_cpu.sp)
            assert (stock.sp,candidate_cpu.sp)==sp_before
            saved.append(a-b);cases+=1
            for c in (stock,candidate_cpu):c.x=slot
            stock.call(api['MATH_SEEK16_STEP'],4_000_000)
            candidate_cpu.call(api['MATH_SEEK16_STEP'],4_000_000)
            assert stock.mem[STATES[0]:STATES[1]]==candidate_cpu.mem[STATES[0]:STATES[1]],(profile,i,speed,'step')
            assert stock.c==candidate_cpu.c
            steps+=1
    assert cases==moves*len(SPEEDS)
    report.update(status='PASS_V1V5_NORMAL_RESIDENT_SEEK_SOURCE_MODEL',paired_INIT_calls=cases,
                  paired_STEP_calls=steps,mean_cycles_saved=statistics.mean(saved),
                  worst_cycles_saved=min(saved),best_cycles_saved=max(saved),
                  slower_cases=sum(x<0 for x in saved),
                  reference_PRG_modified=False,normal_ZP_growth=0,caller_RAM_growth=0,
                  native_VICE_qualified=False,full_56_entry_public_ABI_qualified=False)
    return report

def main():
    results={p:verify(p,80) for p in ('v1_balanced','v5_hybrid_lowzp')}
    print(json.dumps({'status':'PASS_RESEARCH' if all(x['status'].startswith('PASS') for x in results.values())
                      else 'FIT_RESEARCH_INCOMPLETE','profiles':results},indent=2,sort_keys=True))
    assert all(x['status'].startswith('PASS') for x in results.values())

if __name__=='__main__':main()
