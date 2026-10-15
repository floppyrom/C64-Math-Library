#!/usr/bin/env python3
"""Independent native x64sc source-only full-Q/R/C opt-in UDIV32/16 screen.

No published PRG/REU changes; all candidate code is in caller-owned $0800.
Check both public UDIV32_16/UMOD32_16 baseline against candidate source
at $0800. V2-V4, including D=0, D8, low D16 and high D16.
Native timing, interrupts and arbitrary $0800 ownership are NOT qualified.
"""
from __future__ import annotations
import hashlib,json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from native_issue39_u24_txa_resident import command
from validate_signed_division import parse_api
from issue144_u3216_nooverflow_public_optional_screen import assemble,PROFILES,OPS,ENTRY
COUNT=24
STRIDE=32
IN=0x0200
OUT=0x0500
H=0x0B00
FIELDS=[0xC018+i for i in range(4)]+[0xC01C+i for i in range(2)]+[0xC010+i for i in range(6)]+[0xC030,0xC032]
assert OUT+STRIDE*len(FIELDS)<ENTRY
VECTORS=[
(0,0),(1,0),(0xffffffff,0),(0xffffffff,1),
(0x80000000,1),(0xffffffff,255),(0x7fffffff,256),(0xffffffff,256),
(0x80000000,257),(0xffffffff,257),(0xffffffff,0x7fff),
(0x80000000,0x7fff),(0x7fffffff,0x7ffe),(0x12345678,0x0100),
(0xdeadbeef,0x4000),(0x80000000,0x8000),(0xffffffff,0x8000),
(0xffffffff,0xffff),(0x12345678,0xffff),(0xffffffff,0x8001),
(0x00010000,0x4000),(0x0000ffff,0x4000),(0x4321abcd,0x4321),
(0xff123456,0x6001)]
assert len(VECTORS)==COUNT

def harness(entry):
 lines=["!cpu 6510","* = $0B00","start:","sei","cld","ldx #$FF","txs",
        "lda #$34","sta $01","jsr $3280","ldx #$00","loop:"]
 for i in range(6):
  lines += ["lda $"+format(IN+i*STRIDE,"04X")+",x",
            "sta $"+format(0xC010+i,"04X")]
 lines += ["txa","pha","lda #$00","tax","tay","sec","jsr $"+format(entry,"04X"),
           "php","pla","sta $C030","tsx","stx $C032","pla","tax"]
 for i,a in enumerate(FIELDS):
  lines += ["lda $"+format(a,"04X"),"sta $"+format(OUT+i*STRIDE,"04X")+",x"]
 lines += ["inx","cpx #$18","beq done","jmp loop","done:","halt:","jmp halt"]
 program,labels,_=Assembler().assemble("\n".join(lines)+"\n")
 assert min(program)==H and max(program)<0x0D00
 return program,labels["halt"]

def run(profile,op,optimized,tmp,port,exe,overlay):
 binary=(ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")).read_bytes()
 load=int.from_bytes(binary[:2],"little")
 assert load==0x1000
 mem=bytearray(65536)
 mem[load:load+len(binary)-2]=binary[2:]
 entry=ENTRY if optimized else parse_api(profile)[op]
 assert entry==(ENTRY if optimized else parse_api(profile)[op])
 if optimized:
  for pc,b in overlay.items():
   assert pc<0x0B00
   mem[pc]=b
 program,stop=harness(entry)
 for pc,b in program.items():mem[pc]=b
 for i,(n,d) in enumerate(VECTORS):
  for k in range(6):
   value=(n>>(8*k))&255 if k<4 else (d>>(8*(k-4)))&255
   mem[IN+k*STRIDE+i]=value
 prefix=profile+"_"+op+("_opt" if optimized else "_stock")
 prg=tmp/(prefix+".prg");dump=tmp/(prefix+".dump");log=tmp/(prefix+".log")
 prg.write_bytes(bytes([IN&255,IN>>8])+mem[IN:0xD000])
 cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
      "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),"-initbreak","reset"]
 with log.open("w") as fp:
  proc=subprocess.Popen(cmd,cwd=tmp,stdout=fp,stderr=fp)
  try:
   sock=None
   for _ in range(250):
    try: sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
    except (ConnectionRefusedError,TimeoutError):time.sleep(.05)
   if sock is None:raise RuntimeError(("VICE did not start",log.read_text()[-1000:]))
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
 if not dump.exists():raise RuntimeError((profile,op,optimized,log.read_text()[-1800:]))
 data=dump.read_bytes()
 assert len(data)==STRIDE*len(FIELDS)
 for i,(n,d) in enumerate(VECTORS):
  row=[data[k*STRIDE+i] for k in range(len(FIELDS))]
  q=sum(row[k]<<(8*k) for k in range(4))
  rem=sum(row[4+k]<<(8*k) for k in range(2))
  n0=sum(row[6+k]<<(8*k) for k in range(4))
  d0=sum(row[10+k]<<(8*k) for k in range(2))
  expected=((n//d,n%d,0) if d else (0,0,1))
  assert (q,rem,row[12]&1)==expected,(profile,op,optimized,i,hex(n),hex(d),(q,rem,row[12]&1),expected)
  assert (n0,d0)==(n,d),(profile,op,optimized,i,"N/D changed")
  assert row[13]==0xFE,(profile,op,optimized,i,"SP mismatch",row[13])
 return data

def main():
 exe=os.getenv("VICE_WRAPPER","x64sc")
 overlay=assemble()
 records={"status":"PASS_REAL_X64SC_OPTIN_PUBLIC_DIVMOD",
          "profiles":{},"native_calls":0,
          "native_cycles_measured":False,
          "normal_public_API_promoted":False,
          "extra_normal_ZP":0,"caller_owned_RAM":"$0800-$"+format(max(overlay),"04X"),
          "production_resident_or_REU_changed":False,
          "private_optisearch_published":False}
 with tempfile.TemporaryDirectory(prefix="issue144_u3216_low_vice_") as td:
  tmp=Path(td)
  for idx,p in enumerate(PROFILES):
   records["profiles"][p]={}
   for j,op in enumerate(OPS):
    port=18400+idx*8+j*2
    stock=run(p,op,False,tmp,port,exe,overlay)
    candidate=run(p,op,True,tmp,port+1,exe,overlay)
    for row in range(len(FIELDS)):
     for i in range(COUNT):
      off=row*STRIDE+i
      if row==12: assert stock[off]&1==candidate[off]&1
      else: assert stock[off]==candidate[off],(p,op,row,i)
    records["profiles"][p][op]={
       "baseline_calls":COUNT,"candidate_calls":COUNT,
       "ABI_records_identical_except_volatile_flags":True,
       "baseline_sha256":hashlib.sha256(stock).hexdigest(),
       "candidate_sha256":hashlib.sha256(candidate).hexdigest()}
    records["native_calls"]+=COUNT*2
    print(p,op,"native real x64sc PASS",COUNT*2,flush=True)
 assert records["native_calls"]==288
 print(json.dumps(records,indent=2))
if __name__=="__main__":main()
