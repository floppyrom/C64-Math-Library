#!/usr/bin/env python3
"""Native x64sc old/new complete-resident root16/root32 ABI proof, no timing claim.

48 deterministic operands, 2 root APIs, 4 upgraded profiles, old/new images:
768 native 6510 public calls. REU-assisted V4 root stays byte-for-byte unchanged.
"""
from pathlib import Path
import argparse,hashlib,json,math,os,random,socket,subprocess,tempfile,time
from native_issue39_u24_txa_resident import command

R=Path(__file__).resolve().parents[1]
PARENT="f7164dd07223f2f1761dfe6260293af3420357fa"
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k","v5_hybrid_lowzp")
API={"MATH_ISQRT16":0x5E2D,"MATH_ISQRT32":0x5E30}
SHA={"v1_balanced":"41d744c2aaf06a5d40cfece1c16255576950a8e6e3328d5fe4196c0ac753171e",
     "v2_pareto_fast":"8b52fe47c4d6aff5331a5d3a4aca73e34d84696a5aa83dba14c48f62a4ee9d92",
     "v3_reu_512k":"52565df27dc892be9da8e12b8ac6267179debbd3d521331d7cd3d0a49ced2755",
     "v5_hybrid_lowzp":"b27e0885c7241dd7bdc3b2e25be6b2c616685cb426436a3c2b8260eff7a21ebb"}
H=0x0B00;IN=0x0400;OUT=0x0600;STRIDE=64;COUNT=48;IO=0xC000
FIELDS=[IO+0x08+j for j in range(4)]+[IO+0x10+j for j in range(4)]+[0xC030,0xC024,0xC032]
assert OUT+STRIDE*len(FIELDS)<H
def sha(b):return hashlib.sha256(b).hexdigest()

