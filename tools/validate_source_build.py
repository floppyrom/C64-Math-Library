#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,json,math,random,hashlib,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU,REV
REV[0xBF]=('lax','absy'); REV[0xAF]=('lax','abs')
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']
REU={'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu','v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}
MASK=lambda b:(1<<b)-1
def unhx(s):return int(s[1:],16) if isinstance(s,str) and s.startswith('$') else int(s,0) if isinstance(s,str) else int(s)
def si(v,b):return v-(1<<b) if v&(1<<(b-1)) else v
def wr(c,a,v,n):
 for i in range(n):c.mem[a+i]=(v>>(8*i))&255
def rd(c,a,n):return sum(c.mem[a+i]<<(8*i) for i in range(n))
def snap(c,a,n):return bytes(c.mem[a:a+n])
def truncdiv(n,d):
 q=abs(n)//abs(d);q=-q if (n<0)^(d<0) else q;return q,n-q*d

def load(profile,build):
 man=json.loads((build/profile/'source_build_manifest.json').read_text());p=build/profile/man['output_prg'];b=p.read_bytes();ld=b[0]|b[1]<<8;m=bytearray(65536);m[ld:ld+len(b)-2]=b[2:]
 reu_path=None
 if profile in REU:
  ri=man.get('reu_image')
  reu_path=(build/profile/ri['file']) if ri else REU[profile]
  reu=bytearray(reu_path.read_bytes())
 else: reu=None
 c=CPU(m,reu=reu);c.d=0;pub={k:unhx(v) for k,v in man['public_entries'].items()};io=unhx(man['public_io'].split('-')[0]);init=unhx(man['math_init']);cy=c.call(init,2_000_000);assert c.c==0,(profile,'MATH_INIT carry')
 man['_resolved_reu_path']=str(reu_path) if reu_path else None
 return c,pub,io,man,cy

def cases(bits,seed,count=24):
 m=MASK(bits); e=[0,1,2,3,7,15,16,31,127,128,255,m>>1,(m>>1)+1,m-1,m]
 e=[x&m for x in e];r=random.Random(seed);return list(dict.fromkeys(e+[r.randrange(m+1) for _ in range(count)]))
def pairs(bits,seed,count=32):
 a=cases(bits,seed,10);r=random.Random(seed^0xA5A5A5A5);return [(x,y) for x in a[:9] for y in a[:9]]+[(r.randrange(1<<bits),r.randrange(1<<bits)) for _ in range(count)]

def validate(profile,build):
 t=time.time();c,P,I,M,initcy=load(profile,build);X=I;Y=I+4;Z=I+8;N=I+0x10;D=I+0x14;Q=I+0x18;R=I+0x1c
 hits={k:0 for k in P};checks=0
 def call(n,lim=2_000_000):
  nonlocal checks;cy=c.call(P[n],lim);hits[n]+=1;checks+=1;return cy
 # Publication stubs for game entries remain JMP ABI slots at the relocated block.
 for n in list(P)[26:]:
  if n != 'MATH_VEC2_NORMALIZE_Q8_8': assert c.mem[P[n]]==0x4c,(profile,n,hex(P[n]),hex(c.mem[P[n]]))
 # Unsigned and signed multiply, including ready aliases.
 for bits,n in [(8,'MATH_UMUL8'),(16,'MATH_UMUL16'),(24,'MATH_UMUL24'),(32,'MATH_UMUL32')]:
  nb=bits//8
  for x,y in pairs(bits,0x1000+bits):
   wr(c,X,x,nb);wr(c,Y,y,nb);xs=snap(c,X,nb);ys=snap(c,Y,nb);call(n);assert rd(c,Z,2*nb)==(x*y)&MASK(2*bits) and snap(c,X,nb)==xs and snap(c,Y,nb)==ys and c.c==0,(profile,n,x,y,hex(rd(c,Z,2*nb)))
 # ready unsigned 32
 for x,y in pairs(32,0x3200,12)[:24]:wr(c,X,x,4);wr(c,Y,y,4);call('MATH_UMUL32_READY');assert rd(c,Z,8)==x*y and c.c==0
 for bits,n in [(8,'MATH_SMUL8'),(16,'MATH_SMUL16'),(24,'MATH_SMUL24'),(32,'MATH_SMUL32')]:
  nb=bits//8
  for x,y in pairs(bits,0x5000+bits):
   wr(c,X,x,nb);wr(c,Y,y,nb);xs=snap(c,X,nb);ys=snap(c,Y,nb);call(n);exp=(si(x,bits)*si(y,bits))&MASK(2*bits);assert rd(c,Z,2*nb)==exp and snap(c,X,nb)==xs and snap(c,Y,nb)==ys and c.c==0,(profile,n,hex(x),hex(y),hex(rd(c,Z,2*nb)),hex(exp))
 for x,y in pairs(32,0x5320,12)[:24]:wr(c,X,x,4);wr(c,Y,y,4);call('MATH_SMUL32_READY');assert rd(c,Z,8)==(si(x,32)*si(y,32))&MASK(64) and c.c==0
 # Unsigned divide + modulo aliases.
 divspec=[(8,8,'MATH_UDIV8'),(16,16,'MATH_UDIV16'),(24,24,'MATH_UDIV24'),(32,16,'MATH_UDIV32_16')]
 for nb,db,n in divspec:
  nn=nb//8;dn=db//8
  for a,d in pairs(nb,0xD000+nb,20)[:70]:
   d &= MASK(db);wr(c,N,a,nn);wr(c,D,d,dn);ns=snap(c,N,nn);ds=snap(c,D,dn);call(n);q=rd(c,Q,nn);r=rd(c,R,dn)
   if d==0:assert c.c==1 and q==0 and r==0,(profile,n,'div0',q,r)
   else:assert c.c==0 and (q,r)==divmod(a,d),(profile,n,a,d,q,r,divmod(a,d))
   assert snap(c,N,nn)==ns and snap(c,D,dn)==ds
 # UMOD8 is independent; wider UMOD entries alias UDIV.
 for a,d in pairs(8,0xD808,20)[:70]:
  wr(c,N,a,1);wr(c,D,d,1);call('MATH_UMOD8');r=rd(c,R,1);assert (c.c==1 and r==0) if d==0 else (c.c==0 and r==a%d)
 for nb,db,n in [(16,16,'MATH_UMOD16'),(24,24,'MATH_UMOD24'),(32,16,'MATH_UMOD32_16')]:
  nn=nb//8;dn=db//8
  for a,d in pairs(nb,0xE000+nb,8)[:24]:
   d&=MASK(db);wr(c,N,a,nn);wr(c,D,d,dn);call(n);q=rd(c,Q,nn);r=rd(c,R,dn);assert (c.c==1 and q==0 and r==0) if d==0 else (c.c==0 and (q,r)==divmod(a,d))
 # Signed divide and signed modulo aliases; quotient is truncation toward zero.
 for nb,db,n,mn in [(8,8,'MATH_SDIV8','MATH_SMOD8'),(16,16,'MATH_SDIV16','MATH_SMOD16'),(24,24,'MATH_SDIV24','MATH_SMOD24'),(32,16,'MATH_SDIV32_16','MATH_SMOD32_16')]:
  nn=nb//8;dn=db//8
  for a,d0 in pairs(nb,0xA000+nb,20)[:70]:
   d=d0&MASK(db);sa=si(a,nb);sd=si(d,db)
   for ent in (n,mn):
    wr(c,N,a,nn);wr(c,D,d,dn);call(ent);q=rd(c,Q,nn);r=rd(c,R,dn)
    if sd==0:assert c.c==1 and q==0 and r==0,(profile,ent,'div0',q,r)
    else:
     eq,er=truncdiv(sa,sd);assert c.c==0 and q==(eq&MASK(nb)) and r==(er&MASK(db)),(profile,ent,sa,sd,hex(q),hex(r),eq,er)
 # Game 32/32 divmod, both aliases, unsigned+signed.
 for a,d in pairs(32,0x323232,32)[:100]:
  for ent in ('MATH_UDIV32_32','MATH_UMOD32_32'):
   wr(c,N,a,4);wr(c,D,d,4);call(ent);q=rd(c,Q,4);r=rd(c,R,4);assert (c.c==1 and q==0 and r==0) if d==0 else (c.c==0 and (q,r)==divmod(a,d))
  sa=si(a,32);sd=si(d,32)
  for ent in ('MATH_SDIV32_32','MATH_SMOD32_32'):
   wr(c,N,a,4);wr(c,D,d,4);call(ent);q=rd(c,Q,4);r=rd(c,R,4)
   if sd==0:assert c.c==1 and q==0 and r==0
   else:eq,er=truncdiv(sa,sd);assert c.c==0 and q==(eq&MASK(32)) and r==(er&MASK(32))
 # Fixed multiply shifts.
 for x,y in pairs(16,0x161608,24)[:80]:
  wr(c,X,x,2);wr(c,Y,y,2);call('MATH_UMUL16_SHR8');assert rd(c,Z,3)==((x*y)>>8)&MASK(24) and c.c==0
  wr(c,X,x,2);wr(c,Y,y,2);call('MATH_SMUL16_SHR8');assert rd(c,Z,3)==((si(x,16)*si(y,16))>>8)&MASK(24) and c.c==0
 for x,y in pairs(32,0x323216,16)[:60]:
  wr(c,X,x,4);wr(c,Y,y,4);call('MATH_UMUL32_SHR16');assert rd(c,Z,6)==((x*y)>>16)&MASK(48) and c.c==0
  wr(c,X,x,4);wr(c,Y,y,4);call('MATH_SMUL32_SHR16');assert rd(c,Z,6)==((si(x,32)*si(y,32))>>16)&MASK(48) and c.c==0
 # Fixed divide shifts.
 for a,d in pairs(16,0x1616D8,16)[:60]:
  wr(c,N,a,2);wr(c,D,d,2);call('MATH_UDIV16_SHL8');q=rd(c,Q,3);r=rd(c,R,2);assert (c.c==1 and q==0 and r==0) if d==0 else (c.c==0 and (q,r)==divmod(a<<8,d))
  sa=si(a,16);sd=si(d,16);wr(c,N,a,2);wr(c,D,d,2);call('MATH_SDIV16_SHL8');q=rd(c,Q,3);r=rd(c,R,2)
  if sd==0:assert c.c==1 and q==0 and r==0
  else:eq,er=truncdiv(sa<<8,sd);assert c.c==0 and q==(eq&MASK(24)) and r==(er&MASK(16))
 # Reciprocal structured + random.
 for d in cases(16,0xBEEF,48):
  wr(c,D,d,2);call('MATH_URECIP16_Q16');q=rd(c,Q,3);assert (c.c==1 and q==0) if d==0 else (c.c==0 and q==65536//d),(profile,'recip',d,q)
 # Trig: full phase domain is cheap and catches table base relocation.
 for a in range(256):
  wr(c,X,a,1);call('MATH_SIN8');assert c.mem[Z]==(round(127*math.sin(2*math.pi*a/256))&255) and c.c==0
  wr(c,X,a,1);call('MATH_COS8');assert c.mem[Z]==(round(127*math.cos(2*math.pi*a/256))&255) and c.c==0
  wr(c,X,a,1);call('MATH_SINCOS8');assert c.mem[Z]==(round(127*math.sin(2*math.pi*a/256))&255) and c.mem[Z+1]==(round(127*math.cos(2*math.pi*a/256))&255) and c.c==0
 # atan2 sample grid (V1-V3 approximation tolerance <= 1 unit; V4 exact table also meets it).
 vals=[-128,-127,-64,-2,-1,0,1,2,63,64,126,127]
 for sy in vals:
  for sx in vals:
   xb=sx&255;yb=sy&255;wr(c,X,xb,1);wr(c,Y,yb,1);call('MATH_ATAN2_8');g=c.mem[Z];e=0 if sx==0 and sy==0 else round((math.atan2(sy,sx)%(2*math.pi))*256/(2*math.pi))&255;er=min((g-e)&255,(e-g)&255);assert er<=1,(profile,'atan2',sx,sy,g,e,er)
 # sqrt16/32 structured+random; independent ISQRT32 result is checked directly.
 for n in cases(16,0x161651,64):wr(c,N,n,2);call('MATH_ISQRT16');assert rd(c,Z,2)==math.isqrt(n) and c.c==0,(profile,'sqrt16',n,rd(c,Z,2))
 s32=[0,1,2,3,4,15,16,17,255,256,257,65535,65536,0x7fffffff,0x80000000,0xffffffff]+[random.Random(0x3251+i).randrange(1<<32) for i in range(80)]
 for n in s32:wr(c,N,n,4);call('MATH_ISQRT32');assert rd(c,Z,2)==math.isqrt(n) and c.c==0,(profile,'sqrt32',n,rd(c,Z,2),math.isqrt(n))
 # Distance sample signed plane.
 for sy in vals:
  for sx in vals:
   xb=sx&255;yb=sy&255;M0=max(abs(sx),abs(sy));m0=min(abs(sx),abs(sy));wr(c,X,xb,1);wr(c,Y,yb,1);call('MATH_DIST8_FAST');assert c.mem[Z]==((M0+(m0>>1))&255) and c.c==0
   wr(c,X,xb,1);wr(c,Y,yb,1);call('MATH_DIST8_ACCURATE');assert c.mem[Z]==((round(243*M0/256)+round(107*m0/256))&255) and c.c==0
 # Q8.8 vector normalize -> Q1.15 signed unit vector. Inputs are preserved; C marks zero vector.
 nv=[-32768,-32767,-256,-255,-129,-128,-2,-1,0,1,2,127,128,255,256,32766,32767]
 nr=random.Random(0x4E4F524D)
 norm_cases=[(x,y) for x in nv for y in nv]+[(nr.randrange(-32768,32768),nr.randrange(-32768,32768)) for _ in range(128)]
 for sx,sy in norm_cases:
  wr(c,X,sx&MASK(16),2);wr(c,Y,sy&MASK(16),2);xs=snap(c,X,2);ys=snap(c,Y,2);call('MATH_VEC2_NORMALIZE_Q8_8')
  ox=si(rd(c,Z,2),16);oy=si(rd(c,Z+2,2),16)
  assert snap(c,X,2)==xs and snap(c,Y,2)==ys,(profile,'normalize input preserve',sx,sy)
  if sx==0 and sy==0:
   assert c.c==1 and ox==0 and oy==0,(profile,'normalize zero',ox,oy,c.c)
  else:
   assert c.c==0,(profile,'normalize carry',sx,sy)
   h=math.hypot(sx,sy);ex=round(sx/h*32767);ey=round(sy/h*32767)
   ce=max(abs(ox-ex),abs(oy-ey));assert ce<=202,(profile,'normalize component',sx,sy,ox,oy,ex,ey,ce)
   ae=abs((math.atan2(oy,ox)-math.atan2(sy,sx)+math.pi)%(2*math.pi)-math.pi)*180/math.pi
   assert ae<=0.3621+1e-12,(profile,'normalize angle',sx,sy,ae)
 # Every stable entry must have executed literally at its generated address.
 missing=[n for n,v in hits.items() if v==0];assert not missing,(profile,'unexecuted entries',missing)
 # REU transport must point at relocated C64-side buffer after MATH_INIT/normal calls restore lookup mode.
 reu_detail=None
 if profile in REU:
  # Explicitly rerun MATH_INIT, then inspect programmed one-byte C64 address.
  c.call(unhx(M['math_init']),1_000_000);dest=c.mem[0xDF02]|c.mem[0xDF03]<<8;expected=unhx(M['reu_scratch'].split('-')[0]);assert dest==expected,(profile,'REU C64 destination',hex(dest),hex(expected));rp=Path(M['_resolved_reu_path']);reu_detail={'programmed_c64_destination':f'${dest:04X}','expected':f'${expected:04X}','reu_image_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'reu_banks':M.get('reu_banks',{})}
 return {'profile':profile,'status':'PASS','math_init_cycles':initcy,'public_entries_executed':len(hits),'machine_calls':sum(hits.values()),'assertion_groups':checks,'entry_hits':hits,'reu_transport':reu_detail}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('profile',choices=PROFILES+['all']);ap.add_argument('--build',type=Path,default=ROOT/'build/alternate');ap.add_argument('--out',type=Path,default=ROOT/'validation/relocation');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);ps=PROFILES if a.profile=='all' else [a.profile];res=[]
 for p in ps:
  r=validate(p,a.build);res.append(r);(a.out/f'{p}_alternate_validation.json').write_text(json.dumps(r,indent=2)+'\n');print(p,'PASS',r['public_entries_executed'],'entries',r['machine_calls'],'calls',flush=True)
 if a.profile=='all':(a.out/'ALTERNATE_MAP_VALIDATION.json').write_text(json.dumps({'status':'PASS','profiles':res},indent=2)+'\n')
if __name__=='__main__':main()
