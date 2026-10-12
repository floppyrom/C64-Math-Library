#!/usr/bin/env python3
"""Issue39: exact-public 32/16 N16 + D-high-gated reuse of the resident 16/16 core.

Does NOT alter shipped image: a temporary 33-byte CPU emulator overlay in
$E100 (under usual C64 KERNAL mapping). Candidate must be relocated into
proven writable executable RAM and natively qualified before any promotion.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load
from screen_issue39_u3216_n16_delegate import inputs,sample,OPS,OVERLAY
THRESHOLDS=(1,4,16,64)
SOURCE="""* = $E100
N16_DHI_GATE:
    lda $C012
    ora $C013
    bne ORIGINAL
    lda $C015
    cmp #$%02X
    bcc ORIGINAL
    jsr $3140
    lda #0
    sta $C01A
    sta $C01B
    rts
ORIGINAL:
    lda $C010
    jmp $31B3
"""
def make(t):
    code,labels,_=Assembler().assemble(SOURCE%t)
    assert len(code)==33 and labels['N16_DHI_GATE']==OVERLAY
    return code
def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path);args=a.parse_args()
    state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    r={'status':'PASS_RESEARCH_ONLY','source':'tools/screen_issue39_u3216_divisor_gated.py',
       'resident_changed':False,'research_under_kernal_rom_not_natively_qualified':True,
       'thresholds_d1_min':list(THRESHOLDS),'code_bytes':33,
       'normal_zp_growth':0,'additional_nested_jsr_stack_bytes':2,
       'pairwise_tests':0,'complete_resident_cpu_calls':0,
       'arithmetic_or_abi_errors':0,'profiles':{}}
    for profile in PROFILES:
        p=ROOT/profile/'resident'/('math_'+profile+'_game_math.prg')
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        assert state['reference_prg_sha256'][profile]==h
        original,entries=load(profile)
        new={}
        for limit in THRESHOLDS:
            c,ce=load(profile)
            assert ce==entries and bytes(c.mem[0x31b0:0x31b3])==bytes.fromhex('ad10c0')
            asm=make(limit)
            assert all(c.mem[pc]==0 for pc in asm)
            c.mem[0x31b0:0x31b3]=bytes((0x4c,0x00,0xe1))
            for pc,v in asm.items():c.mem[pc]=v
            new[limit]=c
        item={'resident_sha256':h,'operations':{}}
        for op in OPS:
            assert entries[op] in (0x31b0,0x3226)
            item['operations'][op]={}
            for group,vec in inputs(op).items():
                datasets={limit:[] for limit in THRESHOLDS}
                groups={limit:defaultdict(list) for limit in THRESHOLDS}
                hashinputs=hashlib.sha256()
                for n,d in vec:
                    hashinputs.update(n.to_bytes(4,'little')+d.to_bytes(2,'little'))
                    oldtick,oldout=sample(original,entries[op],n,d)
                    r['complete_resident_cpu_calls']+=1
                    for limit in THRESHOLDS:
                        tick,out=sample(new[limit],entries[op],n,d)
                        r['complete_resident_cpu_calls']+=1
                        assert out==oldout,(profile,op,limit,n,d,'public state mismatch',out,oldout)
                        diff=tick-oldtick
                        datasets[limit].append(diff)
                        kind='N16_D8' if n<=0xffff and 0<d<256 else ('N16_DHI' if n<=0xffff and d>=256 else ('N16_D0' if n<=0xffff else 'N_wide'))
                        groups[limit][kind].append(diff)
                    r['pairwise_tests']+=1
                bythreshold={}
                for limit,x in datasets.items():
                    bythreshold[str(limit)]={'cases':len(x),
                      'mean_delta':sum(x)/len(x),'faster':sum(v<0 for v in x),
                      'slower':sum(v>0 for v in x),'equal':sum(v==0 for v in x),
                      'max_regression':max(x),'max_speedup':-min(x),
                      'groups':{k:{'cases':len(v),'mean_delta':sum(v)/len(v),
                        'faster':sum(t<0 for t in v),'slower':sum(t>0 for t in v)} for k,v in groups[limit].items()}}
                item['operations'][op][group]={'cases':len(vec),'input_sha256':hashinputs.hexdigest(),'thresholds':bythreshold}
                print(profile,op,group,' '.join('Dhi>='+str(limit)+' '+str(round(bythreshold[str(limit)]['mean_delta'],3)) for limit in THRESHOLDS),flush=True)
        r['profiles'][profile]=item
    assert r['pairwise_tests']==79130 and r['complete_resident_cpu_calls']==79130*(len(THRESHOLDS)+1)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print('ISSUE39 U3216 DHI-GATED PUBLIC SCREEN PASS',r['complete_resident_cpu_calls'],flush=True)
if __name__=='__main__':main()
