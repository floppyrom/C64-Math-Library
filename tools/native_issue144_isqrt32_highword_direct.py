#!/usr/bin/env python3
"""Real VICE native ISQRT32 highword seed clone, exact full-width operands."""
from __future__ import annotations
import os,sys,tempfile,json,hashlib,time,socket,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from issue144_isqrt32_highword_direct_experiment import build,PROFILES
from native_issue39_u24_txa_resident import command
from mini6502 import Assembler
N=24; IN=0x0400; OUT=0x0700; H=0x0B00
from validate_unsigned_division import api
def execute(p,t,optional,temp,port,exe):
 resident=(ROOT/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
 ld=int.from_bytes(resident[:2],"little");assert ld==0x1000
 mem=bytearray(65536);mem[ld:ld+len(resident)-2]=resident[2:]
 code=[]
 lines=["!cpu 6510","* = $0B00","    sei","    cld","    lda #$34","    sta $01","    jsr $3280","    ldx #$00","loop:"]
 for k in range(6):lines += [f"    lda ${IN+k*64:04X},x",f"    sta ${0xC010+k:04X}"]
 lines += ["    txa","    pha",f"    jsr ${t['entry'] if optional else api(p)['MATH_ISQRT32']:04X}","    php","    pla","    sta $C030","    pla","    tax","    lda $C030",f"    sta ${OUT+128:04X},x"]
 for k in range(2):lines += [f"    lda ${0xC008+k:04X}",f"    sta ${OUT+k*64:04X},x"]
 lines += ["    inx","    cpx #$18","    beq done","    jmp loop","done:","    jmp done"]
 program,labels,_=Assembler().assemble("\n".join(lines)+"\n")
 assert max(program)<0x0C00
 for k,b in program.items():mem[k]=b
 if optional:
  source=(ROOT/t['source']).read_text()
  candidate,lbl,_=Assembler().assemble(source)
  assert lbl['LCB40']==0xC00
  for k,b in candidate.items():assert mem[k]==0;mem[k]=b
 for i,(n,d) in enumerate(t['vectors']):
  for k in range(4):mem[IN+i+k*64]=(n>>(k*8))&255
  for k in range(2):mem[IN+i+(k+4)*64]=(d>>(k*8))&255
 stem=p+('_candidate' if optional else '_stock')
 image=temp/(stem+'.prg');dump=temp/(stem+'.dump');log=temp/(stem+'.log')
 image.write_bytes(bytes((IN&255,IN>>8))+mem[IN:0xD000])
 cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp","-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
 if p=='v4_reu_16m':
  cmd += ['-reu','-reusize','16384','-reuimage',str(ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu')]
 with log.open('w') as stream:
  proc=subprocess.Popen(cmd,cwd=temp,stdout=stream,stderr=stream)
  try:
   conn=None
   for _ in range(180):
    try:conn=socket.create_connection(('127.0.0.1',port),timeout=.2);break
    except (TimeoutError,ConnectionRefusedError):time.sleep(.06)
   if conn is None:raise RuntimeError(('VICE missing',log.read_text()[-1000:]))
   conn.settimeout(.8)
   try:
    command(conn,'load "'+str(image)+'" 0','Loading')
    command(conn,'break '+f"{labels['done']:04x}",'BREAK:')
    command(conn,'g '+f"{H:04x}",'Stop on  exec')
    command(conn,'bsave "'+str(dump)+'" 0 '+f"{OUT:04x} "+f"{OUT+191:04x}",'Saving')
    conn.sendall(b'quit\n')
   finally:conn.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 if not dump.exists():raise RuntimeError((p,optional,log.read_text()[-1300:]))
 raw=dump.read_bytes();assert len(raw)==192
 for i,(n,d) in enumerate(t['vectors']):
  value=raw[i]|raw[64+i]<<8
  assert value==__import__('math').isqrt(n),(p,optional,i,value,n)
  assert raw[128+i]&1==0
 return raw

SRC=ROOT/'optional/issue144_isqrt32_highword_direct'
VECTORS=[0,1,2,3,4,7,15,16,17,255,256,257,32767,65535,65536,65537,0x12345678,0x7FFFFFFF,0x80000000,0x80000001,0xBADDCAFE,0xFFFFFFFD,0xFFFFFFFE,0xFFFFFFFF]
assert len(VECTORS)==N

def main():
  vice=os.environ.get('VICE_WRAPPER','x64sc')
  report={'status':'PASS_REAL_NATIVE_VICE_UNRESTRICTED_ISQRT32_HIGHWORD_SEED','native_pairs_each_profile':N,'native_baseline_and_candidate_calls':0,'native_cpu_cycles_measured':False,'profiles':{}}
  with tempfile.TemporaryDirectory(prefix='issue144_isqrt_native_') as name:
    temp=Path(name)
    for i,p in enumerate(PROFILES):
      source,code=build(p)
      assert (SRC/(p+'.asm')).read_text()==source
      t={'source':str((SRC/(p+'.asm')).relative_to(ROOT)), 'label':'LCB40', 'entry':0xC00, 'public':'MATH_ISQRT32','result':0xC008, 'vectors':[(n,0) for n in VECTORS]}
      before=execute(p,t,False,temp,19900+2*i,vice)
      after=execute(p,t,True,temp,19901+2*i,vice)
      assert before[:128]==after[:128]
      assert all((before[128+j]^after[128+j])&1==0 for j in range(N))
      report['profiles'][p]={'status':'PASS_NATIVE_ALL_32BITS_ROOT_AND_CARRY','native_pairs':N,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'stock_public_entry':hex(api(p)['MATH_ISQRT32']),'source_code_bytes':len(code)}
      report['native_baseline_and_candidate_calls']+=N*2
      print('NATIVE VICE HIGHWORD ROOT',p,'PASS',N*2,flush=True)
    assert report['native_baseline_and_candidate_calls']==N*2*len(PROFILES)
    v4_test={'source':'', 'entry':0xC00, 'public':'MATH_ISQRT32', 'vectors':[(n,0) for n in VECTORS]}
    # V4 has a distinct REU lookup producer, not part of the RAM-side clone.
    v4_raw=execute('v4_reu_16m',v4_test,False,temp,19980,vice)
    assert len(v4_raw)==192
    report['v4_16m_REU_original_only']={'status':'PASS_ORIGINAL_REU_NATIVE_CORRECTNESS','native_calls':N,'actual_REU_image_loaded':True,'candidate_not_applicable':True}
    print('NATIVE VICE V4 REU reference (no new clone)',N,'PASS',flush=True)
  dst=ROOT/'validation/review/ISSUE144_ISQRT32_DIRECT_HIGHWORD_SEED_NATIVE_VICE.json'
  dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
  print('NATIVE 4 PROFILE PASS',report['native_baseline_and_candidate_calls'])
if __name__=='__main__':main()
