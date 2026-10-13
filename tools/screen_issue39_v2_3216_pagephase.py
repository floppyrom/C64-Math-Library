#!/usr/bin/env python3
"""Issue39: page-phase screen for source-owned V2 unrestricted UDIV32/16 core.

Exploratory only: never modifies shipped binaries. Tests complete public
UDIV32_16 and UMOD32_16 entries on identical official and six scenario
operand sets. Candidate V2 core origin is shifted within SOURCE-VERIFIED
zero-filled slack, keeping D8 island / shared API unchanged. Records
candidates that cannot assemble without conflicts as REJECTED, not wins.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from assemble_sources import preprocess
from mini6502 import Assembler,CPU
from validate_unsigned_division import load
from screen_issue39_u3216_n16_delegate import sample,OPS
from benchmark_unsigned_common_corpus import corpus,SPECS
from benchmark_unsigned_3216_workloads import WORKLOADS,pairs

PROFILE='v2_pareto_fast'
TARGET='U3216_MAIN_BASE = REG_KERNEL+$0E00'
MAIN_BASE=0x4E00
D8_BASE=0x5272
DELTAS=(-48,-32,-24,-16,-12,-8,-4,0,4,8,12,16,24,32,48)
SAME_INPUT=[
  ('official',lambda op: [(n,d) for n,d,_ in corpus(
      op,next(s for s in SPECS if s[0]==op)[1],
      next(s for s in SPECS if s[0]==op)[2],0,
      next(s for s in SPECS if s[0]==op)[7])[1]]),
]+[(name,lambda op,n=name: pairs(n)) for name in WORKLOADS]

def hash_bytes(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def assemble(text):
    mem,labels,_=Assembler().assemble(text)
    if not mem or min(mem)!=0x1000:
        raise AssertionError(('unexpected source load',min(mem) if mem else None))
    end=max(mem)
    return mem,labels,bytes((0,0x10))+bytes(mem.get(pc,0) for pc in range(0x1000,end+1))

def candidate_cpu(base_cpu,refmem,mem,start,end,ref_start,ref_end):
    # A relocated instruction may only occupy code-owned original bytes
    # or exact zero slack. If the candidate would clobber another routine,
    # it must be discarded regardless of its synthetic cycle savings.
    assert MAIN_BASE-0x40 <= start < D8_BASE
    assert end <= D8_BASE,('overlaps 32/8 donor',hex(end))
    assert ref_start==MAIN_BASE
    for pc in range(start,end):
        if not (ref_start<=pc<ref_end):
            assert refmem.get(pc,0)==0,('no empty placement',hex(pc))
    for pc in range(ref_start,ref_end):
        if not (start<=pc<end):
            assert mem.get(pc,0)==0,('old bytes retained',hex(pc))
    lo=0x1000;hi=max(max(refmem),max(mem))
    changed=[pc for pc in range(lo,hi+1)
             if refmem.get(pc,0)!=mem.get(pc,0)]
    assert changed, 'candidate identical to baseline'
    # Source overlays must change only their owned MAIN island and the
    # public wrapper's call/jump relocations.
    allowed=lambda pc:(MAIN_BASE-0x40 <= pc < D8_BASE) or (0x31B0<=pc<0x3200)
    rogue=[hex(a) for a in changed if not allowed(a)]
    assert not rogue,('writes outside kernel or public slot',rogue[:18])
    c=CPU(bytearray(base_cpu.mem))
    for pc in changed:c.mem[pc]=mem.get(pc,0)
    c.d=0
    return c,changed

def main():
    ar=argparse.ArgumentParser()
    ar.add_argument('--out',type=Path)
    args=ar.parse_args()
    from validate_unsigned_division import PROFILES
    assert PROFILE in PROFILES
    status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    resident=(ROOT/PROFILE/'resident'/f'math_{PROFILE}_game_math.prg').read_bytes()
    assert hash_bytes(resident)==status['reference_prg_sha256'][PROFILE]
    baseline,entries=load(PROFILE)
    src=ROOT/'relocatable_source'/PROFILE/'math_relocatable.asm'
    cfg=ROOT/'relocatable_source'/PROFILE/'math_config_reference.inc'
    text=preprocess(src,cfg)
    assert text.count(TARGET)==1,'source-owned 32/16 MAIN parameter missing'
    original,labels,raw=assemble(text)
    assert raw==resident,'canonical source no longer reproduces published V2 image'
    assert labels['U3216_ENTRY']==MAIN_BASE
    assert MAIN_BASE < labels['U3216_MAIN_END'] <= D8_BASE
    assert labels['U3216_D8']==D8_BASE
    report={
        'status':'PASS_RESEARCH_ONLY_NO_DEFAULT_CHANGE',
        'baseline_profile':PROFILE,
        'baseline_resident_sha256':hash_bytes(resident),
        'source':str(Path(__file__).relative_to(ROOT)),
        'native_vice_calls':0,
        'pairwise_6502_public_calls':0,
        'recommended_promotion':False,
        'hardware_bus_timing_measured':False,
        'no_extra_zp':True,
        'baseline_main_span':[hex(MAIN_BASE),hex(labels['U3216_MAIN_END'])],
        'd8_island_start':hex(D8_BASE),
        'variants':{},
    }
    # Stable vectors; both aliases share exact same six generated workloads.
    vectors={op:{name:generator(op) for name,generator in SAME_INPUT} for op in OPS}
    input_hashes={op:{name:hash_bytes(b''.join(
        n.to_bytes(4,'little')+d.to_bytes(2,'little') for n,d in vec))
        for name,vec in sets.items()} for op,sets in vectors.items()}
    # Full resident origin not changed in published files.
    base_cpus={op:load(PROFILE)[0] for op in OPS}
    reference_cycles={}
    for op in OPS:
        reference_cycles[op]={}
        for name,vec in vectors[op].items():
            out=[]
            for n,d in vec:
                tick,state=sample(base_cpus[op],entries[op],n,d)
                out.append((tick,state))
            reference_cycles[op][name]=out
    for delta in DELTAS:
        key=f'{delta:+d}'
        if delta==0:
            report['variants'][key]={'status':'BASELINE','main_start':hex(MAIN_BASE),
             'operations':{op:{name:{'cases':len(vec),
                                    'mean_delta':0.0,
                                    'input_sha256':input_hashes[op][name]}
               for name,vec in vectors[op].items()} for op in OPS}}
            continue
        row={'offset_bytes':delta,'main_start':hex(MAIN_BASE+delta)}
        try:
            expression=f'U3216_MAIN_BASE = REG_KERNEL+\u0024{0x0e00+delta:04X}'
            if delta < -0xE00:raise AssertionError('origin underflow')
            altered=text.replace(TARGET,expression,1)
            mem,lab,newraw=assemble(altered)
            if len(newraw)!=len(raw):
                raise AssertionError(('resident length growth',len(newraw),len(raw)))
            c,changed=candidate_cpu(baseline,original,mem,
                                   lab['U3216_ENTRY'],lab['U3216_MAIN_END'],
                                   labels['U3216_ENTRY'],labels['U3216_MAIN_END'])
            row.update(status='VALIDATED',changed_byte_count=len(changed),
                candidate_prg_sha256=hash_bytes(newraw),
                main_end=hex(lab['U3216_MAIN_END']),
                operations={})
            for op in OPS:
                row['operations'][op]={}
                for name,vec in vectors[op].items():
                    deltas=[]
                    for (n,d),(prior,prior_state) in zip(
                            vec,reference_cycles[op][name]):
                        newer,state=sample(c,entries[op],n,d)
                        assert state==prior_state,(op,name,n,d,'ABI changed')
                        deltas.append(newer-prior)
                    row['operations'][op][name]={
                        'cases':len(vec),'input_sha256':input_hashes[op][name],
                        'mean_delta':sum(deltas)/len(deltas),
                        'faster':sum(x<0 for x in deltas),
                        'equal':sum(x==0 for x in deltas),
                        'slower':sum(x>0 for x in deltas),
                        'max_regression':max(deltas),
                        'max_speedup':-min(deltas)}
                    report['pairwise_6502_public_calls']+=len(deltas)*2
            print('SOURCE PAGE PHASE',key,'official UDIV/UMOD deltas',
                  *(f'{row["operations"][op]["official"]["mean_delta"]:+.6f}' for op in OPS),flush=True)
        except (ValueError,RuntimeError,AssertionError,KeyError) as exc:
            row={'status':'REJECTED','reason':str(exc)[:350],
                 'offset_bytes':delta,'main_start':hex(MAIN_BASE+delta)}
            print('SOURCE PAGE PHASE',key,'REJECT',row['reason'],flush=True)
        report['variants'][key]=row
    validated=[x for x in report['variants'].values() if x['status']=='VALIDATED']
    report['validated_candidate_count']=len(validated)
    report['rejected_candidate_count']=sum(x['status']=='REJECTED' for x in report['variants'].values())
    def dominates(v):
        return all(v['operations'][op][name]['mean_delta'] <=0
                   for op in OPS for name in vectors[op]) and any(
                   v['operations'][op][name]['mean_delta'] <0
                   for op in OPS for name in vectors[op])
    report['nonregressing_offsets']=[v['offset_bytes'] for v in validated if dominates(v)]
    # This is research. Native + dual-map + all-profile integration would be
    # required even if a nonregressing phase happens to exist.
    report['needs_native_source_and_alt_map_for_any_promotion']=True
    assert report['status'].startswith('PASS_')
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 V2 U3216 PAGE PHASE SCREEN PASS:',
          len(validated),'valid;',report['rejected_candidate_count'],
          'rejected;',report['pairwise_6502_public_calls'],'old/new calls',flush=True)

if __name__=='__main__':main()
