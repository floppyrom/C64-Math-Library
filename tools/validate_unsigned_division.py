#!/usr/bin/env python3
"""Validate the shipped unsigned divide/modulo family at the stable public ABI.

The corpus is deterministic. UDIV8 is exhaustive in every fixed profile; wider
entries combine structured edges, random inputs, and explicit divide-by-zero
cases. Modulo aliases are exercised independently. URECIP16_Q16 is exhaustive.
"""
from pathlib import Path
import argparse,json,random,re,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
REU={'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu','v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}
def mask(b):return (1<<b)-1
def wr(m,a,v,n):
 for i in range(n):m[a+i]=(v>>(8*i))&255
def rd(m,a,n):return sum(m[a+i]<<(8*i) for i in range(n))
def api(p):
 out={}
 for l in (ROOT/p/'resident/math_api.inc').read_text().splitlines():
  q=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',l)
  if q:out[q.group(1)]=int(q.group(2),16)
 return out
def load(p):
 f=ROOT/p/'resident'/f'math_{p}_game_math.prg';b=f.read_bytes();lo=b[0]|b[1]<<8;m=bytearray(65536);m[lo:lo+len(b)-2]=b[2:]
 r=bytearray(REU[p].read_bytes()) if p in REU else None;c=CPU(m,reu=r);c.d=0;c.call(0x3280,2_000_000);return c,api(p)
def edge(b):
 M=mask(b);s=1<<(b-1)
 return list(dict.fromkeys(x&M for x in [0,1,2,3,4,7,15,16,31,63,127,128,255,256,511,1023,s-2,s-1,s,s+1,M-2,M-1,M]))
def expected(n,d,qb,rb,shift=0):
 if d==0:return 0,0,1
 n<<=shift;return (n//d)&mask(qb),(n%d)&mask(rb),0
def run(cpu,entry,cases,nb,db,qb,rb,shift=0,remainder_only=False):
 N,D,Q,R=0xc010,0xc014,0xc018,0xc01c;nn=(nb+7)//8;dn=(db+7)//8;qn=(qb+7)//8;rn=(rb+7)//8
 total=errs=0;mi=None;ma=None
 for n,d in cases:
  wr(cpu.mem,N,n,nn);wr(cpu.mem,D,d,dn);bn=bytes(cpu.mem[N:N+nn]);bd=bytes(cpu.mem[D:D+dn]);cy=cpu.call(entry,4_000_000)
  eq,er,ec=expected(n,d,qb,rb,shift);gq=rd(cpu.mem,Q,qn);gr=rd(cpu.mem,R,rn)
  ok=((gr,cpu.c)==(er,ec)) if remainder_only else ((gq,gr,cpu.c)==(eq,er,ec))
  if not ok or bytes(cpu.mem[N:N+nn])!=bn or bytes(cpu.mem[D:D+dn])!=bd:
   errs+=1
   if errs<=4:print('ERROR',hex(entry),hex(n),hex(d),'got',hex(gq),hex(gr),cpu.c,'exp',hex(eq),hex(er),ec)
  total+=cy;mi=cy if mi is None else min(mi,cy);ma=cy if ma is None else max(ma,cy)
 return {'cases':len(cases),'errors':errs,'mean_cycles':total/len(cases),'min_cycles':mi,'max_cycles':ma}
def recip(cpu,entry):
 D,Q=0xc014,0xc018;total=errs=0;mi=None;ma=None
 for d in range(65536):
  wr(cpu.mem,D,d,2);bd=bytes(cpu.mem[D:D+2]);cy=cpu.call(entry,4_000_000);g=rd(cpu.mem,Q,3);eq=0 if d==0 else 65536//d;ec=1 if d==0 else 0
  if (g,cpu.c)!=(eq,ec) or bytes(cpu.mem[D:D+2])!=bd:
   errs+=1
   if errs<=4:print('RECIP ERROR',hex(d),hex(g),cpu.c,hex(eq),ec)
  total+=cy;mi=cy if mi is None else min(mi,cy);ma=cy if ma is None else max(ma,cy)
 return {'cases':65536,'errors':errs,'mean_cycles':total/65536,'min_cycles':mi,'max_cycles':ma,'mode':'exhaustive'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--profile',choices=PROFILES);ap.add_argument('--out',type=Path);a=ap.parse_args();runp=[a.profile] if a.profile else PROFILES;result={};t=time.time()
 defs=[('MATH_UDIV8',8,8,8,8,0),('MATH_UDIV16',16,16,16,16,0),('MATH_UDIV24',24,24,24,24,0),('MATH_UDIV32_16',32,16,32,16,0),('MATH_UDIV32_32',32,32,32,32,0),('MATH_UDIV16_SHL8',16,16,24,16,8)]
 aliases=[('MATH_UMOD8',8,8,8,8,0),('MATH_UMOD16',16,16,16,16,0),('MATH_UMOD24',24,24,24,24,0),('MATH_UMOD32_16',32,16,32,16,0),('MATH_UMOD32_32',32,32,32,32,0)]
 for p in runp:
  pi=PROFILES.index(p);c,A=load(p);pr={}
  for name,nb,db,qb,rb,sh in defs:
   if name=='MATH_UDIV8':cases=[(n,d) for n in range(256) for d in range(256)];mode='exhaustive'
   else:
    cases=[(n,d) for n in edge(nb) for d in edge(db)];r=random.Random(0xD1700000+pi*0x10000+nb*257+db+sh);count=4096 if name!='MATH_UDIV32_32' else 6144
    cases += [(r.randrange(1<<nb),r.randrange(1<<db)) for _ in range(count)];cases += [(r.randrange(1<<nb),0) for _ in range(128)];mode='structured_random'
   z=run(c,A[name],cases,nb,db,qb,rb,sh);z['mode']=mode;pr[name]=z
  for i,(name,nb,db,qb,rb,sh) in enumerate(aliases):
   r=random.Random(0xA7700000+pi*0x1000+i);cases=[(n,d) for n in edge(nb) for d in edge(db)]+[(r.randrange(1<<nb),r.randrange(1<<db)) for _ in range(1024)]
   pr[name]=run(c,A[name],cases,nb,db,qb,rb,sh,remainder_only=True)
  pr['MATH_URECIP16_Q16']=recip(c,A['MATH_URECIP16_Q16'])
  if any(v['errors'] for v in pr.values()):raise AssertionError((p,pr))
  result[p]=pr;print(p,'PASS',sum(v['cases'] for v in pr.values()),'unsigned division/modulo calls',flush=True)
 out={'status':'PASS','profiles':result,'summary':{'profiles':len(runp),'machine_calls':sum(v['cases'] for pr in result.values() for v in pr.values()),'elapsed_seconds':round(time.time()-t,2)}}
 path=a.out or ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n');print('UNSIGNED DIVISION PASS',out['summary']['machine_calls'],'calls')
if __name__=='__main__':main()
