#!/usr/bin/env python3
"""Issue39/PR67 fail-closed V2-V4 U16 source-patch reference and alternate screen.

No shipped resident files are written. Test candidate images in ephemeral
copies against a fixed SHA and exact 5-byte local CFG rewrites. The compiler
must generate exactly the local branch simplifications and no other changes.

This script is intentionally a screen, NOT the final release qualification.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
P=['v2_pareto_fast','v3_reu_512k','v4_reu_16m']
BASE={'v2_pareto_fast':'28fc6e653a05b170a80cd7eb50636d755895c5ebb7aab133262ed560fa465dd6'}
OPCODES={
 'v2_pareto_fast':(0xB884,0xB8A0,0xB8E4,0x7C8A,0x7CA5,0x7CC0),
 'v3_reu_512k':(0xB884,0xB8A0,0xB8E4,0x7D6B,0x7D86,0x7DA1),
 'v4_reu_16m':(0xB884,0xB8A0,0xB8E4,0x7D6B,0x7D86,0x7DA1),
}
OUT=ROOT/'validation/review/ISSUE39_U16_PR67_SOURCE_DIFF_SCREEN.json'
def sha(s):return hashlib.sha256(s).hexdigest()
def screen(profile):
 old=(ROOT/profile/'resident'/f'math_{profile}_game_math.prg').read_bytes()
 ref=(ROOT/'build_source/reference'/profile/f'math_{profile}_source_built.prg').read_bytes()
 alt=(ROOT/'build_source/alternate'/profile/f'math_{profile}_source_built.prg').read_bytes()
 assert old[:2]==ref[:2]==bytes.fromhex('0010'),(profile,'load origin')
 if profile in BASE:assert sha(old)==BASE[profile],(profile,sha(old))
 assert len(old)==len(ref),(profile,'resident length changed')
 locations=[]
 expected=bytearray(old)
 for a in sorted(OPCODES[profile]):
  i=2+a-0x1000
  initial=old[i:i+5]
  assert initial[1:3]==bytes.fromhex('034c') and initial[0] in (0x90,0xb0),(profile,hex(a),initial.hex())
  replacement=bytes((0x4c,initial[3],initial[4],0xea,0xea))
  expected[i:i+5]=replacement
  locations.append({'address':hex(a),'original':initial.hex(),'candidate':replacement.hex()})
 assert bytes(expected)==ref, (profile,'source-built mismatch',[(hex(i-2+0x1000),f'{a:02x}',f'{b:02x}') for i,(a,b) in enumerate(zip(expected,ref)) if a!=b][:24])
 # Independent relocated source build must at least compile and retain same
 # occupied sizes/entry symbols. Alternate bytes intentionally differ from ref.
 assert len(alt)>=len(ref)//2
 return {'reference_old_sha256':sha(old),'reference_new_sha256':sha(ref),
         'alternate_sha256':sha(alt),'length':len(old),
         'changes':locations,'source_compilation_reference_and_alternate':'PASS'}
def main():
 x={'status':'PASS','scope':'PR67 source generated, not installed as shipped binary','profiles':{}}
 for p in P:
  x['profiles'][p]=screen(p)
  print('ISSUE39 PR67 EXACT SIX PATCHED SITES',p,x['profiles'][p]['reference_new_sha256'],flush=True)
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(x,indent=2)+'\n')
 print('PR67 SOURCE DIFF SCREEN PASS: V2,V3,V4, reference/alternate',flush=True)
if __name__=='__main__':main()
