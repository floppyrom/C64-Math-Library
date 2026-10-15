#!/usr/bin/env python3
"""Native x64sc source-only full-Q32/R16/C dual 32/16 divisor engine.

The test loads source-assembled V2/V3/V4 resident code AFTER deterministic
mini6502 MATH_INIT. The 461-byte optional low-D code resides at $0800.
Full normal source remains immutable. 6510 executes both the unchanged
public DIV/MOD entry and the conditional low-D path. No hardware cycle
or REU DMA wall-time certification is asserted.
"""
from __future__ import annotations
import hashlib,json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from issue144_u3216_dualtail_direct_dispatch_screen import builds,PROFILES,OPS
from validate_unsigned_division import expected
from native_issue39_u24_txa_resident import command

N=24;STRIDE=24;IN=0x0200;OUT=0x0400;H=0x0B00
VECTORS=[
 (0,0),(0xffffffff,0),(0x80000000,0),(0x7fffffff,0),
 (0,1),(0xffffffff,1),(0x12345678,3),(0xffffffff,255),
 (0xffffffff,256),(0x80000000,257),(0x7fffffff,32767),
 (0x80000001,32767),(0xffffffff,0x0100),(0x76543210,0x4321),
 (0x11112222,0x7fff),(0xffffffff,0x7fff),
 (0,0x8000),(0xffffffff,0x8000),(0x80000000,0x8001),
 (0x7fffffff,0x8001),(0xfedcba98,0xffff),
 (0xffffffff,0xffff),(0xdeadbeef,0xfffe),(0x01020304,0x0101)]
assert len(VECTORS)==N
FIELDS=14
assert OUT+STRIDE*FIELDS < 0x0800

def make_harness(entry,io):
    fields=[io+0x18+k for k in range(4)]
    fields += [io+0x1c+k for k in range(2)]
    fields += [io+0x10+k for k in range(4)]
    fields += [io+0x14+k for k in range(2)]
    fields += [io+0x30,io+0x31]
    assert len(fields)==FIELDS
    s=["!cpu 6510","* = $0B00","start:","  sei","  cld",
       "  ldx #$FF","  txs","  lda #$34","  sta $01",
       "  ldx #$00","loop:"]
    for k in range(6):
        s.extend([f"  lda ${IN+STRIDE*k:04X},x",f"  sta ${io+0x10+k:04X}"])
    s.extend(["  txa","  pha","  lda #0","  tax","  tay","  sec",
              f"  jsr ${entry:04X}",
              "  php","  pla",f"  sta ${io+0x30:04X}",
              "  tsx",f"  stx ${io+0x31:04X}",
              "  pla","  tax"])
    for k,addr in enumerate(fields):
        s.extend([f"  lda ${addr:04X}",f"  sta ${OUT+k*STRIDE:04X},x"])
    s.extend(["  inx",f"  cpx #${N:02X}","  beq done","  jmp loop",
              "done:","halt:","  jmp halt"])
    mem,labels,_=Assembler().assemble("\n".join(s)+"\n")
    assert min(mem)==H and max(mem)<0x0C00,(hex(max(mem)),"harness code overflow")
    return mem,labels["halt"]

def native(cpu,entry,io,key,port,tmp,exe):
    mem=bytearray(cpu.mem)
    h,stop=make_harness(entry,io)
    for pc,val in h.items():mem[pc]=val
    for k,(n,d) in enumerate(VECTORS):
        for t in range(6):
            mem[IN+t*STRIDE+k]=((n>>(t*8))&255 if t<4 else (d>>((t-4)*8))&255)
    prog=tmp/(key+".prg");dump=tmp/(key+".dump");log=tmp/(key+".log")
    prog.write_bytes(bytes((IN&255,IN>>8))+mem[IN:0xD000])
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
         "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
         "-initbreak","reset"]
    with log.open("w") as fout:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=fout,stderr=fout)
        try:
            sock=None
            for _ in range(250):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.2)
                    break
                except (TimeoutError,ConnectionRefusedError):time.sleep(.05)
            if sock is None:raise RuntimeError((key,"VICE not listening",log.read_text()[-1600:]))
            sock.settimeout(1)
            try:
                command(sock,'load "'+str(prog)+'" 0',"Loading")
                command(sock,'break '+format(stop,"04x"),"BREAK:")
                command(sock,'g '+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+format(OUT,"04x")+' '+format(OUT+FIELDS*STRIDE-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=4)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():raise RuntimeError((key,"missing native capture",log.read_text()[-1200:]))
    result=dump.read_bytes()
    assert len(result)==FIELDS*STRIDE,(key,len(result))
    for i,(n,d) in enumerate(VECTORS):
        row=[result[t*STRIDE+i] for t in range(FIELDS)]
        q=sum(row[k]<<(8*k) for k in range(4))
        rm=row[4]|row[5]<<8
        nr=sum(row[6+k]<<(8*k) for k in range(4))
        dr=row[10]|row[11]<<8
        assert (q,rm,row[12]&1)==expected(n,d,32,16),(key,i,hex(n),hex(d),hex(q),hex(rm),row[12]&1)
        assert (nr,dr)==(n,d),(key,i,"inputs not preserved")
    return result

def main():
    exe=os.getenv("VICE_WRAPPER")
    assert exe,"Set VICE_WRAPPER to pinned headless x64sc"
    rec={"status":"PASS_NATIVE_U3216_DUALTAIL_FULL_UNSIGNED",
         "native_calls":0,"profiles":{},"native_cycles_measured":False,
         "caller_RAM_required_bytes":461,
         "public_reference_PRGs_modified":False}
    with tempfile.TemporaryDirectory(prefix="issue144b_dualtail_") as dirname:
        d=Path(dirname)
        for pi,p in enumerate(PROFILES):
            for ki,kind in enumerate(("reference","alternate")):
                original,trial,api,config,_=builds(p,kind)
                for oi,operation in enumerate(OPS):
                    port=27000+pi*24+ki*12+oi*4
                    key=f"{p}_{kind}_{operation}"
                    before=native(original,api[operation],config["MATH_IO"],key+"_old",port,d,exe)
                    after=native(trial,api[operation],config["MATH_IO"],key+"_new",port+1,d,exe)
                    # A/N/Z/V can be caller-volatile, but Q/R/C and N/D and
                    # balanced stack are strict. Sign and carry snapshots checked.
                    differences=0
                    for i in range(N):
                        for field in range(FIELDS):
                            if field==12:continue
                            assert before[field*STRIDE+i]==after[field*STRIDE+i],(key,i,field)
                        assert (before[12*STRIDE+i]&1)==(after[12*STRIDE+i]&1),(key,i,"carry")
                        differences+=before[12*STRIDE+i]!=after[12*STRIDE+i]
                    rec["profiles"][key]={"native_calls":2*N,
                       "full_outputs_N_D_SP_identical":True,
                       "volatile_status_mismatches":differences,
                       "new_output_sha256":hashlib.sha256(after).hexdigest()}
                    rec["native_calls"]+=2*N
                    print("NATIVE ISSUE144 DUALTAIL",key,"PASS",2*N,flush=True)
    assert rec["native_calls"]==576
    print(json.dumps(rec,indent=2,sort_keys=True))

if __name__=="__main__":main()
