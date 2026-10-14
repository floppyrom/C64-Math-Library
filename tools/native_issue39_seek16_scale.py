#!/usr/bin/env python3
"""Native x64sc SEEK16 INIT scaler: shipped vs source-built public ABI.

16 deterministic cases per resident, plus 248 state bytes after all calls.
Validates true distinct optimized PRGs, real REU on V3/V4, public signed X,
input preservation, carry, stack and initialized movement state vs CPU model.
Timing claims are CPU-model only; not native VICE cycles.
"""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU,REV
REV[0xAF]=("lax","abs")
REV[0xBF]=("lax","absy")
from native_issue39_signed_multiply_family import api
from native_issue39_u24_txa_resident import command
from native_issue39_trig_angle import original_prg,original_reu
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
POINTS=(
 (0,0,319,199,0x8100),(319,199,0,0,0x8180),
 (0,10,319,10,0x8300),(319,10,0,10,0x8080),
 (0,0,319,199,0x0100),(319,199,0,0,0x0200),
 (50,20,50,190,0x8100),(100,100,100,100,0x8100),
 (0,0,255,199,0x8200),(100,0,319,100,0x8480),
 (300,0,0,190,0x0180),(0,50,32767,50,0x8100),
 (32767,100,0,100,0x8180),(1000,20,32000,110,0x8100),
 (31,99,33,101,0x0080),(319,199,10,20,0x8400))
COUNT=len(POINTS);assert COUNT<32
STRIDE=32;INPUT=0x0400;OUTPUT=0x0600;H=0x0B00;LOOPZ=0x02FF
SCR=(0x02A0,0x02A1,0x02A2)
IO=0xC000
def sha(b):return hashlib.sha256(b).hexdigest()
def candidate(p):
 d=R/("build_hybrid" if p==P[4] else "build_source")/"reference"/p
 man=json.loads((d/"source_build_manifest.json").read_text())
 return (d/man["output_prg"]).read_bytes()
def harness(names):
 code=bytearray()
 def b(*v):code.extend(v)
 def absop(op,addr):b(op,addr&255,(addr>>8)&255)
 b(0x78,0xD8,0xA9,0x35,0x85,0x01)
 absop(0x20,names["MATH_INIT"])
 b(0xA9,0);absop(0x8D,LOOPZ)
 loop=H+len(code)
 absop(0xAE,LOOPZ)
 # Eight input planes; 3 start position bytes saved in test-only scratch.
 addresses=(*SCR,IO,IO+1,IO+4,IO+0x10,IO+0x11)
 for j,adr in enumerate(addresses):
  absop(0xBD,INPUT+j*STRIDE)
  absop(0x8D,adr)
 b(0x8A,0x29,0x07,0xAA)
 for temp,dest in zip(SCR,(names["MATH_SEEK16_POS_XL"],
                           names["MATH_SEEK16_POS_XH"],
                           names["MATH_SEEK16_POS_Y"])):
  absop(0xAD,temp);absop(0x9D,dest)
 absop(0x20,names["MATH_SEEK16_INIT"])
 b(0x08,0x68);absop(0x8D,IO+0x30) # flags after init
 absop(0x8E,IO+0x31)              # preserved X slot
 b(0xBA);absop(0x8E,IO+0x32)      # TSX STX stack
 absop(0xAE,LOOPZ)
 fields=(IO+0x30,IO+0x31,IO+0x32,IO,IO+1,IO+4,IO+0x10,IO+0x11)
 for j,adr in enumerate(fields):
  absop(0xAD,adr);absop(0x9D,OUTPUT+j*STRIDE)
 b(0xE8);absop(0x8E,LOOPZ)
 b(0xE0,COUNT,0xF0,0x03)
 absop(0x4C,loop)
 stop=H+len(code);absop(0x4C,stop)
 assert H+len(code)<0x1000
 return bytes(code),stop
def cpu_reference(p,prg,reu):
 ld=int.from_bytes(prg[:2],"little")
 mem=bytearray(65536);mem[ld:ld+len(prg)-2]=prg[2:]
 c=CPU(mem,reu=bytearray(reu.read_bytes()) if reu else None)
 names=api(p);c.d=0;c.call(names["MATH_INIT"],2_000_000)
 out=[];base=names["MATH_SEEK16_POS_XL"]
 for i,(x0,y0,x1,y1,speed) in enumerate(POINTS):
  slot=i&7
  for addr,value in ((names["MATH_SEEK16_POS_XL"]+slot,x0&255),
   (names["MATH_SEEK16_POS_XH"]+slot,(x0>>8)&255),
   (names["MATH_SEEK16_POS_Y"]+slot,y0),
   (names["MATH_X"],x1&255),(names["MATH_X"]+1,(x1>>8)&255),
   (names["MATH_Y"],y1),(names["MATH_N"],speed&255),
   (names["MATH_N"]+1,speed>>8)):
   c.mem[addr]=value
  c.x=slot;c.d=0
  c.call(names["MATH_SEEK16_INIT"],2_000_000)
  assert c.x==slot and c.sp==0xfd
  out.append((c.c,slot,0xfd,x1&255,(x1>>8)&255,y1,speed&255,speed>>8))
 return out,bytes(c.mem[base:base+248])
