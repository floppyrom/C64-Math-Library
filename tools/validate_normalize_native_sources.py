#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

from mini6502 import Assembler
from assemble_sources import parse_config

ENTRY_OFFSET=0x39
ROUTINE_BYTES={
 'v1_balanced':392,
 'v2_pareto_fast':383,
 'v3_reu_512k':346,
 'v4_reu_16m':346,
 'v5_hybrid_lowzp':392,
}
FIXED=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m')
ALL=FIXED+('v5_hybrid_lowzp',)

def sha(path:Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

def load_prg(path:Path):
 b=path.read_bytes();lo=b[0]|b[1]<<8
 mem=bytearray(65536);mem[lo:lo+len(b)-2]=b[2:]
 return mem

def native_path(profile):
 return ROOT/profile/'resident/vector/native/vec2_normalize_q8_8.asm'

def config_path(profile,kind):
 return ROOT/'relocatable_source'/profile/f'math_config_{kind}.inc'

def build_dir(profile,kind):
 if profile=='v5_hybrid_lowzp':return ROOT/'build_hybrid'/kind/profile
 return ROOT/'build_source'/kind/profile

def strip_cpu(text):
 return '\n'.join(x for x in text.splitlines() if not x.strip().lower().startswith('!cpu'))+'\n'

def main():
 out={'status':'PASS','checks':[],'profiles':{}}
 def ck(name,ok,detail=None):
  out['checks'].append({'name':name,'status':'PASS' if ok else 'FAIL','detail':detail})
  if not ok:
   out['status']='FAIL'
   raise AssertionError(f'{name}: {detail}')

 # Shared backends are intentionally duplicated in profile-local native directories
 # for easy extraction; keep the copies byte-identical so they cannot drift.
 ck('v1_v5_native_identical',native_path('v1_balanced').read_bytes()==native_path('v5_hybrid_lowzp').read_bytes())
 ck('v3_v4_native_identical',native_path('v3_reu_512k').read_bytes()==native_path('v4_reu_16m').read_bytes())

 # V1-V4 canonical relocatable source must include the profile-native file.
 for p in FIXED:
  src=(ROOT/'relocatable_source'/p/'math_relocatable.asm').read_text()
  rel=f'../../{p}/resident/vector/native/vec2_normalize_q8_8.asm'
  ck(f'{p}_canonical_include',f'!source "{rel}"' in src,rel)

 # Assemble every native file independently at each selected map, and compare its
 # bytes against the corresponding integrated build. This proves the extracted
 # source is the actual implementation, not documentation-only pseudocode.
 for kind in ('reference','alternate'):
  for p in ALL:
   cfg=config_path(p,kind)
   vals=parse_config(cfg)
   entry=vals['REG_GAME_API']+ENTRY_OFFSET
   src=native_path(p).read_text()
   text=cfg.read_text().rstrip()+f'\n* = REG_GAME_API+${ENTRY_OFFSET:04X}\n'+strip_cpu(src)
   mem,labels,const=Assembler().assemble(text)
   n=ROUTINE_BYTES[p]
   isolated=bytes(mem.get(a,0) for a in range(entry,entry+n))
   bdir=build_dir(p,kind)
   man=json.loads((bdir/'source_build_manifest.json').read_text())
   integrated=load_prg(bdir/man['output_prg'])
   actual=bytes(integrated[entry:entry+n])
   ck(f'{p}_{kind}_isolated_equals_integrated',isolated==actual,
      {'bytes':n,'entry':f'${entry:04X}','isolated_sha256':hashlib.sha256(isolated).hexdigest(),
       'integrated_sha256':hashlib.sha256(actual).hexdigest()})
   prof=out['profiles'].setdefault(p,{'native_source':str(native_path(p).relative_to(ROOT)),
                                      'native_sha256':sha(native_path(p)),'maps':{}})
   prof['maps'][kind]={'entry':f'${entry:04X}','bytes':n,
                       'routine_sha256':hashlib.sha256(isolated).hexdigest()}
 outpath=ROOT/'validation/normalize/NATIVE_SOURCE_VALIDATION.json'
 outpath.parent.mkdir(parents=True,exist_ok=True)
 outpath.write_text(json.dumps(out,indent=2)+'\n')
 print('NORMALIZE NATIVE SOURCE PASS',len(out['checks']),'checks')

if __name__=='__main__':main()
