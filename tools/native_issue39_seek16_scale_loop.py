#!/usr/bin/env python3
"""Native x64sc compare SEEK16_INIT state of shipped and candidate source PRGs.

32 signed-delta x Euclidean/major-axis setup cases, all five profiles with
V3/V4 real REU, public X-slot, output carry, hardware SP and complete per-slot
INIT state used by four STEP variants. No native cycle timing.
"""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from native_issue39_u24_txa_resident import command
from benchmark_seek_profiles import api
from native_issue39_trig_angle import original_prg,original_reu
from mini6502 import CPU
from validate_source_build import seek_symbols
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
INPUT=0x0400;OUTPUT=0x0600;H=0x0B00;IO=0xC000;STRIDE=32
OFFSETS=(0,8,16,24,32,40,48,56,64,72,80,88,96,104,112,
 120,128,136,144,152,160,168,176,184,192,200,208,216,224,232,240)
FIELDS=len(OFFSETS)+2
assert OUTPUT+FIELDS*STRIDE<=H
VECTORS=((0,0,319,199,0x8100),(319,199,0,0,0x8180),
 (0,0,32767,199,0x8200),(32767,199,0,0,0x8300),
 (0,0,320,199,0x8100),(300,0,3,198,0x8200),
 (1,2,2,1,0x8100),(10,10,10,10,0x8100),
 (60000,20,59000,200,0x8180),(500,0,501,1,0x8200),
 (160,100,161,101,0x0100),(0,0,319,199,0x0100),
 (30000,255,50000,0,0x8380),(50000,0,30000,255,0x8380),
 (0,0,5000,19,0x8000),(1200,200,3,5,0x0080),
 (0,0,127,127,0x8100),(260,0,300,0,0x8200),
 (0,0,20,255,0x8400),(65535,255,33000,0,0x8300),
 (200,200,2,0,0x8180),(200,200,1,1,0x8100),
 (80,100,80,200,0x8180),(101,0,0,100,0x8200),
 (32000,3,60000,200,0x8100),(32000,3,32000,200,0x8100),
 (7000,250,200,0,0x8300),(12345,123,5678,100,0x8200),
 (320,200,321,201,0x8180),(0,0,0,1,0x8100),
 (319,199,318,199,0x8000),(300,200,300,200,0x0000))
COUNT=len(VECTORS)
assert COUNT==32
def sha(data):return hashlib.sha256(data).hexdigest()
def candidate(p):
 d=ROOT/("build_hybrid" if p==P[4] else "build_source")/"reference"/p
 info=json.loads((d/"source_build_manifest.json").read_text())
 return (d/info["output_prg"]).read_bytes()
def asm(p):
 a=api(p);st=a["MATH_SEEK16_POS_XL"]
 out=bytearray()
 def emit(*v):out.extend(v)
 def absop(op,addr):emit(op,addr&255,(addr>>8)&255)
 emit(0x78,0xd8,0xa9,0x35,0x85,0x01)
 absop(0x20,a["MATH_INIT"])
 emit(0xa2,0x00)
 loop=H+len(out)
 for inputpage,dest in enumerate((IO+0x20,IO+0x21,IO+0x22,IO,IO+1,IO+4,IO+0x10,IO+0x11)):
  absop(0xbd,INPUT+inputpage*STRIDE)
  absop(0x8d,dest)
 emit(0x8a,0x48,0x29,0x07,0xaa)
 for off,iooff in ((0,0x20),(8,0x21),(16,0x22)):
  absop(0xad,IO+iooff)
  absop(0x9d,st+off)
 absop(0x20,a["MATH_SEEK16_INIT"])
 emit(0x08,0x68)
 absop(0x8d,0x03fc)
 emit(0x68,0xa8)
 absop(0x8e,0x03fd)
 emit(0xba)
 absop(0x8e,0x03fe)
 absop(0xae,0x03fd)
 for index,off in enumerate(OFFSETS):
  absop(0xbd,st+off)
  absop(0x99,OUTPUT+index*STRIDE)
 for field,temp in ((len(OFFSETS),0x03fc),(len(OFFSETS)+1,0x03fe)):
  absop(0xad,temp)
  absop(0x99,OUTPUT+field*STRIDE)
 emit(0x98,0xaa,0xe8,0xe0,COUNT,0xf0,0x03)
 absop(0x4c,loop)
 stop=H+len(out)
 absop(0x4c,stop)
 assert len(out)<0x300
 return bytes(out),stop
