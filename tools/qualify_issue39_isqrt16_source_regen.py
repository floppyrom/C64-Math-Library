#!/usr/bin/env python3
"""Protected ISQRT16 source-regeneration/hybrid promotion preflight.

Works in a disposable GitHub Actions checkout only. Rebuilds 4 stock profiles
and V5 before/after canonical source regeneration, ensuring identical
candidate PRG SHA and stable public API on reference and alternate maps.
No commits or shipped release files are written by this script itself.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm, build_hybrid
from validate_unsigned_division import PROFILES
ROOT_PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k')
V4='v4_reu_16m';V5='v5_hybrid_lowzp'
def filehash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def image(p):return ROOT/p/'resident'/('math_'+p+'_game_math.prg')
def assembly(p,kind,output):
    cfg=ROOT/'relocatable_source'/p/('math_config_'+kind+'.inc')
    man=asm.build(p,cfg,output)
    return output/man['output_prg'],man
def hybrid(kind,output):
    cfg=ROOT/'relocatable_source'/V5/('math_config_'+kind+'.inc')
    man=build_hybrid.build(cfg,output)
    return output/man['output_prg'],man

def main():
    before=json.loads((ROOT/'RELEASE_STATUS.json').read_text())['reference_prg_sha256']
    assert {p:filehash(image(p)) for p in PROFILES}==before
    doc={'status':'PASS_PREPROMOTION_SOURCE_ROUNDTRIP_ONLY',
         'not_released':True,'native_vice_calls':0,'source_regenerated':False,
         'reference':{},'alternate':{},'old_sha256':before}
    with tempfile.TemporaryDirectory(prefix='issue39_isqrt16_source_regen_') as temp:
        tmp=Path(temp)
        expected={}
        candidate_paths={}
        lengths={p:image(p).stat().st_size for p in PROFILES}
        for p in ROOT_PROFILES:
            out,man=assembly(p,'reference',tmp/'original'/p)
            expected[p]=man['output_sha256']
            candidate_paths[p]=out
            assert filehash(out)!=before[p],(p,'no speed change assembled')
            assert out.stat().st_size==lengths[p],(p,'resident size expanded')
        assert filehash(image(V4))==before[V4]
        out,man=hybrid('reference',tmp/'original'/V5)
        expected[V5]=man['output_sha256']
        candidate_paths[V5]=out
        assert filehash(out)!=before[V5],('V5 did not inherit V1 source change')
        assert out.stat().st_size==lengths[V5],('V5 size expansion')
        expected[V4]=before[V4]
        # The source-reconstruction tool owns the active resident objects in
        # this disposable checkout. A later release script must still separately
        # stage and verify all artifacts before commit.
        for p in (*ROOT_PROFILES,V5):
            shutil.copyfile(candidate_paths[p],image(p))
        print('STAGED TEMP RESIDENTS',expected,flush=True)
        subprocess.run([sys.executable,str(ROOT/'tools/generate_sources.py')],
                       cwd=ROOT,check=True)
        doc['source_regenerated']=True
        for kind in ('reference','alternate'):
            values={}
            for p in (*ROOT_PROFILES,V4):
                built,man=assembly(p,kind,tmp/'regenerated'/kind/p)
                values[p]=filehash(built)
                assert man['status']=='BUILT_FROM_SOURCE'
                if kind=='reference':
                    assert values[p]==expected[p],(p,'source regen SHA drift',values[p],expected[p])
            built,man=hybrid(kind,tmp/'regenerated'/kind/V5)
            values[V5]=filehash(built)
            if kind=='reference':
                assert values[V5]==expected[V5],('V5 source regen SHA drift',values[V5],expected[V5])
            doc[kind]=values
            print('REGENERATED',kind,values,flush=True)
        for p in ROOT_PROFILES:
            source=(ROOT/'relocatable_source'/p/'math_relocatable.asm').read_text()
            assert 'isqrt16_seed_square_trial.inc' in source,(p,'regeneration lost root include')
        assert expected[V4]==before[V4]
        doc['resident_unchanged_v4']=True
        doc['reference_candidate_sha256']=expected
    target=ROOT/'validation/review/ISSUE39_ISQRT16_SOURCE_REGEN_TRIAL.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n')
    print('ISQRT16 SOURCE-REGENERATION V1 V2 V3 V4 V5 ROUNDTRIP PASS',flush=True)
if __name__=='__main__':main()
