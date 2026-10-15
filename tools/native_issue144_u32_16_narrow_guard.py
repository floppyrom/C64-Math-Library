#!/usr/bin/env python3
"""Native x64sc qualified full Q32+R16+C all-domain 22-byte UDIV32_16 guard.

Native tests only correctness, not CPU cycle timing. A/X/Y and N/Z/V
are expressly volatile in USER_MANUAL.md. Tests include divide-by-zero,
negative-looking unsigned values, narrow and full-width numerators,
and sequential repeated calls to both public aliases.
"""
from __future__ import annotations
import hashlib,json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,api,expected
from native_issue39_u24_txa_resident import command
SOURCE='optional/issue144_u32_16_narrow_guard/guard.asm'
OUTPATH='validation/review/ISSUE144_U32DIV32_16_NARROW_GUARD_NATIVE_VICE.json'
N=24;IN=0x0400;OUT=0x0700;H=0x0B00;STRIDE=64
LAYOUT=[0xC018+i for i in range(4)]+[0xC01C+i for i in range(2)]+[0xC010+i for i in range(4)]+[0xC014+i for i in range(2)]+[0xC030,0xC032]
assert len(LAYOUT)==14 and OUT+len(LAYOUT)*STRIDE<H

PAIRS=[
(0,0),(1,0),(65535,0),(0xffffffff,0),(0x80000000,0),
(0,1),(1,1),(65535,1),(65536,1),(0xffffffff,1),
(32768,32768),(65535,32768),(65535,65535),(65536,65535),
(0xffffffff,65535),(0x80000000,0x8000),(0x7fffffff,0x7fff),
(0x1234,0x23),(0x12345678,0x23),(0xabcdffff,0x100),
(0x00010000,0x1111),(0x00ffffff,0xffff),(0x00000001,0xffff),
(0x7fff,0x8000)]
assert len(PAIRS)==N

def source_bytes():
 text=(R/SOURCE).read_text();d,labels,_=Assembler().assemble(text)
 assert len(d)==22 and labels['MATH_UDIV32_16_NARROW_GUARDED']==0x0C80
 return d,hashlib.sha256(text.encode()).hexdigest()

def harness(entry):
 lines=['!cpu 6510','* = $0B00','  sei','  cld','  lda #$34','  sta $01',
        '  jsr $3280','  ldx #0','loop:']
 for i in range(6):
  lines += [f'  lda ${IN+i*STRIDE:04X},x',f'  sta ${0xC010+i:04X}']
 lines+=['  txa','  pha','  ldx #$5A','  ldy #$CC',f'  jsr ${entry:04X}',
        '  php','  pla','  sta $C030','  tsx','  stx $C032',
        '  pla','  tax']
 for i,p in enumerate(LAYOUT):
  lines += [f'  lda ${p:04X}',f'  sta ${OUT+i*STRIDE:04X},x']
 lines+=['  inx','  cpx #$18','  beq done','  jmp loop','done:','  jmp done']
 code,labels,_=Assembler().assemble('\n'.join(lines)+'\n')
 assert max(code)<0x0C80
 return code,labels['done']

