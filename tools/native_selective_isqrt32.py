#!/usr/bin/env python3
"""Independent headless x64sc check of source-linked ISQRT32, two RAM maps."""
from __future__ import annotations
import hashlib
from math import isqrt
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


def cases():
    edges = [0,1,2,3,4,7,8,9,15,16,17,24,25,26,255,256,257,
             65534,65535,65536,65537,0x7fffffff,0x80000000,
             0xfffffffe,0xffffffff]
    for root in (0,1,2,3,15,16,127,128,255,256,32767,32768,65534,65535):
        v=root*root
        edges.extend(x for x in range(v-2,v+3) if 0<=x<=0xffffffff)
    edges=list(dict.fromkeys(edges))
    r=random.Random(0xC643232)
    return edges[:N]+[r.getrandbits(32) for _ in range(N-len(edges))]


def harness(entry, io):
    b = bytearray()
    def emit(*v): b.extend(v)
    def absolute(opcode, addr): emit(opcode, addr & 255, addr >> 8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0x00)  # SEI CLD map RAM and X=0
    loop = H+len(b)
    for k in range(4):
        absolute(0xbd, INPUT+k*STRIDE)
        absolute(0x8d, io+16+k)
    emit(0xa9,0x55)
    absolute(0x8d, io+8)
    absolute(0x8d, io+9)
    emit(0x8a,0x48)                       # save X
    absolute(0x20, entry)
    emit(0x08,0x68)                       # save P as data, before PL[A] changes flags
    absolute(0x8d, 0xc030)
    emit(0x68,0xaa)                       # restore index
    for src,dst in ((io+8,OUTPUT),(io+9,OUTPUT+STRIDE),
                    (0xc030,OUTPUT+2*STRIDE),(io+16,OUTPUT+3*STRIDE),
                    (io+17,OUTPUT+4*STRIDE),
                    (io+18,OUTPUT+5*STRIDE),
                    (io+19,OUTPUT+6*STRIDE)):
        absolute(0xad,src)
        absolute(0x9d,dst)
    emit(0xe8,0xe0,N,0xf0,0x03)          # INX CPX #N BEQ done
    absolute(0x4c, loop)
    stop = H+len(b)
    absolute(0x4c, stop)
    return bytes(b), stop


def verify(vice, image, entry, origin, io, tag, port, folder):
    mem = bytearray(65536)
    mem[origin:origin+len(image)-2] = image[2:]
    code, stop = harness(entry, io)
    assert len(code)<0x300
    mem[H:H+len(code)]=code
    operands=cases()
    for idx,value in enumerate(operands):
        for k in range(4):
            mem[INPUT+k*STRIDE+idx]=(value>>(8*k))&255
    prg=folder/(tag+".prg")
    dump=folder/(tag+".bin")
    prg.write_bytes(bytes((H&255,H>>8))+mem[H:0xc100])
    args=[vice,"-console","-silent","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),
          "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as output:
        proc=subprocess.Popen(args,cwd=folder,stdout=output,stderr=output)
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
                        data=sock.recv(16384)
                        if not data: break
                        received+=data
                        if marker.encode() in received and received.endswith(b") "):
                            break
                    except socket.timeout:
                        continue
                if marker.encode() not in received:
                    raise RuntimeError("VICE monitor: %r %r" % (command,received[-600:]))
            monitor('load "'+str(prg)+'" 0',"Loading")
            monitor("break "+format(stop,"04x"),"BREAK:")
            monitor("g "+format(H,"04x"),"Stop on  exec")
            monitor('bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+
                    format(OUTPUT+7*STRIDE-1,"04x"),"Saving")
            sock.sendall(b"quit\n")
            sock.close()
        finally:
            proc.terminate()
            try: proc.wait(timeout=3)
            except subprocess.TimeoutExpired: proc.kill()
    result=dump.read_bytes()
    assert len(result)==7*STRIDE
    for i,n in enumerate(operands):
        root = result[i] | result[STRIDE+i]<<8
        p = result[2*STRIDE+i]
        original = sum(result[(3+k)*STRIDE+i]<<(8*k) for k in range(4))
        assert (root,original,p&1)==(isqrt(n),n,0),(tag,i,n,root,original,p)
    return hashlib.sha256(result).hexdigest()


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to a working x64sc binary")
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="selective_isqrt32_vice_") as temp:
        dest=Path(temp)
        for iteration,(origin,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(
                index,["ISQRT32"],zp_budget=0,ram_budget=246,
                pins={"ISQRT32":"link:radix4-zerozp"})
            result=selective_linker.build(
                plan,dest,memory={"code_base":origin,"math_io":io})
            entry=int(result["operations"][0]["entry"][1:],16)
            img=(dest/"math_selective.prg").read_bytes()
            assert entry==origin
            digest=verify(vice,img,entry,origin,io,
                "isqrt32_%04x"%origin,7580+iteration,dest)
            print("NATIVE ISQRT32",hex(origin),"PASS",N,digest,flush=True)
    print("NATIVE SELECTIVE ISQRT32 PASS",2*N)


if __name__=="__main__":
    main()
