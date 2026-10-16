#!/usr/bin/env python3
"""Issue #144 P5: model-only cross-call lifetime test for nine public kernels.

One 6510 CPU instance per source/frozen binary is reused throughout. This is
NOT real x64sc, nested IRQ/NMI or physical VIC/REU DMA timing qualification.
"""
from __future__ import annotations
import argparse, hashlib, json, random, re, sys, tempfile
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import issue144_nine_kernel_candidate_benchmark as base
from issue144_isqrt32_release_candidate import PROFILES,FROZEN,REUS,radicands,frozen_seals,digest
from assemble_sources import build as build_source
from build_hybrid import build as build_hybrid
from validate_source_build import unhx

def source_api(dest,manifest):
    api={name:unhx(value) for name,value in manifest['public_entries'].items()}
    api['MATH_INIT']=unhx(manifest['math_init'])
    for line in (dest/'math_api.inc').read_text().splitlines():
        m=re.fullmatch(r'\s*(MATH_SEEK16_POS_[A-Z]+)\s*=\s*\$([0-9A-Fa-f]+)\s*',line)
        if m: api[m.group(1)]=int(m.group(2),16)
    assert len(manifest['public_entries'])==56 and set(base.OPS).issubset(api)
    assert all(k in api for k in ('MATH_SEEK16_POS_XL','MATH_SEEK16_POS_XH','MATH_SEEK16_POS_Y'))
    return api

def profile_test(p,layout,rounds,stage):
    config=ROOT/'relocatable_source'/p/('math_config_'+layout+'.inc')
    dest=stage/p
    manifest=(build_hybrid(config,dest) if p==PROFILES[-1] else build_source(p,config,dest))
    prg=dest/manifest['output_prg']
    assert digest(prg)==manifest['output_sha256']
    reu=dest/manifest['reu_image']['file'] if manifest.get('reu_image') else None
    old_api=base.api_frozen(p);new_api=source_api(dest,manifest)
    old,_=base.init_machine(p,FROZEN[p],REUS.get(p),
                           {k:f'${v:04X}' for k,v in old_api.items()})
    new,_=base.init_machine(p,prg,reu,
                           {k:f'${v:04X}' for k,v in new_api.items()})
    old_sp,new_sp=old.sp,new.sp
    pairs,division,seeking=base.corpus(rounds+64)
    roots=radicands()
    inputs={op:(roots if op=='MATH_ISQRT32' else
                seeking if op=='MATH_SEEK16_INIT' else
                division if op in base.DIV else pairs) for op in base.OPS}
    io_new=unhx(manifest['public_io'].split('-')[0])
    rng=random.Random(0x1445A+PROFILES.index(p))
    counts=Counter();seal=hashlib.sha256()
    for i in range(rounds):
        order=list(base.OPS);rng.shuffle(order)
        for op in order:
            samples=inputs[op]
            k=i if i<min(rounds//2,len(samples)) else (i*37+13)%len(samples)
            item=samples[k]
            old_c,old_out=base.sample(old,old_api,op,item,0xc000)
            new_c,new_out=base.sample(new,new_api,op,item,io_new)
            assert old_c>0 and new_c>0
            if op=='MATH_SEEK16_INIT':
                assert old_out[0]==new_out[0]
                assert base.trace_seek(old,old_api,old_out)==base.trace_seek(new,new_api,new_out), (p,layout,op,i)
            else:
                assert old_out==new_out,(p,layout,op,i,item)
            assert old.sp==old_sp and new.sp==new_sp,(p,layout,op,'stack')
            assert old.d==new.d==0,(p,layout,op,'decimal flag')
            seal.update(repr((i,op,item,old_out)).encode())
            counts[op]+=1
    assert all(counts[k]==rounds for k in base.OPS)
    return {'profile':p,'layout':layout,'rounds_per_api':rounds,
            'sequential_public_calls':sum(counts.values()),
            'calls_by_api':dict(sorted(counts.items())),
            'mixed_outputs_sha256':seal.hexdigest(),
            'frozen_prg_sha256':digest(FROZEN[p]),
            'source_prg_sha256':digest(prg),
            'source_reu_sha256':digest(reu) if reu else None,
            'stack_balanced_after_each_call':True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--layout',required=True,choices=('reference','alternate'))
    ap.add_argument('--rounds',type=int,default=96)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    assert 1<=args.rounds<=1024
    frozen=frozen_seals()
    with tempfile.TemporaryDirectory(prefix='issue144_mixed_p5_') as t:
        rows=[profile_test(p,args.layout,args.rounds,Path(t)) for p in PROFILES]
    assert frozen_seals()==frozen
    proof={'status':'PASS_MODEL_SEQUENTIAL_MIXED_NINE_APIS',
           'qualification':'model, not native VICE, interrupted calls or physical hardware',
           'layout':args.layout,'profiles':rows,'routines':list(base.OPS),
           'total_sequential_public_calls':sum(r['sequential_public_calls'] for r in rows),
           'irq_nmi_reentrancy_tested':False,
           'physical_bus_time_tested':False,
           'native_vice_tested_by_this_script':False,
           'shipped_reference_images_modified':False,
           'private_optisearch_code_used_or_published':False}
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/('ISSUE144_MIXED_NINE_'+args.layout+'.json')).write_text(
        json.dumps(proof,indent=2,sort_keys=True)+'\n')
    print('ISSUE144 P5 MIXED MODEL',args.layout,'PASS',
          proof['total_sequential_public_calls'],'sequential calls',flush=True)

if __name__=='__main__':main()
