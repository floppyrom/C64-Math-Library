#!/usr/bin/env python3
"""Issue39: same-input public Q/R/C for twelve-byte caller-opt-in N16 producer."""
from pathlib import Path
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd,expected
SRC=ROOT/'routines/standalone_lab/library_dependent/div_u32_u16_n16_optin.asm'
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
MAPS=(0x800,0xA00)
def batches():
 rng=random.Random(0xC643216)
 edge=[0,1,2,127,128,255,256,257,65534,65535]
 div=[0,1,2,3,127,254,255,256,257,511,512,1023,32768,65535]
 return {'dhi_random':[(rng.randrange(65536),rng.randrange(256,65536)) for _ in range(2048)],
 'dhi_edge':[(n,d) for n in edge for d in div if d>=256],
 'd8':[(rng.randrange(65536),rng.randrange(1,256)) for _ in range(512)],
 'd0':[(rng.randrange(65536),0) for _ in range(64)],
 'mixed_edge':[(n,d) for n in edge for d in div]}
def call(cpu,entry,n,d):
 mem=cpu.mem;wr(mem,0xc010,n,4);wr(mem,0xc014,d,2)
 wr(mem,0xc018,0x9ac41875,4);wr(mem,0xc01c,0x6ff02d17,4)
 mem[0xc016]=0xa7;mem[0xc017]=0x69;mem[0xc020]=0xbd
 cpu.d=0;sp=cpu.sp
 cycles=cpu.call(entry,4000000)
 q,r,carry=expected(n,d,32,16)
 obs=(rd(mem,0xc018,4),rd(mem,0xc01c,4),cpu.c,rd(mem,0xc010,4),
 rd(mem,0xc014,2),mem[0xc016],mem[0xc017],mem[0xc020],cpu.sp)
 assert obs[0]==q and obs[1]&65535==r and obs[2]==carry
 assert obs[3:]==(n,d,0xa7,0x69,0xbd,sp)
 return cycles,obs
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args()
 released=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 out={'status':'PASS','type':'caller opt-in library-dependent code',
 'code_bytes':12,'normal_zp_growth':0,'extra_stack_bytes':2,
 'modified_residents':False,'public_entry_patched':False,'native_vice_calls':0,
 'maps':[hex(x) for x in MAPS],'profiles':{},'paired_inputs':0,'cpu_calls':0}
 workload=batches()
 for profile in PROFILES:
  prg=ROOT/profile/'resident'/('math_'+profile+'_game_math.prg')
  sha=hashlib.sha256(prg.read_bytes()).hexdigest()
  assert sha==released['reference_prg_sha256'][profile]
  data={'resident_sha256':sha,'maps':{}}
  for location in MAPS:
   asm=SRC.read_text().replace('* = $0800','* = $'+format(location,'04X'))
   instructions,labels,_=Assembler().assemble(asm)
   assert len(instructions)==12 and labels['U3216_N16_OPTIN']==location
   assert bytes(instructions[location+i] for i in range(12))==bytes.fromhex('20 40 31 a9 00 8d 1a c0 8d 1b c0 60')
   original,entry=load(profile);candidate,entry2=load(profile)
   assert entry==entry2 and all(candidate.mem[x]==0 for x in instructions)
   for addr,value in instructions.items():candidate.mem[addr]=value
   assert candidate.mem[0x31b0:0x31b3]==original.mem[0x31b0:0x31b3]
   data['maps'][hex(location)]={}
   for op in OPS:
    details={}
    for name,inputs in workload.items():
     oldsum=newsum=fast=slow=tie=0
     digest=hashlib.sha256()
     for n,d in inputs:
      digest.update(n.to_bytes(4,'little')+d.to_bytes(2,'little'))
      t0,o0=call(original,entry[op],n,d)
      t1,o1=call(candidate,location,n,d)
      assert o0==o1,(profile,op,name,n,d,o0,o1)
      oldsum+=t0;newsum+=t1;fast+=t1<t0;slow+=t1>t0;tie+=t1==t0
      out['paired_inputs']+=1;out['cpu_calls']+=2
     details[name]={'cases':len(inputs),'mean_before':oldsum/len(inputs),
      'mean_after':newsum/len(inputs),'mean_delta':(newsum-oldsum)/len(inputs),
      'faster':fast,'slower':slow,'equal':tie,'operand_sha256':digest.hexdigest()}
    assert details['dhi_random']['mean_delta'] < -300
    if profile=='v1_balanced':assert details['d8']['mean_delta']<0
    else:assert details['d8']['mean_delta']>0
    data['maps'][hex(location)][op]=details
   print(profile,hex(location),'DHI',*[round(data['maps'][hex(location)][k]['dhi_random']['mean_delta'],3) for k in OPS],flush=True)
  assert data['maps']['0x800']==data['maps']['0xa00'],'different timing/behavior after relocation'
  out['profiles'][profile]=data
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 OPT-IN N16 12B CORRECT',out['paired_inputs'],out['cpu_calls'],flush=True)
if __name__=='__main__':main()
