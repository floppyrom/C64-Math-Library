#!/usr/bin/env python3
"""Native x64sc 5-profile S32/16 DIV/MOD alias direct-jump equivalence.

Unrestricted signed operands + denominator zero. Original vs disposable
patched resident public entries, complete quotient and remainder, C, inputs,
X/Y, SP and flags. Native tests correctness, NOT CPU cycle timing.
"""
from __future__ import annotations
import hashlib,json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_signed_division import PROFILES,parse_api,div_expected
from issue144_signed_divmod_alias_direct_research import EXPECTED_CHAINS,API
from issue144_signed32_divmod_alias_installer import prepare
from native_issue39_u24_txa_resident import command
N=24;STRIDE=64;IN=0x0200;OUT=0x0500;H=0x0B00
FIELDS=[0xc018+i for i in range(4)]+[0xc01c+i for i in range(2)]+[0xc010+i for i in range(6)]+[0xc030,0xc032,0xc034,0xc036,0xc038]
assert OUT+len(FIELDS)*STRIDE<H
VECTORS=[(0,0),(0xffffffff,0),(0x80000000,0),(0x7fffffff,0),(0,1),(0,-1 & 0xffff),
(1,1),(0xffffffff,1),(0x80000000,0xffff),(0x7fffffff,0xffff),(0x80000000,0x8000),
(0x7fffffff,0x8000),(0x80000000,0x7fff),(0x7fffffff,0x7fff),(0xdeadbeef,0x0100),
(0x80000001,0x0100),(0xffffffff,0x0002),(0xffff8000,0x8000),(0x00008000,0x8000),
(0x00010000,0x0002),(0xffff0000,0xfffe),(0x00000001,0x0000),(0x12345678,0x4321),(0xfedcba98,0xabcd)]
assert len(VECTORS)==N

def sha(b):return hashlib.sha256(b).hexdigest()
def harness(entry,enable=None,disable=None):
 lines=['!cpu 6510','* = $0B00','start:','  sei','  cld','  ldx #$FF','  txs','  lda #$34','  sta $01','  jsr $3280']
 if enable is not None:lines.append(f'  jsr ${enable:04X}')
 lines+=['  ldx #$00','loop:']
 for i in range(6):
  lines.extend([f'  lda ${IN+i*STRIDE:04X},x',f'  sta ${0xc010+i:04X}'])
 lines.extend(['  txa','  pha','  lda #$00','  tax','  tay','  sec',f'  jsr ${entry:04X}',
               '  php','  pla','  sta $C030','  stx $C034','  sty $C036','  tsx','  stx $C038','  pla','  tax'])
 for i,address in enumerate(FIELDS):
  lines.extend([f'  lda ${address:04X}',f'  sta ${OUT+i*STRIDE:04X},x'])
 lines.extend(['  inx','  cpx #$18','  beq done','  jmp loop','done:'])
 if disable is not None:lines.append(f'  jsr ${disable:04X}')
 lines+=['halt:','  jmp halt']
 code,label,_=Assembler().assemble('\n'.join(lines)+'\n')
 assert min(code)==H and max(code)<0x0c00
 return code,label['halt']

