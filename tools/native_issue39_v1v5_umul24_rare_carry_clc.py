#!/usr/bin/env python3
"""Native VICE 384-call source-only V1/V5 FAST24 carry-clear specialization proof.

The tested candidate is built from the *current* public source in temporary
source output directories, not installed into tracked resident binary images.
"""
from pathlib import Path
import hashlib, json, os, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm
import build_hybrid
from screen_issue39_v1v5_umul24_tail_carry_clc import (
    SOURCE,OLD_RARE,NEW_RARE,OLD_TAIL,NEW_TAIL,PROFILES)
from native_issue39_v1v5_umul24_tailcall import native
COUNT=48
ENTRIES=('MATH_UMUL24','MATH_SMUL24')
def sha(b):return hashlib.sha256(b).hexdigest()

def screen():
    before=SOURCE.read_text()
    assert before.count(OLD_RARE)==before.count(OLD_TAIL)==1
    after=before.replace(OLD_RARE,NEW_RARE).replace(OLD_TAIL,NEW_TAIL)
    report={'status':'PASS_NATIVE_VICE_RESEARCH_NO_RELEASE_CHANGE',
            'native_cycle_timing_measured':False,'tracked_residents_changed':False,
            'native_public_calls':0,'profiles':{}}
    exe=os.getenv('VICE_WRAPPER','x64sc')
    with tempfile.TemporaryDirectory(prefix='issue39_v1v5_umul24_clc_native_') as temp:
        folder=Path(temp)
        try:
            SOURCE.write_text(after)
            candidates={}
            for p in PROFILES:
                cfg=ROOT/'relocatable_source'/p/'math_config_reference.inc'
                buildfolder=folder/'build'/p
                buildfolder.mkdir(parents=True)
                manifest=asm.build(p,cfg,buildfolder) if p=='v1_balanced' else build_hybrid.build(cfg,buildfolder)
                candidates[p]=(buildfolder/manifest['output_prg']).read_bytes()
        finally:
            SOURCE.write_text(before)
        assert SOURCE.read_text()==before
        for i,p in enumerate(PROFILES):
            published=(ROOT/p/'resident'/f'math_{p}_game_math.prg').read_bytes()
            modified=candidates[p]
            assert len(published)==len(modified),(p,'resident length drift')
            lo=int.from_bytes(published[:2],'little')
            assert lo==int.from_bytes(modified[:2],'little')==0x1000
            delta=[lo+j for j,(x,y) in enumerate(zip(published[2:],modified[2:])) if x!=y]
            assert delta and all(0x2700<=x<0x3000 for x in delta),(p,'outside owned source',delta[:20])
            rows={'baseline_sha256':sha(published),'candidate_sha256':sha(modified),
                  'changed_code_bytes':len(delta),'entries':{}}
            for k,op in enumerate(ENTRIES):
                base=native(published,op,f'{p}_{op}_old',8550+4*i+2*k,folder,exe)
                new=native(modified,op,f'{p}_{op}_candidate',8551+4*i+2*k,folder,exe)
                assert base['records']==new['records'],(p,op,'native public ABI drift')
                rows['entries'][op]={
                    'calls_before':len(base['records']),
                    'calls_after':len(new['records']),
                    'product_carry_input_stack_sentinel':True,
                    'before_dump_sha256':base['dump_sha256'],
                    'after_dump_sha256':new['dump_sha256']}
                report['native_public_calls']+=len(base['records'])+len(new['records'])
                print('NATIVE V1V5 UMUL24 CARRY CLC',p,op,'PASS',flush=True)
            report['profiles'][p]=rows
    assert report['native_public_calls']==2*2*COUNT*2
    return report
if __name__=='__main__':
    r=screen()
    if '--output' in sys.argv:
        path=Path(sys.argv[sys.argv.index('--output')+1])
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 V1/V5 UMUL24 RARE-CARRY VICE PASS',r['native_public_calls'])
