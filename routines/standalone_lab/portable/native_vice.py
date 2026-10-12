#!/usr/bin/env python3
"""Run independent RAM-backed correctness checks in native VICE x64sc.

Requires a headless x64sc launcher, set VICE_WRAPPER=/path/to/run-x64sc.sh.
Checks 96 identical input pairs for each of three sources at two RAM maps.
This verifies results and carry, NOT native cycle timings.
"""
from pathlib import Path
import hashlib,json,os,random,socket,subprocess,sys,tempfile,time
from verify import CASES,MAPS,render
from mini6502 import Assembler
HERE=Path(__file__).resolve().parent
VICE=Path(os.environ.get("VICE_WRAPPER",""))
H=0x2000;N=96;INPUT=0x3000;OUTPUT=0x3800;STRIDE=0x80
def operands(bits):
 mask=(1<<bits)-1
 p=[(0,0),(1,0),(mask,0),(0,mask),(mask,1),(mask,mask),(1,1),(2,1),(mask,2),(mask,7),(0x8000 if bits==16 else 0x80000000,0x4000 if bits==16 else 0x40000000),(0x1234,0xff),(0x1234,0x100),(0xffff,65535)]
 p=[(a&mask,b&mask) for a,b in p]
 r=random.Random(20261012+bits)
 while len(p)<N:
  n=r.getrandbits(bits);d=[0,1,2,3,7,15,255,256,65535,r.getrandbits(bits)][r.randrange(10)]
  p.append((n,d&mask))
 return p
def make_harness(entry,bits,mp):
 b=bytearray()
 def emit(*v):b.extend(v)
 def op(code,addr):emit(code,addr&255,addr>>8)
 size=bits//8
 emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0x00)
 loop=H+len(b)
 for k in range(size):
  op(0xbd,INPUT+k*STRIDE);op(0x8d,mp["INPUT_NUM"]+k)
  op(0xbd,INPUT+(size+k)*STRIDE);op(0x8d,mp["INPUT_DIV"]+k)
 for dest,val in [(mp["OUTPUT_QUOT"],0x55),(mp["OUTPUT_REM"],0x66)]:
  emit(0xa9,val)
  for k in range(size):op(0x8d,dest+k)
 emit(0x8a,0x48);op(0x20,entry)
 emit(0x08,0x68);op(0x8d,0xc030);emit(0x68,0xaa)
 for k in range(size):op(0xad,mp["OUTPUT_QUOT"]+k);op(0x9d,OUTPUT+k*STRIDE)
 for k in range(size):op(0xad,mp["OUTPUT_REM"]+k);op(0x9d,OUTPUT+(size+k)*STRIDE)
 op(0xad,0xc030);op(0x9d,OUTPUT+2*size*STRIDE)
 emit(0xe8,0xe0,N,0xf0,0x03);op(0x4c,loop)
 halt=H+len(b);op(0x4c,halt)
 assert len(b)<0x300
 return bytes(b),halt
def check(mem,entry,bits,mp,tag,port,folder,mod_only):
 code,halt=make_harness(entry,bits,mp);mem[H:H+len(code)]=code
 inp=operands(bits);size=bits//8
 for i,(n,d) in enumerate(inp):
  for k in range(size):
   mem[INPUT+k*STRIDE+i]=(n>>(8*k))&255
   mem[INPUT+(size+k)*STRIDE+i]=(d>>(8*k))&255
 prog=folder/(tag+".prg");dump=folder/(tag+".bin")
 prog.write_bytes(bytes((H&255,H>>8))+mem[H:0xc100])
 args=[str(VICE),"-console","-silent","-sounddev","dummy","-warp","-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),"-initbreak","reset"]
 with (folder/"vice.log").open("a") as log:
  proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=log)
  try:
   for _ in range(150):
    try:sock=socket.create_connection(("127.0.0.1",port),timeout=.1);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.04)
   else:raise RuntimeError("VICE monitor connection timeout")
   sock.settimeout(.25)
   def command(text,needle):
    sock.sendall((text+"\n").encode());out=b""
    for _ in range(180):
     try:
      x=sock.recv(16384)
      if not x:break
      out+=x
      if needle.encode() in out and out.endswith(b") "):break
     except socket.timeout:continue
    if needle.encode() not in out:raise RuntimeError((text,out[-600:]))
   command('load "'+str(prog)+'" 0',"Loading")
   command("break "+format(halt,"04x"),"BREAK:")
   command("g "+format(H,"04x"),"Stop on  exec")
   command('bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+format(OUTPUT+(2*size+1)*STRIDE-1,"04x"),"Saving")
   sock.sendall(b"quit\n");sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 data=dump.read_bytes()
 assert len(data)==(2*size+1)*STRIDE
 for i,(n,d) in enumerate(inp):
  values=[data[k*STRIDE+i] for k in range(2*size+1)]
  q=sum(values[k]<<(8*k) for k in range(size))
  r=sum(values[size+k]<<(8*k) for k in range(size))
  want_q=int.from_bytes(b"\x55"*size,"little") if mod_only else n//d if d else 0
  assert (q,r,values[-1]&1)==(want_q,n%d if d else 0,int(d==0)),(tag,i,hex(n),hex(d))
 return {"source":tag,"cases":N,"input_sha256":hashlib.sha256(json.dumps(inp,separators=(",",":")).encode()).hexdigest(),"output_sha256":hashlib.sha256(data).hexdigest()}
def main():
 assert os.environ.get("VICE_WRAPPER") and VICE.is_file(),"Set VICE_WRAPPER to a working x64sc launcher"
 rows=[]
 with tempfile.TemporaryDirectory(prefix="standalone_vice_") as temp:
  folder=Path(temp)
  for ri,(name,bits,mod_only,size,label) in enumerate(CASES):
   for mi,mp in enumerate(MAPS[:2]):
    im,labels,_=Assembler().assemble(render(name,mp))
    assert len(im)==size
    mem=bytearray(65536)
    for addr,byte in im.items():mem[addr]=byte
    tag=name[:-4]+"_"+mp["name"]
    res=check(mem,labels[label],bits,mp,tag,7440+ri*2+mi,folder,mod_only)
    rows.append(res);print(tag,"NATIVE VICE PASS",res["cases"],flush=True)
 assert sum(r["cases"] for r in rows)==576
 print("NATIVE VICE STANDALONE RELOCATION PASS 576")
if __name__=="__main__":main()
