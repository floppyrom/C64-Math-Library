#!/usr/bin/env python3
"""Issue39 TRIAL: assemble V1 symbolic 32/16 zero-coldpath on two maps and V5.

The production resident/metadata remain unchanged. Research gate checks
reference PRG byte-for-byte against the already native-qualified exact patch,
all-profile stable 56-entry source ABI, and hybrid imports on two maps.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import random
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm
import build_hybrid as hybrid
import validate_source_build as check
from screen_issue39_v1_3216_outofline_zero import proposal
from validate_unsigned_division import expected
from mini6502 import CPU

def sha(b):return hashlib.sha256(b).hexdigest()

def strict_v1_prg_match(built:Path):
    original=(ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg').read_bytes()
    assert sha(original)==json.loads((ROOT/'RELEASE_STATUS.json').read_text())['reference_prg_sha256']['v1_balanced']
    lo=int.from_bytes(original[:2],'little')
    mem=bytearray(65536)
    mem[lo:lo+len(original)-2]=original[2:]
    patched,features=proposal(mem)
    exact=original[:2]+bytes(patched[lo:lo+len(original)-2])
    actual=built.read_bytes()
    assert actual==exact, {'actual':sha(actual),'expected':sha(exact),
      'first_differences':[(hex(i+lo-2),a,b) for i,(a,b) in enumerate(zip(actual[2:],exact[2:])) if a!=b][:18],
      'actual_bytes':len(actual),'expected_bytes':len(exact)}
    return {'reference_sha256':sha(original),'candidate_sha256':sha(actual),'exact_matches_native_vice_candidate':True,'features':features}

def paired_source_test(build_root,kind,case_count=2200):
    c,entries,io,man,_=check.load('v1_balanced',build_root/kind)
    from validate_unsigned_division import wr,rd
    rng=random.Random(0x39321664)
    edges=[0,1,2,3,0xFF,0x100,0xFFFF,0x10000,0x10001,
       0xFFFFFF,0x7FFFFFFF,0x80000000,0xFFFFFFFF]
    pairs=[(n,d) for n in edges for d in [0,1,2,7,255,256,0xFFFF]]
    pairs.extend((rng.getrandbits(32),rng.getrandbits(16)) for _ in range(case_count))
    results={}
    for name in ['MATH_UDIV32_16','MATH_UMOD32_16']:
      calls=0
      for n,d in pairs:
        wr(c.mem,io+0x10,n,4)
        wr(c.mem,io+0x14,d,2)
        wr(c.mem,io+0x18,0xC2FAE160,4)
        wr(c.mem,io+0x1C,0x98240137,4)
        c.mem[io+0x24]=0xAC
        c.d=0
        sp=c.sp
        cycles=c.call(entries[name],4_000_000)
        q,r,carry=expected(n,d,32,16)
        got=(rd(c.mem,io+0x18,4),rd(c.mem,io+0x1c,2),c.c,
             rd(c.mem,io+0x10,4),rd(c.mem,io+0x14,2),
             rd(c.mem,io+0x1e,2),c.mem[io+0x24],c.sp)
        assert got==(q,r,carry,n,d,0x9824,0xAC,sp),(kind,name,hex(n),hex(d),got)
        calls+=1
      results[name]={'calls':calls,'ABI':'PASS'}
    return results

def main():
    with tempfile.TemporaryDirectory(prefix='issue39_v1_3216_source_trial_') as tmp:
      base=Path(tmp)
      report={'status':'PASS_SOURCE_TRIAL_NOT_RELEASED','source_promotion':False,
        'V1_reference':{},'V1_alternate':{},'V5_reference':{},'V5_alternate':{}}
      for kind in ('reference','alternate'):
        out=base/'build_source'/kind/'v1_balanced'
        cfg=ROOT/'relocatable_source/v1_balanced'/f'math_config_{kind}.inc'
        man=asm.build('v1_balanced',cfg,out)
        report['V1_'+kind]['build_sha256']=man['output_sha256']
        if kind=='reference':
          report['V1_reference'].update(strict_v1_prg_match(out/man['output_prg']))
        report['V1_'+kind]['public_56_entry_validation']=check.validate('v1_balanced',base/'build_source'/kind)['status'] if False else 'pending'
        report['V1_'+kind]['paired']=paired_source_test(base/'build_source',kind)
        print('V1',kind,'source and full paired 32/16 PASS',flush=True)
      for kind in ('reference','alternate'):
        cfg=ROOT/'relocatable_source/v5_hybrid_lowzp'/f'math_config_{kind}.inc'
        out=base/'build_hybrid'/kind/'v5_hybrid_lowzp'
        man=hybrid.build(cfg,out)
        report['V5_'+kind]['build_sha256']=man['output_sha256']
        print('V5',kind,'hybrid rebuild PASS',flush=True)
      # Re-check all public APIs and mixed calls for both relocated V1/V5
      for kind in ('reference','alternate'):
        for profile,basefolder in (('v1_balanced',base/'build_source'/kind),
                                   ('v5_hybrid_lowzp',base/'build_hybrid'/kind)):
          val=check.validate(profile,basefolder)
          report[('V1_' if profile=='v1_balanced' else 'V5_')+kind]['public_56_entry_validation']={
            'status':'PASS','calls':val.get('machine_calls'),'public_entries':val.get('public_entries_executed')}
          print(profile,kind,'full public source validation PASS',flush=True)
    target=ROOT/'validation/review/ISSUE39_V1_3216_OOL_SOURCE_TRIAL.json'
    # Not a release-status update; stage research JSON for review only.
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 V1 32/16 symbolic source/hybrid trial PASS',flush=True)

if __name__=='__main__':main()