def inputs(width):
 r=random.Random(0xC6390000+width)
 a=[0,1,2,3,4,7,8,9,15,16,17,24,25,26,255,256,257,65534,65535]
 if width==32:a+=[65536,65537,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
 roots=[0,1,2,3,15,16,31,127,128,255]+([256,257,1023,4095,32767,65535] if width==32 else [])
 for root in roots:
  for d in (-1,0,1):
   v=root*root+d
   if 0<=v<(1<<width):a.append(v)
 a=list(dict.fromkeys(a))[:COUNT]
 while len(a)<COUNT:
  v=r.getrandbits(width)
  if v not in a:a.append(v)
 return a

def harness(entry):
 b=bytearray()
 def e(*data):b.extend(data)
 def ab(code,x):e(code,x&255,x>>8)
 e(0x78,0xD8,0xA9,0x34,0x85,0x01) # SEI CLD RAM-under-ROM
 ab(0x20,0x3280)                 # source resident MATH_INIT
 e(0xA2,0x00)                   # index
 loop=H+len(b)
 for j in range(4):
  ab(0xBD,IN+STRIDE*j)
  ab(0x8D,IO+0x10+j)
 e(0xA9,0x91)
 for j in range(4):ab(0x8D,IO+0x08+j)
 e(0xA9,0xA6);ab(0x8D,0xC024)
 e(0x8A,0x48,0x38)  # index push, caller carry=1
 ab(0x20,entry)
 e(0x08,0x68);ab(0x8D,0xC030) # saved carry
 e(0xBA);ab(0x8E,0xC032)   # TSX before index restore
 e(0x68,0xAA)
 for j,a in enumerate(FIELDS):
  ab(0xAD,a);ab(0x9D,OUT+STRIDE*j)
 e(0xE8,0xE0,COUNT,0xF0,0x03);ab(0x4C,loop)
 stop=H+len(b);ab(0x4C,stop)
 assert len(b)<0x300
 return bytes(b),stop

def native(prg,op,tag,port,folder,vice):
 assert int.from_bytes(prg[:2],"little")==0x1000
 m=bytearray(65536);m[0x1000:0x1000+len(prg)-2]=prg[2:]
 code,stop=harness(API[op]);m[H:H+len(code)]=code
 width=16 if op.endswith("16") else 32
 vals=inputs(width)
 for i,n in enumerate(vals):
  bits=n.to_bytes(width//8,"little")+(b"\x77\x88" if width==16 else b"")
  for j in range(4):m[IN+STRIDE*j+i]=bits[j]
 image=folder/(tag+".prg");dump=folder/(tag+".dump");log=folder/(tag+".log")
 image.write_bytes(bytes([IN&255,IN>>8])+m[IN:0xD000])
 cmd=[str(vice),"-console","-silent","-sounddev","dummy","-warp",
      "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
 with log.open("w") as out:
  p=subprocess.Popen(cmd,cwd=folder,stdout=out,stderr=out)
  try:
   sock=None
   for _ in range(180):
    try:sock=socket.create_connection(("127.0.0.1",port),timeout=0.15);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(0.07)
   if sock is None:raise RuntimeError(("VICE socket unavailable",tag,log.read_text()[-800:]))
   sock.settimeout(0.3)
   try:
    command(sock,'load "'+str(image)+'" 0',"Loading")
    command(sock,"break "+format(stop,"04x"),"BREAK:")
    command(sock,"g "+format(H,"04x"),"Stop on  exec")
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUT,"04x")+" "+format(OUT+len(FIELDS)*STRIDE-1,"04x"),"Saving")
    sock.sendall(b"quit\n")
   finally:sock.close()
  finally:
   p.terminate()
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:p.kill()
 if not dump.exists():raise RuntimeError(("VICE dump absent",tag,log.read_text()[-900:]))
 dat=dump.read_bytes()
 assert len(dat)==STRIDE*len(FIELDS),(tag,len(dat))
 rec=[]
 for i,n in enumerate(vals):
  v=[dat[j*STRIDE+i] for j in range(len(FIELDS))]
  z=v[0]|v[1]<<8
  input_out=sum(v[4+j]<<(j*8) for j in range(4))
  want_n=n if width==32 else n+(0x8877<<16)
  assert (z,v[2],v[3],input_out,v[8]&1,v[9])==(
    math.isqrt(n),0x91,0x91,want_n,0,0xA6),(tag,i,hex(n),v)
  rec.append((z,v[2],v[3],input_out,v[8]&1,v[9],v[10]))
 return {"records":rec,"dump_sha256":sha(dat),"input_count":COUNT}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path);args=ap.parse_args()
 state=json.loads((R/"RELEASE_STATUS.json").read_text())
 assert state["issue39_integer_roots_source_release_2026_10_13"]["status"] in ("PASS_STAGED_NATIVE_VICE_PENDING","PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING")
 vice=os.environ.get("VICE_WRAPPER","x64sc")
 report={"status":"PASS_NATIVE_VICE_SOURCE_INSTALLED_ROOTS",
         "native_cycles_measured":False,"profiles":{},"native_calls":0,
         "parent_commit":PARENT}
 with tempfile.TemporaryDirectory(prefix="issue39_isqrt_vice_") as tmp:
  folder=Path(tmp)
  for pi,p in enumerate(PROFILES):
   filename=f"{p}/resident/math_{p}_game_math.prg"
   before=subprocess.check_output(["git","show",f"{PARENT}:{filename}"],cwd=R)
   after=(R/filename).read_bytes()
   assert sha(after)==SHA[p]==state["reference_prg_sha256"][p],(p,"current PRG drift")
   row={"original_sha256":sha(before),"candidate_sha256":sha(after),"entries":{}}
   for oi,op in enumerate(API):
    prefix=p+"_"+op
    a=native(before,op,prefix+"_old",7700+pi*4+oi*2,folder,vice)
    b=native(after,op,prefix+"_new",7701+pi*4+oi*2,folder,vice)
    assert a["records"]==b["records"],(p,op,"native old/new public mismatch")
    report["native_calls"]+=COUNT*2
    row["entries"][op]={"identical_output":True,"cases_per_image":COUNT,
                        "old_dump_sha256":a["dump_sha256"],"new_dump_sha256":b["dump_sha256"]}
    print("NATIVE VICE ROOT",p,op,"PASS",COUNT*2,flush=True)
   report["profiles"][p]=row
 assert report["native_calls"]==768
 if args.out:
  args.out.parent.mkdir(parents=True,exist_ok=True)
  args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("SOURCE-INSTALLED ROOT16/ROOT32 NATIVE VICE PASS",report["native_calls"],flush=True)
if __name__=="__main__":main()
