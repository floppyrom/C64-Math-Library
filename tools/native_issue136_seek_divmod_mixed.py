#!/usr/bin/env python3
"""Native x64sc mixed SEEK16 + UDIV/UMOD public-call proof, V1..V5.

Verifies fixed candidate resident image with real REU on V3/V4. No native
cycle timing and no pre-fix native equivalence claim (the old images overlap).
"""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
sys.path.insert(0,str(R/"routines/movement"))
from seek_model import expected_frames
from native_issue39_signed_multiply_family import api
from native_issue39_trig_angle import original_reu
from native_issue39_u24_txa_resident import command
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
H=0x0b00
OUTPUT=0x0600
STRIDE=32
COUNT=13
SLOT=2
FIELDS=10
IDX=0x03f0
def sha(b):return hashlib.sha256(b).hexdigest()
def candidate(p):
 d=R/("build_hybrid/reference" if p==P[-1] else "build_source/reference")/p
 man=json.loads((d/"source_build_manifest.json").read_text())
 return (d/man["output_prg"]).read_bytes()
def assembly(a):
 code=bytearray()
 def b(*v):code.extend(v)
 def ab(op,where):b(op,where&255,(where>>8)&255)
 def immstore(where,value):
  b(0xa9,value&255)
  ab(0x8d,where)
 def jsr(name):ab(0x20,a[name])
 b(0x78,0xd8,0xa9,0x35,0x85,0x01)
 jsr("MATH_INIT")
 for addr,v in (
  (a["MATH_SEEK16_POS_XL"]+SLOT,0),
  (a["MATH_SEEK16_POS_XH"]+SLOT,0),
  (a["MATH_SEEK16_POS_Y"]+SLOT,0),
  (a["MATH_X"],20),(a["MATH_X"]+1,0),
  (a["MATH_Y"],10),
  (a["MATH_N"],0),(a["MATH_N"]+1,2),
 ):
  immstore(addr,v)
 b(0xa2,SLOT)
 jsr("MATH_SEEK16_INIT")
 # Fixed, intentionally adversarial 1/1 quotient and zero remainder.
 for address in (a["MATH_N"],a["MATH_D"]):immstore(address,1)
 for address in (a["MATH_N"]+1,a["MATH_N"]+2,a["MATH_N"]+3,
                 a["MATH_D"]+1,a["MATH_D"]+2,a["MATH_D"]+3):immstore(address,0)
 immstore(IDX,0)
 loop=H+len(code)
 for op,outslots in (
   ("MATH_UDIV32_16",((a["MATH_Q"],0),(a["MATH_R"],1))),
   ("MATH_UMOD32_16",((a["MATH_R"],2),)),
   ("MATH_UDIV32_32",((a["MATH_Q"],3),)),
   ("MATH_UMOD32_32",((a["MATH_R"],4),)),
 ):
  jsr(op)
  ab(0xac,IDX) # LDY <index>
  for address,j in outslots:
   ab(0xad,address)
   ab(0x99,OUTPUT+j*STRIDE) # STA absolute,Y
 b(0xa2,SLOT)
 jsr("MATH_SEEK16_STEP")
 b(0x08,0x68) # PHP / PLA, keep returned status snapshot
 ab(0xac,IDX)
 ab(0x99,OUTPUT+8*STRIDE)
 for j,where in enumerate((a["MATH_SEEK16_POS_XL"]+SLOT,
                           a["MATH_SEEK16_POS_XH"]+SLOT,
                           a["MATH_SEEK16_POS_Y"]+SLOT),start=5):
  ab(0xad,where)
  ab(0x99,OUTPUT+j*STRIDE)
 b(0xba,0x8a) # TSX, TXA: snapshot hardware stack pointer
 ab(0x99,OUTPUT+9*STRIDE)
 ab(0xee,IDX)
 ab(0xad,IDX)
 b(0xc9,COUNT,0xf0,0x03) # CMP COUNT, BEQ skip JMP
 ab(0x4c,loop)
 stop=H+len(code)
 ab(0x4c,stop)
 assert len(code)<0x300,(len(code),stop)
 return bytes(code),stop

