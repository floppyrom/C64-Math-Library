#!/usr/bin/env python3
"""Issue39: exact, exhaustive old/new V1 and V5 public UMOD8 guard certificate.

65,536 pairs per profile, two resident versions = 262,144 real 6502 calls.
Provenance uses byte-exact SHA-qualified historic parents, never reinterprets
a later release as an earlier optimization's pre-change image.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from validate_unsigned_division import expected,api
from issue39_umod8_guard_parent import restore_umod8_parent,restore_v5_pr67_u16_parent,PARENT_SHA
from issue39_v1_u16_q2_parent import restore_v1_q2_parent,restore_v5_q2_parent
PROFILES=('v1_balanced','v5_hybrid_lowzp')
OUT=ROOT/'validation/review/ISSUE39_V1V5_UMOD8_GUARD_EXHAUSTIVE.json'
j={'status':'PASS','guard_minimum_divisor':32,'bytes_of_new_code':77,
   'input_cases_per_profile':65536,'paired_public_cpu_calls':0,
   'resource':'REG_LOW+$0E00, no additional normal ZP or stack',
   'profiles':{}}
for profile in PROFILES:
    name=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
    new=name.read_bytes()
    # Historical PR57-62 certificate is pinned to the V5 binary as it was
    # BEFORE independent PR67 16-bit code changes. Reversing those changes
    # is SHA-qualified, and neither affects the UMOD8 operand/cycle path.
    if profile=='v5_hybrid_lowzp':
        new=restore_v5_pr67_u16_parent(restore_v5_q2_parent(new))
    old=restore_umod8_parent(profile,new)
    lo=int.from_bytes(new[:2],'little')
    assert lo==0x1000 and len(new)==len(old)
    assert hashlib.sha256(old).hexdigest()==PARENT_SHA[profile]
    assert new[2+0x3200-lo:2+0x3203-lo]==bytes.fromhex('4c001e')
    assert new[2+0x1e00-lo:2+0x1e05-lo]==bytes.fromhex('ad14c0c920')
    cpus=[]
    for blob in (old,new):
        mem=bytearray(65536);mem[lo:lo+len(blob)-2]=blob[2:]
        cpu=CPU(mem);cpu.d=0;cpu.call(0x3280,2_000_000);cpus.append(cpu)
    results={'cases':0,'faster':0,'equal':0,'slower':0,
             'old_total_cycles':0,'new_total_cycles':0,
             'max_regression_cycles':0,'max_speedup_cycles':0,
             'qualified_d32_faster':0,'qualified_d32_equal':0,'qualified_d32_slower':0,
             'fallback_d_lt32_slower':0,'old_cycle_bytes_sha256':'','new_cycle_bytes_sha256':''}
    hashes=[hashlib.sha256(),hashlib.sha256()]
    entry=api(profile)['MATH_UMOD8']
    for n in range(256):
        for d in range(256):
            obs=[]
            for index,cpu in enumerate(cpus):
                m=cpu.mem;m[0xc010]=n;m[0xc014]=d
                m[0xc011]=0xB5;m[0xc015]=0xA9
                m[0xc018]=0xA6;m[0xc019]=0x5B;m[0xc01A]=0x7C;m[0xc01B]=0xD2
                m[0xc01D]=0x3E;m[0xc01E]=0x4F;m[0xc01F]=0x71
                cycles=cpu.call(entry,100000)
                hashes[index].update(cycles.to_bytes(2,'little'))
                obs.append((cycles,m[0xc01c],cpu.c,
                    tuple(m[0xc018:0xc01c]),tuple(m[0xc01d:0xc020]),
                    tuple(m[0xc010:0xc012]),tuple(m[0xc014:0xc016])))
            _,rem,carry=expected(n,d,8,8)
            want=(rem,carry,(0xA6,0x5B,0x7C,0xD2),(0x3E,0x4F,0x71),
                (n,0xB5),(d,0xA9))
            assert obs[0][1:]==obs[1][1:]==want,(profile,n,d,obs,want)
            dt=obs[1][0]-obs[0][0]
            results['faster' if dt<0 else 'slower' if dt>0 else 'equal']+=1
            results['cases']+=1
            results['old_total_cycles']+=obs[0][0]
            results['new_total_cycles']+=obs[1][0]
            results['max_regression_cycles']=max(dt,results['max_regression_cycles'])
            results['max_speedup_cycles']=max(-dt,results['max_speedup_cycles'])
            if d>=32:
                results['qualified_d32_faster' if dt<0 else 'qualified_d32_slower' if dt>0 else 'qualified_d32_equal']+=1
                assert dt<=0,(profile,n,d,'qualified-operand slowdown',dt)
            else:
                results['fallback_d_lt32_slower']+=dt>0
                assert dt<=14,(profile,n,d,'unacceptable fallback penalty',dt)
    assert results['cases']==65536
    assert results['qualified_d32_faster']+results['qualified_d32_equal']==57344
    assert results['fallback_d_lt32_slower']==8192
    assert results['max_regression_cycles']==14
    assert results['old_total_cycles']=={'v1_balanced':4278528,'v5_hybrid_lowzp':4247988}[profile]
    assert results['new_total_cycles']=={'v1_balanced':3482627,'v5_hybrid_lowzp':3462647}[profile]
    results['old_mean_cycles']=results['old_total_cycles']/65536
    results['new_mean_cycles']=results['new_total_cycles']/65536
    results['old_cycle_bytes_sha256']=hashes[0].hexdigest()
    results['new_cycle_bytes_sha256']=hashes[1].hexdigest()
    results['old_resident_sha256']=hashlib.sha256(old).hexdigest()
    results['new_resident_sha256']=hashlib.sha256(new).hexdigest()
    j['profiles'][profile]=results;j['paired_public_cpu_calls']+=131072
    print('UMOD8 guarded',profile,'old',results['old_mean_cycles'],
          'new',results['new_mean_cycles'],'fast/equal/slow',
          results['faster'],results['equal'],results['slower'],flush=True)
assert j['paired_public_cpu_calls']==262144
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
print('ISSUE39 V1/V5 UMOD8 EXHAUSTIVE PAIRED PASS',j['paired_public_cpu_calls'])
