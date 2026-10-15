#!/usr/bin/env python3
"""Real native x64sc validation: all-sign SHR16 cloned core, mixed-call safe.

RAM test layout: input $0200..$03FF, output $0400..$07FF, self-modifying
independent producer $0800..$0DC0, test harness $0E00..$0FFF.
All public MATH_INIT, MATH_SMUL32 and MATH_UMUL32 use ordinary resident code.
Only the SHR16 public JMP target in a disposable memory image is redirected.
"""
from __future__ import annotations
import json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from issue144_independent_signed_shr16 import make_source,sha
from validate_unsigned_division import PROFILES
from native_issue39_signed_multiply_family import api,pairs,COUNT
from native_issue39_u24_txa_resident import command
IN=0x0200;OUT=0x0400;STRIDE=64;H=0x0E00
FIELDS=[0xC008+j for j in range(6)]+[0xC000+j for j in range(8)]+[0xC030,0xC032]
assert IN+8*STRIDE==OUT and OUT+len(FIELDS)*STRIDE==0x0800<H
REPORT="validation/review/ISSUE144_SIGNED_SHR16_INDEPENDENT_NATIVE_VICE.json"

def harness(public):
 code=bytearray()
 def b(*v):code.extend(v)
 def absop(op,addr):b(op,addr&255,addr>>8)
 b(0x78,0xD8,0xA9,0x34,0x85,0x01)  # SEI CLD RAM visible
 absop(0x20,public["MATH_INIT"])
 b(0xA2,0x00)
 loop=H+len(code)
 for j in range(8):
  absop(0xBD,IN+j*STRIDE)
  absop(0x8D,0xC000+j)
 b(0xA9,0x91)
 for j in range(8):absop(0x8D,0xC008+j)
 b(0x8A,0x48)
 b(0x38);absop(0x20,public["MATH_SMUL32"])
 b(0x38);absop(0x20,public["MATH_UMUL32"])
 b(0xA9,0x91)
 for j in range(8):absop(0x8D,0xC008+j)
 b(0x38);absop(0x20,public["MATH_SMUL32_SHR16"])
 b(0x08,0x68);absop(0x8D,0xC030)
 b(0xBA);absop(0x8E,0xC032)
 b(0x68,0xAA)
 for j,addr in enumerate(FIELDS):
  absop(0xAD,addr)
  absop(0x9D,OUT+j*STRIDE)
 b(0xE8,0xE0,COUNT,0xF0,0x03)
 absop(0x4C,loop)
 stop=H+len(code)
 absop(0x4C,stop)
 assert H+len(code)<0x1000
 return bytes(code),stop

