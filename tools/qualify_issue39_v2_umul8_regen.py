#!/usr/bin/env python3
"""V2 UMUL8 zero-growth direct-output source-regeneration preflight.

Deliberately installs only in ephemeral CI checkout, never commits. Rebuilds
reference and alternate V2, regenerates canonical source from source-built
resident, reassembles exact V2 image and checks V5 hybrid. No bin changes on
main, no OptiSearch code published.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm,build_hybrid as hybrid,validate_source_build as check
PROFILE='v2_pareto_fast'
V5='v5_hybrid_lowzp'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(p):return ROOT/p/'resident'/f'math_{p}_game_math.prg'
def build_v2(td,kind):
    path=td/kind/PROFILE
    cfg=ROOT/'relocatable_source'/PROFILE/f'math_config_{kind}.inc'
    m=asm.build(PROFILE,cfg,path)
    return path/m['output_prg'],m
def build_v5(td,kind):
    path=td/kind/V5
    cfg=ROOT/'relocatable_source'/V5/f'math_config_{kind}.inc'
    m=hybrid.build(cfg,path)
    return path/m['output_prg'],m
def main():
    state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    before={p:sha(image(p)) for p in ('v1_balanced',PROFILE,'v3_reu_512k','v4_reu_16m',V5)}
    assert before==state['reference_prg_sha256']
    with tempfile.TemporaryDirectory(prefix='issue39_v2_umul8_regeneration_') as path:
        td=Path(path)
        generated,man=build_v2(td/'original','reference')
        assert sha(generated)!=before[PROFILE]
        assert generated.stat().st_size==image(PROFILE).stat().st_size
        assert (ROOT/'relocatable_source'/PROFILE/'math_relocatable.asm').read_text().count(
                'umul8_directout_trial.inc')==1
        old_v5=before[V5]
        shutil.copyfile(generated,image(PROFILE))
        subprocess.run([sys.executable,str(ROOT/'tools/generate_sources.py')],
                       cwd=ROOT,check=True)
        src=(ROOT/'relocatable_source'/PROFILE/'math_relocatable.asm').read_text()
        assert src.count('umul8_directout_trial.inc')==1, 'source regeneration dropped include'
        data={'status':'PASS_RESEARCH_SOURCE_REGEN_NO_RELEASE',
              'baseline_sha256':before[PROFILE],
              'candidate_sha256':sha(generated),
              'candidate_same_resident_size':True,
              'native_vice_calls':0,'profile':PROFILE,
              'maps':{},'v5':{}}
        for mode in ('reference','alternate'):
            new,manifest=build_v2(td/'regenerated',mode)
            if mode=='reference':
                assert sha(new)==sha(generated),('regeneration drift',mode)
            val=check.validate(PROFILE,td/'regenerated'/mode)
            assert val['status']=='PASS' and val['public_entries_executed']>=56
            data['maps'][mode]={
              'sha256':sha(new),'public_entries':val['public_entries_executed'],
              'machine_calls':val['machine_calls']}
            v5,m5=build_v5(td/'hybrid',mode)
            val5=check.validate(V5,td/'hybrid'/mode)
            assert val5['status']=='PASS' and val5['public_entries_executed']>=56
            data['v5'][mode]={'sha256':sha(v5),
                'public_entries':val5['public_entries_executed'],
                'machine_calls':val5['machine_calls']}
            if mode=='reference':
                data['v5']['base_sha256']=old_v5
                data['v5']['candidate_resident_changed']=sha(v5)!=old_v5
            print('V2 SOURCE REGEN',mode,sha(new),'V5',sha(v5),flush=True)
        if not data['v5']['candidate_resident_changed']:
            assert data['v5']['reference']['sha256']==before[V5]
        path=ROOT/'validation/review/ISSUE39_V2_UMUL8_SOURCE_REGEN_TRIAL.json'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
        print('ISSUE39 UMUL8 ZERO-GROWTH SOURCE ROUNDTRIP PASS',flush=True)
if __name__=='__main__':main()