def run_native(p,prg,reu,port,tmp,exe):
 names=api(p)
 mem=bytearray(65536)
 load=int.from_bytes(prg[:2],"little")
 mem[load:load+len(prg)-2]=prg[2:]
 code,stop=assembly(names)
 mem[H:H+len(code)]=code
 image=tmp/(p+"_mixed.prg")
 dump=tmp/(p+"_mixed.dump")
 log=tmp/(p+"_mixed.log")
 image.write_bytes(bytes((0,4))+mem[0x0400:0xd000])
 cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp"]
 if reu:
  cmd+=["-reu","-reusize",("512" if p==P[2] else "16384"),"-reuimage",str(reu)]
 cmd+=["-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
 with log.open("w") as stream:
  proc=subprocess.Popen(cmd,cwd=tmp,stdout=stream,stderr=stream)
  try:
   sock=None
   for _ in range(240):
    try:
     sock=socket.create_connection(("127.0.0.1",port),timeout=.2)
     break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.06)
   assert sock is not None,(p,"VICE did not start",log.read_text()[-1200:])
   sock.settimeout(1.2)
   try:
    command(sock,'load "'+str(image)+'" 0',"Loading")
    command(sock,"break "+format(stop,"04x"),"BREAK:")
    command(sock,"g "+format(H,"04x"),"Stop on  exec")
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+
                    format(OUTPUT+FIELDS*STRIDE-1,"04x"),"Saving")
    sock.sendall(b"quit\n")
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 assert dump.exists(),(p,"native result absent",log.read_text()[-1200:])
 output=dump.read_bytes()
 assert len(output)==FIELDS*STRIDE,(p,"wrong dump size",len(output))
 return output

def check(p,data):
 path=expected_frames(0,0,20,10,0x0200,"step")
 stacks=set()
 for i in range(COUNT):
  columns=[data[j*STRIDE+i] for j in range(FIELDS)]
  assert columns[:5]==[1,0,0,1,0],(p,i,"DIV/MOD output",columns[:5])
  want,carry=path[i] if i<len(path) else ((20,10),True)
  x=columns[5]|columns[6]<<8
  y=columns[7]
  assert (x,y)==want,(p,i,"movement mismatch",(x,y),want)
  assert columns[8]&1==int(carry),(p,i,"carry mismatch",columns[8],carry)
  stacks.add(columns[9])
 assert len(stacks)==1,(p,"stack imbalance",stacks)
 return {"native_calls":COUNT*5, "native_seeking_calls":COUNT,
         "source_output_sha256":sha(data),"stack_pointer":next(iter(stacks)),
         "expected_path_frames":len(path)}

def main():
 exe=os.environ.get("VICE_WRAPPER","x64sc")
 proof={"status":"PASS_NATIVE_VICE_MIXED_SEEK_DIVMOD",
        "native_cycle_timing_measured":False,"profiles":{},
        "public_calls":0,"private_optisearch_published":False}
 with tempfile.TemporaryDirectory(prefix="issue136_mixed_native_") as t:
  tmp=Path(t)
  for i,p in enumerate(P):
   binary=candidate(p)
   reu=original_reu(p)
   if reu:assert reu.exists()
   result=run_native(p,binary,reu,12110+i,tmp,exe)
   row=check(p,result)
   row["candidate_prg_sha256"]=sha(binary)
   proof["public_calls"]+=row["native_calls"]
   proof["profiles"][p]=row
   print("ISSUE136 MIXED NATIVE",p,"PASS",row,flush=True)
 assert proof["public_calls"]==COUNT*5*len(P)
 out=R/"validation/review/ISSUE136_SEEK_DIVMOD_NATIVE_VICE.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n")
 print("ISSUE136 325 NATIVE MIXED PUBLIC CALLS PASS",flush=True)
if __name__=="__main__":main()
