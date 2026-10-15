#!/usr/bin/env python3
"""Issue144 all-input 22-byte UDIV32_16/UMOD32_16 narrow-N workload screen.

FIVE workload mixtures, same-input baseline vs candidate. A/X/Y and
N/Z/V are volatile in published ABI and explicitly tracked rather than
falsely claimed equal. Q32/R16/C/input/SP must be identical.
"""
import random,statistics,hashlib,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd,edge,expected
S=(ROOT/'optional/issue144_u32_16_narrow_guard/guard.asm').read_text()
CODE,LABELS,_=Assembler().assemble(S)
RANGE=len(CODE)
assert RANGE==22 and LABELS['MATH_UDIV32_16_NARROW_GUARDED']==0x0C80
def digest(v):return hashlib.sha256(v).hexdigest()
def cycles_stat(v):
 a=sorted(v)
 return {'mean':sum(v)/len(v),'median':statistics.median(v),'p95':a[int(.95*(len(a)-1))], 'min':a[0], 'max':a[-1], 'cycle_vector_sha256':digest(b''.join(int(x).to_bytes(4,'little',signed=True) for x in v))}

def suite(which):
 r=random.Random(0x144D100+['uniform','small10pct','small50pct','small100pct','q0q1'].index(which))
 for i in range(256):
  if which=='uniform':n=r.getrandbits(32)
  elif which=='small100pct':n=r.getrandbits(16)
  elif which=='small10pct':n=r.getrandbits(16) if i%10==0 else r.getrandbits(32)
  elif which=='small50pct':n=r.getrandbits(16) if i%2==0 else r.getrandbits(32)
  elif which=='q0q1': n=r.getrandbits(16)
  d=r.getrandbits(16) if i%11 else 0
  if which=='q0q1' and d:n=r.randrange(min(65536,2*d))
  yield n,d

def run_profile(profile):
 c,api=load(profile);alt,_=load(profile)
 for pos,value in CODE.items():
  assert alt.mem[pos]==0,(profile,hex(pos));alt.mem[pos]=value
 report={}
 for op in ('MATH_UDIV32_16','MATH_UMOD32_16'):
  report[op]={}
  for kind in ['uniform','small10pct','small50pct','small100pct','q0q1']:
   baseline=[];candidate=[];volatile_register_diffs=0;volatile_flag_diffs=0
   for n,d in suite(kind):
    for cpu in (c,alt):
     wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,2)
     wr(cpu.mem,0xC018,0xEF112233,4);wr(cpu.mem,0xC01C,0xCEFA,2)
     cpu.x=0x5A;cpu.y=0xCC;cpu.c=1;cpu.d=0
    old_sp,new_sp=c.sp,alt.sp
    a=c.call(api[op],4000000)
    b=alt.call(LABELS['MATH_UDIV32_16_NARROW_GUARDED'],4000000)
    q,r,carry=expected(n,d,32,16)
    v0=(rd(c.mem,0xC018,4),rd(c.mem,0xC01C,2),c.c)
    v1=(rd(alt.mem,0xC018,4),rd(alt.mem,0xC01C,2),alt.c)
    assert v0==v1==(q,r,carry),(profile,op,kind,n,d,v0,v1)
    assert rd(alt.mem,0xC010,4)==n and rd(alt.mem,0xC014,2)==d
    assert (c.sp,alt.sp)==(old_sp,new_sp)
    assert (c.d,alt.d)==(0,0)
    volatile_register_diffs+=(c.x,c.y)!=(alt.x,alt.y)
    volatile_flag_diffs+=(c.n,c.v,c.z)!=(alt.n,alt.v,alt.z)
    baseline.append(a);candidate.append(b)
   paired=[a-b for a,b in zip(baseline,candidate)]
   report[op][kind]={"cases":len(baseline),"stock_mean":sum(baseline)/len(baseline),"optional_mean":sum(candidate)/len(candidate),"saved_mean":sum(paired)/len(paired),"saved_min":min(paired),"saved_max":max(paired),"baseline_cycles":cycles_stat(baseline),"candidate_cycles":cycles_stat(candidate),"paired_savings_cycles":cycles_stat(paired),"corpus_sha256":digest(b''.join(n.to_bytes(4,'little')+d.to_bytes(2,'little') for n,d in suite(kind))),"volatile_xy_differ":volatile_register_diffs,"volatile_nzv_differ":volatile_flag_diffs}
 print(profile,{op:{name:round(row['saved_mean'],2) for name,row in work.items()} for op,work in report.items()},flush=True)
 return report

if __name__=='__main__':
 result={p:run_profile(p) for p in PROFILES}
 dest=ROOT/'validation/review/ISSUE144_U32DIV32_16_NARROW_N_RESEARCH.json'
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps({'status':'PASS_FULL_QR_C_ALL_PROFILES_WORKLOAD_DEPENDENT','code_bytes':RANGE,'source_sha256':digest(S.encode()),'same_input_cases_per_api_profile':1280,'paired_cpu_calls':12800,'baseline_and_candidate_cpu_calls':25600,'full_uniform_regression':14,'public_A_X_Y_NZV_are_volatile':True,'profiles':result},indent=2)+'\n')
 print('SOURCE BYTES',RANGE)
