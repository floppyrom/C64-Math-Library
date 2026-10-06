#!/usr/bin/env python3
"""Validate and benchmark the direct-public 136-ZP Turbo32 candidate in place.

This is an integration experiment: it patches the candidate resident binder/
summation and generated overlay into the current shipped V3/V4 images in memory,
then exercises the real BEGIN/CALL/END lifecycle and stable public ABI.
"""
from pathlib import Path
import random,re,statistics,sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU,Assembler

PROFILES=('v3_reu_512k','v4_reu_16m')
PRG={
 'v3_reu_512k':ROOT/'v3_reu_512k/resident/math_v3_reu_512k_game_math.prg',
 'v4_reu_16m':ROOT/'v4_reu_16m/resident/math_v4_reu_16m_game_math.prg',
}
REU={
 'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
 'v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu',
}

def parse(path):
 out={}
 for raw in Path(path).read_text().splitlines():
  s=raw.split(';',1)[0].strip()
  m=re.fullmatch(r'([A-Z][A-Z0-9_]*)\s*=\s*\$([0-9A-Fa-f]+)',s)
  if m: out[m.group(1)]=int(m.group(2),16)
 return out

def load_prg(path):
 b=path.read_bytes();lo=b[0]|b[1]<<8
 mem=bytearray(65536);mem[lo:lo+len(b)-2]=b[2:]
 return mem

def put(mem,a,v,n):
 for i in range(n):mem[a+i]=(v>>(8*i))&255

def get(mem,a,n):
 return sum(mem[a+i]<<(8*i) for i in range(n))

def assemble_candidate(profile,cfg):
 prefix='\n'.join(f'{k} = ${v:04X}' for k,v in cfg.items())+'\n'
 ovtxt=(ROOT/'relocatable_source/turbo/turbo32_overlay.asm').read_text()
 ov,labels,_=Assembler().assemble(prefix+ovtxt)
 base=cfg['TURBO32_ZP_BASE']
 if not ov or min(ov)!=base or max(ov)!=base+135:
  raise AssertionError((profile,'overlay range',hex(min(ov)),hex(max(ov))))
 expected={
  'umult32x8_same_x':base+0x44,'x0':base+0x45,'NL0':base+0x48,
  'SH0':base+0x4d,'NH0':base+0x50,'x1':base+0x53,'NL1':base+0x58,
  'SH1':base+0x5d,'NH1':base+0x60,'x2':base+0x63,'NL2':base+0x68,
  'SH2':base+0x6d,'NH2':base+0x70,'x3':base+0x73,'NL3':base+0x78,
  'SH3':base+0x7d,'NH3':base+0x80,
 }
 for k,want in expected.items():
  if labels.get(k)!=want:raise AssertionError((profile,k,hex(labels.get(k,-1)),hex(want)))
 api='MATH_REU_UMUL32_BEGIN = REG_API+$08C0\nMATH_REU_UMUL32 = REG_API+$0900\n'
 restxt=(ROOT/'relocatable_source/turbo/turbo32_resident_fast.asm').read_text()
 resident,_,_=Assembler().assemble(prefix+api+restxt)
 return ov,resident

def cases():
 edge=[0,1,2,3,0xff,0x100,0xffff,0x10000,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 out=[(x,y) for x in edge for y in edge]
 r=random.Random(0xC64F32)
 out += [(r.getrandbits(32),r.getrandbits(32)) for _ in range(12000)]
 return out

def run(profile):
 cfg=parse(ROOT/'relocatable_source'/profile/'math_config_reference.inc')
 api=parse(ROOT/profile/'resident/math_api.inc')
 mem=load_prg(PRG[profile]);reu=bytearray(REU[profile].read_bytes())
 ov,resident=assemble_candidate(profile,cfg)
 for a,b in resident.items():mem[a]=b
 bank=cfg['REU_TURBO32_BANK'];base=cfg['TURBO32_ZP_BASE']
 blob=bytes(ov[a] for a in range(base,base+136))
 reu[bank*0x10000:bank*0x10000+136]=blob
 cpu=CPU(mem,reu=reu);cpu.d=0
 cpu.call(api['MATH_INIT'],2_000_000)
 mx,my,mz=api['MATH_X'],api['MATH_Y'],api['MATH_Z']
 cs=cases()

 normal=[]
 for x,y in cs:
  put(cpu.mem,mx,x,4);put(cpu.mem,my,y,4)
  cy=cpu.call(api['MATH_UMUL32'],2_000_000);normal.append(cy)
  if get(cpu.mem,mz,8)!=(x*y)&0xffffffffffffffff:raise AssertionError((profile,'normal',hex(x),hex(y)))

 before=bytes(((i*73+0x32)&255) for i in range(136))
 cpu.mem[base:base+136]=before
 begin=api['MATH_REU_UMUL32_BEGIN'];call=api['MATH_REU_UMUL32'];end=api['MATH_REU_UMUL32_END']
 cb=cpu.call(begin,2_000_000)
 if bytes(cpu.mem[base:base+136])==before:raise AssertionError((profile,'begin did not install'))
 turbo=[]
 for x,y in cs:
  put(cpu.mem,mx,x,4);put(cpu.mem,my,y,4)
  cy=cpu.call(call,2_000_000);turbo.append(cy)
  got=get(cpu.mem,mz,8);want=(x*y)&0xffffffffffffffff
  if got!=want:raise AssertionError((profile,'turbo',hex(x),hex(y),hex(got),hex(want),cy))
 ce=cpu.call(end,2_000_000)
 if bytes(cpu.mem[base:base+136])!=before:raise AssertionError((profile,'end restore'))
 return {
  'cases':len(cs),
  'normal_mean':statistics.fmean(normal),'normal_min':min(normal),'normal_max':max(normal),
  'turbo_mean':statistics.fmean(turbo),'turbo_min':min(turbo),'turbo_max':max(turbo),
  'begin_cycles':cb,'end_cycles':ce,
  'saving_per_call':statistics.fmean(normal)-statistics.fmean(turbo),
 }

def main():
 out={'status':'PASS','candidate':'direct-public 136-ZP Turbo32','profiles':{}}
 for p in PROFILES:
  out['profiles'][p]=run(p)
  x=out['profiles'][p]
  print(p,'normal',f"{x['normal_mean']:.6f}",'turbo',f"{x['turbo_mean']:.6f}",
        'delta',f"{x['saving_per_call']:.6f}",'BEGIN/END',x['begin_cycles'],x['end_cycles'])
 path=ROOT/'validation/turbo_relocation/TURBO32_PUBLIC_FAST_EXPERIMENT.json'
 path.write_text(json.dumps(out,indent=2)+'\n')
 print('PASS',path)
if __name__=='__main__':main()
