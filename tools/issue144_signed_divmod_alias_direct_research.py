#!/usr/bin/env python3
"""Unrestricted S32/16 DIV/MOD signed alias direct-tail zero-RAM optimization.

Patch four operand bytes of the original two public JMPs; all signs, including
signed overflow and denominator 0, follow the stock signed producer at $9200.
No extra code, zero-page or LUT; one less JMP for SDIV32_16, two for SMOD32_16.
"""
from __future__ import annotations
import hashlib,json,random,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_signed_division import PROFILES,load_profile,div_expected,wr,rd,edge
API=('MATH_SDIV32_16','MATH_SMOD32_16')
# Profile-specific JMP chains: do not bypass executable normalization (V1).
EXPECTED_CHAINS={
 'v1_balanced': {'MATH_SDIV32_16':(0x2590,0),'MATH_SMOD32_16':(0x2590,3)},
 'v2_pareto_fast': {'MATH_SDIV32_16':(0x9200,3),'MATH_SMOD32_16':(0x9200,6)},
 'v3_reu_512k': {'MATH_SDIV32_16':(0x9200,3),'MATH_SMOD32_16':(0x9200,6)},
 'v4_reu_16m': {'MATH_SDIV32_16':(0x9200,3),'MATH_SMOD32_16':(0x9200,6)},
 'v5_hybrid_lowzp': {'MATH_SDIV32_16':(0x5D00,0),'MATH_SMOD32_16':(0x5D00,0)},
}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def stat(v):
 a=sorted(v)
 return {'mean':sum(v)/len(v),'median':statistics.median(v),'p95':a[int((len(v)-1)*.95)],'min':a[0],'max':a[-1],
         'cycle_vector_sha256':sha(b''.join(int(x).to_bytes(4,'little',signed=True) for x in v))}
def vectors():
 e1=edge(32);e2=edge(16)
 rng=random.Random(0x14432160)
 v=[(n,d) for n in e1 for d in e2]
 v += [(rng.getrandbits(32),rng.getrandbits(16)) for _ in range(2500)]
 v += [(rng.getrandbits(32),0) for _ in range(128)]
 v += [(rng.getrandbits(16),rng.getrandbits(16)) for _ in range(250)]
 v += [((d+v)&0xffffffff,d) for d in [1,2,3,255,256,32767,32768,65535] for v in (-2,-1,0,1,2)]
 return v

def execute(cpu,entry,n,d):
 m=cpu.mem;wr(m,0xc010,n,4);wr(m,0xc014,d,2)
 wr(m,0xc018,0xaabbccdd,4);wr(m,0xc01c,0xbcbc,2)
 m[0xc017]=0x57;m[0xc01e]=0xe2
 cpu.c=1;cpu.d=0;cpu.x=0x76;cpu.y=0x39
 sp=cpu.sp
 cycles=cpu.call(entry,4000000)
 return cycles,(rd(m,0xc018,4),rd(m,0xc01c,2),cpu.c,rd(m,0xc010,4),rd(m,0xc014,2),cpu.sp,
                 cpu.x,cpu.y,m[0xc017],m[0xc01e],cpu.d)

def main():
 inp=vectors(); digest=sha(b''.join(n.to_bytes(4,'little')+d.to_bytes(2,'little') for n,d in inp))
 report={'status':'PASS_ZERO_EXTRA_RAM_SIGNED32_16_ALIAS_HOPS','same_input_pairs_per_op':len(inp),
 'public_calls_model':len(inp)*len(PROFILES)*2*2,'operand_sha256':digest,
 'original_core_at':'$9200','only_code_bytes_modified_by_profile':{'v1_balanced':2,'v2_pareto_fast':4,'v3_reu_512k':4,'v4_reu_16m':4,'v5_hybrid_lowzp':0},
 'default_binary_files_changed':False,'native_vice_not_measured':True,'profiles':{}}
 for p in PROFILES:
  baseline,api=load_profile(p);alternate,api2=load_profile(p);assert api==api2
  chain=EXPECTED_CHAINS[p]
  assert alternate.mem[0x3EE0]==alternate.mem[0x3FDD]==0x4C
  # Walk only true JMP instructions; V1's $2590 starts JSR (side effects!),
  # and V5 is already one hop away from its actual producer.
  for op in API:
   addr=api[op]; dest=addr; jumps=0
   while baseline.mem[dest]==0x4c:
    dest=baseline.mem[dest+1]|baseline.mem[dest+2]<<8
    jumps+=1
    assert jumps<5
   final,expected_saving=chain[op]
   assert dest==final and expected_saving==3*(jumps-1)
   if expected_saving:
    alternate.mem[addr+1:addr+3]=final.to_bytes(2,'little')
  result={}
  for op in API:
   original_time=[];candidate_time=[]
   for i,(n,d) in enumerate(inp):
    a,ra=execute(baseline,api[op],n,d)
    b,rb=execute(alternate,api[op],n,d)
    expq,expr,expflag=div_expected(n,32,d,16,32,16)
    assert ra==rb,(p,op,i,hex(n),hex(d),ra,rb)
    assert ra[:3]==(expq,expr,expflag),(p,op,i,n,d,ra[:3],(expq,expr,expflag))
    assert ra[3:]==(n,d,ra[5],ra[6],ra[7],0x57,0xe2,0),(p,op,i,'ABI input/sentinel')
    original_time.append(a);candidate_time.append(b)
   saving=[a-b for a,b in zip(original_time,candidate_time)]
   expected_saving=chain[op][1]
   assert min(saving)==max(saving)==expected_saving,(p,op,min(saving),max(saving))
   result[op]={'baseline':stat(original_time),'candidate':stat(candidate_time),'saving':stat(saving),
               'all_input_signs_and_divzero':True,'full_quotient_remainder_and_C':True,
               'public_entry_unchanged':hex(api[op]),'patched_target':hex(chain[op][0]),'bytes_edited':2 if expected_saving else 0}
  report['profiles'][p]=result
  print('ISSUE144 SIGNED DIVMOD TAIL',p,len(inp),{op:chain[op][1] for op in API},'PASS',flush=True)
 outfile=ROOT/'validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_RESEARCH.json'
 outfile.parent.mkdir(parents=True,exist_ok=True)
 outfile.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('FINAL',report['status'],report['public_calls_model'])
if __name__=='__main__':main()