def emulate(p,prg,reu,tmp,port,exe,tag):
 mem=bytearray(65536);ld=int.from_bytes(prg[:2],"little")
 mem[ld:ld+len(prg)-2]=prg[2:]
 names=api(p)
 code,stop=harness(names)
 mem[H:H+len(code)]=code
 for i,(x0,y0,x1,y1,speed) in enumerate(POINTS):
  for plane,value in enumerate((x0&255,(x0>>8)&255,y0,x1&255,(x1>>8)&255,y1,
                                speed&255,speed>>8)):
   mem[INPUT+plane*STRIDE+i]=value
 prefix=p+"_"+tag
 image=tmp/(prefix+".prg")
 dump=tmp/(prefix+".dump")
 state=tmp/(prefix+".state")
 log=tmp/(prefix+".log")
 image.write_bytes(bytes((INPUT&255,INPUT>>8))+mem[INPUT:0xd000])
 cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp"]
 if reu:
  cmd+=["-reu","-reusize",("512" if p==P[2] else "16384"),"-reuimage",str(reu)]
 cmd+=["-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
 with log.open("w") as out:
  proc=subprocess.Popen(cmd,cwd=tmp,stdout=out,stderr=out)
  try:
   sock=None
   for _ in range(220):
    try:
     sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.07)
   if sock is None:raise RuntimeError((prefix,"VICE monitor unavailable",log.read_text()[-1100:]))
   sock.settimeout(.9)
   try:
    command(sock,'load "'+str(image)+'" 0',"Loading")
    command(sock,"break "+format(stop,"04x"),"BREAK:")
    command(sock,"g "+format(H,"04x"),"Stop on  exec")
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+format(OUTPUT+8*STRIDE-1,"04x"),"Saving")
    base=names["MATH_SEEK16_POS_XL"]
    command(sock,'bsave "'+str(state)+'" 0 '+format(base,"04x")+" "+format(base+248-1,"04x"),"Saving")
    sock.sendall(b"quit\n")
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 assert dump.exists() and state.exists(),(prefix,"missing VICE dump",log.read_text()[-1500:])
 result=dump.read_bytes(); final=state.read_bytes()
 assert len(result)==8*STRIDE and len(final)==248,(prefix,len(result),len(final))
 expected,reference_state=cpu_reference(p,prg,reu)
 assert final==reference_state,(prefix,"248 state bytes disagree")
 for i,expect in enumerate(expected):
  actual=tuple(result[j*STRIDE+i] for j in range(8))
  # flags: only C bit, others can differ since caller uses PHP/PLA
  assert (actual[0]&1,)+actual[1:]==expect,(prefix,i,actual,expect)
 return {"cases":COUNT,"output_sha256":sha(result),
   "state_sha256":sha(final),"all_inputs_flags_slot_stack_and_248_state_bytes_match_model":True}
def main():
 st=json.loads((R/"RELEASE_STATUS.json").read_text())
 result={"status":"PASS_SEEK16_SCALE_NATIVE_VICE_OLD_NEW","native_cycle_timing_measured":False,
    "old_new_public_calls":0,"published_binaries_changed":False,"profiles":{}}
 with tempfile.TemporaryDirectory(prefix="seek16scale_native_") as folder:
  tmp=Path(folder)
  for i,p in enumerate(P):
   old=original_prg(p);new=candidate(p)
   assert sha(old)==st["reference_prg_sha256"][p]
   assert old!=new,(p,"stale candidate")
   reu=original_reu(p)
   if reu:assert sha(reu.read_bytes())==st["reference_reu_sha256"][p]
   a=emulate(p,old,reu,tmp,9900+i*2,os.getenv("VICE_WRAPPER","x64sc"),"baseline")
   b=emulate(p,new,reu,tmp,9901+i*2,os.getenv("VICE_WRAPPER","x64sc"),"candidate")
   assert a["state_sha256"]==b["state_sha256"],(p,"candidate state difference")
   assert a["output_sha256"]==b["output_sha256"],(p,"candidate output difference")
   result["profiles"][p]={"baseline_sha256":sha(old),"candidate_sha256":sha(new),
     "native_public_calls_each":COUNT,"state_sha256":a["state_sha256"],
     "per_call_output_sha256":a["output_sha256"],"reu_sha256":sha(reu.read_bytes()) if reu else None}
   result["old_new_public_calls"]+=2*COUNT
   print("NATIVE SEEK16 INIT",p,"PASS",2*COUNT,flush=True)
 assert result["old_new_public_calls"]==2*COUNT*len(P)
 output=R/"validation/review/ISSUE39_SEEK16_SCALE_NATIVE_2026-10-14.json"
 output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("SEEK16 NATIVE OLD/NEW REAL VICE PASS",result["old_new_public_calls"],flush=True)
if __name__=="__main__":main()
