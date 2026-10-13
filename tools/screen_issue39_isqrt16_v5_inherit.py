#!/usr/bin/env python3
"""ISQRT16/32 public V5 hybrid inheritance source-integrity trial.

Rebuilds V5 from the currently installed experimental V1 root overlay (via
build_hybrid.build which reassembles canonical V1 and V2), checks both maps,
and compares public root inputs, flags, registers and sentinels. Never ships.
"""
from pathlib import Path
import argparse,hashlib,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_hybrid as hybrid
import validate_source_build as check
from validate_unsigned_division import load as load_shipped
from screen_issue39_isqrt16_inplace_source import sample
from screen_issue39_isqrt16_seed_square import samples16,samples32
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);arg=ap.parse_args()
    original,entries=load_shipped('v5_hybrid_lowzp')
    report={'status':'PASS_SOURCE_ONLY_V5_RESEARCH','native_vice_calls':0,
      'source_published':False,'maps':{},'ABI':'MATH_ISQRT16/ISQRT32'}
    n16=samples16(2048);n32=samples32(768)
    with tempfile.TemporaryDirectory(prefix='issue39_root_v5_') as td:
        for mode in ('reference','alternate'):
            cfg=ROOT/'relocatable_source/v5_hybrid_lowzp'/('math_config_'+mode+'.inc')
            out=Path(td)/mode/'v5_hybrid_lowzp'
            m=hybrid.build(cfg,out)
            cand,pub,io,man,_=check.load('v5_hybrid_lowzp',Path(td)/mode)
            op16=pub['MATH_ISQRT16'];op32=pub['MATH_ISQRT32']
            row={'sha256':m['output_sha256'],'entries_unchanged':True,
                 'public16_cases':len(n16),'public32_cases':len(n32)}
            for key,values,oldentry,newentry,width in [
                ('ISQRT16',n16,entries['MATH_ISQRT16'],op16,16),
                ('ISQRT32',n32,entries['MATH_ISQRT32'],op32,32)]:
                oldcycles=newcycles=0
                for n in values:
                    new,outcome=sample(cand,newentry,n,width,io)
                    baseline,oldout=sample(original,oldentry,n,width,0xc000)
                    assert oldout==outcome,(mode,key,hex(n),'old/new mismatch')
                    oldcycles+=baseline;newcycles+=new
                row[key+'_old_mean']=oldcycles/len(values)
                row[key+'_candidate_mean']=newcycles/len(values)
                row[key+'_delta']=(newcycles-oldcycles)/len(values)
                print('V5',mode,key,'delta',round(row[key+'_delta'],3),flush=True)
            report['maps'][mode]=row
    if arg.out:
        arg.out.parent.mkdir(parents=True,exist_ok=True)
        arg.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISQRT16/32 V5 HYBRID SOURCE-REBUILD INHERITANCE PASS',flush=True)
if __name__=='__main__':main()
