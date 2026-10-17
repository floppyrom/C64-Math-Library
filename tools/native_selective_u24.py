#!/usr/bin/env python3
"""Native x64sc validation of the portable public 24/24 shared DIV/MOD kernel."""
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker

H=0x2000
INPUT=0x3000
OUTPUT=0x3800
STRIDE=0x80
N=96


def cases():
    edges=(0,1,2,3,255,256,65535,65536,8388607,8388608,16777214,16777215)
    divisors=(0,1,2,3,255,256,65535,16777215)
    items=[(x,d) for x in edges for d in divisors][:60]
    rng=random.Random(0xCAFE2417)
    while len(items)<N:
        items.append((rng.getrandbits(24),rng.getrandbits(24)))
    assert len(items)==N
    return items


def harness(entry,io):
    out=bytearray()
    def emit(*args):out.extend(args)
    def op(code,addr):emit(code,addr&255,addr>>8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0)
    loop=H+len(out)
    for k in range(3):
        op(0xbd,INPUT+k*STRIDE)
        op(0x8d,io+16+k)
    for k in range(3):
        op(0xbd,INPUT+(3+k)*STRIDE)
        op(0x8d,io+20+k)
    emit(0xa9,0x55)
    for k in range(3):op(0x8d,io+24+k)
    emit(0xa9,0x66)
    for k in range(3):op(0x8d,io+28+k)
    emit(0xa9,0x69);op(0x8d,io+27)
    emit(0xa9,0xab);op(0x8d,io+31)
    emit(0x8a,0x48)
    op(0x20,entry)
    emit(0x08,0x68);op(0x8d,0xc030)
    emit(0x68,0xaa)
    for k in range(4):
        op(0xad,io+24+k);op(0x9d,OUTPUT+k*STRIDE)
    for k in range(4):
        op(0xad,io+28+k);op(0x9d,OUTPUT+(4+k)*STRIDE)
    op(0xad,0xc030);op(0x9d,OUTPUT+8*STRIDE)
    emit(0xe8,0xe0,N,0xf0,0x03)
    op(0x4c,loop)
    stop=H+len(out)
    op(0x4c,stop)
    assert len(out)<0x300
    return bytes(out),stop


def native(vice,ram,entry,origin,io,tag,port,folder):
    stub,halt=harness(entry,io)
    ram[H:H+len(stub)]=stub
    inputs=cases()
    for j,(n,d) in enumerate(inputs):
        for k in range(3):
            ram[INPUT+k*STRIDE+j]=(n>>(8*k))&255
        for k in range(3):
            ram[INPUT+(3+k)*STRIDE+j]=(d>>(8*k))&255
    prg=folder/(tag+".prg")
    binary=folder/(tag+".bin")
    prg.write_bytes(bytes((H&255,H>>8))+ram[H:0xc100])
    args=[vice,"-console","-silent","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
          "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as logfile:
        proc=subprocess.Popen(args,cwd=folder,stdout=logfile,stderr=logfile)
        try:
            for _ in range(150):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.04)
            else:
                raise RuntimeError("native VICE monitor unavailable")
            sock.settimeout(.25)
            def monitor(command,marker):
                sock.sendall((command+"\n").encode())
                answer=b""
                for _ in range(180):
                    try:
                        part=sock.recv(16384)
                        if not part:break
                        answer+=part
                        if marker.encode() in answer and answer.endswith(b") "):
                            break
                    except socket.timeout:continue
                if marker.encode() not in answer:
                    raise RuntimeError((command,answer[-400:]))
            monitor(f'load "{prg}" 0',"Loading")
            monitor(f"break {halt:04x}","BREAK:")
            monitor(f"g {H:04x}","Stop on  exec")
            monitor(f'bsave "{binary}" 0 {OUTPUT:04x} {OUTPUT+9*STRIDE-1:04x}',"Saving")
            sock.sendall(b"quit\n");sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    result=binary.read_bytes()
    assert len(result)==9*STRIDE,len(result)
    for idx,(n,d) in enumerate(inputs):
        q=sum(result[k*STRIDE+idx]<<(8*k) for k in range(3))
        rem=sum(result[(4+k)*STRIDE+idx]<<(8*k) for k in range(3))
        carry=result[8*STRIDE+idx]&1
        extra=result[3*STRIDE+idx],result[7*STRIDE+idx]
        expect=(n//d if d else 0,n%d if d else 0,int(not d),(0x69,0xab))
        assert (q,rem,carry,extra)==expect,(tag,idx,hex(n),hex(d),q,rem,carry,extra)
    return hashlib.sha256(result).hexdigest()


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name an installed x64sc executable")
    index=math_builder.operation_index()
    count=0
    with tempfile.TemporaryDirectory(prefix="native_u24_") as path:
        folder=Path(path)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(index,["UDIV24","UMOD24"],
                zp_budget=0,ram_budget=226)
            man=selective_linker.build(plan,folder,memory={
                "code_base":code,"math_io":io})
            assert man["resource_use"]["code_and_tables_bytes"]==190
            image=(folder/"math_selective.prg").read_bytes()
            base=bytearray(65536)
            base[code:code+len(image)-2]=image[2:]
            for j,item in enumerate(man["operations"]):
                entry=int(item["entry"][1:],16)
                tag=f'u24_{i}_{j}'
                checksum=native(vice,bytearray(base),entry,code,io,tag,7680+i*2+j,folder)
                count+=N
                print(tag,"VICE PASS",N,checksum,flush=True)
    assert count==4*N,count
    print("NATIVE UDIV24+UMOD24 PASS",count)


if __name__=="__main__":
    main()
