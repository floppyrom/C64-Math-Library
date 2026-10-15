#!/usr/bin/env python3
"""Issue144 B: native NMOS 6510 V2-V4 signed32/16 R-before-Q exact-output screen.

In-memory source assembled original/candidate, same inputs, no PRGs or REUs
updated. x64sc captures full Q32/R16, N32/D16, C/N/Z/V flags, A/X/Y and SP.
Actual CPU cycle timing is NOT measured here (model paired cycles separately).
"""
from __future__ import annotations
import hashlib,json,os,socket,subprocess,tempfile,time
from pathlib import Path
from issue144_signed32_rq_tail_fusion_screen import pair,PROFILES
from native_issue39_u24_txa_resident import command
from mini6502 import Assembler
from validate_signed_division import div_expected

IN,OUT,H,STRIDE=0x0200,0x0500,0x0B00,64
N=24
VECTORS=[
 (0,0),(0xffffffff,0),(0x80000000,0),(0x7fffffff,0),
 (0,1),(0,0xffff),(1,1),(0xffffffff,1),
 (0x80000000,0xffff),(0x7fffffff,0xffff),
 (0x80000000,0x8000),(0x7fffffff,0x8000),
 (0x80000000,0x7fff),(0x7fffffff,0x7fff),
 (0xdeadbeef,0x0100),(0x80000001,0x0100),
 (0xffffffff,0x0002),(0xffff8000,0x8000),
 (0x00008000,0x8000),(0x00010000,0x0002),
 (0xffff0000,0xfffe),(0x00000001,0x0000),
 (0x12345678,0x4321),(0xfedcba98,0xabcd)]
assert len(VECTORS)==N

def harness(entry,init,io):
    fields=[io+0x18+i for i in range(4)]+[io+0x1c+i for i in range(2)]
    fields+=[io+0x10+i for i in range(6)]
    fields+=[io+0x30,io+0x32,io+0x34,io+0x36,io+0x38]
    assert OUT+len(fields)*STRIDE < H
    L=["!cpu 6510","* = $0B00","start:","  sei","  cld",
       "  ldx #$FF","  txs","  lda #$34","  sta $01",f"  jsr ${init:04X}",
       "  ldx #$00","loop:"]
    for i in range(6):
        L.extend([f"  lda ${IN+i*STRIDE:04X},x",f"  sta ${io+0x10+i:04X}"])
    L += ["  txa","  pha","  lda #$00","  tax","  tay","  sec",
          f"  jsr ${entry:04X}",
          f"  sta ${io+0x32:04X}","  php","  pla",
          f"  sta ${io+0x30:04X}",f"  stx ${io+0x34:04X}",
          f"  sty ${io+0x36:04X}","  tsx",
          f"  stx ${io+0x38:04X}","  pla","  tax"]
    for i,address in enumerate(fields):
        L.extend([f"  lda ${address:04X}",f"  sta ${OUT+i*STRIDE:04X},x"])
    L += ["  inx",f"  cpx #${N:02X}","  beq done",
          "  jmp loop","done:","halt:","  jmp halt"]
    mem,labels,_=Assembler().assemble("\n".join(L)+"\n")
    assert min(mem)==H and max(mem)<0x0C00,(hex(max(mem)),"test harness overflow")
    return mem,labels["halt"],len(fields)

def native(cpu,entry,init,io,p,layout,op,which,port,tmp,exe):
    mem=bytearray(cpu.mem)
    h,stop,field_count=harness(entry,init,io)
    for pc,b in h.items():mem[pc]=b
    for k,(num,div) in enumerate(VECTORS):
        for j in range(6):
            mem[IN+j*STRIDE+k]=((num>>(8*j))&255) if j<4 else ((div>>(8*(j-4)))&255)
    stem=f"{p}_{layout}_{op}_{which}"
    prg=tmp/(stem+".prg"); dump=tmp/(stem+".dump"); logfile=tmp/(stem+".log")
    prg.write_bytes(bytes((IN&255,IN>>8))+mem[IN:0xD000])
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
         "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
         "-initbreak","reset"]
    with logfile.open("w") as log:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=log,stderr=log)
        try:
            sock=None
            for _ in range(250):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.2)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.05)
            if sock is None: raise RuntimeError(("VICE not listening",logfile.read_text()[-1200:]))
            sock.settimeout(1)
            try:
                command(sock,'load "'+str(prg)+'" 0',"Loading")
                command(sock,'break '+format(stop,"04x"),"BREAK:")
                command(sock,'g '+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+format(OUT,"04x")+' '+format(OUT+STRIDE*field_count-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=4)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():
        raise RuntimeError((stem,"missing capture",logfile.read_text()[-1000:]))
    data=dump.read_bytes()
    assert len(data)==STRIDE*field_count,(stem,len(data),STRIDE*field_count)
    for idx,(n,d) in enumerate(VECTORS):
        row=[data[j*STRIDE+idx] for j in range(field_count)]
        q=sum(row[j]<<(8*j) for j in range(4))
        rem=sum(row[4+j]<<(8*j) for j in range(2))
        n1=sum(row[6+j]<<(8*j) for j in range(4))
        d1=sum(row[10+j]<<(8*j) for j in range(2))
        exp=div_expected(n,32,d,16,32,16)
        assert (q,rem,row[12]&1)==exp,(stem,idx,hex(n),hex(d),(q,rem,row[12]&1),exp)
        assert (n1,d1)==(n,d),(stem,idx,"inputs",n1,d1)
    return data

def main():
    exe=os.environ.get("VICE_WRAPPER")
    assert exe,"Set VICE_WRAPPER to checksum-verified x64sc"
    report={"status":"PASS_NATIVE_SIGNED32_R_BEFORE_Q",
            "profiles":{}, "native_calls":0,
            "reference_images_modified":False,
            "physical_bus_cycle_measurement":False}
    with tempfile.TemporaryDirectory(prefix="issue144_signedrq_vice_") as d:
        tmp=Path(d)
        for pi,p in enumerate(PROFILES):
            for li,layout in enumerate(("reference","alternate")):
                old,new,c,v=pair(p,layout)
                io=v["MATH_IO"];init=c["MATH_INIT"]
                for oi,op in enumerate(("MATH_SDIV32_16","MATH_SMOD32_16")):
                    a=native(old,c[op],init,io,p,layout,op,"old",
                             25200+pi*32+li*16+oi*4,tmp,exe)
                    b=native(new,c[op],init,io,p,layout,op,"new",
                             25201+pi*32+li*16+oi*4,tmp,exe)
                    assert a==b,(p,layout,op,"native A/status/X/Y/SP or Q/R/N/D changed",
                                 [k for k,(i,j) in enumerate(zip(a,b)) if i!=j][:10])
                    key=f"{p}/{layout}/{op}"
                    report["profiles"][key]={"native_calls":2*N,
                            "outputs_registers_status_stack_identical":True,
                            "capture_sha256":hashlib.sha256(a).hexdigest()}
                    report["native_calls"]+=2*N
                    print("NATIVE SIGNED RQ",key,"PASS",2*N,flush=True)
    assert report["native_calls"]==2*24*3*2*2
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
