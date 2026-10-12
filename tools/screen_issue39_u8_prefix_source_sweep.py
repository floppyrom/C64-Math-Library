#!/usr/bin/env python3
"""Issue39 bounded 8-bit UDIV quotient-prefix manual architecture sweep.

Source-generates the existing compare/subtract prefix + shift-divisor tail
for K={8,12,16,20,24,28}. Relocatable source resides in caller-owned RAM.
All five current release residents remain unchanged. Native OptiSearch timings
are deliberately NOT compared directly against public ABI timing.
"""
from pathlib import Path
import argparse,hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from benchmark_unsigned_common_corpus import corpus
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,expected,load,rd,wr
N,D,Q,R=(0xc010,0xc014,0xc018,0xc01c)
KS=(8,12,16,20,24,28)
MAPS={'ram_0800':0x0800,'ram_0851':0x0851}
SCRATCH=0x70
def generate(K,origin):
 assert 1<=K<255
 lines=['!cpu 6510',f'* = ${origin:04X}',
 'CANDIDATE_UDIV8_PUBLIC:',
 '    jmp UD8_div',
 'UD8_zero:',
 '    sta $C018',
 '    sta $C01C',
 '    sec',
 '    rts',
 'UD8_div:',
 '    lda $C014',
 '    beq UD8_zero',
 '    lda $C010',
 '    cmp $C014',
 '    bcs UD8_cont0',
 '    sta $C01C',
 '    lda #0',
 '    sta $C018',
 '    rts']
 for i in range(K):
  lines.extend([f'UD8_cont{i}:',
   '    sbc $C014',
   '    cmp $C014',
   f'    bcs UD8_cont{i+1}',
   '    sta $C01C',
   f'    lda #{i+1}',
   '    sta $C018',
   '    rts'])
 lines.extend([f'UD8_cont{K}:',
 '    sta $C01C',
 '    lda $C014',
 f'    sta ${SCRATCH:02X}',
 '    ldx #0',
 '    stx $C018',
 'UD8_align:',
 f'    lda ${SCRATCH:02X}',
 '    asl',
 '    bcs UD8_aligned',
 '    cmp $C01C',
 '    bcc UD8_take',
 '    beq UD8_take',
 'UD8_aligned:',
 '    lda $C01C',
 'UD8_bits:',
 f'    cmp ${SCRATCH:02X}',
 '    bcc UD8_no_sub',
 f'    sbc ${SCRATCH:02X}',
 'UD8_no_sub:',
 '    rol $C018',
 f'    lsr ${SCRATCH:02X}',
 '    dex',
 '    bpl UD8_bits',
 '    sta $C01C',
 '    lda $C018',
 '    clc',
 f'    adc #{K}',
 '    sta $C018',
 '    rts',
 'UD8_take:',
 f'    sta ${SCRATCH:02X}',
 '    inx',
 '    bne UD8_align'])
 return '\n'.join(lines)+'\n'
def inputs():
 _,pairs=corpus('MATH_UDIV8',8,8,0,2048)
 rng=random.Random(0xC6398010)
 edges=(0,1,2,3,4,7,8,15,16,23,31,32,63,64,127,128,129,254,255)
 return {
  'official_common':[(n,d) for n,d,_ in pairs],
  'uniform':[(rng.randrange(256),rng.randrange(1,256)) for _ in range(512)],
  'small_divisor':[(rng.randrange(256),rng.randrange(1,16)) for _ in range(512)],
  'large_divisor':[(rng.randrange(256),rng.randrange(128,256)) for _ in range(512)],
  'quotient_0':[(rng.randrange(d),d) for d in (rng.randrange(1,256) for _ in range(512))],
  'quotient_1':[(d+rng.randrange(d),d) for d in (rng.randrange(1,128) for _ in range(512))],
  'powers_of_two':[(rng.randrange(256),1<<rng.randrange(8)) for _ in range(512)],
  'divisor_zero':[(rng.randrange(256),0) for _ in range(64)],
  'structured_edges':[(n,d) for n in edges for d in edges]}
