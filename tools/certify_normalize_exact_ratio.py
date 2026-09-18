#!/usr/bin/env python3
import math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'certification'
D=json.load(open(B/'component_table_design.json')); comps=D['comps']; recip=D['recip']
def ceildiv(a,b): return -((-a)//b)
def cell_range(s,m):
 den=1<<s; lo=ceildiv(m*256,den); hi=((m+1)*256-1)//den
 return max(0,lo),min(32767,hi)
def major_range(s,m):
 lo,hi=cell_range(s,m); slo=ceildiv(32768,1<<s); shi=min(32767,65535//(1<<s))
 return max(lo,slo),min(hi,shi)
def rbounds(A0,A1,B0,B1,da,db):
 if B0>A1:return None
 rmin=(B0+db)/(A1+da); vals=[]
 if B1<A0: vals.append((B1+db)/(A0+da))
 else:
  L=max(A0,B0);H=min(A1,B1)
  if L<=H: vals += [(L+db)/(L+da),(H+db)/(H+da)]
  if B1<=A1:
   aa=max(A0,B1); vals.append((B1+db)/(aa+da))
 if not vals:return None
 rmax=max(vals);return min(rmin,rmax),max(rmin,rmax)
def add(lo,hi,idx,A0,A1,B0,B1,da,db,tag):
 q=rbounds(A0,A1,B0,B1,da,db)
 if not q:return 0
 a0=math.degrees(math.atan(q[0]));a1=math.degrees(math.atan(q[1]))
 lo[idx]=min(lo[idx],a0);hi[idx]=max(hi[idx],a1);return 1
lo=[999.]*256;hi=[-999.]*256;cells=0
for ma in range(128,256):
 k=recip[ma-128]
 for mi in range(ma+1):
  idx=(1+mi+((mi*k)>>8))&255
  for s in range(1,8):
   A0,A1=major_range(s,ma);B0,B1=cell_range(s,mi)
   if A0>A1 or B0>B1 or B0>A1:continue
   for da in (0,1):
    for db in (0,1): cells += add(lo,hi,idx,A0,A1,B0,B1,da,db,'high')
  for s in range(8,16):
   A0,A1=major_range(s,ma);B0,B1=cell_range(s,mi)
   A0=max(A0,1);A1=min(A1,255);B0=max(B0,0);B1=min(B1,255)
   if A0>A1 or B0>B1 or B0>A1:continue
   cells += add(lo,hi,idx,A0,A1,B0,B1,0,0,'low00')
   if A0<=255<=A1: cells += add(lo,hi,idx,255,255,B0,min(B1,255),1,0,'lowA1')
   if B0<=255<=B1 and A1>=255: cells += add(lo,hi,idx,max(A0,255),A1,255,255,0,1,'lowB1')
   if A0<=255<=A1 and B0<=255<=B1: cells += add(lo,hi,idx,255,255,255,255,1,1,'low11')
maxa=-1;maxc=-1;wa=wc=None;used=0
for idx in range(256):
 if hi[idx]<0:continue
 used+=1;om,oni=comps[idx];oa=math.degrees(math.atan2(oni,om))
 for aa in (lo[idx],hi[idx]):
  ae=abs(oa-aa)
  if ae>maxa:maxa=ae;wa=[idx,lo[idx],hi[idx],oa,aa,om,oni]
  r=math.radians(aa);im=32767*math.cos(r);ii=32767*math.sin(r);ce=max(abs(om-im),abs(oni-ii))
  if ce>maxc:maxc=ce;wc=[idx,lo[idx],hi[idx],aa,om,oni,im,ii]
R={'mapping':'idx=(1+minor+floor(minor*reciprocal[major]/256)) mod 256','profiles':['v1_balanced','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp'],'max_angle_deg':maxa,'max_component_float':maxc,'max_component_ceil':math.ceil(maxc),'angular_contract_deg':0.3621,'component_contract_lsb':202,'status':'PASS' if maxa<=0.3621 and math.ceil(maxc)<=202 else 'FAIL','worst_angle':wa,'worst_component':wc,'used_indices':used,'cells':cells}
print(json.dumps(R,indent=2));json.dump(R,open(B/'exact_ratio_full_domain_precision_certificate.json','w'),indent=2)
