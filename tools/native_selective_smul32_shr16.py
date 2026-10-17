#!/usr/bin/env python3
"""Native x64sc signed32x32 full 64-bit product and input-preservation check."""
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

H = 0x2000
INPUT = 0x3000
OUTPUT = 0x3800
STRIDE = 0x80
N = 96


def operands():
    edges=[(0,0),(1,0),(0,1),(1,1),(0xffffffff,0xffffffff),
           (0xffffffff,1),(1,0xffffffff),(0x80000000,2),
           (0x12345678,0xabcdef01),(0xff000000,0x01010101),
           (0x01010101,0xff000000),(255,255)]
    rng=random.Random(0xC643264)
    edges += [(rng.randrange(1<<32),rng.randrange(1<<24))
              for _ in range(N-len(edges))]
    return edges


def harness(entry,io):
    out=bytearray()
    def emit(*v):out.extend(v)
    def op(code,addr):emit(code,addr&255,addr>>8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0)
    loop=H+len(out)
    for slot,where in enumerate([io+i for i in range(4)]+[io+4+i for i in range(4)]):
        op(0xbd,INPUT+slot*STRIDE);op(0x8d,where)
    emit(0x8a,0x48);op(0x20,entry)
    emit(0x08,0x68);op(0x8d,0xc030)
    emit(0x68,0xaa)
    fields=[io+8+i for i in range(8)]+[io+i for i in range(4)]+[
        io+4+i for i in range(4)]+[0xc030]
    assert len(fields)==17
    for slot,addr in enumerate(fields):
        op(0xad,addr);op(0x9d,OUTPUT+slot*STRIDE)
    emit(0xe8,0xe0,N,0xf0,0x03);op(0x4c,loop)
    halt=H+len(out);op(0x4c,halt)
    assert len(out)<0x300
    return bytes(out),halt


def run_native(vice, prg_bytes, entry, code, io, tag, port, folder, bits=16):
    memory=bytearray(65536)
    memory[code:code+len(prg_bytes)-2]=prg_bytes[2:]
    stub,halt=harness(entry,io)
    memory[H:H+len(stub)]=stub
    tests=operands()
    for i,(x,y) in enumerate(tests):
        for col,byte in enumerate((*x.to_bytes(4,"little"),*y.to_bytes(4,"little"))):
            memory[INPUT+col*STRIDE+i]=byte
    prog=folder/(tag+".prg")
    dump=folder/(tag+".bin")
    prog.write_bytes(bytes((H&255,H>>8))+memory[H:0xC200])
    args=[vice,"-console","-silent","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),
          "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as log:
        proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=log)
        try:
            for _ in range(150):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.04)
            else:
                raise RuntimeError("Native VICE monitor timeout")
            sock.settimeout(.25)
            def command(line,needle):
                sock.sendall((line+"\n").encode())
                data=b""
                for _ in range(180):
                    try:
                        block=sock.recv(16384)
                        if not block:
                            break
                        data+=block
                        if needle.encode() in data and data.endswith(b") "):
                            break
                    except socket.timeout:
                        continue
                if needle.encode() not in data:
                    raise RuntimeError((line,data[-500:]))
            command('load "'+str(prog)+'" 0',"Loading")
            command("break "+format(halt,"04x"),"BREAK:")
            command("g "+format(H,"04x"),"Stop on  exec")
            command('bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+
                    " "+format(OUTPUT+17*STRIDE-1,"04x"),"Saving")
            sock.sendall(b"quit\n")
            sock.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    data=dump.read_bytes()
    assert len(data)==17*STRIDE
    for i,(x,y) in enumerate(tests):
        value=sum(data[j*STRIDE+i]<<(8*j) for j in range(8))
        xb=bytes(data[(8+j)*STRIDE+i] for j in range(4))
        yb=bytes(data[(12+j)*STRIDE+i] for j in range(4))
        status=data[16*STRIDE+i]
        sx=x-(1<<32) if x&0x80000000 else x
        sy=y-(1<<32) if y&0x80000000 else y
        if ((value & ((1<<48)-1))!=(((sx*sy)&((1<<64)-1))>>16) or xb!=x.to_bytes(4,"little")
                or yb!=y.to_bytes(4,"little") or status&1):
            raise AssertionError((tag,i,x,y,value,xb,yb,status))
    return hashlib.sha256(data).hexdigest()


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name installed x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="native_smul32_shr16_") as td:
        folder=Path(td)
        for i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(index,["SMUL32_SHR16"],
                zp_budget=0,ram_budget=378)
            man=selective_linker.build(plan,folder,memory={
                "code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"]==334
            assert man["resource_use"]["private_ram_scratch_bytes"]==12
            entry=int(man["operations"][0]["entry"][1:],16)
            image=(folder/"math_selective.prg").read_bytes()
            result=run_native(vice,image,entry,code,io,
                              "smul32_shr16_%04x"%code,8110+i,folder)
            total+=N
            print("NATIVE SMUL32_SHR16",hex(code),N,"PASS",result,flush=True)
    assert total==2*N
    print("NATIVE SMUL32_SHR16 2-MAP PASS",total)


if __name__=="__main__":
    main()