def execute(p,op,optimized,tmp,port,exe):
 raw=(ROOT/p/'resident'/f'math_{p}_game_math.prg').read_bytes()
 ld=int.from_bytes(raw[:2],'little');assert ld==0x1000
 m=bytearray(65536);m[ld:ld+len(raw)-2]=raw[2:]
 entries=parse_api(p);entry=entries[op]
 prepared=prepare(p) if optimized else None
 if prepared is not None:
  asm,program,labels,changes=prepared
  for pc,val in program.items():
   assert m[pc]==0,(p,hex(pc),'installer occupies real code')
   m[pc]=val
  source,stop=harness(entry,labels['DIRECT_S32_16_ENABLE'],labels['DIRECT_S32_16_DISABLE'])
 else:source,stop=harness(entry)
 for pc,b in source.items():m[pc]=b
 for index,(n,d) in enumerate(VECTORS):
  for byte in range(6):m[IN+byte*STRIDE+index]=(n>>(8*byte))&255 if byte<4 else (d>>(8*(byte-4)))&255
 stem=p+'_'+op+'_'+str(optimized)
 prg=tmp/(stem+'.prg');dump=tmp/(stem+'.dump');saved=tmp/(stem+'.state');log=tmp/(stem+'.log')
 prg.write_bytes(bytes((IN&255,IN>>8))+m[IN:0xD000])
 cmd=[str(exe),'-console','-silent','-sounddev','dummy','-warp','-remotemonitor',
     '-remotemonitoraddress',f'127.0.0.1:{port}','-initbreak','reset']
 with log.open('w') as output:
  proc=subprocess.Popen(cmd,cwd=tmp,stdout=output,stderr=output)
  try:
   sock=None
   for _ in range(250):
    try:sock=socket.create_connection(('127.0.0.1',port),timeout=.2);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.05)
   if sock is None:raise RuntimeError(('VICE not listening',log.read_text()[-1200:]))
   sock.settimeout(.9)
   try:
    command(sock,'load "'+str(prg)+'" 0','Loading')
    command(sock,'break '+format(stop,'04x'),'BREAK:')
    command(sock,'g '+format(H,'04x'),'Stop on  exec')
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUT,'04x')+' '+format(OUT+STRIDE*len(FIELDS)-1,'04x'),'Saving')
    sock.sendall(b'quit\n')
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=4)
   except subprocess.TimeoutExpired:proc.kill()
 if not dump.exists():raise RuntimeError((p,op,optimized,'missing dump',log.read_text()[-1000:]))
 data=dump.read_bytes();assert len(data)==STRIDE*len(FIELDS)
 for i,(n,d) in enumerate(VECTORS):
  row=[data[k*STRIDE+i] for k in range(len(FIELDS))]
  q=sum(row[k]<<(8*k) for k in range(4));rem=sum(row[4+k]<<(8*k) for k in range(2))
  ni=sum(row[6+k]<<(8*k) for k in range(4));di=sum(row[10+k]<<(8*k) for k in range(2))
  qexp,rexp,cexp=div_expected(n,32,d,16,32,16)
  assert (q,rem,row[12]&1)==(qexp,rexp,cexp),(p,op,optimized,i,hex(n),hex(d),(q,rem,row[12]&1),(qexp,rexp,cexp))
  assert (ni,di)==(n,d)
 return data

def main():
 exe=os.getenv('VICE_WRAPPER','x64sc')
 rec={'status':'PASS_FIVE_PROFILE_NATIVE_SIGNED32_16_JMP_DIRECT',
      'profiles':{},'paired_input_cases':len(VECTORS),'native_baseline_and_candidate_calls':0,
      'native_cycle_measurement':False,'ordinary_resident_PRGs_unchanged':True}
 with tempfile.TemporaryDirectory(prefix='issue144_signed_divmod_jmp_') as td:
  temp=Path(td)
  for i,p in enumerate(PROFILES):
   rec['profiles'][p]={}
   for k,op in enumerate(API):
    original=execute(p,op,False,temp,19800+4*i+2*k,exe)
    candidate=execute(p,op,True,temp,19801+4*i+2*k,exe)
    assert original==candidate,(p,op,'complete VICE output/flags/register state changed')
    rec['profiles'][p][op]={'native_cases_per_version':N,'saved_cpu_cycles_from_model':EXPECTED_CHAINS[p][op][1],
                            'all_status_registers_outputs_and_stack_exact':True,
                            'source_assembled_ENABLE_DISABLE_executed_on_native':True,
                            'native_original_byte_restoration_rechecked_by_CPU_model':True,
                            'output_sha256':sha(original)}
    rec['native_baseline_and_candidate_calls']+=2*N
    print('NATIVE SIGNED32 DIVMOD JMP',p,op,'PASS',2*N,flush=True)
 out=ROOT/'validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_NATIVE_VICE.json'
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
 print('ALL',rec['status'],rec['native_baseline_and_candidate_calls'])
if __name__=='__main__':main()