def run_one(cpu,entry,n,d):
 mem=cpu.mem
 wr(mem,N,n,1);wr(mem,D,d,1)
 wr(mem,Q,0xa79b6c58,4);wr(mem,R,0xe47b9256,4)
 mem[0xc012]=0xab;mem[0xc016]=0xcd;mem[0xc024]=0x72
 cpu.d=0;cpu.c=1;sp=cpu.sp
 cycles=cpu.call(entry,1_000_000)
 q,r,c=expected(n,d,8,8)
 got=(mem[Q],mem[R],cpu.c,mem[N],mem[D],
      bytes(mem[Q+1:Q+4]).hex(),bytes(mem[R+1:R+4]).hex(),
      mem[0xc012],mem[0xc016],mem[0xc024],cpu.sp)
 assert got==(q,r,c,n,d,bytes.fromhex('6c9ba7').hex(),
  bytes.fromhex('927be4').hex(),0xab,0xcd,0x72,sp),(entry,n,d,got,q,r,c)
 return cycles
def run(profile=None,ks=None,maps=None):
 profiles=(profile,) if profile else PROFILES
 selected_ks=(ks,) if ks is not None else KS
 selected_maps={k:v for k,v in MAPS.items() if maps is None or k==maps}
 matrix=inputs()
 sha_status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 result={'status':'PASS_BOUNDED_PREFIX_SCREEN_RESEARCH_ONLY',
   'corpus':{name:{'cases':len(inp),'sha256':hashlib.sha256(
     b''.join(bytes((n,d)) for n,d in inp)).hexdigest()} for name,inp in matrix.items()},
   'profiles':{},'K_values':list(selected_ks),'locations':list(selected_maps),
   'paired_inputs':0,'cpu_calls':0,'native_vice_calls':0,
   'normal_resident_changed':False,'public_api_changed':False,
   'caller_owned_extra_zp_bytes':1,
   'source_algorithm':'direct compare-subtract quotient K prefix; restoring tail; existing V1/V2 algorithm re-synthesized'}
 for p in profiles:
  prg=ROOT/p/'resident'/f'math_{p}_game_math.prg'
  sha=hashlib.sha256(prg.read_bytes()).hexdigest()
  assert sha_status['reference_prg_sha256'][p]==sha
  p_out={'resident_sha256':sha,'variants':{}}
  for K in selected_ks:
   p_out['variants'][str(K)]={}
   for map_name,origin in selected_maps.items():
    code,labels,_=Assembler().assemble(generate(K,origin))
    assert len(code)<900 and all(0x800<=a<0x1000 for a in code)
    old,public=load(p);new,_=load(p)
    assert all(new.mem[a]==0 for a in code)
    for addr,val in code.items():new.mem[addr]=val
    assert labels['CANDIDATE_UDIV8_PUBLIC']==origin
    code_sha=hashlib.sha256(bytes(code[a] for a in sorted(code))).hexdigest()
    detail={'code_bytes':len(code),'code_sha256':code_sha,'extra_zp':1,'classes':{}}
    for kind,vec in matrix.items():
     totals=[0,0];faster=slower=equal=0;worst=-10**8;digest=hashlib.sha256()
     for n,d in vec:
      t0=run_one(old,public['MATH_UDIV8'],n,d)
      t1=run_one(new,origin,n,d)
      dt=t1-t0
      totals[0]+=t0;totals[1]+=t1;faster+=dt<0;slower+=dt>0;equal+=dt==0
      worst=max(worst,dt)
      digest.update(t0.to_bytes(4,'little')+t1.to_bytes(4,'little'))
      result['paired_inputs']+=1;result['cpu_calls']+=2
     detail['classes'][kind]={
      'cases':len(vec),'old_mean':totals[0]/len(vec),
      'candidate_mean':totals[1]/len(vec),
      'delta_mean':(totals[1]-totals[0])/len(vec),
      'faster':faster,'slower':slower,'equal':equal,
      'worst_regression':worst,'cycle_pair_sha256':digest.hexdigest()}
    p_out['variants'][str(K)][map_name]=detail
    print(p,'K',K,map_name,'code',len(code),'official delta',
     round(detail['classes']['official_common']['delta_mean'],3),
     'uniform delta',round(detail['classes']['uniform']['delta_mean'],3),flush=True)
  result['profiles'][p]=p_out
 return result
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--profile',choices=PROFILES)
 ap.add_argument('--K',type=int,choices=KS)
 ap.add_argument('--map',choices=list(MAPS))
 ap.add_argument('--out',type=Path)
 a=ap.parse_args()
 rep=run(a.profile,a.K,a.map)
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(rep,sort_keys=True,indent=2)+'\n')
 print('ISSUE39 UDIV8 SOURCE PREFIX SWEEP PASS',rep['paired_inputs'],rep['cpu_calls'],flush=True)
if __name__=='__main__':main()