def run_native(p,prg,reu,port,tmp,exe):
 ld=int.from_bytes(prg[:2],"little")
 mem=bytearray(65536);mem[ld:ld+len(prg)-2]=prg[2:]
 code,stop=asm(p)
 mem[H:H+len(code)]=code
 for i,(x0,y0,x1,y1,speed) in enumerate(VECTORS):
  parts=(x0&255,(x0>>8)&255,y0,x1&255,(x1>>8)&255,y1,speed&255,speed>>8)
  for page,v in enumerate(parts):mem[INPUT+page*STRIDE+i]=v
 img=tmp/(p+".prg");dump=tmp/(p+".dump");log=tmp/(p+".log")
 img.write_bytes(bytes((INPUT&255,INPUT>>8))+mem[INPUT:0xd000])
 args=[str(exe),"-console","-silent","-sounddev","dummy","-warp"]
 if reu:
  args+=["-reu","-reusize",("512" if p==P[2] else "16384"),"-reuimage",str(reu)]
 args+=["-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
 with log.open("w") as stream:
  proc=subprocess.Popen(args,cwd=tmp,stdout=stream,stderr=stream)
  try:
   sock=None
   for _ in range(225):
    try:
     sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.07)
   if sock is None:raise RuntimeError((p,"VICE not ready",log.read_text()[-1200:]))
   sock.settimeout(0.9)
   try:
    command(sock,'load "'+str(img)+'" 0',"Loading")
    command(sock,"break "+format(stop,"04x"),"BREAK:")
    command(sock,"g "+format(H,"04x"),"Stop on  exec")
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+format(OUTPUT+FIELDS*STRIDE-1,"04x"),"Saving")
    sock.sendall(b"quit\n")
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 assert dump.exists(),(p,"missing dump",log.read_text()[-1400:])
 d=dump.read_bytes()
 assert len(d)==FIELDS*STRIDE,(p,len(d))
 for i,(x0,y0,x1,y1,speed) in enumerate(VECTORS):
  arr=[d[f*STRIDE+i] for f in range(FIELDS)]
  # Carry bit on arrival is 1 precisely for the already-on-target case.
  assert (arr[-2]&1)==int(x0==x1 and y0==y1),(p,i,"wrong init carry")
 assert len({d[(FIELDS-1)*STRIDE+i] for i in range(COUNT)})==1,(p,"stack imbalance")
 return d
def main():
 release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 report={"status":"PASS_NATIVE_VICE_SEEK16_INIT_SCALER_5_PROFILE",
         "no_native_cycle_timing":True,"vectors_per_image":COUNT,
         "public_calls":0,"published_binaries_changed":False,"profiles":{}}
 with tempfile.TemporaryDirectory(prefix="seek16_scale_native_") as d:
  dir=Path(d);old=dir/"old";new=dir/"new";old.mkdir();new.mkdir()
  exe=os.getenv("VICE_WRAPPER","x64sc")
  for i,p in enumerate(P):
   resident=original_prg(p);optimized=candidate(p);reu=original_reu(p)
   assert sha(resident)==release["reference_prg_sha256"][p]
   assert sha(resident)!=sha(optimized)
   if reu:assert sha(reu.read_bytes())==release["reference_reu_sha256"][p]
   a=run_native(p,resident,reu,9800+2*i,old,exe)
   b=run_native(p,optimized,reu,9801+2*i,new,exe)
   assert a==b,(p,"native state or flags changed")
   report["profiles"][p]={"old_prg_sha256":sha(resident),
      "candidate_prg_sha256":sha(optimized),
      "native_state_sha256":sha(a),"complete_slot_fields_carry_stack_equal":True}
   report["public_calls"]+=2*COUNT
   print("SEEK16 SCALER NATIVE",p,2*COUNT,"PASS",flush=True)
 assert report["public_calls"]==320
 path=ROOT/"validation/review/ISSUE39_SEEK16_SCALE_LOOP_NATIVE_2026-10-14.json"
 path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("SEEK16 SCALER x64sc REAL NATIVE PASS",report["public_calls"],flush=True)
if __name__=="__main__":main()
