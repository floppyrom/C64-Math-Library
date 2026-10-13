#!/usr/bin/env python3
"""Root RAM placement reconnaissance: initialized resident bytes only.

Zero-filled pages are provisional slack, NOT proof of source ownership.
"""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import PROFILES,load
PAGES=tuple(range(0x6000,0x9c00,0x100))
def main():
    out={'status':'PASS_RESEARCH_ONLY','pages':{},'source_ownership_verified':False,'profiles':{}}
    state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    for p in PROFILES:
        cpu,_=load(p)
        path=ROOT/p/'resident'/('math_'+p+'_game_math.prg')
        h=hashlib.sha256(path.read_bytes()).hexdigest()
        assert h==state['reference_prg_sha256'][p]
        out['profiles'][p]={}
        for pc in PAGES:
            key='$'+format(pc,'04X')
            data=bytes(cpu.mem[pc:pc+256])
            out['profiles'][p][key]={
              'all_zero_after_init':not any(data),
              'nonzero_bytes':sum(v!=0 for v in data),
              'sha256':hashlib.sha256(data).hexdigest()}
    out['common_zero_after_init']=['$'+format(pc,'04X') for pc in PAGES
       if all(out['profiles'][p]['$'+format(pc,'04X')]['all_zero_after_init'] for p in PROFILES)]
    print('ROOT TABLE/CODE COMMON ZERO PAGES',out['common_zero_after_init'])
    for profile in PROFILES:
        print('ROOT PAGES',profile,[p for p,v in out['profiles'][profile].items() if v['all_zero_after_init']])
    dst=ROOT/'validation/review/ISSUE39_ROOT_PLACEMENT_SCAN.json'
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
