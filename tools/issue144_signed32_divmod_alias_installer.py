#!/usr/bin/env python3
"""Generate and execute source-assembled reversible JMP-tail patchers, signed 32/16.

Original JMP-only chains differ across V1..V5. No bypass of V1's
JSR-dependent normalization and no pointless patch in already direct V5.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_signed_division import PROFILES,load_profile
from issue144_signed_divmod_alias_direct_research import API,EXPECTED_CHAINS,vectors,execute
SRC='optional/issue144_signed32_divmod_direct_jump'
OUT='validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_INSTALLER.json'

def prepare(p):
 cpu,api=load_profile(p)
 patch={}
 for op,(target,cycles) in EXPECTED_CHAINS[p].items():
  if not cycles:continue
  addr=api[op]
  assert cpu.mem[addr]==0x4C and target!=int.from_bytes(cpu.mem[addr+1:addr+3],'little')
  patch[addr+1]=(cpu.mem[addr+1],target&255)
  patch[addr+2]=(cpu.mem[addr+2],target>>8)
 if not patch:return None
 lines=['; Issue144 signed S32/16 public alias JMP-chain opt-in, '+p,
 '; Only JMP OPERAND BYTES are changed; no normal 6510 register or ZP budget.',
 '; Invalid during live/concurrent divmod calls or when code is not RAM writable.',
 '; Example loader-owned installer RAM $0C80; move if occupied.',
 '; Source qualifies with the exactly matching stock resident binary.',
 '!cpu 6510','* = $0C80','DIRECT_S32_16_ENABLE:']
 for addr,(_,after) in sorted(patch.items()):
  lines.extend([f'  lda #${after:02X}',f'  sta ${addr:04X}'])
 lines+=['  rts','DIRECT_S32_16_DISABLE:']
 for addr,(before,_) in sorted(patch.items()):
  lines.extend([f'  lda #${before:02X}',f'  sta ${addr:04X}'])
 lines+=['  rts','']
 source='\n'.join(lines)
 code,labels,_=Assembler().assemble(source)
 assert labels['DIRECT_S32_16_ENABLE']==0x0C80
 assert len(code)<75 and max(code)<0x0D00
 return source,code,labels,patch

def main():
 outcome={'status':'PASS_S32_16_REAL_6510_SOURCE_BEGIN_END','profiles':{},
          'normal_resident_prg_unchanged':True,'install_requires_exclusive_patch_transition':True}
 pairs=vectors()[:180]
 for profile in PROFILES:
  prepared=prepare(profile)
  if prepared is None:
   outcome['profiles'][profile]={'already_direct':True,'changed_bytes':0,'expected_cycle_gain':0}
   print('S32/16 INSTALL',profile,'already optimized no-op PASS',flush=True)
   continue
  src,code,labels,patch=prepared
  dest=ROOT/SRC/(profile+'.asm');dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(src)
  old,api=load_profile(profile);candidate,api2=load_profile(profile)
  assert api==api2
  for addr,b in code.items():
   assert candidate.mem[addr]==0,(profile,hex(addr))
   candidate.mem[addr]=b
  before_x,before_y,sp=candidate.x,candidate.y,candidate.sp
  enabled=candidate.call(labels['DIRECT_S32_16_ENABLE'],200000)
  assert candidate.sp==sp and candidate.x==before_x and candidate.y==before_y
  assert all(candidate.mem[addr]==after for addr,(_,after) in patch.items())
  for n,d in pairs:
   for op in API:
    a,states=execute(old,api[op],n,d)
    b,state2=execute(candidate,api[op],n,d)
    assert states==state2
    assert a-b==EXPECTED_CHAINS[profile][op][1],(profile,op,a,b)
  disabled=candidate.call(labels['DIRECT_S32_16_DISABLE'],200000)
  assert all(candidate.mem[addr]==before for addr,(before,_) in patch.items())
  for n,d in pairs[:36]:
   for op in API:
    a,oa=execute(old,api[op],n,d)
    b,ob=execute(candidate,api[op],n,d)
    assert oa==ob and a==b
  outcome['profiles'][profile]={'status':'PASS_6510_BEGIN_END_FULL_ABI_RESTORED',
    'code_bytes':len(code),'changed_operand_bytes':len(patch),
    'enable_cycles':enabled,'disable_cycles':disabled,
    'source_sha256':hashlib.sha256(src.encode()).hexdigest(),
    'probed_pairs_per_api_while_enabled':len(pairs),
    'restored_original_signed_divmod':True,
    'affected_public_entries':[k for k in API if EXPECTED_CHAINS[profile][k][1]>0]}
  print('S32/16 INSTALL',profile,'code bytes',len(code),'enable/disable cycles',enabled,disabled,'PASS',flush=True)
 out=ROOT/OUT;out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(outcome,indent=2,sort_keys=True)+'\n')
 print('ALL',outcome['status'])
if __name__=='__main__':main()
