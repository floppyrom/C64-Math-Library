#!/usr/bin/env python3
"""Native x64sc release gate for source-built V1/V5 32/16 default images.

Reads original 13 October main resident PRGs by immutable git SHA, compares
them against actual staged shipped source-built PRGs, both public aliases.
Requires prior source-regeneration and package staging; does not measure cycles.
"""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
from native_issue39_v1_3216_outofline_zero import run_native,hash_bytes,API,COUNT
PARENT="855bb298cc461ccc7a1636a093586dbc5883065b"
AFTER={
 "v1_balanced":"9af44deda4a1527a0ea5ecc09a48e1ec4927a45099f7b2e26ced0f618274c0a4",
 "v5_hybrid_lowzp":"0662a9644ee4ebb6df7a06f9c77a40ffb5308b69ecd5e6bc9c7d6250b5bd5750"
}
BEFORE={
 "v1_balanced":"2567dccbc4e01f3d606e80126c8150c58e4f30b8b726ff38e116c6aaec644178",
 "v5_hybrid_lowzp":"431824532ef218423b77bfc8353ccac8e380847c824f040aeffa5c7903c0ea2d"
}
def main():
 state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 out={'status':'PASS_STAGED_NATIVE_VICE','native_cycles_measured':False,
    'resident_images_were_source_built':True,'profiles':{},'full_native_calls':0}
 exe=os.getenv('VICE_WRAPPER','x64sc')
 with tempfile.TemporaryDirectory(prefix='issue39_3216_release_vice_') as tmp:
  folder=Path(tmp)
  for p in AFTER:
   rel=f'{p}/resident/math_{p}_game_math.prg'
   old=subprocess.check_output(['git','show',f'{PARENT}:{rel}'],cwd=ROOT)
   new=(ROOT/rel).read_bytes()
   assert hash_bytes(old)==BEFORE[p]
   assert hash_bytes(new)==AFTER[p]==state['reference_prg_sha256'][p]
   o={'old_sha256':BEFORE[p],'source_built_sha256':AFTER[p],'operations':{}}
   for i,op in enumerate(API):
    tag=p+'_'+str(i)
    base=run_native(old,op,tag+'_old',6554+2*i+len(out['profiles'])*4,folder,exe)
    trial=run_native(new,op,tag+'_new',6555+2*i+len(out['profiles'])*4,folder,exe)
    assert base['records']==trial['records'],(p,op,'old/new native mismatch')
    o['operations'][op]={'paired_operands':COUNT,'old_dump_sha256':base['dump_sha256'],
       'new_dump_sha256':trial['dump_sha256'],'exact_match':True}
    out['full_native_calls']+=2*COUNT
    print('NATIVE VICE',p,op,'PASS',2*COUNT,flush=True)
   out['profiles'][p]=o
 assert out['full_native_calls']==384
 dest=ROOT/'validation/review/ISSUE39_V1_3216_OOL_RELEASE_NATIVE.json'
 dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('ISSUE39 V1/V5 FULL SOURCE-INSTALLED NATIVE VICE PASS',384,flush=True)
if __name__=='__main__':main()