def execute(profile,which,entry,optional,temp,port,exe):
 original=(R/profile/'resident'/f'math_{profile}_game_math.prg').read_bytes()
 assert original[:2]==b'\x00\x10'
 mem=bytearray(65536)
 mem[0x1000:0x1000+len(original)-2]=original[2:]
 prog,stop=harness(entry)
 for pc,b in prog.items():
  assert mem[pc]==0,(profile,hex(pc),'harness clashes with resident')
  mem[pc]=b
 if optional:
  code,_=source_bytes()
  for pc,b in code.items():
   assert mem[pc]==0,(profile,hex(pc),'optional code clashes with resident')
   mem[pc]=b
 for i,(n,d) in enumerate(PAIRS):
  for b in range(4):mem[IN+b*STRIDE+i]=(n>>(8*b))&255
  for b in range(2):mem[IN+(4+b)*STRIDE+i]=(d>>(8*b))&255
 path=temp/(profile+'_'+which+('_guard' if optional else '_stock')+'.prg')
 dest=path.with_suffix('.dump');logs=path.with_suffix('.log')
 path.write_bytes(b'\x00\x02'+mem[0x0200:0xD000])
 cmd=[str(exe),'-console','-silent','-sounddev','dummy','-warp',
     '-remotemonitor','-remotemonitoraddress',f'127.0.0.1:{port}',
     '-initbreak','reset']
 with logs.open('w') as output:
  proc=subprocess.Popen(cmd,cwd=temp,stdout=output,stderr=output)
  try:
   sock=None
   for _ in range(160):
    try:
     sock=socket.create_connection(('127.0.0.1',port),timeout=.2);break
    except (TimeoutError,ConnectionRefusedError):time.sleep(.07)
   if sock is None:raise RuntimeError(('VICE did not start',logs.read_text()[-1200:]))
   sock.settimeout(.8)
   try:
    command(sock,'load "'+str(path)+'" 0','Loading')
    command(sock,'break '+f'{stop:04x}','BREAK:')
    command(sock,'g '+f'{H:04x}','Stop on  exec')
    command(sock,'bsave "'+str(dest)+'" 0 '+f'{OUT:04x} '+f'{OUT+len(LAYOUT)*STRIDE-1:04x}','Saving')
    sock.sendall(b'quit\n')
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 if not dest.exists():raise RuntimeError((profile,which,optional,logs.read_text()[-1600:]))
 raw=dest.read_bytes()
 assert len(raw)==len(LAYOUT)*STRIDE,(profile,len(raw))
 seen_sp=set()
 for i,(n,d) in enumerate(PAIRS):
  row=[raw[j*STRIDE+i] for j in range(len(LAYOUT))]
  q=sum(row[j]<<(8*j) for j in range(4))
  rem=row[4]|row[5]<<8
  num=sum(row[6+j]<<(8*j) for j in range(4))
  den=row[10]|row[11]<<8
  flag=row[12]&1
  eq,er,ec=expected(n,d,32,16)
  assert (q,rem,flag)==(eq,er,ec),(profile,which,optional,i,(q,rem,flag),(eq,er,ec))
  assert (num,den)==(n,d),(profile,which,optional,i,'input')
  seen_sp.add(row[13])
 assert len(seen_sp)==1,(profile,which,optional,'stack mismatch',seen_sp)
 return raw

def main():
 exe=os.getenv('VICE_WRAPPER','x64sc')
 code,srcsha=source_bytes()
 report={'status':'PASS_NATIVE_ALL_FIVE_FULL_QR_C_NARROW_GUARD',
         'precondition':'none; all 32-bit unsigned inputs supported',
         'code_bytes':len(code),'source_sha256':srcsha,
         'native_old_and_candidate_calls':0,
         'registered_volatile_XY_and_NZV_may_differ':True,
         'native_cycles_measured':False,'normal_resident_PRGs_unchanged':True,'profiles':{}}
 with tempfile.TemporaryDirectory(prefix='issue144_u32_16guard_') as folder:
  temp=Path(folder)
  for i,p in enumerate(PROFILES):
   results={}
   for j,op in enumerate(('MATH_UDIV32_16','MATH_UMOD32_16')):
    base=execute(p,op,api(p)[op],False,temp,18500+10*i+2*j,exe)
    alt=execute(p,op,0x0C80,True,temp,18501+10*i+2*j,exe)
    for k in range(12):
     assert base[k*STRIDE:(k+1)*STRIDE]==alt[k*STRIDE:(k+1)*STRIDE],(p,op,'Q,R,N,D',k)
    assert all(base[12*STRIDE+k]&1==alt[12*STRIDE+k]&1 for k in range(N)),(p,op,'C')
    assert len(set(base[13*STRIDE+k] for k in range(N)))==len(set(alt[13*STRIDE+k] for k in range(N)))==1
    results[op]={'baseline_native_calls':N,'candidate_native_calls':N,'complete_Q32_R16_C_inputs_stack_equal':True}
    report['native_old_and_candidate_calls']+=2*N
    print('NATIVE U32 DIV32_16 GUARD',p,op,2*N,'PASS',flush=True)
   report['profiles'][p]=results
 assert report['native_old_and_candidate_calls']==5*2*2*N
 out=R/OUTPATH
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('ISSUE144 GUARD FULL Q/R NATIVE PASS',report['native_old_and_candidate_calls'])
if __name__=='__main__':main()
