#!/usr/bin/env python3
"""Real x64sc native 5-profile SEEK16_INIT accumulator-inline research check.

Runs original and separately placed source-assembled alternative, with the
public SEEK16 INIT JMP redirected only in disposable emulator memory. All
normal SEEK8, stepper, reference PRGs and REUs remain byte-identical.
Actual frame states/C/X/SP and reference movement are checked via VICE.
"""
from __future__ import annotations
import hashlib,json,os,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import native_issue39_seek_all_modes as native
from issue144_seek16_accum_all_profiles_v2 import make,CONF
from validate_unsigned_division import PROFILES

SPEEDS=(0x0100,0x0180,0x0200,0x0300,0x0400,0x8100,0x8400)
SCENARIOS=tuple((16,'step',s) for s in SPEEDS)
OUT='validation/review/ISSUE144_SEEK16_ACCUM_NATIVE_VICE.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 vice=os.getenv('VICE_WRAPPER','x64sc')
 orig_get=native.resident;orig_make=native.build_code;orig_scenarios=native.SCENARIOS
 report={'status':'PASS_NATIVE_VICE_SEEK16_INIT_SOURCE_RELOCATED_FIVE_PROFILES','profiles':{},'total_original_plus_candidate_public_init_calls':0,
  'native_real_cycle_measurement':False,'regular_prgs_reu_unchanged':True,'mixed_normal_stepper_calls':True}
 status=json.loads((R/'RELEASE_STATUS.json').read_text())
 try:
  native.SCENARIOS=SCENARIOS
  with tempfile.TemporaryDirectory(prefix='issue144_seek16_accum_vicenative_') as directory:
   tmp=Path(directory)
   for pi,p in enumerate(PROFILES):
    src,code,labels=make(p)
    raw=orig_get(p)
    assert sha(raw)==status['reference_prg_sha256'][p]
    std,_,_ = native.native(p,21300+pi*2,tmp,vice)
    before=native.verify(p,std)
    resident=bytearray(raw)
    init=native.api(p)['MATH_SEEK16_INIT']
    at=init-0x1000+2
    assert resident[at]==0x4C
    expected=int(CONF[p]['start'],16)
    assert int.from_bytes(resident[at+1:at+3],'little')==expected
    resident[at+1:at+3]=(0x0D00).to_bytes(2,'little')
    def extended(api):
     original,stop=orig_make(api)
     padding=0x0D00-(native.ENTRY+len(original))
     assert padding>=0,(p,padding)
     body=bytearray(original)+bytes(padding)
     body.extend(bytes(code.get(pos,0) for pos in range(0x0D00,max(code)+1)))
     assert native.ENTRY+len(body)<0x1000
     return bytes(body),stop
    native.resident=lambda profile:bytes(resident)
    native.build_code=extended
    try: optimized,_,_=native.native(p,21301+pi*2,tmp,vice)
    finally:
     native.resident=orig_get
     native.build_code=orig_make
    after=native.verify(p,optimized)
    assert std==optimized,(p,'native original and alternative frame,status,X,SP differ')
    assert before['sp_after_return']==after['sp_after_return']
    assert before['step_calls']==after['step_calls']==len(SCENARIOS)*native.FRAMES
    report['profiles'][p]={'status':'PASS_REU_NATIVE_FRAME_STATUS_X_STACK_IDENTICAL',
      'original_init_calls':len(SCENARIOS),'candidate_init_calls':len(SCENARIOS),
      'source_sha256':sha(src.encode()),'resident_image_unmodified':True,
      'native_step_calls_each':before['step_calls'],'frame_dump_sha256':sha(optimized)}
    report['total_original_plus_candidate_public_init_calls']+=2*len(SCENARIOS)
    print('NATIVE SEEK16 ACCUM',p,'PASS',len(SCENARIOS)*2,'INIT and',len(SCENARIOS)*native.FRAMES*2,'STEP',flush=True)
 finally:
  native.resident=orig_get;native.build_code=orig_make;native.SCENARIOS=orig_scenarios
 assert report['total_original_plus_candidate_public_init_calls']==len(PROFILES)*2*len(SCENARIOS)
 path=R/OUT;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('ISSUE144 SEEK16 ALL PROFILE NATIVE PASS',report['total_original_plus_candidate_public_init_calls'])
if __name__=='__main__':main()