def execute(profile,producer,entry,changed,port,folder,vice):
 resident=(R/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
 assert int.from_bytes(resident[:2],"little")==0x1000
 mem=bytearray(65536)
 mem[0x1000:0x1000+len(resident)-2]=resident[2:]
 if changed:
  old_full=bytes(mem[0x3C40:0x3C70])
  for pc,v in producer.items():
   assert mem[pc]==0,(profile,hex(pc),"clone code RAM occupied")
   mem[pc]=v
  assert mem[0x5E15]==0x4C
  mem[0x5E16:0x5E18]=entry.to_bytes(2,"little")
  assert bytes(mem[0x3C40:0x3C70])==old_full
 machine,stop=harness(api(profile))
 assert all(pc<H for pc in producer)
 mem[H:H+len(machine)]=machine
 vectors=pairs(32)
 for i,(x,y) in enumerate(vectors):
  for j in range(8):
   mem[IN+j*STRIDE+i]=((x>>(j*8))&255) if j<4 else ((y>>((j-4)*8))&255)
 stem=profile+("_clone" if changed else "_baseline")
 image=folder/(stem+".prg");dump=folder/(stem+".dump");log=folder/(stem+".log")
 image.write_bytes(bytes((IN&255,IN>>8))+mem[IN:0xD000])
 cmd=[vice,"-console","-silent","-sounddev","dummy","-warp",
      "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
      "-initbreak","reset"]
 with log.open("w") as stdout:
  proc=subprocess.Popen(cmd,cwd=folder,stdout=stdout,stderr=stdout)
  try:
   conn=None
   for _ in range(200):
    try:
     conn=socket.create_connection(("127.0.0.1",port),timeout=.2);break
    except (TimeoutError,ConnectionRefusedError):time.sleep(.07)
   if conn is None:raise RuntimeError(("VICE unavailable",log.read_text()[-1200:]))
   conn.settimeout(.7)
   try:
    command(conn,'load "'+str(image)+'" 0',"Loading")
    command(conn,"break "+f"{stop:04x}","BREAK:")
    command(conn,"g "+f"{H:04x}","Stop on  exec")
    command(conn,'bsave "'+str(dump)+'" 0 '+f"{OUT:04x} "+
       f"{OUT+len(FIELDS)*STRIDE-1:04x}","Saving")
    conn.sendall(b"quit\n")
   finally:conn.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 if not dump.exists():raise AssertionError((profile,changed,log.read_text()[-1200:]))
 content=dump.read_bytes()
 assert len(content)==len(FIELDS)*STRIDE
 stacks=set()
 for i,(x,y) in enumerate(vectors):
  row=[content[j*STRIDE+i] for j in range(len(FIELDS))]
  signed=lambda a:a-(1<<32) if a&0x80000000 else a
  product=((signed(x)*signed(y))>>16)&((1<<48)-1)
  result=sum(row[j]<<(8*j) for j in range(6))
  assert result==product,(profile,changed,i,hex(result),hex(product))
  xx=sum(row[6+j]<<(8*j) for j in range(4))
  yy=sum(row[10+j]<<(8*j) for j in range(4))
  assert (xx,yy)==(x,y)
  assert row[14]&1==0,(profile,changed,"carry",i)
  stacks.add(row[15])
 assert len(stacks)==1,(profile,changed,"unstable stack",stacks)
 return content,{"native_vectors":COUNT,
     "signed_and_unsigned_full_producer_calls_interleaved":True,
     "output_six_bytes_correct":True,"inputs_preserved":True,
     "carry_clear":True,"stack_stable":True,"dump_sha256":sha(content)}

def main():
 vice=os.getenv("VICE_WRAPPER","x64sc")
 state=json.loads((R/"RELEASE_STATUS.json").read_text())
 report={"status":"PASS_NATIVE_FIVE_PROFILE_INDEPENDENT_SIGNED_SHR16_MIXED",
   "profiles":{},"original_and_candidate_calls":0,"native_cycle_measurement":False,
   "ordinary_SMUL32_UMUL32_unchanged":True,
   "normal_resident_PRGs_REUs_modified":False,"IRQ_reentrant":False}
 with tempfile.TemporaryDirectory(prefix="issue144_signed_independent_") as path:
  folder=Path(path)
  for i,profile in enumerate(PROFILES):
   source,code,entry,_,_=make_source(profile)
   prg=(R/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
   assert sha(prg)==state["reference_prg_sha256"][profile]
   base,a=execute(profile,code,entry,False,19700+i*2,folder,vice)
   alt,b=execute(profile,code,entry,True,19701+i*2,folder,vice)
   for j in range(15):
    if j==14:
     assert all(base[j*STRIDE+k]&1==alt[j*STRIDE+k]&1==0 for k in range(COUNT))
    else:
     assert base[j*STRIDE:(j+1)*STRIDE]==alt[j*STRIDE:(j+1)*STRIDE],(
       profile,j,"native result/input difference")
   assert len(set(base[15*STRIDE+i] for i in range(COUNT)))==1
   assert len(set(alt[15*STRIDE+i] for i in range(COUNT)))==1
   report["profiles"][profile]={
      "status":"PASS_REAL_X64SC_SEQUENTIAL_MIXED_S32_U32",
      "baseline":a,"independent":b,"source_sha256":sha(source.encode()),
      "executable_bytes":len(code),"signed_output_inputs_carry_equal":True}
   report["original_and_candidate_calls"]+=COUNT*2
   print("NATIVE ISSUE144 INDEPENDENT SIGNED",profile,"PASS",COUNT*2,flush=True)
 assert report["original_and_candidate_calls"]==240
 target=R/REPORT;target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("NATIVE ISSUE144 INDEPENDENT SIGNED SHR16 PASS 240")
if __name__=="__main__":main()
