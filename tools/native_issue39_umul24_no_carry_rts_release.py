#!/usr/bin/env python3
"""Native x64sc original/candidate V2/V3/V4 UMUL24 + SMUL24 no-carry CLC elimination.

3 profiles × 2 public entries × 48 vectors × 2 complete original/candidate
images = 576 actual 6510 calls. Validates product, input, carry and sentinels.
No native cycle timing claims.
"""
from pathlib import Path
import hashlib,json,os,random,socket,subprocess,tempfile,time,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from native_issue39_u24_txa_resident import command
PROFILE=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
PARENT="ffe8d35dcc84b861b38e75d3a38cf73081545f5c"
APIS={"MATH_UMUL24":0x3060,"MATH_SMUL24":0x3BF0}
H=0x0b00;INPUT=0x0400;OUTPUT=0x0600;STRIDE=64;COUNT=48;IO=0xc000
FIELDS=[IO+8+i for i in range(6)]+[IO+i for i in range(3)]+[IO+4+i for i in range(3)]+[0xc030,0xc024,0xc032]
assert OUTPUT+len(FIELDS)*STRIDE < H
def sha(b):return hashlib.sha256(b).hexdigest()
def operands():
 r=random.Random(0xC6392424)
 vals=[0,1,2,3,127,128,255,256,257,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffff,0x800000,0xffffff]
 pairs=[(x,y) for x,y in [(0,0),(0xffffff,0xffffff),(0,0xffffff),(0xffffff,0),
  (1,1),(255,256),(0x10000,0x10001),(0xffffff,1),(0x800000,0x800000)]]
 while len(pairs)<COUNT:
  pairs.append((r.choice(vals) if r.random()<.4 else r.getrandbits(24),
                r.choice(vals) if r.random()<.4 else r.getrandbits(24)))
 return pairs

def make_harness(entry):
 out=bytearray()
 def b(*xs):out.extend(xs)
 def absop(op,a):b(op,a&255,a>>8)
 b(0x78,0xd8,0xa9,0x34,0x85,0x01) # SEI, CLD, RAM under ROM
 absop(0x20,0x3280) # math_init
 b(0xa2,0x00)
 loop=H+len(out)
 for j in range(6):
  absop(0xbd,INPUT+j*STRIDE)
  absop(0x8d,IO+(j if j<3 else j+1))
 b(0xa9,0x91)
 for j in range(6):absop(0x8d,IO+8+j)
 b(0xa9,0xa6);absop(0x8d,0xc024)
 b(0x8a,0x48,0x38) # save index, carry=1
 absop(0x20,entry)
 b(0x08,0x68);absop(0x8d,0xc030)  # PHP PLA store flags
 b(0xba);absop(0x8e,0xc032)  # stack before original index PLA
 b(0x68,0xaa)
 for j,a in enumerate(FIELDS):
  absop(0xad,a);absop(0x9d,OUTPUT+j*STRIDE)
 b(0xe8,0xe0,COUNT,0xf0,0x03)
 absop(0x4c,loop)
 stop=H+len(out);absop(0x4c,stop)
 assert len(out)<0x300
 return bytes(out),stop

