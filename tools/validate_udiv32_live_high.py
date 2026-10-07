#!/usr/bin/env python3
"""Certify four-ZP UDIV32/UMOD32 in both maps, including memory guards."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_smul24_directout import load
from validate_unsigned_division import edge,wr,rd,expected
from generate_consolidated_routine_table import trace

def main():
 r=random.Random(0x32D1F);groups={'edges':[(n,d) for n in edge(32) for d in edge(32)]}
 for tag,count,b in [('uniform32',30000,32),('divisor16',2000,16),('divisor8',2000,8)]:groups[tag]=[(r.getrandbits(32),r.randrange(1,1<<b)) for _ in range(count)]
 groups['quotient_boundaries']=list(dict.fromkeys((n,d) for d in [1,255,256,65535,65536,65537,88257,0x1000001,0x7fffffff,0xffffffff] for q in [0,1,2,3,7,255,256,65535] for n in [d*q-1,d*q,d*q+1] if 0<=n<=0xffffffff))
 out={}
 for p in ('v2_pareto_fast','v3_reu_512k','v4_reu_16m'):
  out[p]={};vectors=[]
  for kind in ('reference','alternate'):
   cpu,api=load(p,kind);code,zp,stack=trace(cpu.mem,api['MATH_UDIV32_32']);assert len(code)==793 and len(zp)==4 and not stack
   allowed=zp|set(range(api['MATH_Q'],api['MATH_Q']+8))|set(range(0x1f8,0x1fe));stats={};vector=[]
   for tag,cases in groups.items():
    cycles=[]
    for i,(n,d) in enumerate(cases):
     wr(cpu.mem,api['MATH_N'],n,4);wr(cpu.mem,api['MATH_D'],d,4)
     before=bytes(cpu.mem) if tag in ('edges','quotient_boundaries') or i%257==0 else None
     for carry in (0,1):
      cpu.c=carry;cy=cpu.call(api['MATH_UDIV32_32'])
      assert (rd(cpu.mem,api['MATH_Q'],4),rd(cpu.mem,api['MATH_R'],4),cpu.c)==expected(n,d,32,32),(p,kind,n,d)
      assert cpu.sp==0xfd
     cycles.append(cy);cpu.c=i&1;cpu.call(api['MATH_UMOD32_32'])
     assert (rd(cpu.mem,api['MATH_R'],4),cpu.c)==expected(n,d,32,32)[1:]
     assert rd(cpu.mem,api['MATH_N'],4)==n and rd(cpu.mem,api['MATH_D'],4)==d and cpu.sp==0xfd
     if before is not None:assert all(a in allowed or x==cpu.mem[a] for a,x in enumerate(before)),(p,kind,n,d,'write outside ABI')
    stats[tag]={'cases':len(cycles),'mean_cycles':sum(cycles)/len(cycles),'min_cycles':min(cycles),'max_cycles':max(cycles)};vector.extend(cycles)
   out[p][kind]={'code_bytes':len(code),'zp_bytes':len(zp),'groups':stats};vectors.append(vector);print(p,kind,'PASS',len(vector)*3,'calls',flush=True)
  assert vectors[0]==vectors[1],(p,'cycle relocation parity')
 (ROOT/'validation/review/UDIV32_LIVE_HIGH_VALIDATION.json').write_text(json.dumps({'status':'PASS','seed':'0x32D1F','basis':'public entry through RTS; both incoming carry states; UMOD independently exercised; equal relocation cycle vectors','results':out},indent=2)+'\n')
if __name__=='__main__':main()
