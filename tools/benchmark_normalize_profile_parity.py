#!/usr/bin/env python3
from pathlib import Path
import sys,json,math,random,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import REV
REV[0xBF]=('lax','absy'); REV[0xAF]=('lax','abs')
import validate_source_build as vsb
from normalize_model import normalized_reference

def s16(lo,hi):
 v=lo|(hi<<8);return v-65536 if v&0x8000 else v
def phase(x,y,ox,oy):
 if x==0 and y==0:return 0.0
 return abs((math.atan2(oy,ox)-math.atan2(y,x)+math.pi)%(2*math.pi)-math.pi)*180/math.pi

def corpus():
 vals={0,1,-1,2,-2,127,-127,128,-128,255,-255,256,-256,32767,-32768}
 for p in range(16):
  v=1<<p
  for d in (-1,0,1):
   q=v+d
   if -32768<=q<=32767: vals.add(q)
   if -32768<=-q<=32767: vals.add(-q)
 vals=sorted(vals); c=[(x,y) for x in vals for y in vals]
 r=random.Random(0xC64)
 c += [(r.randrange(-32768,32768),r.randrange(-32768,32768)) for _ in range(100000)]
 return c
CASES=corpus()

def run(profile,build):
 c,P,I,M,_=vsb.load(profile,Path(build)); entry=P['MATH_VEC2_NORMALIZE_Q8_8'];X=I;Y=I+4;Z=I+8
 backend='exact' if profile in ('v3_reu_512k','v4_reu_16m') else 'log'
 design=json.loads((ROOT/'validation/normalize'/('COMPONENT_TABLE_DESIGN.json' if backend=='exact' else 'LOG_RATIO_TABLE_DESIGN.json')).read_text())
 total=0;lo=10**9;hi=0;ma=0.;mc=0;oe=ce=pe=0; cyc=[]; outputs=[]
 for x,y in CASES:
  xx=x&0xffff;yy=y&0xffff
  c.mem[X]=xx&255;c.mem[X+1]=xx>>8;c.mem[Y]=yy&255;c.mem[Y+1]=yy>>8
  before=bytes(c.mem[X:X+8]); n=c.call(entry);cyc.append(n);total+=n;lo=min(lo,n);hi=max(hi,n)
  ox=s16(c.mem[Z],c.mem[Z+1]);oy=s16(c.mem[Z+2],c.mem[Z+3])
  outputs.append((ox,oy))
  if (ox,oy)!=normalized_reference(x,y,design,backend):oe+=1
  if bytes(c.mem[X:X+8])!=before:pe+=1
  if bool(c.c)!=(x==0 and y==0):ce+=1
  if x==0 and y==0:
   if (ox,oy)!=(0,0):oe+=1
  else:
   h=math.hypot(x,y);ex=round(x/h*32767);ey=round(y/h*32767)
   mc=max(mc,abs(ox-ex),abs(oy-ey));ma=max(ma,phase(x,y,ox,oy))
 assert oe==ce==pe==0 and ma<=.3621 and mc<=202,(profile,build,oe,ce,pe,ma,mc)
 digest=hashlib.sha256(b''.join(struct.pack('<hh',*v) for v in outputs)).hexdigest()
 return {'profile':profile,'config':M['config'],'entry':f'${entry:04X}','backend':backend,'cases':len(CASES),'mean_cycles':total/len(CASES),'min_cycles':lo,'max_cycles':hi,'max_angle_deg':ma,'max_component_lsb':mc,'output_errors':oe,'carry_errors':ce,'input_preserve_errors':pe,'output_sha256':digest,'prg_sha256':M['output_sha256'],'cycles':cyc,'outputs':outputs}

jobs={
 'v1_balanced':(ROOT/'build_source/reference',ROOT/'build_source/alternate'),
 'v2_pareto_fast':(ROOT/'build_source/reference',ROOT/'build_source/alternate'),
 'v3_reu_512k':(ROOT/'build_source/reference',ROOT/'build_source/alternate'),
 'v4_reu_16m':(ROOT/'build_source/reference',ROOT/'build_source/alternate'),
 'v5_hybrid_lowzp':(ROOT/'build_hybrid/reference',ROOT/'build_hybrid/alternate'),
}
def compare_baseline(out):
 baseline=json.loads((ROOT/'validation/normalize/BASELINE_107396.json').read_text())
 digest=hashlib.sha256(b''.join(struct.pack('<hh',*v) for v in CASES)).hexdigest()
 assert digest==baseline['corpus_sha256']
 out['corpus_sha256']=digest
 out['baseline_commit']=baseline['baseline_commit']
 for row in out['profiles']:
  p=row['profile']; old=baseline['profiles'][baseline['equivalent_normalizers'].get(p,p)]; new=row['reference']
  same=new['output_sha256']==old['output_sha256']
  if p in ('v3_reu_512k','v4_reu_16m'):assert same,(p,'REU output regression')
  row['baseline_mean_cycles']=old['mean_cycles']
  row['cycle_reduction_percent']=100*(old['mean_cycles']-new['mean_cycles'])/old['mean_cycles']
  row['outputs_identical_to_baseline']=same
 assert len({r['reference']['output_sha256'] for r in out['profiles'] if r['reference']['backend']=='log'})==1
 return out

def main():
 out=[]
 for p,(rb,ab) in jobs.items():
  r=run(p,rb);a=run(p,ab);mm=sum(x!=y for x,y in zip(r['cycles'],a['cycles']))
  om=sum(x!=y for x,y in zip(r['outputs'],a['outputs']))
  assert mm==om==0,(p,mm,om)
  rr={k:v for k,v in r.items() if k not in ('cycles','outputs')};aa={k:v for k,v in a.items() if k not in ('cycles','outputs')}
  row={'profile':p,'reference':rr,'alternate':aa,'cycle_vector_mismatches':mm,'output_vector_mismatches':om};out.append(row)
  print(p,rr['mean_cycles'],rr['min_cycles'],rr['max_cycles'],'alt',aa['mean_cycles'],'mismatch',mm,'err',rr['max_angle_deg'],rr['max_component_lsb'],flush=True)
 result=compare_baseline({'status':'PASS','corpus_vectors':len(CASES),'profiles':out})
 (ROOT/'validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
