#!/usr/bin/env python3
from pathlib import Path
import json,random,re,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from assemble_sources import parse_config

PROFILES=('v3_reu_512k','v4_reu_16m')
KINDS=('reference','alternate')

def load_prg(path):
 b=Path(path).read_bytes();load=b[0]|b[1]<<8;mem=bytearray(65536);mem[load:load+len(b)-2]=b[2:];return mem

def parse_inc(path):
 out={}
 for raw in Path(path).read_text().splitlines():
  s=raw.split(';',1)[0].strip()
  m=re.fullmatch(r'([A-Z][A-Z0-9_]*)\s*=\s*\$([0-9A-Fa-f]+)',s)
  if m:out[m.group(1)]=int(m.group(2),16)
 return out

def put(mem,a,v,n):
 for i in range(n):mem[a+i]=(v>>(8*i))&255

def get(mem,a,n):return sum(mem[a+i]<<(8*i) for i in range(n))

def cases(bits):
 maxv=(1<<bits)-1
 edge=[0,1,2,3,0xff,0x100,0xffff]
 if bits==32:edge += [0x10000,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 edge=[v&maxv for v in edge]
 out=[]
 for x in edge:
  for y in edge:out.append((x,y))
 rng=random.Random(0xC64A1600+bits)
 for _ in range(2048):out.append((rng.getrandbits(bits),rng.getrandbits(bits)))
 return out

def validate_one(profile,kind):
 bdir=ROOT/'build_source'/kind/profile
 prg=bdir/f'math_{profile}_source_built.prg';reu_path=bdir/f'c64_math_{profile}_source_built.reu'
 cfg=parse_config(ROOT/'relocatable_source'/profile/f'math_config_{kind}.inc');inc=parse_inc(bdir/'math_api.inc')
 mem=load_prg(prg);reu=bytearray(reu_path.read_bytes());cpu=CPU(mem,reu=reu);cpu.d=0
 cpu.call(inc['MATH_INIT'],2_000_000)
 mx,my,mz=inc['MATH_X'],inc['MATH_Y'],inc['MATH_Z']
 results={}
 for bits,prefix,zplen in [(16,'MATH_REU_UMUL16',113),(32,'MATH_REU_UMUL32',135)]:
  base=cfg[f'TURBO{bits}_ZP_BASE'];before=bytearray(((i*73+bits+17)&255) for i in range(zplen))
  cpu.mem[base:base+zplen]=before
  begin=inc[prefix+'_BEGIN'];call=inc[prefix];end=inc[prefix+'_END']
  cy_begin=cpu.call(begin,2_000_000)
  overlay_after_begin=bytes(cpu.mem[base:base+zplen])
  if overlay_after_begin==bytes(before):raise AssertionError(f'{profile} {kind} turbo{bits}: overlay did not install')
  cset=cases(bits);call_cycles=[]
  mask=(1<<(bits*2))-1
  for x,y in cset:
   put(cpu.mem,mx,x,bits//8);put(cpu.mem,my,y,bits//8)
   cy=cpu.call(call,2_000_000);call_cycles.append(cy)
   got=get(cpu.mem,mz,(bits*2)//8);want=(x*y)&mask
   if got!=want:raise AssertionError(f'{profile} {kind} turbo{bits}: {x:#x}*{y:#x} got {got:#x} want {want:#x}')
  cy_end=cpu.call(end,2_000_000)
  if bytes(cpu.mem[base:base+zplen])!=bytes(before):raise AssertionError(f'{profile} {kind} turbo{bits}: END did not restore ZP')
  # Second batch proves the modified SMC overlay swapped back to REU remains reusable.
  cy_begin2=cpu.call(begin,2_000_000)
  x=(0xA55A if bits==16 else 0xA55A1234);y=(0x5AA5 if bits==16 else 0x5AA5FEDC)
  put(cpu.mem,mx,x,bits//8);put(cpu.mem,my,y,bits//8);cy2=cpu.call(call,2_000_000)
  got=get(cpu.mem,mz,(bits*2)//8);want=(x*y)&mask
  if got!=want:raise AssertionError(f'{profile} {kind} turbo{bits}: second batch mismatch')
  cy_end2=cpu.call(end,2_000_000)
  if bytes(cpu.mem[base:base+zplen])!=bytes(before):raise AssertionError(f'{profile} {kind} turbo{bits}: second END restore failed')
  results[f'turbo{bits}']={'cases':len(cset)+1,'begin_cycles':cy_begin,'end_cycles':cy_end,'second_begin_cycles':cy_begin2,'second_call_cycles':cy2,'second_end_cycles':cy_end2,'call_mean_cycles':sum(call_cycles)/len(call_cycles),'call_min_cycles':min(call_cycles),'call_max_cycles':max(call_cycles),'zp_base':f'${base:02X}','zp_end':f'${base+zplen-1:02X}','reu_bank':f'${cfg[f"REU_TURBO{bits}_BANK"]:02X}','installed_overlay_sha256':hashlib.sha256(overlay_after_begin).hexdigest(),'cycle_vector_sha256':hashlib.sha256(','.join(map(str,call_cycles)).encode()).hexdigest()}
 return results

def main():
 allres={};
 for p in PROFILES:
  allres[p]={}
  for k in KINDS:
   r=validate_one(p,k);allres[p][k]=r;print(p,k,'PASS',r['turbo16']['cases'],'T16',r['turbo32']['cases'],'T32')
  # Relocation must be zero-cost: same corpus, same exact cycle vector summaries and lifecycle cycles.
  a=allres[p]['reference'];b=allres[p]['alternate']
  for t in ('turbo16','turbo32'):
   for key in ('begin_cycles','end_cycles','call_mean_cycles','call_min_cycles','call_max_cycles','cycle_vector_sha256'):
    if a[t][key]!=b[t][key]:raise AssertionError(f'{p} {t} relocation changed {key}: {a[t][key]} vs {b[t][key]}')
 product_calls=sum(allres[p][k][t]['cases'] for p in PROFILES for k in KINDS for t in ('turbo16','turbo32'))
 lifecycle_calls=len(PROFILES)*len(KINDS)*2*4  # two modes; BEGIN+END for two batches
 out={'status':'PASS','profiles':allres,'total_product_calls':product_calls,'total_lifecycle_calls':lifecycle_calls,'total_turbo_api_calls':product_calls+lifecycle_calls,'statement':'Turbo16/Turbo32 ZP origins and REU overlay banks are build-time relocatable; alternate relocation is cycle-identical on the canonical test corpus.'}
 od=ROOT/'validation/turbo_relocation';od.mkdir(parents=True,exist_ok=True);(od/'TURBO_RELOCATION_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
 print('TOTAL',out['total_turbo_api_calls'],'Turbo API calls PASS',f"({out['total_product_calls']} products + {out['total_lifecycle_calls']} BEGIN/END)")
if __name__=='__main__':main()
