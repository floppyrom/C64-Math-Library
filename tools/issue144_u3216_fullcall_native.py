#!/usr/bin/env python3
"""Experimental real x64sc check: full ordinary UDIV32_16/UMOD32_16 public calls.

Run after issue144_u3216_fullcall_source_transplant_screen.py in CI.
Does not change the published binary, does not measure native cycles.
"""
import hashlib
import json
import os
import random
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from native_issue39_u24_txa_resident import command
from validate_signed_division import parse_api

PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
OPS=("MATH_UDIV32_16","MATH_UMOD32_16")
COUNT,STRIDE,IN,OUT,H=24,32,0x0200,0x0500,0x0B00
FIELDS=[0xC018+i for i in range(4)]+[0xC01C+i for i in range(2)]+[0xC010+i for i in range(6)]+[0xC030,0xC032]
assert OUT+STRIDE*len(FIELDS)<H

def vectors():
 r=random.Random(0x144B3216)
 return [(0,0),(1,0),(0xffffffff,0),(0xffffffff,1),(0xffffffff,2),
         (0xffffffff,255),(0xffffffff,256),(0xffffffff,65535),
         (0x80000000,65535),(0x80000000,0x8000),(0x7fffffff,0x8000),
         (0x12345678,0x4321),(0xdeadbeef,0x8001),(0x10000,1),
         (0x10001,65535),(0xffff,65535)]+[
          (r.getrandbits(32),r.randrange(1,65536)) for _ in range(8)]
V=vectors()
assert len(V)==COUNT

def harness(entry):
 lines=["!cpu 6510","* = $0B00","start:","sei","cld","ldx #$FF","txs",
        "lda #$34","sta $01","jsr $3280","ldx #$00","loop:"]
 for i in range(6):
  lines += ["lda $"+format(IN+i*STRIDE,"04X")+",x",
            "sta $"+format(0xC010+i,"04X")]
 lines += ["txa","pha","lda #$00","tax","tay","sec",
           "jsr $"+format(entry,"04X"),
           "php","pla","sta $C030","tsx","stx $C032","pla","tax"]
 for j,addr in enumerate(FIELDS):
  lines += ["lda $"+format(addr,"04X"),
            "sta $"+format(OUT+j*STRIDE,"04X")+",x"]
 lines += ["inx","cpx #$18","beq done","jmp loop","done:","halt:","jmp halt"]
 code,labels,_=Assembler().assemble("\n".join(lines)+"\n")
 assert min(code)==H and max(code)<0x0d00
 return code,labels["halt"]

def native(profile,flavor,op,image,entry,tmp,port,exe):
 ld=int.from_bytes(image[:2],"little");assert ld==0x1000
 m=bytearray(65536);m[ld:ld+len(image)-2]=image[2:]
 code,stop=harness(entry)
 for pc,val in code.items():m[pc]=val
 for idx,(n,d) in enumerate(V):
  for i in range(6):
   m[IN+i*STRIDE+idx]=(n>>(8*i))&255 if i<4 else (d>>(8*(i-4)))&255
 stem=profile+"_"+flavor+"_"+op
 prg=tmp/(stem+".prg");dump=tmp/(stem+".dump");log=tmp/(stem+".log")
 prg.write_bytes(bytes([IN&255,IN>>8])+m[IN:0xD000])
 cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
      "-remotemonitor","-remotemonitoraddress",
      "127.0.0.1:"+str(port),"-initbreak","reset"]
 with log.open("w") as output:
  proc=subprocess.Popen(cmd,cwd=tmp,stdout=output,stderr=output)
  try:
   sock=None
   for _ in range(250):
    try:sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.05)
   if sock is None:raise RuntimeError(("no remote monitor",log.read_text()[-1000:]))
   sock.settimeout(.9)
   try:
    command(sock,'load "'+str(prg)+'" 0',"Loading")
    command(sock,"break "+format(stop,"04x"),"BREAK:")
    command(sock,"g "+format(H,"04x"),"Stop on  exec")
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUT,"04x")+' '+format(OUT+STRIDE*len(FIELDS)-1,"04x"),"Saving")
    sock.sendall(b"quit\n")
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=4)
   except subprocess.TimeoutExpired:proc.kill()
 if not dump.exists():raise RuntimeError((profile,flavor,op,log.read_text()[-1500:]))
 b=dump.read_bytes();assert len(b)==STRIDE*len(FIELDS)
 for i,(n,d) in enumerate(V):
  row=[b[j*STRIDE+i] for j in range(len(FIELDS))]
  q=sum(row[j]<<(j*8) for j in range(4))
  rem=sum(row[4+j]<<(j*8) for j in range(2))
  ni=sum(row[6+j]<<(j*8) for j in range(4))
  di=sum(row[10+j]<<(j*8) for j in range(2))
  want=((n//d,n%d,0) if d else (0,0,1))
  assert (q,rem,row[12]&1)==want,(profile,flavor,op,i,hex(n),hex(d),q,rem,row[12],want)
  assert (ni,di)==(n,d),(profile,flavor,op,i,"N/D corruption")
  assert row[13]==0xfe,(profile,flavor,op,i,"stack changed",row[13])
 return b

def main():
 result={"status":"PASS_REAL_X64SC_PUBLIC_DIVMOD_SOURCE_RESEARCH",
         "profiles":{},"native_calls":0,"native_timing_measured":False,
         "production_prgs_unchanged":True}
 exe=os.getenv("VICE_WRAPPER","x64sc")
 with tempfile.TemporaryDirectory(prefix="u3216_fullcall_vice_") as td:
  tmp=Path(td)
  for idx,profile in enumerate(PROFILES):
   old=(ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")).read_bytes()
   md=ROOT/"build_u3216"/"reference"/profile
   manifest=json.loads((md/"source_build_manifest.json").read_text())
   new=(md/manifest["output_prg"]).read_bytes()
   oldapi=parse_api(profile)
   newapi={k:int(str(v).replace("$","0x"),0) for k,v in manifest["public_entries"].items()}
   result["profiles"][profile]={}
   for k,op in enumerate(OPS):
    olddata=native(profile,"stock",op,old,oldapi[op],tmp,18100+idx*4+k,exe)
    newdata=native(profile,"changed",op,new,newapi[op],tmp,18120+idx*4+k,exe)
    for row in range(len(FIELDS)):
     for i in range(COUNT):
      pos=row*STRIDE+i
      if row==12:assert (olddata[pos]&1)==(newdata[pos]&1)
      else:assert olddata[pos]==newdata[pos],(profile,op,row,i,"changed result")
    result["profiles"][profile][op]={"native_calls":COUNT*2,"abi_equal":True,
                                    "stock_record_sha256":hashlib.sha256(olddata).hexdigest(),
                                    "changed_record_sha256":hashlib.sha256(newdata).hexdigest()}
    result["native_calls"]+=COUNT*2
    print(profile,op,"native PASS",COUNT*2,flush=True)
 assert result["native_calls"]==288
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
