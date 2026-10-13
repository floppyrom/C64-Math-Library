#!/usr/bin/env python3
"""Independent native 6510 VICE screen for the unchanged-size UMUL24 RTS/NOP patch.

3 public profiles * 2 variants * 2 operations * 48 inputs = 576 actual calls.
Uses the pre-existing VICE resident harness; not a timing measurement or release.
"""
from pathlib import Path
import hashlib, json, os, sys, tempfile
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from native_issue39_umul24_tail_release import native
PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m')
ADDR=0x5747
OLD=bytes.fromhex('18 60')
NEW=bytes.fromhex('60 ea')
def sha(b):return hashlib.sha256(b).hexdigest()

def run():
    report={'status':'PASS_NATIVE_VICE_RESEARCH_NO_PRODUCTION_CHANGE',
            'native_cycle_timing_measured':False,'production_prgs_changed':False,
            'native_public_calls':0,'profiles':{}}
    exe=os.getenv('VICE_WRAPPER','x64sc')
    with tempfile.TemporaryDirectory(prefix='issue39_umul24_clc_vice_') as temporary:
        wd=Path(temporary)
        port=6510
        for profile in PROFILES:
            b=(R/profile/'resident'/f'math_{profile}_game_math.prg').read_bytes()
            lo=int.from_bytes(b[:2],'little')
            index=2+ADDR-lo
            assert lo==0x1000 and b[index:index+2] in (OLD,NEW),(profile,'resident tail mismatch')
            if b[index:index+2]==NEW:
                # When released, reconstruct the exact historical two-byte
                # resident in memory; never change the tracked candidate.
                old=b[:index]+OLD+b[index+2:]
                changed=b
            else:
                old=b
                changed=b[:index]+NEW+b[index+2:]
            assert len(old)==len(changed)
            entry={'before_sha256':sha(old),'after_sha256':sha(changed),'entries':{}}
            for kind in ('MATH_UMUL24','MATH_SMUL24'):
                before=native(old,kind,profile+'_'+kind+'_old',port,wd,exe)
                port+=1
                after=native(changed,kind,profile+'_'+kind+'_new',port,wd,exe)
                port+=1
                assert before['records']==after['records'],(profile,kind,'public output/status drift')
                entry['entries'][kind]={'calls_before':len(before['records']),
                                         'calls_after':len(after['records']),
                                         'preserved_results_flags_inputs_stack':True,
                                         'before_dump_sha256':before['dump_sha256'],
                                         'after_dump_sha256':after['dump_sha256']}
                report['native_public_calls']+=len(before['records'])+len(after['records'])
            report['profiles'][profile]=entry
            print('NATIVE UMUL24 CLC',profile,'PASS',flush=True)
    assert report['native_public_calls']==576,report['native_public_calls']
    return report
if __name__=='__main__':
    result=run()
    if '--output' in sys.argv:
        path=Path(sys.argv[sys.argv.index('--output')+1])
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+chr(10))
    print('ISSUE39 UMUL24 CLC NATIVE VICE PASS',result['native_public_calls'])
