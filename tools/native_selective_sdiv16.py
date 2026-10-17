#!/usr/bin/env python3
"""Native x64sc signed16/16 shared quotient/remainder, full ABI, two relocations."""
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


def signed16(v):
    return v-65536 if v&32768 else v

def divide(n,d):
    n,d=signed16(n),signed16(d)
    if not d:
        return 0,0,1
    q=abs(n)//abs(d)
    if (n<0)!=(d<0):
        q=-q
    r=n-q*d
    return q&65535,r&65535,0

def pairs():
    edges=(0,1,2,3,7,127,128,255,256,257,32767,32768,32769,65534,65535)
    selected=[(x,y) for x in edges for y in (0,1,32767,32768,65535)]
    rng=random.Random(0x5D1616)
    selected.extend((rng.randrange(65536),rng.randrange(65536))
                    for _ in range(N-len(selected)))
    assert len(selected)==N
    return selected


def harness(entry,io):
    b=bytearray()
    def emit(*v):b.extend(v)
    def op(instruction,address):emit(instruction,address&255,address>>8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0x00)
    loop=H+len(b)
    for i,where in enumerate((io+16,io+17,io+20,io+21)):
        op(0xbd,INPUT+i*STRIDE);op(0x8d,where)
    for where,value in ((io+18,0x5a),(io+19,0xa5),
                        (io+22,0x7c),(io+23,0x6b),
                        (io+26,0x29),(io+27,0x39),
                        (io+30,0x49),(io+31,0x59)):
        emit(0xa9,value);op(0x8d,where)
    emit(0x8a,0x48)
    op(0x20,entry)
    emit(0x08,0x68);op(0x8d,0xc030)
    emit(0x68,0xaa)
    fields=[io+24,io+25,io+28,io+29,0xc030,
            io+16,io+17,io+20,io+21,
            io+18,io+19,io+22,io+23,
            io+26,io+27,io+30,io+31]
    assert len(fields)==17
    for i,address in enumerate(fields):
        op(0xad,address);op(0x9d,OUTPUT+i*STRIDE)
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
        for i,v in enumerate((*n.to_bytes(2,"little"),*d.to_bytes(2,"little"))):
            memory[INPUT+i*STRIDE+idx]=v
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
        q=fields[0]|(fields[1]<<8)
        rem=fields[2]|(fields[3]<<8)
        c=fields[4]&1
        preserved=(fields[5:9],fields[9:13],fields[13:17])
        expected=divide(n,d)
        if ((q,rem,c)!=expected or
            fields[5:9]!=[n&255,n>>8,d&255,d>>8] or
            fields[9:13]!=[0x5a,0xa5,0x7c,0x6b] or
            fields[13:17]!=[0x29,0x39,0x49,0x59]):
            raise AssertionError((tag,i,n,d,q,rem,c,expected,preserved))
    return hashlib.sha256(saved).hexdigest()


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to an installed x64sc")
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="selective_sdiv16_vice_") as directory:
        folder=Path(directory)
        for sequence,(origin,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["SDIV16","SMOD16"],zp_budget=0,ram_budget=241)
            result=selective_linker.build(
                plan,folder,memory={"code_base":origin,"math_io":io})
            entry=int(result["operations"][0]["entry"][1:],16)
            assert entry==origin
            assert len(result["operations"])==2
            assert len(result["link_order"])==1
            assert result["operations"][0]["entry"]==result["operations"][1]["entry"]
            image=(folder/"math_selective.prg").read_bytes()
            digest=verify(vice,image,entry,origin,io,
                "sdiv16_%04x"%origin,8020+sequence,folder)
            print("NATIVE SDIV16_SMOD16_SHARED",hex(origin),"PASS",N,digest,flush=True)
    print("NATIVE SDIV16_SMOD16_SHARED PASS",2*N)

if __name__=="__main__":
    main()
