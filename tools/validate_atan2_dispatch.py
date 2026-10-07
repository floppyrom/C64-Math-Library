#!/usr/bin/env python3
"""Exhaustively verify installed ATAN2 branch ordering in both memory maps."""
from pathlib import Path
import hashlib,json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'routines/atan2'))
from validate_smul24_directout import PROFILES,KINDS,load
from tables import exact_phase,phase_error,signed8

def main():
    # The unchanged original compact kernel is the exact-output compatibility
    # oracle. Its full-domain output digest was independently certified earlier.
    prior=json.loads((ROOT/'validation/ATAN2_OPTIMIZATION_VALIDATION.json').read_text())
    reference_hash=next(x['outputs_sha256'] for x in prior['checks'] if x['kernel']=='compact')
    results={}
    for profile in PROFILES:
        results[profile]={}
        vectors=[]
        for kind in KINDS:
            cpu,api=load(profile,kind)
            xaddr,yaddr,zaddr=(api[x] for x in ('MATH_X','MATH_Y','MATH_Z'))
            out=bytearray();cycles=[];max_error=0
            for x in range(256):
                for y in range(256):
                    cpu.mem[xaddr]=x;cpu.mem[yaddr]=y;cpu.mem[zaddr]=0xa5
                    cpu.c=(x^y)&1
                    cy=cpu.call(api['MATH_ATAN2_8'])
                    got=cpu.mem[zaddr]
                    error=phase_error(got,exact_phase(signed8(x),signed8(y)))
                    assert error<=(0 if profile=='v4_reu_16m' else 1),(profile,kind,x,y,error)
                    assert cpu.c==0 and cpu.sp==0xfd,(profile,kind,x,y,'flags/stack')
                    assert cpu.mem[xaddr]==x and cpu.mem[yaddr]==y,(profile,kind,x,y,'inputs')
                    if profile!='v4_reu_16m':assert cpu.a==got
                    out.append(got);cycles.append(cy);max_error=max(max_error,error)
            digest=hashlib.sha256(out).hexdigest()
            if profile!='v4_reu_16m':assert digest==reference_hash,(profile,kind,'output parity')
            row={'cases':len(cycles),'mean_cycles':sum(cycles)/len(cycles),
                 'min_cycles':min(cycles),'max_cycles':max(cycles),
                 'outputs_sha256':digest,'max_phase_error':max_error,
                 'input_or_carry_or_stack_failures':0}
            results[profile][kind]=row;vectors.append(cycles)
            print(profile,kind,'ATAN2 PASS',row['mean_cycles'],flush=True)
        assert vectors[0]==vectors[1],(profile,'relocation cycle parity')
    path=ROOT/'validation/ATAN2_DISPATCH_VALIDATION.json'
    path.write_text(json.dumps({'status':'PASS','date':'2026-10-06',
        'basis':'all 65536 signed-byte vectors per profile/map; public entry through RTS, excluding caller JSR/input stores',
        'machine_calls':65536*len(PROFILES)*len(KINDS),'results':results},indent=2)+'\n')

if __name__=='__main__':main()
