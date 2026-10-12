#!/usr/bin/env python3
"""Issue39: V2-V5 existing-size 16-bit D-high cutoff sweep, research only.

Runs exact current resident images with one CPX immediate edited in memory.
Includes full public Q/R/C, unchanged N/D and SP, class-specific cycle vectors.
"""
from pathlib import Path
import argparse, hashlib, json, random, sys
from collections import defaultdict
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from validate_unsigned_division import load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus
PROFILES=('v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV16','MATH_UMOD16')
MARKER=bytes.fromhex('ae15c0e00fb0')
THRESHOLDS=(1,2,4,8,10,12,13,14,15,16,18,20,24,32,48,64,96)
N,D,Q,REM=0xc010,0xc014,0xc018,0xc01c

def pairs(op):
 rng=random.Random(0x39B116 if op=='MATH_UDIV16' else 0x39B117)
 canonical=corpus(op,16,16,0,2048 if op=='MATH_UDIV16' else 1024)[1]
 out=[(n,d,'canonical_'+kind) for n,d,kind in canonical]
 for lo,hi in ((2,9),(10,31),(32,255)):
  for _ in range(256):
   q=rng.randrange(lo,hi+1)
   d=rng.randrange(1,min(8192,65535//q)+1)
   remainder=rng.randrange(min(d,65536-q*d))
   out.append((q*d+remainder,d,'quotient_'+str(lo)+'_'+str(hi)))
 out += [(rng.randrange(65536),rng.randrange(65536),'uniform') for _ in range(384)]
 out += [(rng.randrange(65536),rng.randrange(1,256),'divisor8') for _ in range(256)]
 out += [(rng.randrange(65536),0,'divide_zero') for _ in range(64)]
 assert all(0<=n<65536 and 0<=d<65536 for n,d,_ in out)
 return out

def sample(c,entry,n,d,op):
 m=c.mem;wr(m,N,n,2);wr(m,D,d,2)
 wr(m,Q,0xa55a,2);wr(m,REM,0x5aa5,2)
 sp=c.sp;c.d=0
 ticks=c.call(entry,3000000)
 eq,er,ec=expected(n,d,16,16)
 got=(rd(m,Q,2),rd(m,REM,2),c.c)
 assert (got==(eq,er,ec) if op=='MATH_UDIV16' else got[1:]==(er,ec))
 assert rd(m,N,2)==n and rd(m,D,2)==d and c.sp==sp
 return ticks,got

def main():
 arg=argparse.ArgumentParser();arg.add_argument('--out',type=Path);args=arg.parse_args()
 release=json.loads((R/'RELEASE_STATUS.json').read_text())
 report={'status':'PASS','scope':'research-only no stable source/PRG changes',
  'patch':'LDX D+1; CPX #imm; BCS threshold; exact single opcode operand',
  'thresholds':THRESHOLDS,'profiles':{},'correctness_rejections':[],
  'publication_decision':'no promotion from a single weighted mean'}
 for profile in PROFILES:
  binary=R/profile/'resident'/('math_'+profile+'_game_math.prg')
  h=hashlib.sha256(binary.read_bytes()).hexdigest()
  assert h==release['reference_prg_sha256'][profile]
  original,entries=load(profile)
  hits=[x for x in range(0xb000,0xc000) if original.mem[x:x+6]==MARKER]
  assert hits==[0xb8eb],(profile,hits)
  operand=hits[0]+4
  assert original.mem[operand]==15
  info={'resident_sha256':h,'cutoff_operand_address':hex(operand),
        'original_cutoff':15,'operations':{}}
  for op in OPS:
   vec=pairs(op)
   fingerprint=hashlib.sha256(''.join(f'{n:04x}:{d:04x}:{k}\n' for n,d,k in vec).encode()).hexdigest()
   baseline=[sample(original,entries[op],n,d,op) for n,d,k in vec]
   rows=[]
   for cutoff in THRESHOLDS:
    candidate,ce=load(profile);candidate.mem[operand]=cutoff
    total=oldtotal=faster=slower=equal=0
    classes=defaultdict(lambda:[0,0,0])
    invalid=None
    for i,(n,d,k) in enumerate(vec):
     try:tick,value=sample(candidate,ce[op],n,d,op)
     except Exception as exc:
      invalid={'index':i,'n':n,'d':d,'class':k,'error':str(exc)[:130]};break
     previous,oldval=baseline[i]
     if value!=oldval:
      invalid={'index':i,'n':n,'d':d,'class':k,'error':'Q/R/C differs from current'};
      break
     total+=tick;oldtotal+=previous
     faster+=tick<previous;slower+=tick>previous;equal+=tick==previous
     x=classes[k];x[0]+=tick;x[1]+=previous;x[2]+=1
    if invalid:
     report['correctness_rejections'].append({'profile':profile,'op':op,'threshold':cutoff,**invalid})
     rows.append({'threshold':cutoff,'status':'REJECT_CORRECTNESS','first_failure':invalid})
    else:
     rows.append({'threshold':cutoff,'status':'PASS','cases':len(vec),
      'before_mean':oldtotal/len(vec),'after_mean':total/len(vec),
      'mean_delta':(total-oldtotal)/len(vec),'faster':faster,'slower':slower,'equal':equal,
      'classes':{k:{'cases':v[2],'before_mean':v[1]/v[2],
                    'after_mean':v[0]/v[2]} for k,v in classes.items()}})
    print(profile,op,'Dhi',cutoff,rows[-1]['status'],
          round(rows[-1].get('mean_delta',0),6),flush=True)
   originalrow=next(x for x in rows if x['threshold']==15)
   assert originalrow['status']=='PASS' and originalrow['slower']==originalrow['faster']==0
   info['operations'][op]={'cases':len(vec),'corpus_sha256':fingerprint,
                            'threshold_results':rows}
  report['profiles'][profile]=info
 if args.out:
  args.out.parent.mkdir(parents=True,exist_ok=True)
  args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 16-BIT D1 DISPATCH SWEEP PASS: profiles',len(report['profiles']),
       'rejected combinations',len(report['correctness_rejections']),flush=True)
if __name__=='__main__':main()
