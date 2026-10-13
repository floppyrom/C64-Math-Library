#!/usr/bin/env python3
"""Isolated issue39 promotion-preflight: source regeneration round-trip, no commit.

In its throwaway CI checkout, replace only V1 and V5 resident images with
source-built candidates, regenerate canonical source, and build both maps.
The script never stages or pushes a production release. No changed binaries
are committed unless a later, separate release workflow passes all gates.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm
import build_hybrid as hybrid
import validate_source_build as sourcecheck
V1='v1_balanced'
V5='v5_hybrid_lowzp'
PROFILES=(V1,'v2_pareto_fast','v3_reu_512k','v4_reu_16m',V5)
def sha(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):return sha(Path(p).read_bytes())
def shipped(p):return ROOT/p/'resident'/f'math_{p}_game_math.prg'
def run(*parts):subprocess.run([str(x) for x in parts],cwd=ROOT,check=True)
def src_build(p,kind,td):
    cfg=ROOT/'relocatable_source'/p/f'math_config_{kind}.inc'
    folder=td/'build_source'/kind/p
    data=asm.build(p,cfg,folder)
    return folder/data['output_prg'],data
def hybrid_build(kind,td):
    cfg=ROOT/'relocatable_source'/V5/f'math_config_{kind}.inc'
    folder=td/'build_hybrid'/kind/V5
    data=hybrid.build(cfg,folder)
    return folder/data['output_prg'],data
def main():
    prev=json.loads((ROOT/'RELEASE_STATUS.json').read_text())['reference_prg_sha256']
    assert all(sha_file(shipped(p))==prev[p] for p in PROFILES)
    with tempfile.TemporaryDirectory(prefix='issue39_3216_regen_') as path:
        td=Path(path)
        original_source=(ROOT/'relocatable_source'/V1/'math_relocatable.asm').read_text()
        assert original_source.count('udiv32_16_ool_zero_trial.inc')==1
        ref,manifest=src_build(V1,'reference',td)
        assert sha_file(ref)=='9af44deda4a1527a0ea5ecc09a48e1ec4927a45099f7b2e26ced0f618274c0a4'
        v5,man5=hybrid_build('reference',td)
        assert sha_file(v5)=='0662a9644ee4ebb6df7a06f9c77a40ffb5308b69ecd5e6bc9d4250b5bd5750'
        shutil.copyfile(ref,shipped(V1))
        shutil.copyfile(v5,shipped(V5))
        run(sys.executable,ROOT/'tools/generate_sources.py')
        new_source=(ROOT/'relocatable_source'/V1/'math_relocatable.asm').read_text()
        assert new_source.count('udiv32_16_ool_zero_trial.inc')==1, 'regeneration lost overlay'
        result={'status':'PASS_REGENERATION_PREPROMOTION_ONLY','committed':False,
            'v1_reference_sha256':sha_file(ref),'v5_reference_sha256':sha_file(v5),
            'source_overlay_preserved':True,'reference':{},'alternate':{},'no_new_zp':True}
        for kind in ('reference','alternate'):
            one,meta=src_build(V1,kind,td)
            five,meta5=hybrid_build(kind,td)
            assert sha_file(one)==sha_file(ref) if kind=='reference' else one.exists()
            assert sha_file(five)==sha_file(v5) if kind=='reference' else five.exists()
            oneval=sourcecheck.validate(V1,td/'build_source'/kind)
            fiveval=sourcecheck.validate(V5,td/'build_hybrid'/kind)
            result[kind]={'v1_sha256':sha_file(one),'v5_sha256':sha_file(five),
              'v1_public_calls':oneval['machine_calls'],
              'v5_public_calls':fiveval['machine_calls']}
            print('SOURCE REGENERATED',kind, 'V1/V5 source and public calls PASS',flush=True)
        out=ROOT/'validation/review/ISSUE39_V1_3216_OOL_REGENERATION_TRIAL.json'
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('ISSUE39 V1 32/16 SOURCE REGENERATION ROUND TRIP PASS',flush=True)

if __name__=='__main__':main()