def native(prg,api,label,port,folder,exe):
 base=int.from_bytes(prg[:2],"little")
 assert base==0x1000
 mem=bytearray(65536);mem[base:base+len(prg)-2]=prg[2:]
 code,stop=make_harness(APIS[api]);mem[H:H+len(code)]=code
 pairs=operands()
 for i,(x,y) in enumerate(pairs):
  for j in range(3):
   mem[INPUT+j*STRIDE+i]=(x>>(8*j))&255
   mem[INPUT+(j+3)*STRIDE+i]=(y>>(8*j))&255
 image=folder/(label+".prg");dump=folder/(label+".dump");log=folder/(label+".log")
 image.write_bytes(bytes([INPUT&255,INPUT>>8])+mem[INPUT:0xd000])
 cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
      "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
      "-initbreak","reset"]
 with log.open("w") as dest:
  process=subprocess.Popen(cmd,cwd=folder,stdout=dest,stderr=dest)
  try:
   sock=None
   for _ in range(180):
    try:
     sock=socket.create_connection(("127.0.0.1",port),timeout=0.15);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(0.07)
   if sock is None:raise RuntimeError((label,"VICE connection failed",log.read_text()[-500:]))
   sock.settimeout(0.3)
   try:
    command(sock,'load "'+str(image)+'" 0',"Loading")
    command(sock,"break "+format(stop,"04x"),"BREAK:")
    command(sock,"g "+format(H,"04x"),"Stop on  exec")
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+
            format(OUTPUT+len(FIELDS)*STRIDE-1,"04x"),"Saving")
    sock.sendall(b"quit\n")
   finally:sock.close()
  finally:
   process.terminate()
   try:process.wait(timeout=3)
   except subprocess.TimeoutExpired:process.kill()
 if not dump.exists():raise RuntimeError((label,"no dump",log.read_text()[-900:]))
 data=dump.read_bytes();assert len(data)==STRIDE*len(FIELDS),(label,len(data))
 result=[]
 for i,(x,y) in enumerate(pairs):
  v=[data[j*STRIDE+i] for j in range(len(FIELDS))]
  z=sum(v[k]<<(8*k) for k in range(6))
  xx=sum(v[k+6]<<(8*k) for k in range(3))
  yy=sum(v[k+9]<<(8*k) for k in range(3))
  signed=lambda n:n-(1<<24) if n&(1<<23) else n
  product=((signed(x)*signed(y)) if api=="MATH_SMUL24" else x*y)&((1<<48)-1)
  assert (z,xx,yy,v[12]&1,v[13])==(product,x,y,0,0xa6),(
    label,i,hex(x),hex(y),v,hex(product))
  result.append((z,xx,yy,v[12]&1,v[13],v[14]))
 return {"dump_sha256":sha(data),"records":result}

def main():
 state=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 row=state["issue39_umul24_no_carry_rts_2026_10_13"]
 assert row["status"]=="PASS_STAGED_NATIVE_VICE_PENDING"
 result={"status":"PASS_NATIVE_SOURCE_INSTALLED_NOT_YET_MERGED",
         "native_calls":0,"native_cycle_timing_measured":False,"profiles":{}}
 exe=os.getenv("VICE_WRAPPER","x64sc")
 with tempfile.TemporaryDirectory(prefix="issue39_umul24_native_") as temp:
  folder=Path(temp)
  for k,p in enumerate(PROFILE):
   rel=f"{p}/resident/math_{p}_game_math.prg"
   old=subprocess.check_output(["git","show",f"{PARENT}:{rel}"],cwd=ROOT)
   new=(ROOT/rel).read_bytes()
   assert sha(old)==row["baseline"][p]
   assert sha(new)==row["candidate"][p]==state["reference_prg_sha256"][p]
   entries={}
   for i,api in enumerate(APIS):
    label=p+"_"+api
    prior=native(old,api,label+"_old",7300+4*k+2*i,folder,exe)
    changed=native(new,api,label+"_new",7301+4*k+2*i,folder,exe)
    assert prior["records"]==changed["records"],(p,api,"old/new mismatch")
    result["native_calls"]+=2*COUNT
    entries[api]={"old_sha256":prior["dump_sha256"],
                  "new_sha256":changed["dump_sha256"],
                  "paired_inputs":COUNT}
    print("NATIVE VICE SOURCE UMUL24",p,api,"PASS",2*COUNT,flush=True)
   result["profiles"][p]=entries
 assert result["native_calls"]==576
 dest=ROOT/"validation/review/ISSUE39_UMUL24_NO_CARRY_RTS_NATIVE_2026-10-13.json"
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("UMUL24 V2-V4 FULL RESIDENT NATIVE VICE PASS 576",flush=True)
if __name__=="__main__":main()
