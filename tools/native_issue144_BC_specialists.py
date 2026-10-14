#!/usr/bin/env python3
"""Native x64sc B/C optional specialist versus true V1-V5 resident public call.

Remainder-only has a narrower output contract: check R16 and C only (not Q).
ISQRT requires the V4 16-MiB REU *image*, not merely the REU CPU model.
VICE runs check arithmetic/carry, not native cycle timing. CPU cycle metrics
come solely from the deterministic mini6502 paired tests.
"""
from __future__ import annotations
import hashlib, json, math, os, socket, subprocess, sys, tempfile, time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,api
from native_issue39_u24_txa_resident import command
from validate_signed_division import div_expected
N=24; IN=0x0400; OUT=0x0700; H=0x0B00
TESTS={
 "mod_pow2":{"source":"optional/issue144_pow2_mod32_16/mod32_16_pow2_remainder_only.asm",
    "label":"MATH_UMOD32_16_POW2_RONLY","entry":0x0C00,
    "public":"MATH_UMOD32_16","result":0xC01C,
    "vectors":[(x&0xFFFFFFFF,1<<k) for k in range(16) for x in
              [0xFFFFFFFF,0x12345678,0x00010001]][::2][:N]},
 "signed_mod_pow2":{"source":"optional/issue144_pow2_smod32_16/smod32_16_r_only.asm",
    "label":"MATH_SMOD32_16_POSPOW2_RONLY","entry":0x0C80,
    "public":"MATH_SMOD32_16","result":0xC01C,
    "vectors":[(n&0xFFFFFFFF,1<<k) for k in range(12) for n in
              [0xFFFFFFFF,0x80000001]][:N]},
 "isqrt_low16":{"source":"optional/issue144_isqrt32_u16/low16_dispatch.asm",
    "label":"MATH_ISQRT32_LOW16_ONLY","entry":0x0C40,
    "public":"MATH_ISQRT32","result":0xC008,
    "vectors":[(n,0) for n in
         [0,1,2,3,4,7,15,16,17,63,64,65,127,255,256,257,
          1023,1024,1025,4095,4096,32767,65534,65535]]}
}
def sha(b):return hashlib.sha256(b).hexdigest()
def source_bytes(t):
 asm=(R/t["source"]).read_text()
 code,lbl,_=Assembler().assemble(asm)
 assert lbl[t["label"]]==t["entry"]
 return code,sha(asm.encode())
def harness(entry,result):
 lines=["!cpu 6510","* = $0B00","    sei","    cld","    lda #$34",
       "    sta $01","    jsr $3280","    ldx #$00","loop:"]
 for i in range(6):
  lines+= [f"    lda ${IN+i*64:04X},x",f"    sta ${0xC010+i:04X}"]
 lines+=["    txa","    pha",f"    jsr ${entry:04X}",
         "    php","    pla","    sta $C030","    pla","    tax","    lda $C030",
         f"    sta ${OUT+128:04X},x"]
 for i in range(2):
  lines += [f"    lda ${result+i:04X}",f"    sta ${OUT+i*64:04X},x"]
 lines += ["    inx","    cpx #$18","    beq done","    jmp loop","done:","    jmp done"]
 obj,labels,_=Assembler().assemble("\n".join(lines)+"\n")
 assert max(obj)<0x0C00
 return obj,labels["done"]
def execute(p,t,optional,temp,port,exe):
 resident=(R/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
 ld=int.from_bytes(resident[:2],"little");assert ld==0x1000
 memory=bytearray(65536);memory[ld:ld+len(resident)-2]=resident[2:]
 entry=t["entry"] if optional else api(p)[t["public"]]
 code,stop=harness(entry,t["result"])
 for pc,b in code.items():memory[pc]=b
 if optional:
  prog,_=source_bytes(t)
  for pc,b in prog.items():
   assert memory[pc]==0,("optional overlaps existing image",p,pc)
   memory[pc]=b
 for i,(num,den) in enumerate(t["vectors"]):
  for k in range(4):memory[IN+i+k*64]=(num>>(k*8))&255
  for k in range(2):memory[IN+i+(k+4)*64]=(den>>(k*8))&255
 image=temp/(p+"_"+t["public"]+"_"+str(optional)+".prg")
 dump=image.with_suffix(".dump");log=image.with_suffix(".log")
 image.write_bytes(bytes((IN&255,IN>>8))+memory[IN:0xD000])
 cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
      "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
      "-initbreak","reset"]
 if p=="v4_reu_16m" and t["public"]=="MATH_ISQRT32":
  cmd+=["-reu","-reusize","16384","-reuimage",
      str(R/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu")]
 with log.open("w") as output:
  proc=subprocess.Popen(cmd,cwd=temp,stdout=output,stderr=output)
  try:
   sock=None
   for _ in range(160):
    try:sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.06)
   if sock is None:raise RuntimeError(("VICE not listening",log.read_text()[-600:]))
   sock.settimeout(.8)
   try:
    command(sock,'load "'+str(image)+'" 0',"Loading")
    command(sock,"break "+f"{stop:04x}","BREAK:")
    command(sock,"g "+f"{H:04x}","Stop on  exec")
    command(sock,'bsave "'+str(dump)+'" 0 '+f"{OUT:04x} "+f"{OUT+191:04x}","Saving")
    sock.sendall(b"quit\n")
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 if not dump.exists():raise RuntimeError((p,t["public"],log.read_text()[-1200:]))
 raw=dump.read_bytes();assert len(raw)==192
 for i,(n,d) in enumerate(t["vectors"]):
  expected=((n&(d-1)) if t["public"]=="MATH_UMOD32_16" else
            div_expected(n,32,d,16,32,16)[1] if t["public"]=="MATH_SMOD32_16"
            else math.isqrt(n))
  value=raw[i]|raw[64+i]<<8
  assert value==expected,(p,t["public"],optional,i,value,expected)
  assert raw[128+i]&1==0,(p,t["public"],optional,"carry")
 return raw
def main():
 exe=os.getenv("VICE_WRAPPER","x64sc")
 report={"status":"PASS_NATIVE_VICE_BC_DOMAIN_SPECIALISTS","profiles":{},
   "native_cycle_timing_measured":False,"stock_resident_binaries_changed":False,
   "quotient_from_remainder_only_producer":False,
   "V4_sqrt_real_REU_image_loaded":True}
 with tempfile.TemporaryDirectory(prefix="issue144_BC_native_") as folder:
  tmp=Path(folder)
  for pi,p in enumerate(PROFILES):
   row={}
   for j,(key,t) in enumerate(TESTS.items()):
    old=execute(p,t,False,tmp,18100+pi*20+j*2,exe)
    new=execute(p,t,True,tmp,18101+pi*20+j*2,exe)
    assert old[:128]==new[:128]
    assert all((old[128+i]^new[128+i])&1==0 for i in range(N))
    row[key]={"cases_each":N,"original_native":N,"specialist_native":N,
       "results_and_carry_equal":True,"source_sha256":source_bytes(t)[1]}
    print("NATIVE BC",p,key,N*2,"PASS",flush=True)
   report["profiles"][p]=row
 out=R/"validation/review/ISSUE144_BC_SPECIALISTS_NATIVE_VICE.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 B/C NATIVE VICE ALL PASS",len(PROFILES)*len(TESTS)*N*2)
if __name__=="__main__":main()
