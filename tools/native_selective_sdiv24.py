#!/usr/bin/env python3
"""Native VICE signed24/24 DIV/MOD shared full-width source and caller ABI."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker

H, INPUT, OUTPUT, STRIDE, N = 0x2000, 0x3000, 0x3800, 0x80, 96


def signed24(v):
    return v-(1<<24) if v&0x800000 else v

def divide(n,d):
    n,d=signed24(n),signed24(d)
    if not d:
        return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)!=(d<0):q=-q
    r=n-q*d
    return q&0xffffff,r&0xffffff,0

def pairs():
    edges=(0,1,2,3,127,255,256,65535,0x7fffff,0x800000,
           0x800001,0xfffffe,0xffffff)
    selected=[(x,y) for x in edges for y in (0,1,0x7fffff,0x800000,0xffffff)]
    rng=random.Random(0x5D2424)
    selected.extend((rng.randrange(1<<24),rng.randrange(1<<24))
                    for _ in range(N-len(selected)))
    assert len(selected)==N
    return selected

def harness(entry,io):
    b=bytearray()
    def emit(*v):b.extend(v)
    def op(opcode,addr):emit(opcode,addr&255,addr>>8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0)
    loop=H+len(b)
    for i,addr in enumerate([io+16+j for j in range(3)]+[io+20+j for j in range(3)]):
        op(0xbd,INPUT+i*STRIDE);op(0x8d,addr)
    for addr,value in ((io+19,0x5a),(io+23,0xa5),
                       (io+27,0x39),(io+31,0x59)):
        emit(0xa9,value);op(0x8d,addr)
    emit(0x8a,0x48);op(0x20,entry)
    emit(0x08,0x68);op(0x8d,0xc030)
    emit(0x68,0xaa)
    fields=[io+24+j for j in range(3)]+[io+28+j for j in range(3)]+[0xc030]+[
        io+16+j for j in range(3)]+[io+20+j for j in range(3)]+[
        io+19,io+23,io+27,io+31]
    assert len(fields)==17
    for i,addr in enumerate(fields):
        op(0xad,addr);op(0x9d,OUTPUT+i*STRIDE)
    emit(0xe8,0xe0,N,0xf0,0x03);op(0x4c,loop)
    stop=H+len(b);op(0x4c,stop)
    assert len(b)<0x300
    return bytes(b),stop


def verify(vice, image, entry, origin, io, tag, port, folder):
    memory = bytearray(65536)
    memory[origin:origin+len(image)-2] = image[2:]
    code, stop = harness(entry, io)
    assert len(code) < 0x300
    memory[H:H+len(code)] = code
    operands=pairs()
    for idx,(n,d) in enumerate(operands):
        for slot,v in enumerate((*n.to_bytes(3,"little"),*d.to_bytes(3,"little"))):
            memory[INPUT+slot*STRIDE+idx]=v
    prg=folder/(tag+".prg")
    dump=folder/(tag+".bin")
    prg.write_bytes(bytes((H&255,H>>8))+memory[H:0xc100])
    args=[vice,"-console","-silent","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),
          "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as out:
        proc=subprocess.Popen(args,cwd=folder,stdout=out,stderr=out)
        try:
            for _ in range(150):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.04)
            else:
                raise RuntimeError("x64sc remote monitor connection failed")
            sock.settimeout(.25)
            def monitor(command,marker):
                sock.sendall((command+"\n").encode())
                received=b""
                for _ in range(180):
                    try:
                        part=sock.recv(16384)
                        if not part:
                            break
                        received+=part
                        if marker.encode() in received and received.endswith(b") "):
                            break
                    except socket.timeout:
                        continue
                if marker.encode() not in received:
                    raise RuntimeError("VICE monitor failed: %r %r" %
                                       (command,received[-600:]))
            monitor('load "'+str(prg)+'" 0',"Loading")
            monitor("break "+format(stop,"04x"),"BREAK:")
            monitor("g "+format(H,"04x"),"Stop on  exec")
            monitor('bsave "'+str(dump)+'" 0 '+
                    format(OUTPUT,"04x")+" "+
                    format(OUTPUT+17*STRIDE-1,"04x"),"Saving")
            sock.sendall(b"quit\n")
            sock.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    saved = dump.read_bytes()
    assert len(saved) == 17*STRIDE, len(saved)
    for i,(n,d) in enumerate(operands):
        fields=[saved[j*STRIDE+i] for j in range(17)]
        q=sum(fields[j]<<(8*j) for j in range(3))
        r=sum(fields[3+j]<<(8*j) for j in range(3))
        c=fields[6]&1
        if ((q,r,c)!=divide(n,d) or
            fields[7:10]!=list(n.to_bytes(3,"little")) or
            fields[10:13]!=list(d.to_bytes(3,"little")) or
            fields[13:17]!=[0x5a,0xa5,0x39,0x59]):
            raise AssertionError((tag,i,n,d,fields,divide(n,d)))
    return hashlib.sha256(saved).hexdigest()


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must identify native x64sc")
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="selective_sdiv24_vice_") as td:
        folder=Path(td)
        for seq,(origin,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(index,["SDIV24","SMOD24"],
                                          zp_budget=0,ram_budget=364)
            man=selective_linker.build(plan,folder,memory={
                "code_base":origin,"math_io":io})
            self_entries=[int(op["entry"][1:],16) for op in man["operations"]]
            assert self_entries==[origin,origin] and len(man["link_order"])==1
            assert man["resource_use"]["image_span_bytes"]==325
            assert man["resource_use"]["zero_page_bytes"]==0
            image=(folder/"math_selective.prg").read_bytes()
            digest=verify(vice,image,origin,origin,io,
                "sdiv24_%04x"%origin,8040+seq,folder)
            print("NATIVE SDIV24_SMOD24",hex(origin),"PASS",N,digest,flush=True)
    print("NATIVE SDIV24_SMOD24 TWO-MAP PASS",2*N)
if __name__=="__main__":
    main()
